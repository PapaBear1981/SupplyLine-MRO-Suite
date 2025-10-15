#!/usr/bin/env python3
"""
Script to set admin password to a specific value
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def set_admin_password(new_password):
    """Set admin password to a specific value"""
    with app.app_context():
        admin = User.query.filter_by(employee_number='ADMIN001').first()
        
        if not admin:
            print("❌ Admin user ADMIN001 not found!")
            return False
        
        # Set the new password
        admin.set_password(new_password)
        db.session.commit()
        
        print("✅ Admin password updated successfully!")
        print(f"   Employee Number: ADMIN001")
        print(f"   New Password: {new_password}")
        
        # Verify it works
        if admin.check_password(new_password):
            print("\n✅ Password verified - login should work now!")
            return True
        else:
            print("\n❌ Password verification failed!")
            return False

if __name__ == '__main__':
    # Set password to Caden1234!
    new_password = "Caden1234!"
    
    print("=" * 60)
    print("Setting Admin Password")
    print("=" * 60)
    
    success = set_admin_password(new_password)
    
    if success:
        print("\n" + "=" * 60)
        print("You can now login with:")
        print("  Employee Number: ADMIN001")
        print("  Password: Caden1234!")
        print("=" * 60)
    
    sys.exit(0 if success else 1)

