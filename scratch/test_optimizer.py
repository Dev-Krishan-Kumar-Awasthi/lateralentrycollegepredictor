import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from main import app

sample_payload = {
    "cgpa": "8.5",
    "category": "UR",
    "gender": "M",
    "domicile": "Y",
    "year": "2025",
    "choices": [
        {"college_name": "Shri G.S. Institute of Technology & Science Indore (M.P.) (1952)", "branch": "CSE"},
        {"college_name": "Jabalpur Engineering College Jabalpur (M.P.) (1947)", "branch": "MECH"},
        {"college_name": "Acropolis Institute of Technology & Research Indore (M.P.) (1961)", "branch": "IT"}
    ]
}

with app.test_request_context('/api/v1/choices/optimize', method='POST', json=sample_payload):
    try:
        view_func = app.view_functions['api_optimize_choices']
        res = view_func()
        print("Success!")
        print("Response status:", res.status_code)
        print("Response body:", res.get_data(as_text=True))
    except Exception as e:
        import traceback
        print("Exception occurred:")
        traceback.print_exc()
