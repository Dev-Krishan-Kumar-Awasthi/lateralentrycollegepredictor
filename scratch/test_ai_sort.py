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
        {"college_name": "Lakshmi Narain College of Technology Indore (M.P.) (2004)", "branch": "CSE"}, # Missing/Fallback (prob = 50%)
        {"college_name": "Shri G.S. Institute of Technology & Science Indore (M.P.) (1952)", "branch": "CSE"}, # Dream (prob = 12%, closing = 58)
        {"college_name": "JABALPUR ENGINEERING COLLEGE JABALPUR (JEC) (1947)", "branch": "CSE"}, # Safe (prob = 92%, closing = 225)
        {"college_name": "Missing College Engineering", "branch": "CSE"}, # Missing/Fallback (prob = 50%)
        {"college_name": "Shri G.S. Institute of Technology & Science Indore (M.P.) (1952)", "branch": "IT"} # Safe (prob = 92%, closing = 271)
    ]
}

with app.app_context():
    with app.test_request_context('/api/v1/choices/optimize', method='POST', json=sample_payload):
        view_func = app.view_functions['api_optimize_choices']
        res = view_func()
        data = json.loads(res.get_data(as_text=True))
        
        print("\nOptimized Choice Order:")
        for idx, item in enumerate(data['choices']):
            print(f" #{idx+1} | {item['college_name']} | {item['branch']} | Prob: {item['probability']}% | Closing Rank: {item['closing_rank']} | Bucket: {item['bucket']}")
            
        choices_returned = data['choices']
        
        # We expect the order of probabilities to be ascending: 12% -> 50% -> 92%
        sgsits_cse_idx = [i for i, c in enumerate(choices_returned) if "G.S." in c['college_name'] and c['branch'] == "CSE"][0]
        sgsits_it_idx = [i for i, c in enumerate(choices_returned) if "G.S." in c['college_name'] and c['branch'] == "IT"][0]
        jec_cse_idx = [i for i, c in enumerate(choices_returned) if "JABALPUR" in c['college_name']][0]
        missing_idx = [i for i, c in enumerate(choices_returned) if "Missing" in c['college_name']][0]
        
        # 1. Dream (12%) should come before Target/Missing (50%)
        assert sgsits_cse_idx < missing_idx, "SGSITS CSE (12%) should come before Missing College (50%)!"
        
        # 2. Target/Missing (50%) should come before Safe (92%)
        assert missing_idx < jec_cse_idx, "Missing College (50%) should come before JEC CSE (92%)!"
        assert missing_idx < sgsits_it_idx, "Missing College (50%) should come before SGSITS IT (92%)!"
        
        # 3. For equal probability (92%), sorted by closing_rank ascending: JEC CSE (225) < SGSITS IT (271)
        assert jec_cse_idx < sgsits_it_idx, "For equal 92% probability, JEC CSE (225) should be prioritized above SGSITS IT (271)!"
        
        print("\nAll assertions passed successfully! The sorting order is completely correct and optimized for choice filling.")
