#!/usr/bin/env python3
"""
Script to check and reset admin credentials
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from utils.admin_init import reset_admin_password

def check_admin():
    """Check if admin exists and show info"""
    with app.app_context():
        admin = User.query.filter_by(employee_number='ADMIN001').first()
        
        if not admin:
            print("❌ Admin user ADMIN001 not found!")
            return False
        
        print("✅ Admin user found:")
        print(f"   Employee Number: {admin.employee_number}")
        print(f"   Name: {admin.name}")
        print(f"   Department: {admin.department}")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
        
        # Test common passwords
        test_passwords = ['password123', 'admin123', 'Admin123!', 'Password123!']
        print("\n🔍 Testing common passwords:")
        for pwd in test_passwords:
            if admin.check_password(pwd):
                print(f"   ✅ Password is: {pwd}")
                return True
            else:
                print(f"   ❌ Not: {pwd}")
        
        print("\n⚠️  Password is not a common default.")
        return False

def reset_admin():
    """Reset admin password"""
    with app.app_context():
        success, message, new_password = reset_admin_password()
        
        if success and new_password:
            print(f"\n✅ {message}")
            print(f"\n🔑 NEW ADMIN PASSWORD: {new_password}")
            print("\n⚠️  IMPORTANT: Save this password securely!")
            print("   You can also set INITIAL_ADMIN_PASSWORD environment variable")
            return True
        else:
            print(f"\n❌ {message}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Admin Credential Checker")
    print("=" * 60)
    
    found = check_admin()
    
    if not found:
        print("\n" + "=" * 60)
        print("Would you like to reset the admin password? (y/n): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            reset_admin()
        else:
            print("\nTo reset manually, run:")
            print("  python backend/check_admin.py")
    
    print("\n" + "=" * 60)

