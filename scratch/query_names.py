import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db import db
from models import SeatInfo

with app.app_context():
    # Query distinct college names containing SGSITS or Gov
    names = db.session.query(SeatInfo.college_name).distinct().all()
    print("SGSITS names in database:")
    for n in names:
        if "Shri" in n[0] or "SGS" in n[0] or "JEC" in n[0] or "Jabalpur" in n[0]:
            print(f" - {n[0]}")
