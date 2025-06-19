#!/usr/bin/env python3
"""
Quick admin password reset for testing
"""

import sys
import os
sys.path.append('backend')

from models import db, User
from flask import Flask
import secrets

# Create a minimal Flask app
app = Flask(__name__)

# Use the same database path as the main application
db_path = os.path.abspath(os.path.join('database', 'tools.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(32)

print(f"Using database: {db_path}")

# Initialize the database
db.init_app(app)

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(employee_number='ADMIN001').first()
    
    if admin:
        print(f"Found admin user: {admin.name} ({admin.employee_number})")
        
        # Reset password to test credentials
        admin.set_password('admin123')
        db.session.commit()
        
        print("✓ Admin password reset to 'admin123'")
        
        # Verify the password works
        if admin.check_password('admin123'):
            print("✓ Password verification successful")
        else:
            print("✗ Password verification failed")
    else:
        print("❌ Admin user not found!")
