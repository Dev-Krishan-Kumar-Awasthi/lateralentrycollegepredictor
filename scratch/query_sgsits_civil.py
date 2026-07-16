import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db import db
from models import SeatInfo

with app.app_context():
    seats = SeatInfo.query.filter(
        SeatInfo.college_name.like("%G.S.%"),
        SeatInfo.year == 2025,
        SeatInfo.category == "UR"
    ).all()
    print("SGSITS UR seats in 2025:")
    for s in seats:
        print(f" - {s.branch} | Gender: {s.gender} | Cutoff: {s.closing_rank} | Seats: {s.total_seats}")
