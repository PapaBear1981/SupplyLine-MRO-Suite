from models import db, User
from flask import Flask
import os
import sys

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
        print("Admin user already exists.")
        print("WARNING: This script should not be used in production.")
        print("Use environment variables or secure admin initialization instead.")
    else:
        print("Creating new admin user...")
        from utils.admin_init import create_secure_admin
        success, message, password = create_secure_admin()
        if success:
            print(f"SUCCESS: {message}")
            if password:
                print(f"IMPORTANT: Generated admin password: {password}")
                print("Please save this password securely!")
        else:
            print(f"ERROR: {message}")
            sys.exit(1)

    print("Admin user setup completed!")
    print("Employee Number: ADMIN001")
