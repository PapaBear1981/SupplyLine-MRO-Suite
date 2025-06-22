#!/usr/bin/env python3
"""
Update admin password to a specific value
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User


def main():
    """Update admin password to Freedom2025!"""
    print("🔒 Updating Admin Password")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Find admin user
            admin = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin:
                print("❌ ERROR: Admin user ADMIN001 not found!")
                return
            
            print(f"👤 Found admin user: {admin.name}")
            
            # Update password to Freedom2025!
            new_password = "Freedom2025!"
            admin.set_password(new_password)
            db.session.commit()
            
            print("✅ SUCCESS: Admin password updated!")
            print()
            print("🔑 ADMIN CREDENTIALS:")
            print("=" * 30)
            print(f"Username: ADMIN001")
            print(f"Password: {new_password}")
            print("=" * 30)
            print()
            
            # Verify the new password works
            if admin.check_password(new_password):
                print("✅ Password verification successful!")
            else:
                print("❌ WARNING: Password verification failed!")
            
            # Verify old passwords don't work
            old_passwords = ['admin123', 'mdlQXC*fq_5HRs=;QeT>']
            for old_pwd in old_passwords:
                if not admin.check_password(old_pwd):
                    print(f"✅ Old password '{old_pwd}' is disabled")
                else:
                    print(f"❌ WARNING: Old password '{old_pwd}' still works!")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    main()
