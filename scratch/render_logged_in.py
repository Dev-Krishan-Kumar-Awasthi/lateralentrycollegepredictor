import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import User

form_data = {
    'cgpa': '9.0',
    'category': 'UR',
    'gender': 'M',
    'college_type': 'GOVT',
    'branch': ['CSE', 'IT'],
    'domicile': 'Y',
    'city': 'All',
    'district': 'All',
    'home_city': 'Bhopal',
    'max_distance_km': ''
}

with app.app_context():
    u = User.query.first()
    user_id = u.id if u else None
    email = u.email if u else None

with app.test_client() as client:
    if user_id:
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            print(f"Logging in as: {email}")
    else:
        print("No users found in database!")
            
    response = client.post('/predictor', data=form_data)
    print("Status code:", response.status_code)
    html = response.get_data(as_text=True)
    
    import re
    matches = re.findall(r'<button class="cmp-add-btn route-planner-btn".*?>', html)
    print("Found Route buttons count:", len(matches))
    for m in matches[:5]:
        print(m)
