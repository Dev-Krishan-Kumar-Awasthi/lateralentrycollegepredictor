import sys
sys.path.append('.')
from main import app, db
from models import SeatInfo

with app.app_context():
    categories = db.session.query(SeatInfo.category).distinct().all()
    genders = db.session.query(SeatInfo.gender).distinct().all()
    print(f"Categories: {[c[0] for c in categories]}")
    print(f"Genders: {[g[0] for g in genders]}")
