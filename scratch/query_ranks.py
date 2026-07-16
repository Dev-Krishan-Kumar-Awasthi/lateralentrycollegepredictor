import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db import db
from models import SeatInfo

choices = [
    {"college_name": "Shri G.S. Institute of Technology & Science Indore (M.P.) (1952)", "branch": "CIVIL"},
    {"college_name": "JABALPUR ENGINEERING COLLEGE JABALPUR (JEC) (1947)", "branch": "CSE"},
    {"college_name": "Shri G.S. Institute of Technology & Science Indore (M.P.) (1952)", "branch": "IT"},
    {"college_name": "UJJAIN ENGINEERING COLLEGE (FORMERLY GOVT. ENGG. COLLEGE ESTB. IN 1966)", "branch": "ELECT"}
]

# Let's search the database for these choices for year=2025, category=UR, gender=M (or allowed_genders)
with app.app_context():
    for index, choice in enumerate(choices):
        col_name = choice["college_name"]
        branch = choice["branch"]
        print(f"\nQuerying: {col_name} | {branch}")
        
        # Let's try to query the database using the same query as in main.py
        # We will check if it matches
        seats = SeatInfo.query.filter(
            SeatInfo.college_name == col_name,
            SeatInfo.branch.like(f"%{branch}%"),
            SeatInfo.year == 2025,
            SeatInfo.category == "UR"
        ).all()
        
        print(f"Seats found: {len(seats)}")
        for seat in seats:
            print(f" - Gender: {seat.gender} | Closing Rank: {seat.closing_rank} | College: {seat.college_name} | Branch: {seat.branch}")
