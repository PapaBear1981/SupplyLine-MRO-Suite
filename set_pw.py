import sys
import os
sys.path.insert(0, 'backend')
os.chdir('backend')

from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(employee_number='ADMIN001').first()
    if admin:
        admin.set_password('Caden1234!')
        db.session.commit()
        print("SUCCESS: Password updated!")
        print("Login with:")
        print("  Employee Number: ADMIN001")
        print("  Password: Caden1234!")
    else:
        print("ERROR: Admin not found!")

