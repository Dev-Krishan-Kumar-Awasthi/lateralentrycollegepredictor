import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
from main import app

with app.test_request_context('/api/v1/college/route-info?college_name=Shri+G.S.+Institute+of+Technology+%26+Science+Indore+(M.P.)+(1952)&home_city=Bhopal&category=UR'):
    try:
        view_func = app.view_functions['api_college_route_info']
        res = view_func()
        print("Success:", res)
    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()
