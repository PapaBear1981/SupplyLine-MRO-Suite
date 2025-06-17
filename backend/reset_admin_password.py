#!/usr/bin/env python3
"""
Admin Password Reset Utility for SupplyLine MRO Suite
This script creates or resets the admin user password for testing purposes.

SECURITY NOTE: This script requires the ADMIN_INIT_PASSWORD environment variable
to be set for security reasons. Do not hard-code passwords in scripts.

Usage:
    export ADMIN_INIT_PASSWORD="your-secure-password"
    python reset_admin_password.py
"""

from models import db, User
from flask import Flask
import os
import secrets

# Create a minimal Flask app
app = Flask(__name__)

# Use the same database path as the main application
db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Use secure SECRET_KEY from environment or generate one for this script
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

print(f"Using database: {db_path}")

# Initialize the database
db.init_app(app)

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Get admin user
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    if not admin:
        print("Admin user not found! Creating new admin user...")

        # Get password from environment variable for security
        admin_password = os.environ.get('ADMIN_INIT_PASSWORD')
        if not admin_password:
            raise RuntimeError("ADMIN_INIT_PASSWORD environment variable must be set for this script.")

        # Create admin user
        admin = User(
            name='System Administrator',
            employee_number='ADMIN001',
            department='IT',
            is_admin=True,
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()

        print("✓ Admin user created; password set from environment variable")
    else:
        print(f"Found admin user: {admin.name} ({admin.employee_number})")

        # Get password from environment variable for security
        admin_password = os.environ.get('ADMIN_INIT_PASSWORD')
        if not admin_password:
            raise RuntimeError("ADMIN_INIT_PASSWORD environment variable must be set for this script.")

        # Reset password
        admin.set_password(admin_password)
        db.session.commit()

        print("✓ Admin password reset; password set from environment variable")

    # Verify the password works
    if admin.check_password(admin_password):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")
