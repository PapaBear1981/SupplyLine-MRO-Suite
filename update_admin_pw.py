import sys
sys.path.insert(0, 'backend')

from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(employee_number='ADMIN001').first()
    if admin:
        admin.set_password('Caden1234!')
        db.session.commit()
        print("Password updated to: Caden1234!")
        print("Login with ADMIN001 / Caden1234!")
    else:
        print("Admin not found!")

