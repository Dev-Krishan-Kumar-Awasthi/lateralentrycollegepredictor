import sys
sys.path.append('.')
from main import app, db
from models import SeatInfo

with app.app_context():
    tfw_rows = db.session.query(SeatInfo).filter(SeatInfo.branch.like('%TFW%')).limit(5).all()
    print(f"TFW rows count: {len(tfw_rows)}")
    for r in tfw_rows:
        print(f"{r.college_name} | {r.branch} | {r.category} | {r.gender}")
