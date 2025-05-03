from models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(employee_number='ADMIN001').first()
    
    if not admin:
        print("Admin user not found!")
    else:
        print(f"Found admin user: {admin.name} ({admin.employee_number})")
        
        # Check password
        if admin.check_password('admin123'):
            print("Password 'admin123' is correct!")
        else:
            print("Password 'admin123' is NOT correct!")
            
        # Reset password to ensure it's correct
        admin.set_password('admin123')
        db.session.commit()
        print("Admin password has been reset to 'admin123'")
