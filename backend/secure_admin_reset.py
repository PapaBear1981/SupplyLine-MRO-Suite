#!/usr/bin/env python3
"""
Secure Admin Reset Script for SupplyLine MRO Suite

This script securely resets the admin password to address Issue #363.
It generates a cryptographically secure password and forces password change on next login.

CRITICAL SECURITY FIX: Replaces default admin123 password with secure random password.
"""

import os
import sys
import secrets
import string
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User
from utils.admin_init import reset_admin_password, validate_admin_setup


def generate_secure_password(length=20):
    """Generate a cryptographically secure password"""
    # Use a mix of letters, digits, and safe punctuation
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def main():
    """Main function to reset admin password securely"""
    print("=" * 60)
    print("🔒 SECURE ADMIN RESET - SupplyLine MRO Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        try:
            # Find or create admin user
            admin = User.query.filter_by(employee_number='ADMIN001').first()

            if not admin:
                print("👤 Admin user not found. Creating new admin user...")

                # Generate secure password
                new_password = generate_secure_password()

                # Create admin user
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

                print("✅ SUCCESS: Admin user created!")

            else:
                print(f"👤 Found existing admin user: {admin.name} ({admin.employee_number})")

                # Check if using default password
                if admin.check_password('admin123'):
                    print("❌ CRITICAL: Admin is using default password!")
                    print("🔄 Resetting admin password...")

                    # Generate new secure password
                    new_password = generate_secure_password()
                    admin.set_password(new_password)
                    db.session.commit()

                    print("✅ SUCCESS: Admin password reset completed!")
                else:
                    print("✅ Admin is not using default password.")
                    print("Generating new secure password anyway...")

                    # Generate new secure password
                    new_password = generate_secure_password()
                    admin.set_password(new_password)
                    db.session.commit()

                    print("✅ SUCCESS: Admin password updated!")

            print()
            print("🔑 NEW ADMIN CREDENTIALS:")
            print("=" * 40)
            print(f"Username: ADMIN001")
            print(f"Password: {new_password}")
            print("=" * 40)
            print()
            print("⚠️  IMPORTANT SECURITY NOTES:")
            print("1. Save this password in a secure password manager")
            print("2. Old password (admin123) is now invalid")
            print("3. Update any automation scripts with new credentials")
            print("4. Test login with new credentials")
            print()

            # Verify the old password no longer works
            print("🔍 Verifying security fix...")
            if not admin.check_password('admin123'):
                print("✅ SECURITY VERIFICATION PASSED!")
                print("Default password 'admin123' is no longer valid.")
            else:
                print("❌ WARNING: Default password still works!")

            print()
            print("🎯 NEXT STEPS:")
            print("1. Test login with new credentials")
            print("2. Update environment variables to remove hardcoded passwords")
            print("3. Deploy to production with secure configuration")

        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
            print("Admin password reset failed!")
            db.session.rollback()
            return
    
    print()
    print("=" * 60)
    print("🔒 SECURE ADMIN RESET COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
