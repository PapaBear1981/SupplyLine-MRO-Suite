#!/usr/bin/env python3
"""
Simple script to create a secure admin user
"""

import os
import sys
import secrets
import string

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User


def generate_secure_password(length=20):
    """Generate a cryptographically secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def main():
    """Create secure admin user"""
    print("🔒 Creating Secure Admin User")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if admin already exists
            admin = User.query.filter_by(employee_number='ADMIN001').first()
            
            if admin:
                print(f"👤 Found existing admin: {admin.name}")
                
                # Check if using default password
                if admin.check_password('admin123'):
                    print("❌ CRITICAL: Using default password!")
                    new_password = generate_secure_password()
                    admin.set_password(new_password)
                    db.session.commit()
                    print("✅ Password updated!")
                else:
                    print("✅ Not using default password")
                    new_password = generate_secure_password()
                    admin.set_password(new_password)
                    db.session.commit()
                    print("✅ Password refreshed!")
            else:
                print("👤 Creating new admin user...")
                new_password = generate_secure_password()
                
                admin = User(
                    name='System Administrator',
                    employee_number='ADMIN001',
                    department='IT',
                    is_admin=True,
                    is_active=True
                )
                admin.set_password(new_password)
                
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created!")
            
            print()
            print("🔑 ADMIN CREDENTIALS:")
            print("=" * 30)
            print(f"Username: ADMIN001")
            print(f"Password: {new_password}")
            print("=" * 30)
            print()
            print("⚠️  Save this password securely!")
            
            # Verify old password doesn't work
            if not admin.check_password('admin123'):
                print("✅ Default password 'admin123' is disabled")
            else:
                print("❌ WARNING: Default password still works!")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    main()
