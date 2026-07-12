import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

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

with app.test_client() as client:
    response = client.post('/predictor', data=form_data)
    print("Status code:", response.status_code)
    html = response.get_data(as_text=True)
    
    # Check if login required redirect happened
    if "Login Required" in html or "/account" in html:
        print("REDIRECTED TO LOGIN OR SHOWING LOGIN REQUIRED")
    
    import re
    matches = re.findall(r'<button class="cmp-add-btn route-planner-btn".*?>', html)
    print("Found Route buttons count:", len(matches))
    for m in matches[:5]:
        print(m)
