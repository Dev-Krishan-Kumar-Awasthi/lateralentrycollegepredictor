import json
import os
import re
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, redirect, jsonify, session, url_for, flash, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import quote as url_quote
from db import db
from predictor import (
    fetch_cgpa_to_rank_map, estimate_rank_range,
    fetch_colleges_from_rank, search_colleges,
    calc_probability, MP_CITIES, get_college_detail,
    BRANCH_NAMES, get_compare_data, run_counselling_simulation,
    get_seat_heatmap, get_cutoff_chart_data, get_merit_insights,
)
from college_meta import (
    get_data_metadata, get_counselling_schedule, save_counselling_schedule,
    MP_DISTRICTS, distance_from_home, get_fee_info, format_fee_display,
    infer_city_from_college_name, get_district_for_city, get_college_info_bundle,
    get_city_coords, get_placement_info, get_college_coordinates,
    get_college_profile, get_college_image,
)
from google_college_service import api_key_configured
from smart_choices import build_smart_choices
from auth_helpers import (
    init_auth, login_user, logout_user, current_user,
    register_user, authenticate, login_required,
    save_cloud_shortlist, load_cloud_shortlist,
    pre_validate_registration, send_otp_email, reset_password_in_db,
    pre_validate_profile_update, send_broadcast_email,
)
from models import CollegeReview, User, SeatInfo, ChoiceVault, VisitorCount, Coupon, CgpaRankRange, RecommendationChoice, SiteSetting, get_referral_coins
from faq_data import (
    FAQ_LIST, get_faq_by_slug, get_faqs_by_category, get_all_categories
)
def normalize_name(name: str) -> str:
    n = name.lower()
    n = n.replace("institure", "institute")
    n = n.replace("centre", "center")
    n = n.replace("&", "and")
    n = n.replace(",", " ")
    n = n.replace(".", " ")
    n = n.replace("-", " ")
    n = " ".join(n.split())
    return n



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DB_PATH = os.path.join(BASE_DIR, 'instance', 'data.db').replace('\\', '/')
if not INSTANCE_DB_PATH.startswith('/'):
    INSTANCE_DB_PATH = '/' + INSTANCE_DB_PATH
db_url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI") or f"sqlite://{INSTANCE_DB_PATH}"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
init_auth(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.errorhandler(429)
def ratelimit_handler(e):
    if request.path.startswith('/api/'):
        return jsonify(error="Too many requests. Please try again later.", description=str(e.description)), 429
    return render_template('429.html'), 429

# ── Security Headers (injected on every response) ───────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Cache static assets aggressively for 1 year
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    # Block admin paths from being cached by browser
    elif request.path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response

db.init_app(app)

app.jinja_env.filters['urlencode_val'] = lambda s: url_quote(str(s), safe='')
app.jinja_env.filters['branch_name'] = lambda s: BRANCH_NAMES.get(str(s).strip(), s)

from datetime import timezone, timedelta

def to_ist(dt):
    if not dt:
        return dt
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone(timedelta(hours=5, minutes=30)))

app.jinja_env.filters['to_ist'] = to_ist


@app.context_processor
def inject_years():
    return dict(
        years_list=YEARS,
        referral_coins_reward=get_referral_coins()
    )


RANK_MAPS_CACHE = {}
YEARS = [2025, 2024]


def refresh_years_list():
    global YEARS
    try:
        years_seats = [y[0] for y in db.session.query(SeatInfo.year).distinct().all() if y[0]]
        years_ranks = [y[0] for y in db.session.query(CgpaRankRange.year).distinct().all() if y[0]]
        all_years = set(years_seats + years_ranks)
        if all_years:
            YEARS.clear()
            YEARS.extend(sorted(list(all_years), reverse=True))
    except Exception as e:
        print("Failed to refresh years list:", e)


def fetch_rank_maps_cache():
    refresh_years_list()
    for year in YEARS:
        RANK_MAPS_CACHE[year] = fetch_cgpa_to_rank_map(year)


def get_colleges(cgpa, branch, category, gender, college_type, domicile='Y',
                 city='All', district='All', home_city='All', max_distance_km=None):
    result = {}
    for year in YEARS:
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        min_rank, max_rank = estimate_rank_range(cgpa_to_rank_map, cgpa)
        raw_colleges = fetch_colleges_from_rank(
            min_rank, max_rank, branch, category, gender, college_type, year, domicile
        )

        if city and city != 'All':
            raw_colleges = [c for c in raw_colleges
                            if city.lower() in c.college_name.lower()]

        if district and district != 'All':
            raw_colleges = [
                c for c in raw_colleges
                if get_district_for_city(infer_city_from_college_name(c.college_name) or '') == district
                or (infer_city_from_college_name(c.college_name) and
                    district.lower() in (infer_city_from_college_name(c.college_name) or '').lower())
            ]

        # Build previous year closing ranks lookup for current year colleges
        lookup_prev = {}
        prev_year = year - 1
        if raw_colleges:
            names = list(set(c.college_name for c in raw_colleges))
            branches = list(set(c.branch for c in raw_colleges))
            if names and branches:
                rows_prev = SeatInfo.query.filter(
                    SeatInfo.year == prev_year,
                    SeatInfo.college_name.in_(names),
                    SeatInfo.branch.in_(branches),
                    SeatInfo.category == category,
                    SeatInfo.gender == gender,
                    SeatInfo.domicile == domicile
                ).all()
                lookup_prev = {
                    (r.college_name, r.branch): r.closing_rank
                    for r in rows_prev
                }

        college_data = []
        for c in raw_colleges:
            prob = calc_probability(min_rank, max_rank, c.opening_rank, c.closing_rank)
            dist = distance_from_home(home_city, c.college_name) if home_city and home_city != 'All' else None
            dist_km = dist.get('distance_km') if dist else None
            if max_distance_km and dist_km is not None and dist_km > int(max_distance_km):
                continue
            fee = get_fee_info(c.college_name, c.college_type)
            
            trend_val = None
            trend_diff = None
            closing_prev = lookup_prev.get((c.college_name, c.branch))
            if closing_prev is not None:
                trend_diff = closing_prev - c.closing_rank
                if trend_diff > 0:
                    trend_val = 'up'  # Harder (closing rank dropped, competition went up)
                elif trend_diff < 0:
                    trend_val = 'down'  # Easier (closing rank rose, competition went down)
                else:
                    trend_val = 'stable'
                        
            college_data.append({
                'college': c,
                'probability': prob,
                'distance_km': dist_km,
                'distance_text': dist.get('distance_text') if dist else None,
                'distance_source': dist.get('source') if dist else None,
                'fee_display': format_fee_display(fee),
                'fee': fee,
                'district': get_district_for_city(infer_city_from_college_name(c.college_name) or city or ''),
                'coords': get_college_coordinates(c.college_name),
                'trend_val': trend_val,
                'trend_diff': trend_diff,
            })

        college_data.sort(key=lambda x: (
            -(x['probability']),
            x['distance_km'] if x['distance_km'] is not None else 99999,
        ))

        result[year] = {
            'colleges': college_data,
            'min_rank': min_rank,
            'max_rank': max_rank,
        }
    return result


def get_rank(cgpa):
    result = {}
    for year in YEARS:
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        min_rank, max_rank = estimate_rank_range(cgpa_to_rank_map, cgpa)
        result[year] = {"min_rank": min_rank, "max_rank": max_rank}
    return result


def estimate_cgpa_for_rank(cgpa_to_rank_map, rank):
    if not cgpa_to_rank_map:
        return 0.0
    
    # Check if the rank lies directly inside any range in the list
    for r in cgpa_to_rank_map:
        if r.min_rank <= rank <= r.max_rank:
            return r.cgpa
            
    # If the rank is larger than the worst rank in the map:
    if rank >= cgpa_to_rank_map[-1].max_rank:
        return cgpa_to_rank_map[-1].cgpa
        
    # If the rank is smaller than the best rank in the map:
    if rank <= cgpa_to_rank_map[0].min_rank:
        return cgpa_to_rank_map[0].cgpa
        
    # Otherwise, it falls between two rows in the sorted list.
    # The map is ordered by cgpa descending, so min_rank/max_rank is ascending.
    for i in range(len(cgpa_to_rank_map) - 1):
        r1 = cgpa_to_rank_map[i]
        r2 = cgpa_to_rank_map[i + 1]
        
        # If target rank is between r1.max_rank and r2.min_rank
        if r1.max_rank < rank < r2.min_rank:
            c1 = r1.cgpa
            c2 = r2.cgpa
            denom = r2.min_rank - r1.max_rank
            if denom == 0:
                return c1
            ratio = (rank - r1.max_rank) / denom
            return round(c1 + (c2 - c1) * ratio, 2)
            
    return 0.0


def get_cgpa_for_rank(rank):
    result = {}
    for year in YEARS:
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        result[year] = estimate_cgpa_for_rank(cgpa_to_rank_map, rank)
    return result


def _resolve_simulation_rank(cgpa, year, rank_mode):
    cgpa_map = RANK_MAPS_CACHE[year]
    min_rank, max_rank = estimate_rank_range(cgpa_map, cgpa)
    if rank_mode == 'best':
        return min_rank, min_rank, max_rank
    if rank_mode == 'worst':
        return max_rank, min_rank, max_rank
    avg = (min_rank + max_rank) // 2
    return avg, min_rank, max_rank


@app.context_processor
def inject_globals():
    meta = get_data_metadata()
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    is_admin = user and user.email.strip().lower() == admin_email
    
    from flask import g
    total_visits = getattr(g, 'total_visits', 0)
    if total_visits == 0:
        try:
            counter = db.session.get(VisitorCount, 1)
            if counter:
                total_visits = counter.count
        except Exception:
            pass
            
    return {
        'data_last_updated': meta.get('last_updated', '2025'),
        'data_years': meta.get('years_available', YEARS),
        'current_user': user,
        'mp_districts': MP_DISTRICTS,
        'mp_cities': MP_CITIES,
        'google_api_enabled': api_key_configured(),
        'is_admin': bool(is_admin),
        'total_visits': total_visits,
        'city_coords': get_city_coords(),
        'schedule': get_counselling_schedule(),
        'all_faqs': FAQ_LIST,
        'prefill_reg': None,
        'congrats_coupon_for': None,
        'congrats_referral_by': None,
    }


@app.before_request
def count_visitor():
    # Only count page requests (endpoints returning HTML, skip assets and api paths)
    if request.endpoint and not request.endpoint.startswith('static') and not request.path.startswith('/api/'):
        try:
            from flask import g, session
            counter = db.session.get(VisitorCount, 1)
            if not counter:
                counter = VisitorCount(id=1, count=0)
                db.session.add(counter)
                db.session.commit()
            
            # Increment only once per session
            if not session.get('has_visited'):
                counter.count += 1
                db.session.commit()
                session['has_visited'] = True
                
            g.total_visits = counter.count
        except Exception as e:
            db.session.rollback()
            print("Visitor count increment failed:", e)


DEFAULT_RECOMMENDED_CHOICES = [
    {"sn": 1, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CSE", "display_name": "SGSITS Indore: CS"},
    {"sn": 2, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "IT", "display_name": "SGSITS Indore: IT"},
    {"sn": 3, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CSE", "display_name": "IET DAVV Indore: CS"},
    {"sn": 4, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "IT", "display_name": "IET DAVV Indore: IT"},
    {"sn": 5, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "ET", "display_name": "SGSITS Indore: ETC"},
    {"sn": 6, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "ET", "display_name": "IET DAVV Indore: ETC"},
    {"sn": 7, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "CSE", "display_name": "JEC Jabalpur: CS"},
    {"sn": 8, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "IT", "display_name": "JEC Jabalpur: IT"},
    {"sn": 9, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EE", "display_name": "SGSITS Indore: EE"},
    {"sn": 10, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EI", "display_name": "SGSITS Indore: E&I"},
    {"sn": 11, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "MECH", "display_name": "SGSITS Indore: Mech."},
    {"sn": 12, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "EI", "display_name": "IET DAVV Indore: E&I"},
    {"sn": 13, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "CSE", "display_name": "MITS Gwalior: CS"},
    {"sn": 14, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "IT", "display_name": "MITS Gwalior: IT"},
    {"sn": 15, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "CSE", "display_name": "UIT RGPV Bhopal: CS"},
    {"sn": 16, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "IT", "display_name": "UIT RGPV Bhopal: IT"},
    {"sn": 17, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "CSE", "display_name": "LNCT Bhopal [Main]: CS"},
    {"sn": 18, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "CSE", "display_name": "Acropolis Indore: CS"},
    {"sn": 19, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "IT", "display_name": "Acropolis Indore: IT"},
    {"sn": 20, "db_name": "Oriental Institute of Science & Technology, Bhopal (1995)", "branch": "CSE", "display_name": "Oriental Bhopal: CS/IT"},
    {"sn": 21, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "ET", "display_name": "JEC Jabalpur: ETC"},
    {"sn": 22, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "EE", "display_name": "JEC Jabalpur: EE"},
    {"sn": 23, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "ET", "display_name": "MITS Gwalior: EC"},
    {"sn": 24, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "EE", "display_name": "MITS Gwalior: EE"},
    {"sn": 25, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "ET", "display_name": "RGPV Bhopal: EC"},
    {"sn": 26, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "EE", "display_name": "RGPV Bhopal: EE"},
    {"sn": 27, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CIVIL", "display_name": "SGSITS Indore: Civil"},
    {"sn": 28, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CIVIL", "display_name": "IET DAVV Indore: Civil"},
    {"sn": 29, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "CSE", "display_name": "SATI Vidisha: CS"},
    {"sn": 30, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "IT", "display_name": "SATI Vidisha: IT"},
    {"sn": 31, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "CSE", "display_name": "IPS Indore: CS"},
    {"sn": 32, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "IT", "display_name": "IPS Indore: IT"},
    {"sn": 33, "db_name": "Lakshmi Narain College of Technology & Science, Bhopal (2006)", "branch": "CSE", "display_name": "LNCT Science: CS"},
    {"sn": 34, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "AIML", "display_name": "LNCT Main: CS SP."},
    {"sn": 35, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "AIML", "display_name": "Acropolis: CS SP."},
    {"sn": 36, "db_name": "Rewa Engineering College, Rewa (REC) (1964)", "branch": "CSE", "display_name": "Rewa Engineering: CS"},
    {"sn": 37, "db_name": "UJJAIN ENGINEERING COLLEGE (FORMERLY GOVT. ENGG. COLLEGE ESTB. IN 1966)", "branch": "CSE", "display_name": "UGC: CS"},
]


with app.app_context():
    db.create_all()
    # Seed default recommended choice list if empty
    try:
        if RecommendationChoice.query.count() == 0:
            for item in DEFAULT_RECOMMENDED_CHOICES:
                db.session.add(RecommendationChoice(
                    sn=item["sn"],
                    db_name=item["db_name"],
                    branch=item["branch"],
                    display_name=item["display_name"]
                ))
            db.session.commit()
            print("Successfully seeded default recommendations.")
    except Exception as e:
        db.session.rollback()
        print("Failed to seed default recommendations:", e)
    # Dynamic SQLite migration for User table columns and Performance Indexes
    try:
        from sqlalchemy import text
        for col, col_type in [
            ("mobile_number", "TEXT"),
            ("polytechnic_college", "TEXT"),
            ("diploma_branch", "TEXT"),
            ("cgpa", "REAL"),
            ("category", "TEXT"),
            ("gender", "TEXT"),
            ("notify_counselling", "INTEGER DEFAULT 1"),
            ("coupon_used", "TEXT"),
            ("referred_by_id", "INTEGER"),
            ("predictions_today", "INTEGER DEFAULT 0"),
            ("last_prediction_date", "TEXT"),
            ("is_premium", "INTEGER DEFAULT 0"),
            ("coins", "INTEGER DEFAULT 0")
        ]:
            try:
                db.session.execute(text(f"ALTER TABLE User ADD COLUMN {col} {col_type}"))
                db.session.commit()
            except Exception:
                db.session.rollback()
                
        # Dynamic SQLite migration for Coupon table
        try:
            db.session.execute(text("ALTER TABLE Coupon ADD COLUMN for_whom TEXT"))
            db.session.commit()
        except Exception:
            db.session.rollback()
            
        try:
            db.session.execute(text("ALTER TABLE Coupon ADD COLUMN coins_reward INTEGER DEFAULT 50"))
            db.session.commit()
        except Exception:
            db.session.rollback()
                
        # Create performance-critical indexes dynamically if they don't exist
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_seatinfo_search ON SeatInfo (year, category, domicile, closing_rank, gender)"))
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_seatinfo_college ON SeatInfo (college_name)"))
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_seatinfo_branch ON SeatInfo (branch)"))
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_cgparank_year_cgpa ON CgpaRankRange (year, cgpa)"))
        db.session.commit()
    except Exception as e:
        print("Dynamic schema migration or index creation failed:", e)

    # Auto-seed the admin user
    try:
        from werkzeug.security import generate_password_hash
        admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
        admin_pass = os.getenv("ADMIN_PASSWORD", "kkawasthi@202956@kka")
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_pass),
                display_name="Admin",
                mobile_number="9999999999",
                polytechnic_college="System Admin",
                diploma_branch="Admin",
                cgpa=10.0,
                category="UR",
                gender="M"
            )
            db.session.add(admin_user)
            db.session.commit()
        else:
            # Enforce the password specified by the user
            admin_user.password_hash = generate_password_hash(admin_pass)
            db.session.commit()
    except Exception as e:
        print("Admin seeding failed:", e)

    # Auto-seed initial choice vault slips
    try:
        if ChoiceVault.query.count() == 0:
            initial_slips = [
                ChoiceVault(
                    name="Student #1",
                    cgpa="8.48 (F)",
                    roll_no="571136979331",
                    image_url="choice_vault_1.jpg",
                    focus="Govt/Univ CSE Focus",
                    summary="11 preferences, strictly CSE/IT in Govt & University Owned Colleges in MP."
                ),
                ChoiceVault(
                    name="Student #2",
                    cgpa="8.88",
                    roll_no="571142208900",
                    image_url="choice_vault_3.jpg",
                    focus="Govt/Private CSE/IT",
                    summary="10 preferences, CSE/IT across premium Govt and top Private institutions (SGSITS, DAVV, RGPV, Acropolis)."
                ),
                ChoiceVault(
                    name="Student #3",
                    cgpa="8.33",
                    roll_no="571126268801",
                    image_url="choice_vault_2.jpg",
                    focus="Govt/Private Mix",
                    summary="17 preferences, mixing CSE, IT, AI & Data Science, EC, EE, EI in Govt Aided & Private colleges."
                )
            ]
            db.session.bulk_save_objects(initial_slips)
            db.session.commit()
    except Exception as e:
        print("ChoiceVault seeding failed:", e)

    # Auto-seed visitor count if empty
    try:
        if VisitorCount.query.count() == 0:
            initial_count = VisitorCount(id=1, count=0)
            db.session.add(initial_count)
            db.session.commit()
    except Exception as e:
        print("VisitorCount seeding failed:", e)

    fetch_rank_maps_cache()


def consume_prediction(user):
    if not user:
        return False
    return bool(user.has_unlimited_access)


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', schedule=get_counselling_schedule())


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', metadata=get_data_metadata())


@app.route('/premium', methods=['GET'])
def premium_page():
    limit_reached = request.args.get('limit') == '1'
    user = current_user()
    return render_template('premium.html', limit_reached=limit_reached, user=user)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user = current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'success':
            user.is_premium = True
            db.session.commit()
            flash("Success! Premium Access Unlocked successfully.", "success")
            return redirect(url_for('account_page'))
        else:
            flash("Payment simulation failed. Please try again.", "error")
            return redirect(url_for('premium_page'))
            
    return render_template('checkout.html', user=user)


@app.route('/predictor', methods=['GET', 'POST'])
@limiter.limit("20 per minute", methods=["POST"])
def predictor():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    if request.method == 'GET':
        prefill = {
            'cgpa': request.args.get('cgpa', ''),
            'category': request.args.get('category', ''),
            'gender': request.args.get('gender', ''),
            'college_type': request.args.get('college_type', ''),
            'branch': request.args.getlist('branch') if 'branch' in request.args else '',
            'domicile': request.args.get('domicile', 'Y'),
            'city': request.args.get('city', 'All'),
            'district': request.args.get('district', 'All'),
            'home_city': request.args.get('home_city', 'All'),
            'max_distance_km': request.args.get('max_distance_km', ''),
        }
        has_prefill = bool(prefill['cgpa'] and prefill['category'] and prefill['gender'])
        return render_template(
            'predictor.html', data=None, prediction=None,
            mp_cities=MP_CITIES, prefill=prefill, has_prefill=has_prefill,
            is_premium=is_premium,
        )

    if not user:
        return render_template(
            'predictor.html', data=None, prediction=None,
            needs_login=True, mp_cities=MP_CITIES, prefill=None, has_prefill=False,
            is_premium=False,
        )

    try:
        raw = request.form.get('cgpa', '').strip()
        cgpa = float(raw)
        if not (0.0 <= cgpa <= 10.0):
            raise ValueError("CGPA must be between 0 and 10.")
    except ValueError:
        return render_template(
            'predictor.html', data=None, prediction=None,
            error="Invalid CGPA. Please enter a number between 0 and 10.",
            mp_cities=MP_CITIES, prefill=None, has_prefill=False,
            is_premium=is_premium,
        )

    category = request.form.get('category')
    gender = request.form.get('gender')
    college_type = request.form.get('college_type')
    branch_list = request.form.getlist('branch')
    domicile = request.form.get('domicile', 'Y')
    city = request.form.get('city', 'All')
    district = request.form.get('district', 'All')
    home_city = request.form.get('home_city', 'All')
    max_dist = request.form.get('max_distance_km', '').strip()
    max_distance_km = int(max_dist) if max_dist.isdigit() else None

    # ── Input Validation ─────────────────────────────────────────────────────
    VALID_CATEGORIES = {'UR', 'OBC', 'SC', 'ST'}
    VALID_GENDERS    = {'M', 'F', 'OP'}
    VALID_DOMICILES  = {'Y', 'N'}
    VALID_TYPES      = {'GOVT', 'Private', 'S.F.I.', 'GOVT+SFI', 'Any', '', None}

    if category not in VALID_CATEGORIES:
        return render_template(
            'predictor.html', data=None, prediction=None,
            error="Invalid category selected. Please choose a valid option.",
            mp_cities=MP_CITIES, prefill=None, has_prefill=False,
        )
    if gender not in VALID_GENDERS:
        return render_template(
            'predictor.html', data=None, prediction=None,
            error="Invalid gender selected. Please choose a valid option.",
            mp_cities=MP_CITIES, prefill=None, has_prefill=False,
        )
    if domicile not in VALID_DOMICILES:
        domicile = 'Y'   # silently default to MP domicile
    if college_type not in VALID_TYPES:
        college_type = 'Any'   # silently reset to all types

    form_data = {
        'cgpa': cgpa, 'category': category, 'gender': gender,
        'college_type': college_type, 'branch': branch_list,
        'domicile': domicile, 'city': city, 'district': district,
        'home_city': home_city, 'max_distance_km': max_dist,
    }

    prediction = get_colleges(
        cgpa, branch_list, category, gender, college_type,
        domicile, city, district, home_city, max_distance_km,
    )
    return render_template(
        'predictor.html', data=form_data, prediction=prediction,
        mp_cities=MP_CITIES, prefill=None, has_prefill=False,
        is_premium=is_premium,
    )


@app.route('/choice-builder', methods=['GET', 'POST'])
def choice_builder():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    def normalize(name):
        return " ".join((name or "").replace(",", " ").split()).lower().strip()

    result = None
    form_data = None
    cloud_shortlist = load_cloud_shortlist(user.id) if user else []
    shortlisted_keys = set()
    for item in cloud_shortlist:
        cname = normalize(item.get('college_name'))
        if cname:
            shortlisted_keys.add(cname)

    if request.method == 'POST':
        if not user:
            return render_template(
                'choice_builder.html', result=None, form_data=None,
                needs_login=True, mp_cities=MP_CITIES,
                cloud_shortlist=[], shortlisted_keys=[], is_premium=False, user=None,
            )
        try:
            cgpa = float(request.form.get('cgpa', '').strip())
            form_data = {
                'cgpa': cgpa,
                'category': request.form.get('category'),
                'gender': request.form.get('gender'),
                'college_type': request.form.get('college_type', 'Any'),
                'branch': request.form.getlist('branch') or ['All'],
                'domicile': request.form.get('domicile', 'Y'),
                'city': request.form.get('city', 'All'),
            }
            result = build_smart_choices(
                cgpa, form_data['branch'], form_data['category'],
                form_data['gender'], form_data['college_type'],
                form_data['domicile'], form_data['city'],
                year=YEARS[0] if YEARS else 2025, rank_maps_cache=RANK_MAPS_CACHE,
                max_per_bucket=9999
            )
            # Annotate and sort: official recommendation list first, then shortlisted colleges
            best_choices_list = RecommendationChoice.query.all()
            recommendation_map = {
                (normalize(item.db_name), item.branch.strip().lower()): item.sn
                for item in best_choices_list
            }

            for bucket in ('safe', 'target', 'dream'):
                for item in result[bucket]:
                    key = (normalize(item['college_name']), item['branch'].strip().lower())
                    rec_sn = recommendation_map.get(key)
                    item['in_recommendation'] = rec_sn is not None
                    item['rec_sn'] = rec_sn if rec_sn is not None else 9999
                    item['in_shortlist'] = normalize(item['college_name']) in shortlisted_keys

                result[bucket].sort(key=lambda x: (
                    0 if x.get('in_recommendation') else 1,
                    x.get('rec_sn', 9999),
                    0 if x.get('in_shortlist') else 1,
                    -x['probability'],
                    x['closing_rank']
                ))
                result[bucket] = result[bucket][:15]

            # Rebuild the merged list and update total count using post-sorted and sliced buckets
            merged = []
            for label in ("dream", "target", "safe"):
                for item in result[label]:
                    merged.append({**item, "bucket": label})
            result["merged"] = merged
            result["total"] = len(merged)
        except (ValueError, TypeError):
            form_data = {'error': 'Invalid CGPA'}
    return render_template(
        'choice_builder.html', result=result, form_data=form_data, mp_cities=MP_CITIES,
        shortlisted_keys=list(shortlisted_keys), user=user, is_premium=is_premium,
    )


@app.route('/schedule')
def schedule():
    user = current_user()
    sched_data = get_counselling_schedule()
    return render_template('schedule.html', user=user, schedule=sched_data)


@app.route('/vacant-seats')
def vacant_seats():
    user = current_user()
    vacant_data = []
    json_path = os.path.join(app.root_path, 'data', 'vacant2025_clean.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                vacant_data = json.load(f)
        except Exception:
            vacant_data = []
            
    branches = sorted(list(set(item['branch'] for item in vacant_data if item.get('branch'))))
    colleges = sorted(list(set(item['college_name'] for item in vacant_data if item.get('college_name'))))
    
    total_vacant = sum(item.get('remaining', 0) for item in vacant_data)
    total_allotted = sum(item.get('allotment', 0) for item in vacant_data)
    total_seats = sum(item.get('total_seats', 0) for item in vacant_data)
    
    return render_template(
        'vacant_seats.html',
        user=user,
        vacant_data=vacant_data,
        branches=branches,
        colleges_count=len(colleges),
        total_vacant=total_vacant,
        total_allotted=total_allotted,
        total_seats=total_seats
    )


@app.route('/tentative-institutes')
def tentative_institutes():
    user = current_user()
    tentative_data = []
    json_path = os.path.join(app.root_path, 'data', 'tentative2026_clean.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                tentative_data = json.load(f)
        except Exception:
            tentative_data = []

    branches = sorted(list(set(item['branch'] for item in tentative_data if item.get('branch'))))
    colleges = sorted(list(set(item['college_name'] for item in tentative_data if item.get('college_name'))))
    universities = sorted(list(set(item['university'] for item in tentative_data if item.get('university'))))

    total_intake = sum(item.get('intake', 0) for item in tentative_data)
    total_le_capacity = sum(item.get('intake_10_pct', 0) + item.get('vacancy_2025', 0) for item in tentative_data)

    return render_template(
        'tentative_institutes.html',
        user=user,
        tentative_data=tentative_data,
        branches=branches,
        colleges_count=len(colleges),
        branches_count=len(branches),
        universities=universities,
        total_intake=total_intake,
        total_le_capacity=total_le_capacity
    )


@app.route('/seat-matrix')
def seat_matrix():
    user = current_user()
    seat_matrix_data = []
    json_path = os.path.join(app.root_path, 'data', 'seatmatrix2026_clean.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                seat_matrix_data = json.load(f)
        except Exception:
            seat_matrix_data = []

    branches = sorted(list(set(item['branch'] for item in seat_matrix_data if item.get('branch'))))
    colleges = sorted(list(set(item['college_name'] for item in seat_matrix_data if item.get('college_name'))))

    return render_template(
        'seat_matrix.html',
        user=user,
        seat_matrix_data=seat_matrix_data,
        branches=branches,
        colleges_count=len(colleges)
    )



@app.route('/checklist')
@login_required
def checklist():
    user = current_user()
    return render_template('checklist.html', user=user)


@app.route('/registration-process')
def registration_process():
    user = current_user()
    return render_template('registration_process.html', user=user)


@app.route('/refer-share')
@login_required
def refer_share():
    user = current_user()
    return render_template('refer_share.html', user=user)


@app.route('/college')
def college_detail_page():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))
    name = request.args.get('name', '').strip()
    if not name:
        return redirect('/search')
    detail = get_college_detail(name)
    if not detail:
        return render_template('college_detail.html', detail=None, college_name=name, is_premium=is_premium)
    home_city = request.args.get('home_city', 'All')
    bundle = get_college_info_bundle(name, detail['college_type'], home_city)
    latest_year = YEARS[0] if YEARS else 2025
    prev_year = YEARS[1] if (YEARS and len(YEARS) > 1) else (latest_year - 1)
    heatmap = get_seat_heatmap(name, latest_year)
    chart_data = get_cutoff_chart_data(name)
    reviews = CollegeReview.query.filter_by(
        college_name=name, is_approved=True
    ).order_by(CollegeReview.created_at.desc()).limit(20).all()
    return render_template(
        'college_detail.html', detail=detail, college_name=name,
        heatmap=heatmap, chart_data=chart_data,
        fee_display=bundle['fee_display'], fee=bundle['fee'],
        college_city=bundle['city'], college_district=bundle['district'],
        profile=bundle['profile'], distance=bundle['distance'],
        image_url=bundle.get('image_url'),
        image_urls=bundle.get('image_urls', []),
        home_city=home_city, reviews=reviews,
        mp_cities=MP_CITIES, placement=bundle['placement'],
        coords=bundle['coords'], city_coords=get_city_coords(),
        roi_index=bundle['roi_index'],
        latest_year=latest_year, prev_year=prev_year,
        is_premium=is_premium,
    )


@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')


@app.route('/compare')
def compare():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))
    names = request.args.getlist('colleges')
    names = [n.strip() for n in names if n.strip()][:3]
    data = get_compare_data(names)
    latest_year = YEARS[0] if YEARS else 2025
    prev_year = YEARS[1] if (YEARS and len(YEARS) > 1) else (latest_year - 1)
    return render_template('compare.html', colleges=data, branch_names=BRANCH_NAMES,
                           latest_year=latest_year, prev_year=prev_year, is_premium=is_premium)


@app.route('/search')
def search():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    gender = request.args.get("gender", "").strip()
    college_type = request.args.get("college_type", "").strip()
    branch = request.args.get("branch", "").strip()
    city = request.args.get("city", "All").strip()
    year = request.args.get("year", "").strip()
    
    try:
        min_package = float(request.args.get("min_package", "0").strip() or "0")
    except ValueError:
        min_package = 0.0

    # Execute search if q or min_package or any filters are specified
    has_filters = bool(q or category or gender or college_type or branch or (city and city != 'All') or year or min_package > 0)

    if not has_filters:
        # Load all distinct colleges, resolve type duplicates by preferring GOVT
        colleges_query = db.session.query(
            SeatInfo.college_name, 
            SeatInfo.college_type
        ).order_by(SeatInfo.college_name).all()
        
        from collections import Counter
        raw_counts = Counter(name for name, ctype in colleges_query)
        
        college_map = {}
        for name, ctype in colleges_query:
            norm = normalize_name(name)
            if norm not in college_map:
                college_map[norm] = []
            college_map[norm].append((name, ctype))
            
        deduped_list = []
        for norm, items in college_map.items():
            best_name, best_type = max(items, key=lambda x: raw_counts[x[0]])
            
            has_govt = any(ctype == "GOVT" for name, ctype in items)
            if has_govt:
                best_type = "GOVT"
                
            deduped_list.append((best_name, best_type))
            
        final_deduped_list = []
        seen = set()
        for name, ctype in deduped_list:
            if name not in seen:
                seen.add(name)
                final_deduped_list.append((name, ctype))
                
        final_deduped_list.sort(key=lambda x: x[0])

        if request.args.get('json'):
            deduped_json = [{"college_name": name, "college_type": ctype} for name, ctype in final_deduped_list]
            return jsonify(deduped_json)

        colleges = []
        for name, ctype in final_deduped_list:
            fee = get_fee_info(name, ctype)
            placement = get_placement_info(name, ctype)
            city_val = infer_city_from_college_name(name)
            images = get_college_image(name)
            colleges.append({
                'college_name': name,
                'college_type': ctype,
                'city': city_val,
                'fee_display': format_fee_display(fee),
                'fee_approximate': fee.get('is_approximate', True),
                'placement': placement,
                'image_urls': images,
                'image_url': images[0] if images else None
            })

        # For non-premium users: show only 3 fixed demo colleges
        if not is_premium:
            DEMO_KEYWORDS = ['shri g.s.', 'davv', 'jec', 'jabalpur engineering']
            demo = []
            for kw in DEMO_KEYWORDS:
                for c in colleges:
                    if kw in c['college_name'].lower() and c not in demo:
                        demo.append(c)
                        break
            colleges = demo[:3]

        return render_template(
            "search.html", 
            data=None, 
            colleges=colleges, 
            mp_cities=MP_CITIES,
            directory_mode=True,
            is_premium=is_premium,
        )

    data = {
        "q": q, "category": category, "gender": gender,
        "college_type": college_type, "branch": branch, "city": city, "year": year,
        "min_package": min_package,
    }

    colleges = search_colleges(
        q=q, category=category or None, gender=gender or None,
        college_type=college_type or None, branch=branch or None,
        year=year or None, city=city or None,
    )
    
    filtered_colleges = []
    for c in colleges:
        fee = get_fee_info(c['college_name'], c.get('college_type'))
        c['fee_display'] = format_fee_display(fee)
        c['fee_approximate'] = fee.get('is_approximate', True)
        
        # Attach placement statistics
        placement = get_placement_info(c['college_name'], c.get('college_type'))
        c['placement'] = placement
        
        # Attach image
        images = get_college_image(c['college_name'])
        c['image_urls'] = images
        c['image_url'] = images[0] if images else None
        
        if min_package > 0:
            if placement['average_package_lpa'] >= min_package:
                filtered_colleges.append(c)
        else:
            filtered_colleges.append(c)
            
    colleges = filtered_colleges

    if request.args.get('json'):
        seen = set()
        deduped = []
        for c in colleges:
            key = (c['college_name'], c['branch'])
            if key not in seen:
                seen.add(key)
                deduped.append(c)
        return jsonify(deduped)

    return render_template("search.html", data=data, colleges=colleges, mp_cities=MP_CITIES, is_premium=is_premium)


@app.route('/rank_predictor', methods=['GET', 'POST'])
def rank():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    if request.method == 'GET':
        return render_template('rank.html', data=None, prediction=None, is_premium=is_premium)

    if not user:
        return render_template('rank.html', data=None, prediction=None,
                               needs_login=True, is_premium=False)

    cgpa_str = request.form.get('cgpa', '').strip()
    rank_str = request.form.get('rank', '').strip()

    if cgpa_str:
        try:
            cgpa = float(cgpa_str)
            if not (0.0 <= cgpa <= 10.0):
                raise ValueError()
        except ValueError:
            return render_template(
                'rank.html', data=None, prediction=None,
                error="Invalid CGPA. Please enter a number between 0 and 10.",
                is_premium=is_premium,
            )
        return render_template(
            'rank.html',
            data={"cgpa": cgpa, "mode": "cgpa-to-rank"},
            prediction=get_rank(cgpa),
            is_premium=is_premium,
        )

    elif rank_str:
        try:
            rank_val = int(rank_str)
            if rank_val <= 0:
                raise ValueError()
        except ValueError:
            return render_template(
                'rank.html', data=None, prediction=None,
                error="Invalid Rank. Please enter a positive integer.",
                is_premium=is_premium,
            )
        return render_template(
            'rank.html',
            data={"rank": rank_val, "mode": "rank-to-cgpa"},
            prediction=get_cgpa_for_rank(rank_val),
            is_premium=is_premium,
        )

    return render_template('rank.html', data=None, prediction=None, is_premium=is_premium)


@app.route('/merit-insights', methods=['GET', 'POST'])
def merit_insights():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    if request.method == 'GET':
        return render_template('merit_insights.html', data=None, insights=None, is_premium=is_premium)

    if not user:
        return render_template('merit_insights.html', data=None, insights=None,
                               needs_login=True, is_premium=False)

    try:
        cgpa = float(request.form.get('cgpa', '').strip())
        if not (0.0 <= cgpa <= 10.0):
            raise ValueError()
    except ValueError:
        return render_template(
            'merit_insights.html', data=None, insights=None,
            error="Invalid CGPA. Please enter a number between 0 and 10.",
            is_premium=is_premium,
        )

    insights = get_merit_insights(cgpa, RANK_MAPS_CACHE, YEARS)
    return render_template('merit_insights.html', data={'cgpa': cgpa}, insights=insights,
                           is_premium=is_premium)


@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    user = current_user()
    is_premium = bool(user and getattr(user, 'has_unlimited_access', False))

    if request.method == 'GET':
        return render_template('simulator.html', result=None, is_premium=is_premium)

    if not user:
        return render_template('simulator.html', result=None,
                               needs_login=True, is_premium=False)

    try:
        cgpa = float(request.form.get('cgpa', '').strip())
        category = request.form.get('category')
        gender = request.form.get('gender')
        domicile = request.form.get('domicile', 'Y')
        year = int(request.form.get('year', YEARS[0] if YEARS else 2025))
        rank_mode = request.form.get('rank_mode', 'average')

        raw_choices = request.form.get('choice_list_json', '[]')
        choices = json.loads(raw_choices)

        if not choices:
            return render_template('simulator.html', error="Your choice list is empty. Please add colleges first.",
                                   is_premium=is_premium)

        sim_rank, min_rank, max_rank = _resolve_simulation_rank(cgpa, year, rank_mode)
        sim_result = run_counselling_simulation(
            sim_rank, choices, category, gender, domicile, year,
        )

        user_data = {
            'cgpa': cgpa, 'rank': sim_rank, 'min_rank': min_rank, 'max_rank': max_rank,
            'rank_mode': rank_mode, 'category': category,
            'gender': gender, 'domicile': domicile, 'year': year,
        }

        recommendations = []
        try:
            all_options = get_colleges(cgpa, 'All', category, gender, 'Any', domicile, 'All')
            seen_recommendations = set()
            choice_keys = {(c['college_name'], c['branch']) for c in choices}
            for yr in YEARS:
                if yr in all_options:
                    for item in all_options[yr]['colleges']:
                        col = item['college']
                        prob = item['probability']
                        if prob >= 50 and (col.college_name, col.branch) not in choice_keys:
                            key = (col.college_name, col.branch)
                            if key not in seen_recommendations:
                                seen_recommendations.add(key)
                                recommendations.append({
                                    'college_name': col.college_name,
                                    'branch': col.branch,
                                    'probability': prob,
                                    'college_type': col.college_type,
                                })
                                if len(recommendations) >= 5:
                                    break
                if len(recommendations) >= 5:
                    break
        except Exception:
            pass

        return render_template(
            'simulator.html', result=sim_result, user=user_data,
            choices=choices, recommendations=recommendations,
            is_premium=is_premium,
        )
    except Exception as e:
        return render_template('simulator.html', error=str(e), is_premium=is_premium)


@app.route('/recommendation-list')
def recommendation_list():
    if not current_user():
        return redirect(url_for('account_page', next=request.url))
    best_choices = RecommendationChoice.query.order_by(RecommendationChoice.sn.asc()).all()
    return render_template('recommendation_list.html', choices=best_choices)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/faq')
def faq():
    categories = get_all_categories()
    faqs_by_cat = {cat: get_faqs_by_category(cat) for cat in categories}
    return render_template(
        'faq.html',
        categories=categories,
        faqs_by_cat=faqs_by_cat,
        all_faqs=FAQ_LIST
    )


@app.route('/dte-rules')
def dte_rules():
    return render_template('rules.html')


@app.route('/choice-filling-rules')
def choice_filling_rules():
    return render_template('choice_filling_rules.html')


def parse_slip_file(filename, is_subfolder=False):
    name_without_ext = os.path.splitext(filename)[0]
    rank = None
    roll_no = "N/A"
    
    if '--' in name_without_ext:
        parts = name_without_ext.split('--')
        if len(parts) >= 2:
            rank_str = parts[0].strip()
            roll_no = parts[1].strip()
            try:
                rank = int(rank_str)
            except ValueError:
                pass
                
    # Determine image_url
    if is_subfolder:
        image_url = f"/choice-vault-images/ye niche dekhne chaiye upar bali choice se/{filename}"
    else:
        image_url = f"/choice-vault-images/{filename}"
        
    # Name, cgpa and details mapping
    if rank is not None:
        name = f"Candidate (Rank {rank})"
        cgpa = "N/A"
        focus = f"Rank {rank} Choice List"
        summary = f"Official choice filling slip for Rank {rank}. Roll No: {roll_no}."
    else:
        # Fallback for DocScanner files
        if "pages-1" in name_without_ext:
            name = "Student #1"
            cgpa = "8.48 (F)"
            roll_no = "571136979331"
            image_url = "choice_vault_1.jpg"
            focus = "Govt/Univ CSE Focus"
            summary = "11 preferences, strictly CSE/IT in Govt & University Owned Colleges in MP."
        elif "pages-2" in name_without_ext:
            name = "Student #3"
            cgpa = "8.33"
            roll_no = "571126268801"
            image_url = "choice_vault_2.jpg"
            focus = "Govt/Private Mix"
            summary = "17 preferences, mixing CSE, IT, AI & Data Science, EC, EE, EI in Govt Aided & Private colleges."
        elif "pages-3" in name_without_ext:
            name = "Student #2"
            cgpa = "8.88"
            roll_no = "571142208900"
            image_url = "choice_vault_3.jpg"
            focus = "Govt/Private CSE/IT"
            summary = "10 preferences, CSE/IT across premium Govt and top Private institutions (SGSITS, DAVV, RGPV, Acropolis)."
        else:
            name = "Reference Slip"
            cgpa = "N/A"
            focus = "Official Preference Slip"
            summary = "Official DTE choice filling reference slip."
            
    return {
        "rank": rank,
        "cgpa": cgpa,
        "roll_no": roll_no,
        "image_url": image_url,
        "name": name,
        "focus": focus,
        "summary": summary
    }


def get_choice_vault_slips():
    base_dir = os.path.join(app.root_path, 'Choice_Vault')
    if not os.path.exists(base_dir):
        return []
        
    top_slips = []
    subfolder_slips = []
    
    # 1. Scan top folder
    for filename in os.listdir(base_dir):
        filepath = os.path.join(base_dir, filename)
        if os.path.isdir(filepath):
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            continue
            
        slip = parse_slip_file(filename, is_subfolder=False)
        if slip:
            top_slips.append(slip)
            
    # Sort top slips by rank: Rank None (DocScanner) first, then numeric rank ascending
    top_slips.sort(key=lambda s: (0, s['rank']) if s['rank'] is not None else (1, s['name']))
    
    # 2. Scan subfolder
    sub_dir = os.path.join(base_dir, 'ye niche dekhne chaiye upar bali choice se')
    if os.path.exists(sub_dir) and os.path.isdir(sub_dir):
        for filename in os.listdir(sub_dir):
            filepath = os.path.join(sub_dir, filename)
            if os.path.isdir(filepath):
                continue
                
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.png', '.jpg', '.jpeg']:
                continue
                
            slip = parse_slip_file(filename, is_subfolder=True)
            if slip:
                subfolder_slips.append(slip)
                
        # Sort subfolder slips by rank
        subfolder_slips.sort(key=lambda s: (0, s['rank']) if s['rank'] is not None else (1, s['name']))
        
    # Combine (top slips first, subfolder slips second)
    combined = top_slips + subfolder_slips
    
    # Assign sequential IDs
    for idx, slip in enumerate(combined, start=1):
        slip['id'] = idx
        
    return combined


@app.route('/choice-vault-images/<path:filename>')
@limiter.exempt
def choice_vault_images(filename):
    base_dir = os.path.join(app.root_path, 'Choice_Vault')
    return send_from_directory(base_dir, filename)


@app.route('/choice-vault')
def choice_vault():
    user = current_user()
    is_premium = bool(user and user.has_unlimited_access)
    slips = get_choice_vault_slips()
    return render_template('choice_vault.html', slips=slips, is_premium=is_premium)


@app.route('/faq/<string:slug>')
def faq_detail(slug):
    faq = get_faq_by_slug(slug)
    if not faq:
        return redirect('/faq')
    
    try:
        idx = FAQ_LIST.index(faq)
        prev_faq = FAQ_LIST[idx - 1] if idx > 0 else None
        next_faq = FAQ_LIST[idx + 1] if idx < len(FAQ_LIST) - 1 else None
    except ValueError:
        prev_faq = None
        next_faq = None
        
    related = [f for f in FAQ_LIST if f["category"] == faq["category"] and f["slug"] != faq["slug"]][:4]
    
    return render_template(
        'faq_detail.html',
        faq=faq,
        prev_faq=prev_faq,
        next_faq=next_faq,
        related=related
    )



@app.route('/account', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def account_page():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'logout':
            logout_user()
            return redirect('/account')
        if action == 'login':
            import time
            # ── Rate-limit login attempts (max 5 per 10 minutes per session) ──
            now = time.time()
            login_attempts = session.get("login_attempts", [])
            # purge attempts older than 10 minutes
            login_attempts = [t for t in login_attempts if now - t < 600]
            if len(login_attempts) >= 5:
                return render_template(
                    'account.html',
                    error="Too many login attempts. Please wait 10 minutes before trying again."
                )
            login_attempts.append(now)
            session["login_attempts"] = login_attempts

            user, err = authenticate(
                request.form.get('email', ''),
                request.form.get('password', ''),
            )
            if err:
                return render_template('account.html', error=err)
            # Successful login → clear rate-limit
            session.pop("login_attempts", None)
            login_user(user)
            # ── Safe redirect: only allow relative paths (prevent open redirect) ──
            nxt = request.args.get('next') or ''
            if nxt and (nxt.startswith('http') or nxt.startswith('//') or not nxt.startswith('/')):
                nxt = '/account'
            return redirect(nxt or '/account')
        if action == 'register':
            import time
            now = time.time()
            reg_attempts = session.get("reg_otp_sends", [])
            reg_attempts = [t for t in reg_attempts if now - t < 3600]
            if len(reg_attempts) >= 5:
                return render_template(
                    'account.html',
                    error="Too many registration attempts. Please wait an hour before trying again."
                )

            try:
                cgpa_val = float(request.form.get('cgpa', '0').strip())
            except ValueError:
                cgpa_val = 0.0
            
            sanitized, err = pre_validate_registration(
                email=request.form.get('email', ''),
                password=request.form.get('password', ''),
                display_name=request.form.get('display_name', ''),
                mobile_number=request.form.get('mobile_number', ''),
                polytechnic_college=request.form.get('polytechnic_college', ''),
                diploma_branch=request.form.get('diploma_branch', ''),
                cgpa=cgpa_val,
                category=request.form.get('category', 'UR'),
                gender=request.form.get('gender', 'M'),
            )
            if err:
                return render_template('account.html', error=err, prefill_reg=request.form)

            coupon_code = request.form.get('coupon_code', '').strip()
            coupon_used = None
            referred_by_id = None
            coupon_for_whom = None
            referred_by_name = None
            coins_rewarded = 0
            if coupon_code:
                # 1. Check Coupon Table
                coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
                if coupon:
                    coupon_used = coupon_code
                    coupon_for_whom = coupon.for_whom.strip() if (coupon.for_whom and coupon.for_whom.strip()) else coupon.code
                    coins_rewarded = getattr(coupon, 'coins_reward', 50) or 50
                else:
                    # 2. Check User Table for mobile or email
                    referrer = User.query.filter(
                        (User.mobile_number == coupon_code) | (User.email == coupon_code.lower())
                    ).first()
                    if referrer:
                        coupon_used = coupon_code
                        referred_by_id = referrer.id
                        referred_by_name = referrer.display_name or referrer.email
                        coins_rewarded = get_referral_coins()
                    else:
                        return render_template(
                            'account.html',
                            error="Invalid coupon or referral code. Please check the code or leave it blank.",
                            prefill_reg=request.form
                        )

            sanitized["coupon_used"] = coupon_used
            sanitized["referred_by_id"] = referred_by_id
            sanitized["coupon_for_whom"] = coupon_for_whom
            sanitized["referred_by_name"] = referred_by_name
            sanitized["coins_rewarded"] = coins_rewarded
            
            import random
            otp = str(random.randint(100000, 999999))
            
            session["pending_registration"] = sanitized
            session["registration_otp"] = otp
            session["registration_otp_expiry"] = time.time() + 600
            session["registration_otp_attempts"] = 0
            
            success, msg = send_otp_email(sanitized["email"], otp)
            if success:
                reg_attempts.append(now)
                session["reg_otp_sends"] = reg_attempts
                return render_template('account.html', success=f"Verification OTP has been sent to {sanitized['email']}. Please check your inbox / spam folder. ({msg})")
            else:
                return render_template('account.html', error=f"Could not send OTP: {msg}")

        elif action == 'verify_otp':
            entered_otp = request.form.get('otp', '').strip()
            pending_data = session.get("pending_registration")
            saved_otp = session.get("registration_otp")
            expiry = session.get("registration_otp_expiry", 0)
            
            import time
            if not pending_data or not saved_otp:
                return render_template('account.html', error="No pending registration found. Please try again.")
            
            if time.time() > expiry:
                session.pop("pending_registration", None)
                session.pop("registration_otp", None)
                session.pop("registration_otp_expiry", None)
                session.pop("registration_otp_attempts", None)
                return render_template('account.html', error="OTP verification code expired. Please register again.")
            
            if entered_otp != saved_otp:
                attempts = session.get("registration_otp_attempts", 0) + 1
                session["registration_otp_attempts"] = attempts
                if attempts >= 3:
                    session.pop("pending_registration", None)
                    session.pop("registration_otp", None)
                    session.pop("registration_otp_expiry", None)
                    session.pop("registration_otp_attempts", None)
                    return render_template('account.html', error="Too many failed attempts. Please register again.")
                return render_template('account.html', error=f"Incorrect OTP. Please try again. ({3 - attempts} attempts remaining)")
            
            user, err = register_user(
                email=pending_data["email"],
                password=pending_data["password"],
                display_name=pending_data["display_name"],
                mobile_number=pending_data["mobile_number"],
                polytechnic_college=pending_data["polytechnic_college"],
                diploma_branch=pending_data["diploma_branch"],
                cgpa=pending_data["cgpa"],
                category=pending_data["category"],
                gender=pending_data["gender"],
                coupon_used=pending_data.get("coupon_used"),
                referred_by_id=pending_data.get("referred_by_id")
            )
            if err:
                return render_template('account.html', error=err)
            
            if pending_data.get("coupon_for_whom"):
                session["registered_with_coupon_for"] = pending_data.get("coupon_for_whom")
                session["registered_coins_rewarded"] = pending_data.get("coins_rewarded", 50)
            elif pending_data.get("referred_by_name"):
                session["registered_with_referral_by"] = pending_data.get("referred_by_name")
                session["registered_coins_rewarded"] = pending_data.get("coins_rewarded", 50)
            
            session.pop("pending_registration", None)
            session.pop("registration_otp", None)
            session.pop("registration_otp_expiry", None)
            session.pop("registration_otp_attempts", None)
            
            login_user(user)
            nxt = request.args.get('next') or ''
            if nxt and (nxt.startswith('http') or nxt.startswith('//') or not nxt.startswith('/')):
                nxt = '/account'
            return redirect(nxt or '/account')

        elif action == 'cancel_registration':
            session.pop("pending_registration", None)
            session.pop("registration_otp", None)
            session.pop("registration_otp_expiry", None)
            session.pop("registration_otp_attempts", None)
            nxt = request.args.get('next') or ''
            if nxt and (nxt.startswith('http') or nxt.startswith('//') or not nxt.startswith('/')):
                nxt = '/account'
            return redirect(nxt or '/account')
            
        elif action == 'forgot_password':
            import time
            now = time.time()
            reset_attempts = session.get("reset_otp_sends", [])
            reset_attempts = [t for t in reset_attempts if now - t < 3600]
            if len(reset_attempts) >= 5:
                return render_template(
                    'account.html',
                    error="Too many password reset requests. Please wait an hour before trying again."
                )

            email = request.form.get('email', '').strip().lower()
            if not email:
                return render_template('account.html', error="Please enter your registered email address.")
            
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                return render_template('account.html', error="This email address is not registered with us.")
            
            import random
            otp = str(random.randint(100000, 999999))
            session["reset_email"] = email
            session["reset_otp"] = otp
            session["reset_otp_expiry"] = time.time() + 600
            session["reset_otp_attempts"] = 0
            
            success, msg = send_otp_email(email, otp)
            if success:
                reset_attempts.append(now)
                session["reset_otp_sends"] = reset_attempts
                return render_template('account.html', success=f"A password reset code has been sent to {email}. ({msg})")
            else:
                return render_template('account.html', error=f"Could not send reset code: {msg}")
                
        elif action == 'verify_reset_otp':
            entered_otp = request.form.get('otp', '').strip()
            new_password = request.form.get('new_password', '')
            reset_email = session.get("reset_email")
            saved_otp = session.get("reset_otp")
            expiry = session.get("reset_otp_expiry", 0)
            
            import time
            if not reset_email or not saved_otp:
                return render_template('account.html', error="No active password reset request found.")
            
            if time.time() > expiry:
                session.pop("reset_email", None)
                session.pop("reset_otp", None)
                session.pop("reset_otp_expiry", None)
                session.pop("reset_otp_attempts", None)
                return render_template('account.html', error="Reset code has expired. Please try again.")
            
            if entered_otp != saved_otp:
                attempts = session.get("reset_otp_attempts", 0) + 1
                session["reset_otp_attempts"] = attempts
                if attempts >= 3:
                    session.pop("reset_email", None)
                    session.pop("reset_otp", None)
                    session.pop("reset_otp_expiry", None)
                    session.pop("reset_otp_attempts", None)
                    return render_template('account.html', error="Too many failed attempts. Please try again.")
                return render_template('account.html', error=f"Incorrect OTP. Please try again. ({3 - attempts} attempts remaining)")
                
            ok, err = reset_password_in_db(reset_email, new_password)
            if not ok:
                return render_template('account.html', error=err)
                
            session.pop("reset_email", None)
            session.pop("reset_otp", None)
            session.pop("reset_otp_expiry", None)
            session.pop("reset_otp_attempts", None)
            
            return render_template('account.html', success="Password has been reset successfully. You can now log in.")
            
        elif action == 'cancel_reset':
            session.pop("reset_email", None)
            session.pop("reset_otp", None)
            session.pop("reset_otp_expiry", None)
            session.pop("reset_otp_attempts", None)
            return redirect('/account')
            
        elif action == 'toggle_alerts':
            user = current_user()
            if user:
                user.notify_counselling = 0 if user.notify_counselling == 1 else 1
                db.session.commit()
            return redirect('/account')

        elif action == 'update_profile':
            user = current_user()
            if not user:
                return redirect('/account')
            
            try:
                cgpa_val = float(request.form.get('cgpa', '0').strip())
            except ValueError:
                cgpa_val = 0.0

            sanitized, err = pre_validate_profile_update(
                current_user_id=user.id,
                display_name=request.form.get('display_name', ''),
                mobile_number=request.form.get('mobile_number', ''),
                polytechnic_college=request.form.get('polytechnic_college', ''),
                diploma_branch=request.form.get('diploma_branch', ''),
                cgpa=cgpa_val,
                category=request.form.get('category', 'UR'),
                gender=request.form.get('gender', 'M')
            )
            if err:
                shortlist = load_cloud_shortlist(user.id)
                return render_template('account.html', user=user, cloud_shortlist=shortlist, error=err)
            
            user.display_name = sanitized["display_name"]
            user.mobile_number = sanitized["mobile_number"]
            user.polytechnic_college = sanitized["polytechnic_college"]
            user.diploma_branch = sanitized["diploma_branch"]
            user.cgpa = sanitized["cgpa"]
            user.category = sanitized["category"]
            user.gender = sanitized["gender"]
            db.session.commit()
            
            shortlist = load_cloud_shortlist(user.id)
            return render_template('account.html', user=user, cloud_shortlist=shortlist, success="Profile updated successfully!")

    logged_out_reason = session.pop("logged_out_reason", None)
    user = current_user()
    if not logged_out_reason:
        logged_out_reason = session.pop("logged_out_reason", None)
        
    shortlist = load_cloud_shortlist(user.id) if user else []
    
    congrats_coupon_for = session.pop("registered_with_coupon_for", None)
    congrats_referral_by = session.pop("registered_with_referral_by", None)
    congrats_coins_rewarded = session.pop("registered_coins_rewarded", None)
    
    return render_template(
        'account.html', 
        user=user, 
        cloud_shortlist=shortlist,
        congrats_coupon_for=congrats_coupon_for,
        congrats_referral_by=congrats_referral_by,
        logged_out_reason=logged_out_reason
    )


def get_admin_dashboard_stats(users):
    total_users = len(users)
    total_cgpa = 0.0
    valid_cgpa_count = 0
    branch_stats = {}
    category_stats = {}
    
    for u in users:
        if u.cgpa:
            total_cgpa += u.cgpa
            valid_cgpa_count += 1
        
        br = u.diploma_branch or 'Other'
        branch_stats[br] = branch_stats.get(br, 0) + 1
        
        cat = u.category or 'UR'
        category_stats[cat] = category_stats.get(cat, 0) + 1
        
    avg_cgpa = round(total_cgpa / valid_cgpa_count, 2) if valid_cgpa_count > 0 else 0.0
    return {
        'total_users': total_users,
        'avg_cgpa': avg_cgpa,
        'branch_stats': branch_stats,
        'category_stats': category_stats
    }


def get_shortlist_analytics_stats():
    from collections import Counter
    from models import CloudShortlist
    all_shortlists = CloudShortlist.query.all()
    college_counts = Counter()
    branch_counts = Counter()
    combo_counts = Counter()

    for s in all_shortlists:
        try:
            items = json.loads(s.items_json) if s.items_json else []
            for item in items:
                cname = item.get('college_name', '').strip()
                br = item.get('branch', '').strip()
                if cname:
                    college_counts[cname] += 1
                    if br:
                        branch_counts[br] += 1
                        combo_counts[f"{cname} ({br})"] += 1
        except Exception:
            continue

    return {
        'top_colleges': college_counts.most_common(10),
        'top_branches': branch_counts.most_common(5),
        'top_combos': combo_counts.most_common(10),
        'total_shortlisted': sum(college_counts.values()),
        'total_lists_count': len(all_shortlists)
    }


@app.route('/admin/users')
@login_required
def admin_users():
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    users = User.query.order_by(User.created_at.desc()).all()
    
    export_csv = request.args.get('export')
    if export_csv == '1':
        import io, csv
        from flask import Response
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Email', 'Mobile', 'Polytechnic College', 'Diploma Branch', 'CGPA', 'Category', 'Gender', 'Registered At', 'Coupon Used', 'Referred By'])
        for u in users:
            referred_by_name = ''
            if u.referred_by:
                referred_by_name = f"Student: {u.referred_by.display_name or u.referred_by.email}"
            elif u.coupon_details:
                referred_by_name = f"Coupon: {u.coupon_details.for_whom or u.coupon_details.code}"
            writer.writerow([
                u.id, 
                u.display_name or '', 
                u.email or '', 
                u.mobile_number or '', 
                u.polytechnic_college or '', 
                u.diploma_branch or '', 
                u.cgpa or 0.0, 
                u.category or 'UR', 
                u.gender or 'M', 
                to_ist(u.created_at).strftime('%d %b %Y, %I:%M %p') if u.created_at else '—',
                u.coupon_used or '',
                referred_by_name
            ])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=dte_registered_users.csv"}
        )
        
    stats = get_admin_dashboard_stats(users)
    reviews = CollegeReview.query.order_by(CollegeReview.created_at.desc()).all()
    vault_slips = ChoiceVault.query.order_by(ChoiceVault.id.asc()).all()
    analytics = get_shortlist_analytics_stats()
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    recommendations = RecommendationChoice.query.order_by(RecommendationChoice.sn.asc()).all()

    return render_template(
        'admin_dashboard.html', 
        users=users, 
        total_users=stats['total_users'], 
        avg_cgpa=stats['avg_cgpa'], 
        branch_stats=stats['branch_stats'], 
        category_stats=stats['category_stats'],
        reviews=reviews,
        vault_slips=vault_slips,
        analytics=analytics,
        coupons=coupons,
        recommendations=recommendations,
        referral_coins_reward=get_referral_coins()
    )


@app.route('/admin/update-schedule', methods=['POST'])
@login_required
def admin_update_schedule():
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    academic_year = request.form.get('academic_year', '').strip()
    portal_url = request.form.get('portal_url', '').strip()
    welcome_title = request.form.get('welcome_title', '').strip()
    banner_warning = request.form.get('banner_warning', '').strip()
    banner_btn_text = request.form.get('banner_btn_text', '').strip()
    banner_btn_url = request.form.get('banner_btn_url', '').strip()
    
    clc_instructions_raw = request.form.get('clc_instructions', '').strip()
    clc_instructions = [line.strip() for line in clc_instructions_raw.split('\n') if line.strip()]

    events = []
    idx = 0
    while f"event_id_{idx}" in request.form:
        ev_id = request.form.get(f"event_id_{idx}").strip()
        ev_title = request.form.get(f"event_title_{idx}").strip()
        ev_status = request.form.get(f"event_status_{idx}").strip()
        ev_date = request.form.get(f"event_date_{idx}", "").strip() or None
        
        event = {
            "id": ev_id,
            "title": ev_title,
            "status": ev_status
        }
        
        if ev_date:
            event["date"] = ev_date

        if f"event_end_date_{idx}" in request.form:
            end_date = request.form.get(f"event_end_date_{idx}").strip()
            if end_date:
                event["end_date"] = end_date

        if f"event_reg_date_{idx}" in request.form:
            reg_date = request.form.get(f"event_reg_date_{idx}").strip()
            if reg_date:
                event["reg_date"] = reg_date

        if f"event_reg_end_date_{idx}" in request.form:
            reg_end_date = request.form.get(f"event_reg_end_date_{idx}").strip()
            if reg_end_date:
                event["reg_end_date"] = reg_end_date

        if f"event_time_desc_{idx}" in request.form:
            time_desc = request.form.get(f"event_time_desc_{idx}").strip()
            if time_desc:
                event["time_desc"] = time_desc

        if f"event_description_{idx}" in request.form:
            desc = request.form.get(f"event_description_{idx}").strip()
            if desc:
                event["description"] = desc

        events.append(event)
        idx += 1

    schedule_data = {
        "academic_year": academic_year,
        "portal_url": portal_url,
        "welcome_title": welcome_title,
        "banner_warning": banner_warning,
        "banner_btn_text": banner_btn_text,
        "banner_btn_url": banner_btn_url,
        "clc_instructions": clc_instructions,
        "events": events
    }

    save_counselling_schedule(schedule_data)
    return redirect('/admin/users?success=schedule#schedule')


@app.route('/admin/add-vault-slip', methods=['POST'])
@login_required
def add_vault_slip():
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    name = request.form.get('name', '').strip()
    cgpa = request.form.get('cgpa', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    image_url = request.form.get('image_url', '').strip()
    focus = request.form.get('focus', '').strip()
    summary = request.form.get('summary', '').strip()

    if name and cgpa and roll_no and image_url and focus and summary:
        new_slip = ChoiceVault(
            name=name,
            cgpa=cgpa,
            roll_no=roll_no,
            image_url=image_url,
            focus=focus,
            summary=summary
        )
        db.session.add(new_slip)
        db.session.commit()
    return redirect('/admin/users?success=vault_added#choice-vault')


@app.route('/admin/delete-vault-slip/<int:id>', methods=['POST'])
@login_required
def delete_vault_slip(id):
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    slip = ChoiceVault.query.get_or_404(id)
    db.session.delete(slip)
    db.session.commit()
    return redirect('/admin/users?success=vault_deleted#choice-vault')


@app.route('/admin/toggle-premium/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_premium(user_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    target_user = db.session.get(User, user_id)
    if target_user:
        target_user.is_premium = not target_user.is_premium
        db.session.commit()
        status_msg = f"Premium access updated for {target_user.display_name or target_user.email}!"
        flash(status_msg, "success")
    else:
        flash("User not found.", "error")
        
    return redirect('/admin/users')


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    # Delete child relation shortlists first
    from models import CloudShortlist
    CloudShortlist.query.filter_by(user_id=user_id).delete()
    
    user_to_delete = db.session.get(User, user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        
    return redirect('/admin/users')


@app.route('/admin/coupons/add', methods=['POST'])
@login_required
def admin_add_coupon():
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    code = request.form.get('code', '').strip().upper()
    for_whom = request.form.get('for_whom', '').strip()
    coins_reward_str = request.form.get('coins_reward', '50').strip()
    
    try:
        coins_reward = int(coins_reward_str)
        if coins_reward < 0:
            raise ValueError()
    except ValueError:
        return redirect('/admin/users?error=invalid_coins#coupons')
        
    if not code:
        return redirect('/admin/users?error=coupon_code_empty#coupons')
        
    # Check if coupon already exists
    existing = Coupon.query.filter_by(code=code).first()
    if existing:
        return redirect('/admin/users?error=coupon_exists#coupons')
        
    coupon = Coupon(code=code, for_whom=for_whom, created_by="admin", is_active=True, coins_reward=coins_reward)
    db.session.add(coupon)
    db.session.commit()
    return redirect('/admin/users?success=coupon_added#coupons')


@app.route('/admin/settings/referral-coins', methods=['POST'])
@login_required
def admin_update_referral_coins():
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    coins_str = request.form.get('referral_coins_reward', '50').strip()
    try:
        coins = int(coins_str)
        if coins < 0:
            raise ValueError()
        SiteSetting.set('referral_coins_reward', str(coins))
    except ValueError:
        return redirect('/admin/users?error=invalid_referral_coins#coupons')
        
    return redirect('/admin/users?success=referral_coins_updated#coupons')


@app.route('/admin/add-coins/<int:user_id>', methods=['POST'])
@login_required
def admin_add_coins(user_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
        
    amount_str = request.form.get('amount', '0').strip()
    try:
        amount = int(amount_str)
    except ValueError:
        flash("Invalid coins amount.", "error")
        return redirect('/admin/users')
        
    target_user = db.session.get(User, user_id)
    if target_user:
        target_user.coins = (target_user.coins or 0) + amount
        if target_user.coins < 0:
            target_user.coins = 0
        db.session.commit()
        flash(f"Updated coins balance for {target_user.display_name or target_user.email} by {amount} coins!", "success")
    else:
        flash("User not found.", "error")
        
    return redirect('/admin/users')


@app.route('/admin/coupons/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_coupon(id):
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
        
    coupon = db.session.get(Coupon, id)
    if coupon:
        db.session.delete(coupon)
        db.session.commit()
        return redirect('/admin/users?success=coupon_deleted#coupons')
    return redirect('/admin/users?error=coupon_not_found#coupons')


@app.route('/admin/upload-csv', methods=['POST'])
@login_required
def admin_upload_csv():
    user = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not user or user.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    csv_type = request.form.get('csv_type', '').strip()
    try:
        year = int(request.form.get('year', '').strip())
    except ValueError:
        return redirect('/admin/users?error=invalid_year#db')

    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        return redirect('/admin/users?error=invalid_file_type#db')

    import csv
    import io

    try:
        content = file.stream.read().decode("utf-8")
        stream = io.StringIO(content, newline=None)
        reader = csv.reader(stream)
        rows = list(reader)
    except Exception as e:
        return redirect(f"/admin/users?error=Failed to read CSV: {url_quote(str(e))}#db")

    if not rows:
        return redirect('/admin/users?error=empty_file#db')

    # Auto-detect header
    first_row = [c.strip().lower() for c in rows[0]]
    has_header = False
    header_map = {}
    if 'college_name' in first_row or 'college name' in first_row or 'college' in first_row or 'cgpa' in first_row:
        has_header = True
        for idx, col in enumerate(first_row):
            col_clean = col.replace(" ", "_").replace(".", "")
            header_map[col_clean] = idx
        rows = rows[1:]

    # Delete existing data for selected year to prevent duplicates (do not commit yet)
    try:
        if csv_type == 'cutoff':
            SeatInfo.query.filter_by(year=year).delete()
        elif csv_type == 'rank':
            CgpaRankRange.query.filter_by(year=year).delete()
        else:
            return redirect('/admin/users?error=invalid_csv_type#db')
    except Exception as e:
        db.session.rollback()
        return redirect(f"/admin/users?error=Database reset failed: {url_quote(str(e))}#db")

    inserted_count = 0
    errors = []

    for line_num, row in enumerate(rows, start=1 if not has_header else 2):
        if not row or not any(x.strip() for x in row):
            continue  # Skip empty lines
        try:
            if csv_type == 'cutoff':
                if has_header:
                    college_name = row[header_map.get('college_name', header_map.get('college', 1))].strip()
                    college_type = row[header_map.get('college_type', 2)].strip()
                    branch = row[header_map.get('branch', 3)].strip()
                    opening_rank = int(row[header_map.get('opening_rank', header_map.get('opening', 4))].strip())
                    closing_rank = int(row[header_map.get('closing_rank', header_map.get('closing', 5))].strip())
                    
                    if 'category' in header_map and 'gender' in header_map:
                        category = row[header_map['category']].strip()
                        gender = row[header_map['gender']].strip()
                    elif 'category_field' in header_map:
                        cat_field = row[header_map['category_field']].strip()
                        if '/' in cat_field:
                            parts = cat_field.split('/')
                            category = parts[0].strip()
                            gender = parts[2].strip() if len(parts) >= 3 else (parts[1].strip() if len(parts) == 2 else 'OP')
                        else:
                            category = cat_field
                            gender = 'OP'
                    else:
                        category = 'UR'
                        gender = 'OP'

                    domicile = row[header_map.get('domicile', 7)].strip().upper()
                    total_seats = int(row[header_map.get('total_seats', header_map.get('seats', 8))].strip())
                    year_val = int(row[header_map.get('year', 9)].strip())
                else:
                    if len(row) >= 11:
                        _sno, college_name, college_type, branch, _quota, opening_rank, closing_rank, category_field, domicile, total_seats, year_val = [c.strip() for c in row[:11]]
                        if '/' in category_field:
                            parts = category_field.split('/')
                            category = parts[0].strip()
                            gender = parts[2].strip() if len(parts) >= 3 else (parts[1].strip() if len(parts) == 2 else 'OP')
                        else:
                            category = category_field
                            gender = 'OP'
                        opening_rank = int(opening_rank)
                        closing_rank = int(closing_rank)
                        total_seats = int(total_seats)
                        year_val = int(year_val)
                    elif len(row) >= 10:
                        college_name, college_type, branch, opening_rank, closing_rank, category, gender, domicile, total_seats, year_val = [c.strip() for c in row[:10]]
                        opening_rank = int(opening_rank)
                        closing_rank = int(closing_rank)
                        total_seats = int(total_seats)
                        year_val = int(year_val)
                    else:
                        raise ValueError(f"Expected at least 10 columns, got {len(row)}")

                # Validate Domicile, Gender, Type and Category
                college_type_upper = college_type.upper()
                if college_type_upper == 'GOVERNMENT':
                    college_type = 'GOVT'
                elif college_type_upper == 'GOVT':
                    college_type = 'GOVT'
                elif college_type_upper == 'PRIVATE':
                    college_type = 'Private'
                elif college_type_upper == 'SFI' or college_type_upper == 'S.F.I.':
                    college_type = 'S.F.I.'

                category = category.strip().upper()
                gender = gender.strip().upper()
                domicile = domicile.strip().upper()

                if college_type not in {'GOVT', 'Private', 'S.F.I.'}:
                    raise ValueError(f"Invalid college type: {college_type}")
                if category not in {'UR', 'OBC', 'SC', 'ST'}:
                    raise ValueError(f"Invalid category: {category}")
                if gender not in {'M', 'F', 'OP'}:
                    raise ValueError(f"Invalid gender: {gender}")
                if domicile not in {'Y', 'N'}:
                    raise ValueError(f"Invalid domicile: {domicile}")

                new_record = SeatInfo(
                    college_name=college_name,
                    college_type=college_type,
                    branch=branch,
                    opening_rank=opening_rank,
                    closing_rank=closing_rank,
                    category=category,
                    gender=gender,
                    domicile=domicile,
                    total_seats=total_seats,
                    year=year
                )
                db.session.add(new_record)

            elif csv_type == 'rank':
                if has_header:
                    cgpa = float(row[header_map.get('cgpa', 0)].strip())
                    min_rank = int(row[header_map.get('min_rank', header_map.get('min', 1))].strip())
                    max_rank = int(row[header_map.get('max_rank', header_map.get('max', 2))].strip())
                    year_val = int(row[header_map.get('year', 3)].strip())
                else:
                    if len(row) < 4:
                        raise ValueError(f"Expected 4 columns, got {len(row)}")
                    cgpa, min_rank, max_rank, year_val = [c.strip() for c in row[:4]]
                    cgpa = float(cgpa)
                    min_rank = int(min_rank)
                    max_rank = int(max_rank)
                    year_val = int(year_val)

                new_record = CgpaRankRange(
                    cgpa=cgpa,
                    min_rank=min_rank,
                    max_rank=max_rank,
                    year=year
                )
                db.session.add(new_record)

            inserted_count += 1

        except Exception as e:
            errors.append(f"Line {line_num}: {str(e)}")

    if errors:
        db.session.rollback()
        err_str = f"Upload aborted: {len(errors)} validation errors encountered. No database changes were saved. Sample errors: " + "; ".join(errors[:4])
        return redirect(f"/admin/users?error={url_quote(err_str)}#db")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return redirect(f"/admin/users?error=Commit failed: {url_quote(str(e))}#db")

    fetch_rank_maps_cache()

    success_msg = f"Successfully uploaded CSV! Inserted {inserted_count} rows for the year {year}."
    return redirect(f"/admin/users?success={url_quote(success_msg)}#db")


@app.route('/api/v1/admin/user-shortlist/<int:user_id>')
@login_required
def admin_user_shortlist(user_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return jsonify({"error": "Access Denied"}), 403
        
    items = load_cloud_shortlist(user_id)
    return jsonify({"items": items})


@app.route('/admin/broadcast', methods=['POST'])
@login_required
def admin_broadcast():
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    subject = request.form.get('subject', '').strip()
    body = request.form.get('body', '').strip()
    recipient_type = request.form.get('recipient_type', 'all').strip()
    specific_user_id = request.form.get('specific_user_id', '').strip()

    users = User.query.order_by(User.created_at.desc()).all()
    stats = get_admin_dashboard_stats(users)
    reviews = CollegeReview.query.order_by(CollegeReview.created_at.desc()).all()
    vault_slips = ChoiceVault.query.order_by(ChoiceVault.id.asc()).all()
    analytics = get_shortlist_analytics_stats()
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    recommendations = RecommendationChoice.query.order_by(RecommendationChoice.sn.asc()).all()

    if not subject or not body:
        return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
            avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
            reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
            broadcast_error="Subject and Message body cannot be empty.")

    emails = []
    recipient_display = ""

    if recipient_type == 'single':
        if not specific_user_id:
            return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
                avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
                reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
                broadcast_error="Please select a specific student to send the message.")
        
        target_user = db.session.get(User, specific_user_id)
        if not target_user:
            return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
                avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
                reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
                broadcast_error="Selected student not found in database.")
        
        if not target_user.email:
            return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
                avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
                reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
                broadcast_error="Selected student does not have a valid email address.")
        
        emails = [target_user.email]
        recipient_display = target_user.display_name or target_user.email
    else:
        # Only send to users who have alerts enabled
        subscribed_users = User.query.filter_by(notify_counselling=1).all()
        emails = [u.email for u in subscribed_users if u.email]
        recipient_display = f"{len(emails)} subscribed students"

    if not emails:
        return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
            avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
            reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
            broadcast_error="No recipients found for this selection.")

    success_count, fail_count = send_broadcast_email(emails, subject, body)

    return render_template('admin_dashboard.html', users=users, total_users=stats['total_users'],
        avg_cgpa=stats['avg_cgpa'], branch_stats=stats['branch_stats'], category_stats=stats['category_stats'],
        reviews=reviews, vault_slips=vault_slips, analytics=analytics, coupons=coupons, recommendations=recommendations,
        broadcast_success=f"Email sent successfully to {recipient_display}. ({success_count} succeeded, {fail_count} failed)")


@app.route('/admin/approve-review/<int:review_id>', methods=['POST'])
@login_required
def admin_approve_review(review_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    review = db.session.get(CollegeReview, review_id)
    if review:
        review.is_approved = True
        db.session.commit()
    return redirect('/admin/users#reviews')


@app.route('/admin/delete-review/<int:review_id>', methods=['POST'])
@login_required
def admin_delete_review(review_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403
    
    review = db.session.get(CollegeReview, review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
    return redirect('/admin/users#reviews')


@app.route('/admin/recommendation/save', methods=['POST'])
@login_required
def admin_save_recommendation():
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    choice_id = request.form.get('choice_id', '').strip()
    sn_val = request.form.get('sn', '').strip()
    db_name = request.form.get('db_name', '').strip()
    branch = request.form.get('branch', '').strip()
    display_name = request.form.get('display_name', '').strip()

    if not sn_val or not db_name or not branch or not display_name:
        return redirect('/admin/users?error=All+fields+are+required#recommendations')

    try:
        sn = int(sn_val)
    except ValueError:
        return redirect('/admin/users?error=Serial+number+must+be+an+integer#recommendations')

    if choice_id:
        choice = db.session.get(RecommendationChoice, int(choice_id))
        if not choice:
            return redirect('/admin/users?error=Recommendation+not+found#recommendations')
        choice.sn = sn
        choice.db_name = db_name
        choice.branch = branch
        choice.display_name = display_name
    else:
        choice = RecommendationChoice(
            sn=sn,
            db_name=db_name,
            branch=branch,
            display_name=display_name
        )
        db.session.add(choice)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return redirect(f"/admin/users?error=Database+error:+{url_quote(str(e))}#recommendations")

    return redirect('/admin/users?success=Recommendation+saved+successfully#recommendations')


@app.route('/admin/recommendation/delete/<int:choice_id>', methods=['POST'])
@login_required
def admin_delete_recommendation(choice_id):
    admin = current_user()
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    if not admin or admin.email.strip().lower() != admin_email:
        return "Access Denied: Admin privileges required.", 403

    choice = db.session.get(RecommendationChoice, choice_id)
    if choice:
        db.session.delete(choice)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return redirect(f"/admin/users?error=Failed+to+delete:+{url_quote(str(e))}#recommendations")

    return redirect('/admin/users?success=Recommendation+deleted+successfully#recommendations')


@app.route('/shortlist/print')
@login_required
def shortlist_print():
    user = current_user()
    shortlist = load_cloud_shortlist(user.id) if user else []
    return render_template('shortlist_print.html', user=user, shortlist=shortlist)


@app.route('/shortlist/export/csv')
@login_required
def shortlist_export_csv():
    import csv
    import io
    from flask import Response
    user = current_user()
    shortlist = load_cloud_shortlist(user.id) if user else []
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow([
        "S.No.",
        "College Name",
        "Branch Name",
        "Branch Code",
        "Admission Chance (Probability)",
        "City",
        "Counselling Year"
    ])
    
    # Write CSV rows
    for index, item in enumerate(shortlist, start=1):
        writer.writerow([
            index,
            item.get('college_name', ''),
            item.get('branch_name', ''),
            item.get('branch', ''),
            item.get('prob_type', 'N/A'),
            item.get('city', ''),
            item.get('year', '')
        ])
    
    output.seek(0)
    
    # Clean user name for filename compatibility
    safe_name = "".join(c for c in (user.display_name or "student") if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_name = safe_name.replace(" ", "_")
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=MP_DTE_Shortlist_{safe_name}.csv"}
    )


# ── API v1 ───────────────────────────────────────────────────────────────────

@app.route('/api/v1/counselling-schedule')
def api_schedule():
    return jsonify(get_counselling_schedule())


@app.route('/api/v1/college/route-info')
def api_college_route_info():
    home_city = request.args.get('home_city', 'All').strip()
    college_name = request.args.get('college_name', '').strip()
    category = request.args.get('category', 'UR').strip()
    
    if not college_name:
        return jsonify({"error": "college_name required"}), 400
        
    dest_city = infer_city_from_college_name(college_name) or "Unknown"
    
    distance_km = 0
    distance_text = "—"
    if home_city and home_city != 'All':
        dist = distance_from_home(home_city, college_name)
        if dist:
            distance_km = dist.get('distance_km', 0)
            distance_text = dist.get('distance_text', '—')
            
    route_steps = []
    if home_city == 'All':
        route_steps.append("Please specify your Home City to generate customized travel instructions.")
        route_steps.append(f"Once you reach {dest_city}, take local transport (Auto/E-rickshaw) to the {college_name} campus.")
    elif home_city == dest_city:
        route_steps.append(f"Since you are in {home_city}, you can use local city transport (Auto-rickshaw, E-rickshaw, or City Bus).")
        route_steps.append(f"Head directly towards the administrative block of {college_name}.")
        route_steps.append("Ask for the 'Admission Reporting Cell' inside the campus.")
    else:
        route_steps.append(f"Start from your residence in {home_city} and go to the nearest railway station or major bus stand.")
        
        has_train = True
        duration = "4-6 hours"
        if distance_km > 0:
            hrs = max(1, round(distance_km / 55))
            duration = f"~{hrs} to {hrs + 2} hours"
            
        route_steps.append(f"Board a direct Express/Superfast train or an AC/Charter sleeper bus towards {dest_city} (Travel duration: {duration}).")
        
        cost_est = max(100, int(distance_km * 2.2)) if distance_km > 0 else 250
        route_steps.append(f"Estimated transit ticket cost: ₹{cost_est} - ₹{cost_est + 200} (Sleeper/AC Bus).")
        
        route_steps.append(f"After arriving at {dest_city} Railway Station / Bus Stand, take a local auto-rickshaw or e-rickshaw directly to the {college_name} campus.")
        route_steps.append("Report to the 'Admission Reporting Cell' inside the administrative block.")

    profile = get_college_profile(college_name) or {}
    
    import urllib.parse
    AUTHENTIC_CONTACTS = [
        {
            "keys": ["sgsits", "g.s. institute of technology"],
            "website": "https://www.sgsits.ac.in",
            "phone": "0731-2582100",
            "email": "director@sgsits.ac.in",
            "address": "23 Sir M. Visvesvaraya Marg, Vallabh Nagar, Indore, Madhya Pradesh 452003"
        },
        {
            "keys": ["jabalpur engineering", "jec"],
            "website": "https://www.jecjabalpur.ac.in",
            "phone": "0761-2673114",
            "email": "principal@jecjabalpur.ac.in",
            "address": "Gokalpur, Ranjhi, Jabalpur, Madhya Pradesh 482011"
        },
        {
            "keys": ["iet davv", "institute of engineering and technology davv", "institute of engineering & technology davv"],
            "website": "https://www.ietdavv.edu.in",
            "phone": "0731-2361116",
            "email": "director@ietdavv.edu.in",
            "address": "Khandwa Road, Indore, Madhya Pradesh 452001"
        },
        {
            "keys": ["madhav institute", "mits"],
            "website": "https://www.mitsgwalior.in",
            "phone": "0751-2403095",
            "email": "director@mitsgwalior.in",
            "address": "Gola ka Mandir, Gwalior, Madhya Pradesh 474005"
        },
        {
            "keys": ["uit rgpv bhopal", "university institute of technology rgpv", "university institute of technology repv"],
            "website": "https://www.uitrgpv.ac.in",
            "phone": "0755-2678812",
            "email": "uit_director@rgtu.net",
            "address": "Airport Bypass Road, Gandhi Nagar, Bhopal, Madhya Pradesh 462033"
        },
        {
            "keys": ["ujjain engineering", "uec"],
            "website": "http://www.uecu.ac.in",
            "phone": "0734-2511912",
            "email": "principal@uecu.ac.in",
            "address": "Sanwer Road, Ujjain, Madhya Pradesh 456010"
        },
        {
            "keys": ["rewa engineering", "rec"],
            "website": "http://www.recrewamp.ac.in",
            "phone": "07662-220065",
            "email": "principalrec@rediffmail.com",
            "address": "Rewa, Madhya Pradesh 486001"
        },
        {
            "keys": ["samrat ashok", "sati"],
            "website": "https://www.satiengg.in",
            "phone": "07592-250121",
            "email": "director@satiengg.in",
            "address": "Civil Lines, Vidisha, Madhya Pradesh 464001"
        },
        {
            "keys": ["indira gandhi", "igec"],
            "website": "http://www.igecsagar.ac.in",
            "phone": "07582-263850",
            "email": "principaligec@gmail.com",
            "address": "Baheriya, Sagar, Madhya Pradesh 470021"
        },
        {
            "keys": ["rustamji", "rjit"],
            "website": "https://www.rjit.ac.in",
            "phone": "07524-274319",
            "email": "rjit_bsf@yahoo.com",
            "address": "BSF Academy, Tekanpur, Gwalior, Madhya Pradesh 475005"
        },
        {
            "keys": ["lakshmi narain college of technology jabalpur", "lnct jabalpur"],
            "website": "http://www.lnctjabalpur.ac.in",
            "phone": "0761-4261100",
            "email": "admission@lnctjabalpur.ac.in",
            "address": "Andhua, Near Medical College, Jabalpur, Madhya Pradesh 482003"
        },
        {
            "keys": ["lakshmi narain college of technology indore", "lnct indore"],
            "website": "http://www.lnctindore.ac.in",
            "phone": "0731-4253100",
            "email": "admission@lnctindore.ac.in",
            "address": "Sector-D, Sanwer Road, Indore, Madhya Pradesh 452015"
        },
        {
            "keys": ["lakshmi narain", "lnct"],
            "website": "https://www.lnct.ac.in",
            "phone": "0755-6185300",
            "email": "admission@lnct.ac.in",
            "address": "Kalchuri Nagar, Raisen Road, Bhopal, Madhya Pradesh 462022"
        },
        {
            "keys": ["oriental institute of science & technology, jabalpur", "oriental institute of science and technology, jabalpur"],
            "website": "http://www.oistjabalpur.org",
            "phone": "0761-2441334",
            "email": "oistjabalpur@oriental.ac.in",
            "address": "Katni Bypass Road, Jabalpur, Madhya Pradesh 482003"
        },
        {
            "keys": ["oriental college of technology"],
            "website": "https://www.oriental.ac.in",
            "phone": "0755-2529026",
            "email": "admissions@oriental.ac.in",
            "address": "Thakral Nagar, Raisen Road, Bhopal, Madhya Pradesh 462021"
        },
        {
            "keys": ["oriental institute", "oist"],
            "website": "https://www.oriental.ac.in",
            "phone": "0755-2529026",
            "email": "admissions@oriental.ac.in",
            "address": "Thakral Nagar, Raisen Road, Bhopal, Madhya Pradesh 462021"
        },
        {
            "keys": ["acropolis"],
            "website": "https://www.acropolis.in",
            "phone": "0731-4730000",
            "email": "admission@acropolis.in",
            "address": "Bypass Road, Manglia, Indore, Madhya Pradesh 453771"
        },
        {
            "keys": ["ips academy"],
            "website": "https://ies.ipsacademy.org",
            "phone": "0731-4014601",
            "email": "admission.ies@ipsacademy.org",
            "address": "Knowledge Village, Rajendra Nagar, A.B. Road, Indore, Madhya Pradesh 452012"
        },
        {
            "keys": ["rgpv shivpuri"],
            "website": "http://www.uitrgpvshivpuri.ac.in",
            "phone": "07492-223657",
            "email": "uitrgpvshivpuri@gmail.com",
            "address": "Satanwada, Shivpuri, Madhya Pradesh 473551"
        },
        {
            "keys": ["rgpv shahdol"],
            "website": "http://www.uitrgpvshahdol.ac.in",
            "phone": "07652-242045",
            "email": "principaluitshahdol@gmail.com",
            "address": "Near Jail Building, Shahdol, Madhya Pradesh 484001"
        },
        {
            "keys": ["uit jhabua", "rgpv jhabua"],
            "website": "http://www.uitrgpvjhabua.ac.in",
            "phone": "07392-244312",
            "email": "uitrgpvjhabua@gmail.com",
            "address": "Near Gadwada, Jhabua, Madhya Pradesh 457661"
        },
        {
            "keys": ["barkatullah", "buit"],
            "website": "http://www.buit.ac.in",
            "phone": "0755-2677329",
            "email": "director@buit.ac.in",
            "address": "Barkatullah University Campus, Hoshangabad Road, Bhopal, Madhya Pradesh 462026"
        },
        {
            "keys": ["gyan ganga college of technology"],
            "website": "https://www.ggct.co.in",
            "phone": "0761-2203001",
            "email": "admission@gyanganga.org",
            "address": "P.O. Tilwara Ghat, Near Bargi Hills, Jabalpur, Madhya Pradesh 482003"
        },
        {
            "keys": ["gyan ganga", "ggits"],
            "website": "https://www.gyanganga.org",
            "phone": "0761-2203001",
            "email": "admission@gyanganga.org",
            "address": "P.O. Tilwara Ghat, Near Bargi Hills, Jabalpur, Madhya Pradesh 482003"
        },
        {
            "keys": ["shri ram institute of technology", "srit"],
            "website": "https://www.sritgroup.org",
            "phone": "0761-4001933",
            "email": "info@sritgroup.org",
            "address": "Shri Ram Group Campus, Near ITI, Madhotal, Jabalpur, Madhya Pradesh 482002"
        },
        {
            "keys": ["prestige institute"],
            "website": "https://www.piemr.edu.in",
            "phone": "0731-4013000",
            "email": "info@piemr.edu.in",
            "address": "Sector-D, Scheme No 74, Opp. Vijay Nagar, Indore, Madhya Pradesh 452010"
        },
        {
            "keys": ["sagar institute of research", "sirt"],
            "website": "https://www.sirtbhopal.ac.in",
            "phone": "0755-4983100",
            "email": "sirtbhopal@sagar.ac.in",
            "address": "Ayodhya Bypass Road, Bhopal, Madhya Pradesh 462041"
        },
        {
            "keys": ["sistec"],
            "website": "https://www.sistec.ac.in",
            "phone": "0755-4206035",
            "email": "admissions@sistec.ac.in",
            "address": "Opp. International Airport, Gandhi Nagar, Bhopal, Madhya Pradesh 462036"
        },
        {
            "keys": ["bansal institute of science"],
            "website": "https://bistbhopal.ac.in",
            "phone": "0755-6681100",
            "email": "bist@bansal.ac.in",
            "address": "Kokta, Anand Nagar, Raisen Road, Bhopal, Madhya Pradesh 462021"
        },
        {
            "keys": ["truba"],
            "website": "https://www.trubainstitute.ac.in",
            "phone": "0755-2734691",
            "email": "info@trubainstitute.ac.in",
            "address": "Karond-Gandhi Nagar Bypass Road, Bhopal, Madhya Pradesh 462038"
        },
        {
            "keys": ["nowgong engineering", "nec"],
            "website": "https://www.necnowgong.ac.in",
            "phone": "07685-257525",
            "email": "principalnecnowgong@gmail.com",
            "address": "Nowgong, Chhatarpur, Madhya Pradesh 471111"
        },
        {
            "keys": ["jiwaji"],
            "website": "http://www.jiwaji.edu",
            "phone": "0751-2442701",
            "email": "director@jiwaji.edu",
            "address": "Jiwaji University Campus, Sachin Tendulkar Road, Gwalior, Madhya Pradesh 47411"
        },
        {
            "keys": ["vikram university"],
            "website": "http://www.vikramuniv.ac.in",
            "phone": "0734-2514270",
            "email": "director.soet.vu@gmail.com",
            "address": "Vikram University, Dewas Road, Ujjain, Madhya Pradesh 456010"
        }
    ]

    name_norm = re.sub(r'[^a-z0-9]', '', college_name.lower())
    matched_info = None
    for item in AUTHENTIC_CONTACTS:
        for k in item["keys"]:
            k_norm = re.sub(r'[^a-z0-9]', '', k.lower())
            if k_norm in name_norm:
                matched_info = item
                break
        if matched_info:
            break

    if matched_info:
        contact = {
            "address": matched_info["address"],
            "phone": matched_info["phone"],
            "email": matched_info["email"],
            "website": matched_info["website"]
        }
    else:
        q = urllib.parse.quote_plus(f"{college_name} official website")
        website = f"https://www.google.com/search?q={q}"
        phone = "0755-6720200 (DTE Support Helpline)"
        address = profile.get("address") or f"{college_name}, {dest_city}, Madhya Pradesh, India"
        email = "Refer to Official Website"
        contact = {
            "address": address,
            "phone": phone,
            "email": email,
            "website": website
        }

    docs = [
        {"name": "DTE Seat Allotment Letter", "desc": "Original copy + 3 photocopies. Print from DTE candidate login portal."},
        {"name": "DTE Verification Slip", "desc": "Original copy + 3 photocopies. Issued after online document verification."},
        {"name": "Diploma Marksheets (All Semesters)", "desc": "Original marksheets of all semesters (1st to 6th sem)."},
        {"name": "High School (10th) Marksheet", "desc": "Original certificate for candidate date of birth verification."},
        {"name": "Transfer Certificate (TC) & Character Certificate", "desc": "Original certificates issued by your last attended Polytechnic institute."},
        {"name": "Migration Certificate", "desc": "Original certificate (required if you completed Diploma from outside MP or a different board than RGPV)."},
        {"name": "Aadhaar Card", "desc": "Photocopy of candidate's Aadhaar Card for identification."},
        {"name": "Passport Size Photographs", "desc": "4-6 recent colored passport size photographs."}
    ]
    
    if category in ['OBC', 'SC', 'ST']:
        docs.append({"name": f"{category} Category Caste Certificate", "desc": "Digital Caste Certificate issued by SDM / competent authority of Govt. of Madhya Pradesh."})
        docs.append({"name": "Income Certificate", "desc": "Valid Family Income Certificate issued recently for scholarship verification."})
    elif category == 'EWS':
        docs.append({"name": "Economically Weaker Section (EWS) Certificate", "desc": "Valid certificate issued by competent authority for the current financial year."})
        docs.append({"name": "Income Certificate", "desc": "Family Income Certificate to support EWS status."})
        
    if request.args.get('tfw') == 'Y':
        docs.append({"name": "TFW Income Certificate", "desc": "Original Income Certificate showing family income < 8 LPA (mandatory for Tuition Fee Waiver seats)."})

    docs.append({"name": "Gap Certificate (if applicable)", "desc": "Notarized affidavit on ₹50 Stamp Paper if there was any gap year in your studies after completing Diploma."})

    return jsonify({
        "college_name": college_name,
        "home_city": home_city,
        "dest_city": dest_city,
        "distance_text": distance_text,
        "route_steps": route_steps,
        "contact": contact,
        "documents": docs
    })


@app.route('/api/v1/choices/optimize', methods=['POST'])
def api_optimize_choices():
    data = request.get_json(silent=True) or {}
    cgpa_str = data.get('cgpa')
    category = data.get('category', 'UR').strip()
    gender = data.get('gender', 'M').strip()
    domicile = data.get('domicile', 'Y').strip()
    year_str = data.get('year', '')
    choices = data.get('choices', [])

    if not cgpa_str:
        return jsonify({"error": "Missing CGPA for optimization"}), 400

    try:
        cgpa = float(cgpa_str)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid CGPA value"}), 400

    try:
        year = int(year_str) if year_str else (YEARS[0] if YEARS else 2025)
    except (TypeError, ValueError):
        year = YEARS[0] if YEARS else 2025

    cgpa_map = fetch_cgpa_to_rank_map(year)
    if not cgpa_map:
        return jsonify({"error": f"No rank mapping data found for year {year}"}), 400

    min_rank, max_rank = estimate_rank_range(cgpa_map, cgpa)

    optimized = []
    for index, choice in enumerate(choices):
        col_name = choice.get('college_name', '').strip()
        branch = choice.get('branch', '').strip()
        if not col_name or not branch:
            continue

        # Look up SeatInfo for this specific college/branch/category
        allowed_genders = ["F", "M", "OP"] if gender == "F" else ["M", "OP"]
        seat = SeatInfo.query.filter_by(
            college_name=col_name,
            branch=branch,
            year=year,
            category=category,
            domicile=domicile
        ).filter(SeatInfo.gender.in_(allowed_genders)).order_by(SeatInfo.closing_rank.desc()).first()

        if not seat:
            # Fallback 1: category only
            seat = SeatInfo.query.filter_by(
                college_name=col_name,
                branch=branch,
                year=year,
                category=category
            ).first()

        if not seat:
            # Fallback 2: general UR/OP seat
            seat = SeatInfo.query.filter_by(
                college_name=col_name,
                branch=branch,
                year=year
            ).first()

        if seat:
            prob = calc_probability(min_rank, max_rank, seat.opening_rank, seat.closing_rank)
            closing_rank = seat.closing_rank
        else:
            prob = 50
            closing_rank = 99999

        optimized.append({
            "college_name": col_name,
            "branch": branch,
            "branch_name": BRANCH_NAMES.get(branch, branch),
            "probability": prob,
            "closing_rank": closing_rank,
            "original_index": index
        })

    # Sort by probability ascending first, then by closing_rank ascending as a tie-breaker
    # This places Dream choices (lowest probability) at the top, and Safe choices at the bottom.
    optimized.sort(key=lambda x: (x["probability"], x["closing_rank"]))

    # Dynamic bucket labels and count calculation
    dream_count = 0
    target_count = 0
    safe_count = 0
    for item in optimized:
        prob = item["probability"]
        if item["closing_rank"] == 99999: # Default fallback rank (data missing)
            item["bucket"] = "safe"
            safe_count += 1
        elif prob < 40:
            item["bucket"] = "dream"
            dream_count += 1
        elif prob < 75:
            item["bucket"] = "target"
            target_count += 1
        else:
            item["bucket"] = "safe"
            safe_count += 1

    return jsonify({
        "success": True,
        "choices": optimized,
        "dream_count": dream_count,
        "target_count": target_count,
        "safe_count": safe_count
    })


@app.route('/api/v1/reviews', methods=['GET', 'POST'])
def api_reviews():
    if request.method == 'GET':
        name = request.args.get('college_name', '').strip()
        if not name:
            return jsonify({"error": "college_name required"}), 400
        rows = CollegeReview.query.filter_by(
            college_name=name, is_approved=True,
        ).order_by(CollegeReview.created_at.desc()).limit(30).all()
        return jsonify([{
            "author_name": r.author_name,
            "rating": r.rating,
            "comment": r.comment,
            "branch": r.branch,
        } for r in rows])

    user = current_user()
    if not user:
        return jsonify({"error": "Login is required to submit a review."}), 401

    data = request.get_json(silent=True) or request.form
    name = (data.get('college_name') or '').strip()
    author = (user.display_name or 'Anonymous').strip()[:80]
    comment = (data.get('comment') or '').strip()
    try:
        rating = int(data.get('rating', 0))
    except (TypeError, ValueError):
        rating = 0
    if not name or not comment or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid review data"}), 400
    review = CollegeReview(
        college_name=name, author_name=author,
        rating=rating, comment=comment[:1000],
        branch=(data.get('branch') or '')[:32],
        is_approved=False,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"success": True, "id": review.id})


@app.route('/api/v1/shortlist/cloud', methods=['GET', 'POST'])
@login_required
@limiter.limit("60 per minute")
def api_cloud_shortlist():
    user = current_user()
    if request.method == 'GET':
        return jsonify({"items": load_cloud_shortlist(user.id)})
    data = request.get_json(silent=True) or {}
    items = data.get('items', [])
    save_cloud_shortlist(user.id, items)
    return jsonify({"success": True, "count": len(items)})


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate dynamic sitemap.xml for SEO indexing."""
    from urllib.parse import quote
    
    # Core student-facing pages
    static_routes = [
        '',
        'about',
        'predictor',
        'choice-builder',
        'merit-insights',
        'schedule',
        'how-it-works',
        'compare',
        'search',
        'contact',
        'faq',
        'account'
    ]
    
    base_url = request.url_root.rstrip('/')
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Add static routes
    from datetime import datetime
    today = datetime.utcnow().strftime('%Y-%m-%d')
    for route in static_routes:
        loc = f"{base_url}/{route}" if route else base_url
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{loc}</loc>')
        xml_lines.append(f'    <lastmod>{today}</lastmod>')
        xml_lines.append('    <changefreq>weekly</changefreq>')
        xml_lines.append('    <priority>0.8</priority>')
        xml_lines.append('  </url>')
        
    # Add dynamic college details pages
    try:
        colleges = db.session.query(SeatInfo.college_name).distinct().all()
        for c in colleges:
            name = c[0]
            if name:
                encoded_name = quote(name)
                loc = f"{base_url}/college?name={encoded_name}"
                xml_lines.append('  <url>')
                # Escape XML entity characters in loc if any remain
                xml_loc = loc.replace('&', '&amp;').replace("'", '&apos;').replace('"', '&quot;')
                xml_lines.append(f'    <loc>{xml_loc}</loc>')
                xml_lines.append(f'    <lastmod>{today}</lastmod>')
                xml_lines.append('    <changefreq>monthly</changefreq>')
                xml_lines.append('    <priority>0.6</priority>')
                xml_lines.append('  </url>')
    except Exception as e:
        # Fallback if DB query fails
        pass
        
    # Add dynamic FAQ details pages
    for f in FAQ_LIST:
        loc = f"{base_url}/faq/{f['slug']}"
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{loc}</loc>')
        xml_lines.append(f'    <lastmod>{today}</lastmod>')
        xml_lines.append('    <changefreq>monthly</changefreq>')
        xml_lines.append('    <priority>0.7</priority>')
        xml_lines.append('  </url>')
        
    xml_lines.append('</urlset>')
    
    xml_content = '\n'.join(xml_lines)
    return app.response_class(xml_content, mimetype='application/xml')


@app.route('/robots.txt', methods=['GET'])
def robots():
    """Serve standard robots.txt file."""
    base_url = request.url_root.rstrip('/')
    content = f"""User-agent: *
Allow: /
Allow: /about
Allow: /predictor
Allow: /choice-builder
Allow: /schedule
Allow: /how-it-works
Allow: /compare
Allow: /search
Allow: /contact
Allow: /faq
Allow: /college
Disallow: /admin/
Disallow: /checklist
Disallow: /shortlist/print
Disallow: /api/
Disallow: /account

Sitemap: {base_url}/sitemap.xml
"""
    return app.response_class(content, mimetype='text/plain')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/buy-premium-with-coins', methods=['POST'])
@login_required
def buy_premium_with_coins():
    user = current_user()
    if not user:
        return redirect('/account')
        
    if user.is_premium:
        flash("You already have Premium access!", "info")
        return redirect('/account')
        
    # Cost in coins: 1990
    required_coins = 1990
    if (user.coins or 0) < required_coins:
        flash(f"Insufficient coins. You need {required_coins} coins (₹199) but you only have {user.coins} coins.", "error")
        return redirect('/premium')
        
    user.coins -= required_coins
    user.is_premium = True
    db.session.commit()
    flash("Congratulations! You have unlocked Premium Pro using your coins!", "success")
    return redirect('/account')


if __name__ == '__main__':
    app.run(debug=False)
