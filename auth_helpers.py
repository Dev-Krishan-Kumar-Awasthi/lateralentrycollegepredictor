"""Optional user accounts — session-based auth with cloud shortlist."""
import json
import os
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

from flask import session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from models import User, CloudShortlist, Coupon


def init_auth(app):
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        # In production, always set SECRET_KEY in .env
        # Using a generated default for local dev only
        import secrets as _secrets
        secret = _secrets.token_hex(32)
        print("[SECURITY WARNING] SECRET_KEY not set in environment. "
              "Using a randomly generated key — sessions will be invalidated on restart. "
              "Set SECRET_KEY in your .env file for production.")
    app.config["SECRET_KEY"] = secret
    # ── Secure session cookie settings ──
    app.config["SESSION_COOKIE_HTTPONLY"] = True       # JS cannot read the cookie
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"     # CSRF protection
    app.config["SESSION_COOKIE_SECURE"] = False        # Set True when HTTPS is enabled
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400   # Sessions last 24h if made permanent


def login_user(user: User):
    session.permanent = False  # Session dies when browser closes
    token = str(uuid.uuid4())
    user.current_session_token = token
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.display_name or user.email.split("@")[0]
    session["session_token"] = token


def logout_user():
    session.pop("user_id", None)
    session.pop("user_email", None)
    session.pop("user_name", None)
    session.pop("session_token", None)


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    user = db.session.get(User, uid)
    if not user:
        session.clear()
        return None

    # Single Device Session Validation
    stoken = session.get("session_token")
    if not user.current_session_token:
        # Assign a token if user doesn't have one in DB yet
        token = str(uuid.uuid4())
        user.current_session_token = token
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        session["session_token"] = token
    elif stoken != user.current_session_token:
        # Token mismatch! Account logged in on another device.
        session.clear()
        session["logged_out_reason"] = "other_device"
        return None

    from datetime import date
    today_str = date.today().isoformat()
    if user.last_prediction_date != today_str:
        user.last_prediction_date = today_str
        user.predictions_today = 0
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    return user


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            if session.pop("logged_out_reason", None) == "other_device":
                return redirect(url_for('account_page', reason="logged_out_other_device"))
            if request.path.startswith("/api/"):
                return jsonify({"error": "Login required"}), 401
            return redirect(url_for("account_page", next=request.path))
        return f(*args, **kwargs)
    return wrapped


import re

def validate_password_strength(password: str) -> tuple:
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, None


def is_gibberish(text: str) -> bool:
    text_clean = text.strip().lower()
    if not text_clean:
        return True
    # Check if same char is repeated 4 times continuously
    if re.search(r'(.)\1\1\1', text_clean):
        return True
    # Keyboard walks block
    keyboard_walks = ["asdf", "sdfg", "dfgh", "fghj", "ghjk", "hjkl", "qwerty", "zxcv"]
    for walk in keyboard_walks:
        if walk in text_clean:
            return True
    return False

def validate_email_strict(email: str) -> bool:
    email = email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    
    # Common disposable / mock email domains (allow test emails used in automated testing)
    blacklisted_domains = [
        "yopmail.com", "tempmail.com", "mailinator.com", "10minutemail.com",
        "guerrillamail.com", "dispostable.com", "fakeinbox.com", "trashmail.com",
        "abc.com", "xyz.com", "test.com"
    ]
    domain = email.split('@')[-1]
    if domain in blacklisted_domains:
        return False
        
    username = email.split('@')[0]
    if is_gibberish(username) or len(username) < 3:
        return False
        
    return True


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(to_email: str, otp: str) -> tuple:
    """Sends a verification OTP to the target email asynchronously. Returns (success, message)."""
    import os
    from flask import current_app
    
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.environ.get("SMTP_PORT", "587")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    resend_api_key = os.environ.get("RESEND_API_KEY", "").strip()
    brevo_api_key = os.environ.get("BREVO_API_KEY", "").strip()
    
    # HTML template for beautiful email styling
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Password Reset Code</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-font-smoothing: antialiased;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
        <tr>
          <td align="center">
            <!-- Main Wrapper -->
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
              
              <!-- Saffron Header Strip -->
              <tr>
                <td style="background-color: #d97706; height: 5px; line-height: 5px; font-size: 1px;">&nbsp;</td>
              </tr>
              
              <!-- Logo & Brand Header -->
              <tr>
                <td align="center" style="padding: 32px 24px 20px 24px; background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);">
                  <table border="0" cellpadding="0" cellspacing="0">
                    <tr>
                      <td align="center" style="background-color: #1e3a8a; width: 64px; height: 64px; border-radius: 50%; text-align: center; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);">
                        <span style="font-size: 32px; line-height: 64px; display: block;">🔐</span>
                      </td>
                    </tr>
                  </table>
                  <h1 style="margin: 16px 0 4px 0; font-size: 20px; font-weight: 800; color: #1e3a8a; letter-spacing: -0.5px;">MP DTE Lateral Entry Predictor</h1>
                  <p style="margin: 0; font-size: 13px; color: #64748b; font-weight: 500;">Account Password Recovery</p>
                </td>
              </tr>
              
              <!-- Content Body -->
              <tr>
                <td style="padding: 0 40px 24px 40px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                      <td align="center" style="padding-top: 10px; border-top: 1px solid #f1f5f9;">
                        <h2 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 20px 0 12px 0;">Reset Your Password</h2>
                        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0 0 24px 0; text-align: center;">
                          We received a request to reset your password. Please use the 6-digit OTP code below to verify and choose a new password:
                        </p>
                      </td>
                    </tr>
                    
                    <!-- OTP Box -->
                    <tr>
                      <td align="center">
                        <table border="0" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%); border-radius: 12px; border: 1.5px solid #fde68a; width: 100%;">
                          <tr>
                            <td align="center" style="padding: 22px 16px;">
                              <div style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #d97706; font-family: 'Courier New', Courier, monospace; margin-left: 8px;">{otp}</div>
                              <div style="font-size: 11px; color: #b45309; font-weight: 600; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.5px;">Password Reset OTP</div>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    
                    <!-- Expiry Note -->
                    <tr>
                      <td align="center" style="padding-top: 16px;">
                        <table border="0" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="background-color: #fff1f2; border-radius: 20px; padding: 6px 14px; border: 1px solid #ffe4e6;">
                              <span style="font-size: 12px; color: #e11d48; font-weight: 600;">⚠️ Code expires in 10 minutes</span>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>

                    <tr>
                      <td style="padding-top: 24px; font-size: 13px; line-height: 1.5; color: #64748b; text-align: center;">
                        If you did not request a password reset, you can safely ignore this email. Your current password will remain unchanged.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              
              <!-- Divider -->
              <tr>
                <td style="padding: 0 40px;"><hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 0;"></td>
              </tr>
              
              <!-- Footer -->
              <tr>
                <td style="padding: 24px 40px 32px 40px; background-color: #fafafa; text-align: center;">
                  <p style="margin: 0 0 8px 0; font-size: 12px; color: #94a3b8; font-weight: 500;">
                    &copy; 2025 MP Lateral Entry College Predictor. All rights reserved.
                  </p>
                  <p style="margin: 0; font-size: 11px; color: #cbd5e1;">
                    This is an automated security transmission. Please do not reply directly to this mail.
                  </p>
                </td>
              </tr>
              
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    plain_text = f"""Your MP DTE Lateral Entry Predictor password reset code is:

{otp}

This code expires in 10 minutes.

If you did not request a password reset, please ignore this email.

-- MP DTE Lateral Entry College Predictor
https://lateralentrycollegepredictor.pythonanywhere.com"""

    # 1. Option A: Resend HTTP API (HTTPS Port 443 — 100% reliable on Railway & PythonAnywhere)
    if resend_api_key:
        try:
            import urllib.request
            import json
            payload = json.dumps({
                "from": os.environ.get("RESEND_FROM", "MP DTE Predictor <onboarding@resend.dev>"),
                "to": [to_email],
                "subject": f"Password Reset Code: {otp} - MP DTE Lateral Entry Predictor",
                "html": html,
                "text": plain_text
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=payload,
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status in (200, 201):
                    print(f"[RESEND SUCCESS] Email sent to {to_email}")
                    return True, "Email sent successfully via Resend API"
        except Exception as e:
            print(f"[RESEND ERROR] {e}")

    # 2. Option B: Brevo HTTP API (HTTPS Port 443 — 100% reliable on Railway & PythonAnywhere)
    if brevo_api_key:
        try:
            import urllib.request
            import json
            sender_email = os.environ.get("SMTP_USERNAME", "admin@lateralentry.in")
            payload = json.dumps({
                "sender": {"name": "MP DTE Predictor", "email": sender_email},
                "to": [{"email": to_email}],
                "subject": f"Password Reset Code: {otp} - MP DTE Lateral Entry Predictor",
                "htmlContent": html,
                "textContent": plain_text
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.brevo.com/v3/smtp/email",
                data=payload,
                headers={
                    "api-key": brevo_api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status in (200, 201):
                    print(f"[BREVO SUCCESS] Email sent to {to_email}")
                    return True, "Email sent successfully via Brevo API"
        except Exception as e:
            print(f"[BREVO ERROR] {e}")

    # 3. Fallback/Simulator if SMTP credentials are not configured
    if not smtp_username or not smtp_password or is_testing or to_email.endswith('@example.com'):
        print(f"\n=======================================================")
        print(f"[SMTP SIMULATOR] Email verification code for {to_email} is: {otp}")
        print(f"To configure live SMTP, set SMTP_USERNAME and SMTP_PASSWORD in your env.")
        print(f"=======================================================\n")
        return True, "Simulator Mode: OTP logged to console."

    # 4. Option C: Direct SMTP
    import threading
    import uuid
    from email.utils import formatdate
    
    clean_user = smtp_username.strip()
    clean_pass = smtp_password.strip().replace(" ", "")
    smtp_port = int(smtp_port_str)
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Password Reset Code: {otp} - MP DTE Lateral Entry Predictor"
    msg["From"] = f"MP DTE Predictor <{clean_user}>"
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = f"<{uuid.uuid4()}@lateralentrycollegepredictor.pythonanywhere.com>"
    msg["X-Mailer"] = "MP-Lateral-Entry-Predictor/1.0"
    msg["Reply-To"] = clean_user
    msg["Precedence"] = "transactional"
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    def _do_send():
        ports_to_try = [465, 587] if smtp_port in (465, 587) else [smtp_port, 465, 587]
        for p in ports_to_try:
            server = None
            try:
                if p == 465:
                    server = smtplib.SMTP_SSL(smtp_server, p, timeout=8)
                else:
                    server = smtplib.SMTP(smtp_server, p, timeout=8)
                    server.starttls()
                server.login(clean_user, clean_pass)
                server.sendmail(clean_user, to_email, msg.as_string())
                server.quit()
                print(f"[SMTP SUCCESS] Verification email sent to {to_email} via port {p}.")
                return True
            except Exception as err:
                print(f"[SMTP WARNING] Port {p} failed: {err}")
                if server:
                    try:
                        server.quit()
                    except Exception:
                        pass
        return False

    # Attempt direct send, or background thread if needed
    threading.Thread(target=_do_send, name=f"EmailThread-{to_email}").start()
    return True, "Code dispatched"


def pre_validate_registration(email: str, password: str, display_name: str = "",
                              mobile_number: str = "", polytechnic_college: str = "",
                              diploma_branch: str = "", cgpa: float = 0.0,
                              category: str = "UR", gender: str = "M") -> tuple:
    email = email.strip().lower()
    display_name = display_name.strip()
    mobile = mobile_number.strip()
    poly_col = polytechnic_college.strip()
    diploma_branch = diploma_branch.strip()
    category = category.strip()
    gender = gender.strip()

    # Mandatory field check
    if not display_name:
        return None, "Full Name is mandatory"
    if not email:
        return None, "Email address is mandatory"
    if not password:
        return None, "Password is mandatory"
    if not mobile:
        return None, "Mobile number is mandatory"
    if not poly_col:
        return None, "Polytechnic College name is mandatory"
    if not diploma_branch:
        return None, "Diploma branch selection is mandatory"
    if not cgpa:
        return None, "Diploma CGPA is mandatory"

    # 1. Full Name check
    if len(display_name) < 3:
        return None, "Full Name must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z\s.]+$', display_name):
        return None, "Full Name can only contain letters, spaces, and dots"
    if is_gibberish(display_name):
        return None, "Please enter a valid, real Full Name"

    # 2. Email Validation
    if not validate_email_strict(email):
        return None, "Please enter a valid email address (no disposable/gibberish emails)"
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"

    # 3. Password Validation
    is_ok, pass_err = validate_password_strength(password)
    if not is_ok:
        return None, pass_err

    # 4. Mobile Number Validation
    if not re.match(r'^[6-9]\d{9}$', mobile):
        return None, "Please enter a valid 10-digit Indian mobile number (starting with 6, 7, 8, or 9)"
    # Prevent sequential/repeating digits like 9999999999, 1234567890
    if len(set(mobile)) <= 2:
        return None, "Invalid mobile number: Too many repeating digits"
    if mobile in ["1234567890", "0987654321"]:
        return None, "Invalid mobile number: Sequential numbers are not allowed"

    # 5. Polytechnic College Validation
    if len(poly_col) < 6:
        return None, "College name must be at least 6 characters long"
    if not re.search(r'[a-zA-Z]', poly_col):
        return None, "College name must contain letters"
    if is_gibberish(poly_col):
        return None, "Please enter a valid Polytechnic College name"

    # 6. CGPA Validation
    try:
        cgpa_val = float(cgpa)
        if cgpa_val < 2.0 or cgpa_val > 10.0:
            return None, "Diploma CGPA must be a valid number between 2.0 and 10.0"
    except (ValueError, TypeError):
        return None, "Please enter a valid decimal CGPA"

    # 7. Category & Gender options
    if category not in ["UR", "OBC", "SC", "ST"]:
        return None, "Please select a valid reservation category"
    if gender not in ["M", "F"]:
        return None, "Please select a valid gender"

    return {
        "email": email,
        "password": password,
        "display_name": display_name,
        "mobile_number": mobile,
        "polytechnic_college": poly_col,
        "diploma_branch": diploma_branch,
        "cgpa": cgpa_val,
        "category": category,
        "gender": gender
    }, None


def register_user(email: str, password: str, display_name: str = "",
                  mobile_number: str = "", polytechnic_college: str = "",
                  diploma_branch: str = "", cgpa: float = 0.0,
                  category: str = "UR", gender: str = "M",
                  coupon_used: str = None, referred_by_id: int = None) -> tuple:
    
    sanitized, err = pre_validate_registration(
        email=email, password=password, display_name=display_name,
        mobile_number=mobile_number, polytechnic_college=polytechnic_college,
        diploma_branch=diploma_branch, cgpa=cgpa,
        category=category, gender=gender
    )
    # Note: If called from inside authenticate() or seeds, we bypass
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if err and email.strip().lower() != admin_email:
        return None, err

    # Use sanitized inputs if available, else fall back to raw (e.g. for hardcoded admin seeding)
    data = sanitized if sanitized else {
        "email": email.strip().lower(),
        "password": password,
        "display_name": display_name.strip(),
        "mobile_number": mobile_number.strip(),
        "polytechnic_college": polytechnic_college.strip(),
        "diploma_branch": diploma_branch.strip(),
        "cgpa": float(cgpa),
        "category": category.strip(),
        "gender": gender.strip()
    }

    from models import get_referral_coins
    ref_coins = get_referral_coins()
    initial_coins = 0
    if coupon_used:
        if not referred_by_id:
            coupon = Coupon.query.filter_by(code=coupon_used, is_active=True).first()
            if coupon:
                initial_coins = getattr(coupon, 'coins_reward', 50) or 50
        else:
            initial_coins = ref_coins

    user = User(
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        display_name=data["display_name"],
        mobile_number=data["mobile_number"],
        polytechnic_college=data["polytechnic_college"],
        diploma_branch=data["diploma_branch"],
        cgpa=data["cgpa"],
        category=data["category"],
        gender=data["gender"],
        coupon_used=coupon_used,
        referred_by_id=referred_by_id,
        coins=initial_coins
    )
    db.session.add(user)
    
    if referred_by_id:
        referrer = db.session.get(User, referred_by_id)
        if referrer:
            referrer.coins = (referrer.coins or 0) + ref_coins

    db.session.commit()
    return user, None


def authenticate(email: str, password: str) -> tuple:
    email = email.strip().lower()
    
    # Hardcoded Admin authentication bypass to guarantee success
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    admin_pass = os.getenv("ADMIN_PASSWORD", "kkawasthi@202956@kka")
    if email == admin_email and password == admin_pass:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                display_name="Admin",
                mobile_number="9999999999",
                polytechnic_college="System Admin",
                diploma_branch="Admin",
                cgpa=10.0,
                category="UR",
                gender="M"
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Ensure the password hash matches the hardcoded one
            if not check_password_hash(user.password_hash, password):
                user.password_hash = generate_password_hash(password)
                db.session.commit()
        return user, None

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None, "Invalid email or password"
    return user, None


def save_cloud_shortlist(user_id: int, items: list, name: str = "My Shortlist") -> CloudShortlist:
    payload = json.dumps(items)
    existing = CloudShortlist.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        existing.items_json = payload
        db.session.commit()
        return existing
    row = CloudShortlist(user_id=user_id, name=name, items_json=payload)
    db.session.add(row)
    db.session.commit()
    return row


def load_cloud_shortlist(user_id: int, name: str = "My Shortlist") -> list:
    from models import User, SeatInfo, CgpaRankRange
    from predictor import estimate_rank_range, calc_probability, BRANCH_NAMES
    from college_meta import infer_city_from_college_name

    user = db.session.get(User, user_id)
    row = CloudShortlist.query.filter_by(user_id=user_id, name=name).first()
    if not row:
        return []
    try:
        items = json.loads(row.items_json)
        if not isinstance(items, list):
            return []
        normalized = []
        seen = set()
        for item in items:
            college_name = ""
            branch_code = ""
            year_val = 2025
            
            if isinstance(item, str):
                parts = item.split('|')
                if parts:
                    college_name = parts[0]
                    branch_code = parts[1] if len(parts) > 1 else ""
                    if len(parts) == 3:
                        try:
                            year_val = int(parts[2])
                        except ValueError:
                            year_val = 2025
                    elif len(parts) >= 4:
                        try:
                            year_val = int(parts[3])
                        except ValueError:
                            year_val = 2025
            elif isinstance(item, dict):
                college_name = item.get('college_name', '')
                branch_code = item.get('branch', '') or item.get('branch_code', '')
                try:
                    year_val = int(item.get('year', 2025))
                except (ValueError, TypeError):
                    year_val = 2025
            
            if not college_name:
                continue

            key = (college_name.strip().lower(), branch_code.strip().lower())
            if key in seen:
                continue
            seen.add(key)

            branch_name = BRANCH_NAMES.get(branch_code.strip().upper(), branch_code)
            city = infer_city_from_college_name(college_name)
            
            prob_type = "N/A"
            prob_percent = None
            if user and user.cgpa and user.category and user.gender:
                cgpa_map = CgpaRankRange.query.filter_by(year=year_val).order_by(CgpaRankRange.cgpa.desc()).all()
                if cgpa_map:
                    min_rank, max_rank = estimate_rank_range(cgpa_map, user.cgpa)
                    allowed_genders = ["F", "M", "OP"] if user.gender == "F" else ["M", "OP"]
                    seat = SeatInfo.query.filter(
                        SeatInfo.college_name == college_name,
                        SeatInfo.branch == branch_code,
                        SeatInfo.category == user.category,
                        SeatInfo.gender.in_(allowed_genders),
                        SeatInfo.year == year_val
                    ).order_by(SeatInfo.closing_rank.desc()).first()
                    closing_rank = None
                    if seat:
                        closing_rank = seat.closing_rank
                        prob_percent = calc_probability(min_rank, max_rank, seat.opening_rank, seat.closing_rank)
                        if prob_percent >= 75:
                            prob_type = "Safe"
                        elif prob_percent >= 40:
                            prob_type = "Moderate"
                        else:
                            prob_type = "Borderline"
            
            normalized.append({
                "college_name": college_name,
                "branch": branch_code,
                "branch_name": branch_name,
                "city": city,
                "year": year_val,
                "prob_type": prob_type,
                "prob_percent": prob_percent,
                "closing_rank": closing_rank
            })
        return normalized
    except json.JSONDecodeError:
        return []


def reset_password_in_db(email: str, new_password: str) -> tuple:
    email = email.strip().lower()
    is_ok, pass_err = validate_password_strength(new_password)
    if not is_ok:
        return False, pass_err
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "User not found"
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return True, None


def pre_validate_profile_update(current_user_id: int, display_name: str, mobile_number: str, 
                                polytechnic_college: str, diploma_branch: str, cgpa: float, 
                                category: str, gender: str) -> tuple:
    display_name = display_name.strip()
    mobile = mobile_number.strip()
    poly_col = polytechnic_college.strip()
    diploma_branch = diploma_branch.strip()
    category = category.strip()
    gender = gender.strip()

    # Mandatory field check
    if not display_name:
        return None, "Full Name is mandatory"
    if not mobile:
        return None, "Mobile number is mandatory"
    if not poly_col:
        return None, "Polytechnic College name is mandatory"
    if not diploma_branch:
        return None, "Diploma branch selection is mandatory"
    if not cgpa:
        return None, "Diploma CGPA is mandatory"

    # 1. Full Name check
    if len(display_name) < 3:
        return None, "Full Name must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z\s.]+$', display_name):
        return None, "Full Name can only contain letters, spaces, and dots"
    if is_gibberish(display_name):
        return None, "Please enter a valid, real Full Name"

    # 2. Mobile Number Validation
    if not re.match(r'^[6-9]\d{9}$', mobile):
        return None, "Please enter a valid 10-digit Indian mobile number (starting with 6, 7, 8, or 9)"
    if len(set(mobile)) <= 2:
        return None, "Invalid mobile number: Too many repeating digits"
    if mobile in ["1234567890", "0987654321"]:
        return None, "Invalid mobile number: Sequential numbers are not allowed"

    # 3. Polytechnic College Validation
    if len(poly_col) < 6:
        return None, "College name must be at least 6 characters long"
    if not re.search(r'[a-zA-Z]', poly_col):
        return None, "College name must contain letters"
    if is_gibberish(poly_col):
        return None, "Please enter a valid Polytechnic College name"

    # 4. CGPA Validation
    try:
        cgpa_val = float(cgpa)
        if cgpa_val < 2.0 or cgpa_val > 10.0:
            return None, "Diploma CGPA must be a valid number between 2.0 and 10.0"
    except (ValueError, TypeError):
        return None, "Please enter a valid decimal CGPA"

    # 5. Category & Gender options
    if category not in ["UR", "OBC", "SC", "ST"]:
        return None, "Please select a valid reservation category"
    if gender not in ["M", "F"]:
        return None, "Please select a valid gender"

    sanitized = {
        "display_name": display_name,
        "mobile_number": mobile,
        "polytechnic_college": poly_col,
        "diploma_branch": diploma_branch,
        "cgpa": cgpa_val,
        "category": category,
        "gender": gender
    }
    return sanitized, None


def send_broadcast_email(recipients: list, subject: str, body_content: str, template_type: str = 'general') -> tuple:
    """Sends a custom broadcast notification email with HTML templates and student dynamic placeholders. Returns (success_count, fail_count)."""
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.environ.get("SMTP_PORT", "587")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    # Check if app is running in testing/mock mode or target emails are test addresses
    from flask import current_app
    is_testing = False
    try:
        is_testing = current_app.config.get('TESTING', False) or current_app.testing
    except Exception:
        pass

    def check_is_mock(rec):
        if isinstance(rec, str):
            return rec.endswith('@example.com')
        elif isinstance(rec, dict):
            return rec.get('email', '').endswith('@example.com')
        return False

    if not smtp_username or not smtp_password or is_testing or any(check_is_mock(r) for r in recipients):
        print(f"\n=======================================================")
        print(f"[SMTP SIMULATOR] Broadcast email to {len(recipients)} users. (Template: {template_type})")
        print(f"Subject: {subject}")
        print(f"Body:\n{body_content}")
        print(f"=======================================================\n")
        return len(recipients), 0
    
    success_count = 0
    fail_count = 0
    
    TEMPLATES = {
        'general': {
            'strip_color': '#ff9933', # Saffron
            'icon': '🎓',
            'banner_bg': '#1e3a8a', # Navy
            'header_title': 'MP DTE Lateral Entry Predictor',
            'sub_title': 'Official Counselling Alerts & Updates'
        },
        'critical': {
            'strip_color': '#dc2626', # Red
            'icon': '⚠️',
            'banner_bg': '#dc2626', # Red
            'header_title': 'CRITICAL ALERTS & TIMELINES',
            'sub_title': 'Urgent Counselling Notification'
        },
        'choice_alert': {
            'strip_color': '#7c3aed', # Purple
            'icon': '⚡',
            'banner_bg': '#7c3aed', # Purple
            'header_title': 'CHOICE FILLING ALERT & STRATEGY',
            'sub_title': 'Smart Choice List Recommendation'
        }
    }
    
    cfg = TEMPLATES.get(template_type, TEMPLATES['general'])
    
    try:
        smtp_port = int(smtp_port_str)
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            
        clean_user = smtp_username.strip()
        clean_pass = smtp_password.strip().replace(" ", "")
        server.login(clean_user, clean_pass)
        
        for item in recipients:
            if isinstance(item, str):
                email = item
                r_name = "Student"
                r_cgpa = "N/A"
                r_category = "UR"
                r_branch = "N/A"
            elif isinstance(item, dict):
                email = item.get("email")
                r_name = item.get("name") or "Student"
                r_cgpa = str(item.get("cgpa") or "N/A")
                r_category = item.get("category") or "UR"
                r_branch = item.get("branch") or "N/A"
            else:
                continue

            if not email:
                continue

            try:
                p_subject = subject.replace("{name}", r_name).replace("{cgpa}", r_cgpa).replace("{category}", r_category).replace("{branch}", r_branch)
                p_body = body_content.replace("{name}", r_name).replace("{cgpa}", r_cgpa).replace("{category}", r_category).replace("{branch}", r_branch)

                msg = MIMEMultipart("alternative")
                msg["Subject"] = p_subject
                msg["From"] = f"MP Polytechnic Predictor Alert <{smtp_username}>"
                msg["To"] = email
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="utf-8">
                  <title>{p_subject}</title>
                </head>
                <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f8fafc; color: #1e293b; -webkit-font-smoothing: antialiased;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
                    <tr>
                      <td align="center">
                        <!-- Main Wrapper -->
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
                          
                          <!-- Dynamic Header Strip -->
                          <tr>
                            <td style="background-color: {cfg['strip_color']}; height: 5px; line-height: 5px; font-size: 1px;">&nbsp;</td>
                          </tr>
                          
                          <!-- Logo & Brand Header -->
                          <tr>
                            <td align="center" style="padding: 32px 24px 20px 24px; background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);">
                              <table border="0" cellpadding="0" cellspacing="0">
                                <tr>
                                  <td align="center" style="background-color: {cfg['banner_bg']}; width: 64px; height: 64px; border-radius: 50%; text-align: center; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);">
                                    <span style="font-size: 32px; line-height: 64px; display: block;">{cfg['icon']}</span>
                                  </td>
                                </tr>
                              </table>
                              <h1 style="margin: 16px 0 4px 0; font-size: 20px; font-weight: 800; color: #1e3a8a; letter-spacing: -0.5px;">{cfg['header_title']}</h1>
                              <p style="margin: 0; font-size: 13px; color: #64748b; font-weight: 500;">{cfg['sub_title']}</p>
                            </td>
                          </tr>
                          
                          <!-- Content Body -->
                          <tr>
                            <td style="padding: 0 40px 24px 40px;">
                              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                  <td style="padding-top: 10px; border-top: 1px solid #f1f5f9;">
                                    <h2 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 20px 0 12px 0; text-align: center;">{p_subject}</h2>
                                    <div style="font-size: 15px; line-height: 1.6; color: #334155; margin: 0 0 24px 0; white-space: pre-line;">
                                        {p_body}
                                    </div>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                          
                          <!-- Divider -->
                          <tr>
                            <td style="padding: 0 40px;"><hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 0;"></td>
                          </tr>
                          
                          <!-- Footer -->
                          <tr>
                            <td style="padding: 24px 40px 32px 40px; background-color: #fafafa; text-align: center;">
                              <p style="margin: 0 0 8px 0; font-size: 12px; color: #94a3b8; font-weight: 500;">
                                &copy; 2025 MP Lateral Entry College Predictor. All rights reserved.
                              </p>
                              <p style="margin: 0; font-size: 11px; color: #cbd5e1; line-height: 1.4;">
                                You received this email because you subscribed to counselling alerts on the MP Polytechnic Predictor.
                                <br>To unsubscribe, log in to your account dashboard and toggle the alerts switch.
                              </p>
                            </td>
                          </tr>
                          
                        </table>
                      </td>
                    </tr>
                  </table>
                </body>
                </html>
                """
                msg.attach(MIMEText(html, "html"))
                server.sendmail(smtp_username, email, msg.as_string())
                success_count += 1
            except Exception as e:
                print(f"[SMTP BROADCAST ERROR] Failed to send to {email}: {e}")
                fail_count += 1
                
        server.quit()
        return success_count, fail_count
    except Exception as e:
        print(f"[SMTP BROADCAST CONNECTION ERROR]: {e}")
        return 0, len(recipients)
