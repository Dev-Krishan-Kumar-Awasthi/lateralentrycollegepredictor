import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db import db
from models import SeatInfo
from predictor import fetch_colleges_from_rank
from smart_choices import build_smart_choices

with app.app_context():
    print("Testing fetch_colleges_from_rank for female candidate in 2025...")
    # Acropolis CSE branch has both UR/X/M and UR/X/F in 2025.
    # Let's query colleges using female candidate:
    colleges = fetch_colleges_from_rank(
        rank_min=100, rank_max=2000,
        branch="CSE", category="UR", gender="F",
        college_type="Private", year=2025, domicile="Y"
    )
    
    acropolis_cse_seats = [c for c in colleges if "Acropolis" in c.college_name]
    print(f"Total Acropolis CSE seats found for Female in 2025: {len(acropolis_cse_seats)}")
    for seat in acropolis_cse_seats:
        print(f" - {seat.college_name} | {seat.branch} | Gender: {seat.gender} | Closing Rank: {seat.closing_rank}")
        
    genders_found = {s.gender for s in acropolis_cse_seats}
    assert "M" in genders_found, "BUG: Female candidate was not shown 'M' (open) seats in 2025!"
    assert "F" in genders_found, "Female candidate was not shown 'F' (female-reserved) seats!"
    print("fetch_colleges_from_rank gender test passed!")

    print("\nTesting build_smart_choices deduplication for female candidate...")
    # Since raw.sort(reverse=True) is used, we should see the seat with the highest closing rank kept.
    # For Acropolis CSE in 2025, UR/X/M has closing 1592, and UR/X/F has closing 1210.
    choices = build_smart_choices(
        cgpa=8.5, branch="CSE", category="UR", gender="F",
        college_type="Private", domicile="Y", city="All", year=2025
    )
    
    acropolis_cse_options = [c for c in choices["safe"] + choices["target"] + choices["dream"] if "Acropolis" in c["college_name"]]
    print(f"Smart choice option kept: {acropolis_cse_options}")
    if acropolis_cse_options:
        opt = acropolis_cse_options[0]
        print(f"Chosen seat closing rank: {opt['closing_rank']} (expected 1592 or higher/easier cutoff)")
        assert opt['closing_rank'] == 1592, f"BUG: Kept incorrect seat with cutoff {opt['closing_rank']} instead of 1592!"
        print("Smart choices deduplication test passed!")
