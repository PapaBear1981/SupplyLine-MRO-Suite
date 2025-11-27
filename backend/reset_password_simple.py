#!/usr/bin/env python3
"""
Simple script to reset ADMIN001 password
"""
import sys
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(employee_number="ADMIN001").first()
    
    if not admin:
        print("ERROR: Admin user ADMIN001 not found!")
        sys.exit(1)
    
    # Set password to admin123
    admin.set_password("admin123")
    db.session.commit()
    
    print("SUCCESS: Admin password reset to admin123")
    print(f"Employee Number: {admin.employee_number}")
    print(f"Name: {admin.name}")
    
    # Verify
    if admin.check_password("admin123"):
        print("VERIFIED: Password check passed!")
    else:
        print("ERROR: Password check failed!")
        sys.exit(1)
