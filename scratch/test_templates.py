import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

def test_predictor_template():
    print("=== Testing Predictor Template Render ===")
    with app.test_request_context('/predictor?cgpa=8.0&category=UR&gender=M'):
        with app.test_client() as client:
            resp = client.get('/predictor?cgpa=8.0&category=UR&gender=M')
            print(f"GET /predictor status code: {resp.status_code}")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            # Verify GET works
            html = resp.get_data(as_text=True)
            assert "whatif-slider" not in html, "whatif-slider should have been removed!"
            assert "whatif-preview" not in html, "whatif-preview should have been removed!"
            assert "What-if" not in html, "What-if text should have been removed!"
            assert "toggleAdvancedLocation" in html, "toggleAdvancedLocation script should be present!"
            assert "advanced-location-row" in html, "advanced-location-row container should be present!"
            
            # Verify POST works
            post_data = {
                'cgpa': '8.5',
                'category': 'UR',
                'gender': 'M',
                'college_type': 'Any',
                'branch': ['CSE', 'ECE'],
                'domicile': 'Y',
                'city': 'All',
                'district': 'All',
                'home_city': 'All',
                'max_distance_km': ''
            }
            resp_post = client.post('/predictor', data=post_data)
            print(f"POST /predictor status code: {resp_post.status_code}")
            assert resp_post.status_code == 200, f"Expected 200 on POST, got {resp_post.status_code}"
            html_post = resp_post.get_data(as_text=True)
            assert "Analysis of Available Colleges" in html_post, "Should display results section"
            print("Template POST test passed successfully!")

def test_mobile_navbar():
    print("=== Testing Mobile Navbar Elements ===")
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "nav-brand-mobile" in html, "nav-brand-mobile element should be in HTML"
        assert "nav-hamburger" in html, "nav-hamburger button should be in HTML"
        assert "nav-links" in html, "nav-links container should be in HTML"
        assert 'href="/"' in html, "Home link should be present in header or menu"
        assert 'class="header-content"' in html, "header-content should be in HTML"
        print("Mobile navbar assertion test passed successfully!")

def test_compare_template():
    print("=== Testing Compare Template Render ===")
    with app.test_client() as client:
        resp = client.get('/compare?colleges=Acropolis+Institute+of+Technology+%26+Research%2C+Indore+(2005)&colleges=ADINA+INSTITUTE+OF+SCIENCE+%26+TECHNOLOGY%2C+SAGAR+(2009)')
        print(f"GET /compare status code: {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        html = resp.get_data(as_text=True)
        assert "Avg Placement Package" in html, "Placement Package row should be present!"
        assert "Highest Package" in html, "Highest Package row should be present!"
        assert "Top Recruiters" in html, "Top Recruiters row should be present!"
        print("Compare template test passed successfully!")

def test_account_registration_and_admin():
    print("=== Testing Account Registration and Admin Dashboard ===")
    
    # Clean up any existing test user to guarantee test idempotency
    with app.app_context():
        from models import User, CloudShortlist
        from db import db
        u = User.query.filter_by(email='student_test@example.com').first()
        if u:
            CloudShortlist.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
            db.session.commit()

    with app.test_client() as client:
        # 1. GET /account should render without errors
        resp_acc = client.get('/account')
        assert resp_acc.status_code == 200, f"Expected 200, got {resp_acc.status_code}"
        assert "Register New Student Account" in resp_acc.get_data(as_text=True)

        # 2. Test registration post validation and OTP flow
        reg_data = {
            'action': 'register',
            'display_name': 'Test Student',
            'email': 'student_test@example.com',
            'password': 'SecurePass123!',
            'mobile_number': '9876543210',
            'polytechnic_college': 'Govt Polytechnic Bhopal',
            'diploma_branch': 'CSE',
            'cgpa': '8.75',
            'category': 'OBC',
            'gender': 'M'
        }
        resp_reg = client.post('/account', data=reg_data, follow_redirects=True)
        assert resp_reg.status_code == 200, f"Expected 200 on registration POST, got {resp_reg.status_code}"
        assert "Verification OTP has been sent" in resp_reg.get_data(as_text=True)

        # Retrieve OTP from the mock session
        with client.session_transaction() as sess:
            otp = sess.get("registration_otp")
            assert otp is not None, "OTP should be stored in the session"

        # Submit OTP to verify and complete registration
        resp_verify = client.post('/account', data={
            'action': 'verify_otp',
            'otp': otp
        }, follow_redirects=True)
        assert resp_verify.status_code == 200
        html_reg = resp_verify.get_data(as_text=True)
        assert "student_test@example.com" in html_reg
        assert "Govt Polytechnic Bhopal" in html_reg
        assert "CSE" in html_reg
        assert "8.75" in html_reg

        # 3. Test Admin Dashboard Access
        # Standard logged in student should get 403 Access Denied and should not see the navbar Admin link
        resp_admin_fail1 = client.get('/admin/users')
        assert resp_admin_fail1.status_code == 403, f"Expected 403 on standard user, got {resp_admin_fail1.status_code}"
        
        resp_nav_standard = client.get('/about')
        assert "Admin Panel" not in resp_nav_standard.get_data(as_text=True), "Standard user should not see Admin Panel in navbar"

        # Logout standard user
        client.post('/account', data={'action': 'logout'}, follow_redirects=True)

        # Anonymous user should get 403 Access Denied and should not see navbar Admin link
        resp_admin_fail2 = client.get('/admin/users')
        assert resp_admin_fail2.status_code == 403, f"Expected 403 on anonymous user, got {resp_admin_fail2.status_code}"
        
        resp_nav_anon = client.get('/about')
        assert "Admin Panel" not in resp_nav_anon.get_data(as_text=True), "Anonymous user should not see Admin Panel in navbar"

        # Log in as hardcoded Admin
        login_data = {
            'action': 'login',
            'email': 'krishnaawasthi701@gmail.com',
            'password': 'kkawasthi@202956@kka'
        }
        resp_login = client.post('/account', data=login_data, follow_redirects=True)
        assert resp_login.status_code == 200

        # Admin user should see Admin Panel in navbar
        resp_nav_admin = client.get('/about')
        assert "Admin Panel" in resp_nav_admin.get_data(as_text=True), "Admin user should see Admin Panel in navbar"


        # Now admin page should render successfully (200)
        resp_admin_success = client.get('/admin/users')
        assert resp_admin_success.status_code == 200, f"Expected 200, got {resp_admin_success.status_code}"
        html_admin = resp_admin_success.get_data(as_text=True)
        assert "Student Registration Database" in html_admin
        assert "student_test@example.com" in html_admin
        assert "Govt Polytechnic Bhopal" in html_admin
        assert "9876543210" in html_admin

        # 4. Test Export CSV feature
        resp_csv = client.get('/admin/users?export=1')
        assert resp_csv.status_code == 200
        assert resp_csv.mimetype == 'text/csv'
        csv_data = resp_csv.get_data(as_text=True)
        assert "student_test@example.com" in csv_data
        assert "Govt Polytechnic Bhopal" in csv_data
        assert "9876543210" in csv_data

        print("Account registration and Admin database tests passed successfully!")

def test_seo_routes_and_choice_builder_recs():
    print("=== Testing SEO Routes and Choice Builder Recommendations ===")
    with app.test_client() as client:
        # 1. Test sitemap.xml
        resp_sitemap = client.get('/sitemap.xml')
        print(f"GET /sitemap.xml status code: {resp_sitemap.status_code}")
        assert resp_sitemap.status_code == 200, f"Expected 200, got {resp_sitemap.status_code}"
        assert resp_sitemap.mimetype == 'application/xml', f"Expected application/xml, got {resp_sitemap.mimetype}"
        sitemap_xml = resp_sitemap.get_data(as_text=True)
        assert "<urlset" in sitemap_xml
        assert "/about" in sitemap_xml
        assert "/predictor" in sitemap_xml
        assert "/choice-builder" in sitemap_xml
        assert "/faq/minimum-cgpa-for-lateral-entry-btech-mp" in sitemap_xml
        print("Sitemap test passed!")

        # 1b. Test FAQ index route
        resp_faq = client.get('/faq')
        assert resp_faq.status_code == 200
        faq_html = resp_faq.get_data(as_text=True)
        assert "MP B.Tech Lateral Entry — FAQ" in faq_html
        assert "CGPA &amp; Eligibility" in faq_html or "CGPA & Eligibility" in faq_html
        assert "minimum-cgpa-for-lateral-entry-btech-mp" in faq_html
        print("FAQ index page test passed!")

        # 1c. Test FAQ detail route
        resp_faq_detail = client.get('/faq/minimum-cgpa-for-lateral-entry-btech-mp')
        assert resp_faq_detail.status_code == 200
        faq_detail_html = resp_faq_detail.get_data(as_text=True)
        assert "What is the minimum CGPA required for B.Tech lateral entry admission in MP?" in faq_detail_html
        assert "FAQPage" in faq_detail_html
        assert "BreadcrumbList" in faq_detail_html
        print("FAQ detail page test passed!")

        # 2. Test robots.txt
        resp_robots = client.get('/robots.txt')
        print(f"GET /robots.txt status code: {resp_robots.status_code}")
        assert resp_robots.status_code == 200, f"Expected 200, got {resp_robots.status_code}"
        assert resp_robots.mimetype == 'text/plain', f"Expected text/plain, got {resp_robots.mimetype}"
        robots_txt = resp_robots.get_data(as_text=True)
        assert "User-agent: *" in robots_txt
        assert "Disallow: /admin/" in robots_txt
        assert "Sitemap:" in robots_txt
        print("Robots.txt test passed!")

        # 3. Test Choice Builder priority sort
        cb_data = {
            'cgpa': '8.5',
            'category': 'UR',
            'gender': 'M',
            'college_type': 'Any',
            'branch': ['CSE', 'IT'],
            'domicile': 'Y',
            'city': 'All'
        }
        resp_cb = client.post('/choice-builder', data=cb_data)
        print(f"POST /choice-builder status code: {resp_cb.status_code}")
        assert resp_cb.status_code == 200
        cb_html = resp_cb.get_data(as_text=True)
        # Should have the new priority separators and recommended badges
        assert "── OTHER SUGGESTED COLLEGES ──" in cb_html or "── GENERAL COLLEGES ──" in cb_html
        assert "Rec #" in cb_html
        print("Choice Builder priority sort and badges test passed!")


def test_otp_brute_force_limits():
    print("=== Testing OTP Brute-Force Limits (Max 3 attempts) ===")
    
    with app.app_context():
        from models import User, CloudShortlist
        from db import db
        u = User.query.filter_by(email='otp_limit_test@example.com').first()
        if u:
            CloudShortlist.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
            db.session.commit()

    with app.test_client() as client:
        # 1. Register a test user to trigger OTP generation
        reg_data = {
            'action': 'register',
            'display_name': 'Limit Student',
            'email': 'otp_limit_test@example.com',
            'password': 'SecurePass123!',
            'mobile_number': '9876543210',
            'polytechnic_college': 'Govt Polytechnic Bhopal',
            'diploma_branch': 'CSE',
            'cgpa': '8.75',
            'category': 'OBC',
            'gender': 'M'
        }
        resp_reg = client.post('/account', data=reg_data, follow_redirects=True)
        assert "Verification OTP has been sent" in resp_reg.get_data(as_text=True)

        # Ensure OTP is in session
        with client.session_transaction() as sess:
            correct_otp = sess.get("registration_otp")
            assert correct_otp is not None

        # 2. Try entering wrong OTP 1st time
        resp_w1 = client.post('/account', data={'action': 'verify_otp', 'otp': '000000'}, follow_redirects=True)
        assert "Incorrect OTP" in resp_w1.get_data(as_text=True)
        assert "2 attempts remaining" in resp_w1.get_data(as_text=True)

        # Try entering wrong OTP 2nd time
        resp_w2 = client.post('/account', data={'action': 'verify_otp', 'otp': '000000'}, follow_redirects=True)
        assert "Incorrect OTP" in resp_w2.get_data(as_text=True)
        assert "1 attempts remaining" in resp_w2.get_data(as_text=True)

        # Try entering wrong OTP 3rd time (should fail and delete session details)
        resp_w3 = client.post('/account', data={'action': 'verify_otp', 'otp': '000000'}, follow_redirects=True)
        assert "Too many failed attempts. Please register again." in resp_w3.get_data(as_text=True)

        # Verify session is cleaned up
        with client.session_transaction() as sess:
            assert sess.get("registration_otp") is None
            assert sess.get("pending_registration") is None

        # 3. Test Reset OTP limits
        # First, we need a registered user to test forgot password OTP flow
        with app.app_context():
            from werkzeug.security import generate_password_hash
            from models import User
            # Seed user
            db.session.add(User(
                email='otp_limit_test@example.com',
                password_hash=generate_password_hash('SecurePass123!'),
                display_name='Limit Student',
                mobile_number='9876543210',
                polytechnic_college='Govt Polytechnic Bhopal',
                diploma_branch='CSE',
                cgpa=8.75,
                category='OBC',
                gender='M'
            ))
            db.session.commit()

        # Trigger password reset OTP
        resp_forgot = client.post('/account', data={
            'action': 'forgot_password',
            'email': 'otp_limit_test@example.com'
        }, follow_redirects=True)
        assert "password reset code has been sent" in resp_forgot.get_data(as_text=True)

        # Ensure reset OTP is in session
        with client.session_transaction() as sess:
            reset_otp = sess.get("reset_otp")
            assert reset_otp is not None

        # Try entering wrong reset OTP 1st time
        resp_rw1 = client.post('/account', data={'action': 'verify_reset_otp', 'otp': '000000', 'new_password': 'NewSecurePass123!'}, follow_redirects=True)
        assert "Incorrect OTP" in resp_rw1.get_data(as_text=True)
        assert "2 attempts remaining" in resp_rw1.get_data(as_text=True)

        # Try entering wrong reset OTP 2nd time
        resp_rw2 = client.post('/account', data={'action': 'verify_reset_otp', 'otp': '000000', 'new_password': 'NewSecurePass123!'}, follow_redirects=True)
        assert "Incorrect OTP" in resp_rw2.get_data(as_text=True)
        assert "1 attempts remaining" in resp_rw2.get_data(as_text=True)

        # Try entering wrong reset OTP 3rd time
        resp_rw3 = client.post('/account', data={'action': 'verify_reset_otp', 'otp': '000000', 'new_password': 'NewSecurePass123!'}, follow_redirects=True)
        assert "Too many failed attempts. Please try again." in resp_rw3.get_data(as_text=True)

        # Ensure reset session fields are cleared
        with client.session_transaction() as sess:
            assert sess.get("reset_otp") is None
            assert sess.get("reset_email") is None

        # Cleanup test user
        with app.app_context():
            User.query.filter_by(email='otp_limit_test@example.com').delete()
            db.session.commit()

    print("OTP brute-force limit tests passed successfully!")


if __name__ == "__main__":
    test_predictor_template()
    test_mobile_navbar()
    test_compare_template()
    test_account_registration_and_admin()
    test_seo_routes_and_choice_builder_recs()
    test_otp_brute_force_limits()
