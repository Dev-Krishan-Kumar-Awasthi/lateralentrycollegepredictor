import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import SeatInfo

with app.app_context():
    colleges = sorted(list({s.college_name for s in SeatInfo.query.all()}))
    with open("scratch/all_colleges.txt", "w", encoding="utf-8") as f:
        for c in colleges:
            f.write(c + "\n")
    print(f"Extracted {len(colleges)} unique colleges to scratch/all_colleges.txt")
