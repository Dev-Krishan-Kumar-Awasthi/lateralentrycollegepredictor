import sys
sys.path.append('.')
from main import app, db
from models import User, ChoiceVault
import os

with app.app_context():
    # 1. Print all users
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    for u in users:
        print(f" - User #{u.id}: {u.display_name} ({u.email}), notify_counselling={u.notify_counselling}")
        
    client = app.test_client()
    
    # 2. Authenticate by putting an admin user ID in session
    # Let's find or create the admin user to ensure session access passes.
    admin_email = os.getenv("ADMIN_EMAIL", "krishnaawasthi701@gmail.com").strip().lower()
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        # Create user
        admin_user = User(
            email=admin_email,
            password_hash="dummy",
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
        print(f"Created admin user: {admin_email}")

    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['user_email'] = admin_user.email
        sess['user_name'] = admin_user.display_name

    # 3. Test sending broadcast to ALL subscribed students
    print("\n--- Testing broadcast to ALL subscribed students ---")
    response = client.post('/admin/broadcast', data={
        'recipient_type': 'all',
        'subject': 'Alert to all!',
        'body': 'This is a test message to all subscribed students.'
    })
    print("Response status code:", response.status_code)
    # Check if broadcast_success is in the rendered html response.data
    html = response.data.decode('utf-8')
    if "Email sent successfully to" in html:
        print("Success: Broadcast sent successfully message detected in HTML!")
    else:
        print("Failure: Broadcast success message not found in HTML!")
        
    # Check if Choice Vault items are rendered (meaning ChoiceVault wasn't lost)
    if "Choice Vault Management" in html:
        print("Success: Choice Vault management tab is present in response HTML!")
    else:
        print("Warning: Choice Vault tab not found in response HTML!")

    # 4. Test sending message to a SPECIFIC student
    print("\n--- Testing message to a SPECIFIC student ---")
    # Let's find a non-admin student or any user to target
    target_student = User.query.filter(User.email != admin_email).first()
    if not target_student:
        # Create a dummy student
        target_student = User(
            email="test_student@example.com",
            password_hash="dummy",
            display_name="Test Student",
            mobile_number="8888888888",
            polytechnic_college="Test College",
            diploma_branch="CS",
            cgpa=8.5,
            category="UR",
            gender="M",
            notify_counselling=0 # Disable alerts so we verify direct works even if notification is disabled
        )
        db.session.add(target_student)
        db.session.commit()
        print(f"Created target student: {target_student.email}")

    response_single = client.post('/admin/broadcast', data={
        'recipient_type': 'single',
        'specific_user_id': str(target_student.id),
        'subject': 'Alert to you specifically!',
        'body': 'This is a direct message to you.'
    })
    print("Response status code:", response_single.status_code)
    html_single = response_single.data.decode('utf-8')
    expected_msg = f"Email sent successfully to {target_student.display_name or target_student.email}"
    if expected_msg in html_single:
        print(f"Success: Specific user success message '{expected_msg}' detected in HTML!")
    else:
        # Check if the email fallback or general success is there
        if "Email sent successfully to" in html_single:
            print("Success: Specific user email sent successfully message detected in HTML!")
        else:
            print("Failure: Specific user success message not found in HTML!")
            
    # Check if Choice Vault slips are still rendered
    if "Choice Vault Management" in html_single:
        print("Success: Choice Vault management tab is present in single broadcast response HTML!")
    else:
        print("Warning: Choice Vault tab not found in single broadcast response HTML!")

    print("\nDone testing broadcast and single messaging!")
