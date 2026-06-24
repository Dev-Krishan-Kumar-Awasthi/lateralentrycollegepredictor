import sys
sys.path.append('.')
from main import app
from models import User

with app.app_context():
    print("Total registered users:", User.query.count())
