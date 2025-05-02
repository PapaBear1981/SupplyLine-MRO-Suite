from models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'development-key'

# Initialize the database
db.init_app(app)

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Check if admin user exists
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    if admin:
        print("Admin user already exists. Updating password...")
        admin.set_password('admin123')
    else:
        print("Creating new admin user...")
        admin = User(
            name='Admin',
            employee_number='ADMIN001',
            department='IT',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    db.session.commit()
    print("Admin user created/updated successfully!")
    print("Employee Number: ADMIN001")
    print("Password: admin123")
