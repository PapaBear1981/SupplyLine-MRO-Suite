#!/usr/bin/env python3
"""
Debug script to isolate the User serialization issue
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, User
from flask import Flask
from config import Config

def debug_user_serialization():
    """Debug the User.to_dict() method to find the datetime parsing issue"""
    
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize the database
    db.init_app(app)
    
    with app.app_context():
        print("Debugging User serialization...")
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        for i, user in enumerate(users):
            print(f"\n--- Testing User {i+1}: {user.employee_number} ---")
            
            try:
                # Test basic to_dict
                print("Testing basic to_dict()...")
                basic_dict = user.to_dict()
                print(f"✓ Basic to_dict() successful")
                print(f"  created_at: {basic_dict.get('created_at')}")
                
            except Exception as e:
                print(f"✗ Basic to_dict() failed: {str(e)}")
                print(f"  Error type: {type(e).__name__}")
                continue
            
            try:
                # Test with lockout info
                print("Testing to_dict(include_lockout_info=True)...")
                lockout_dict = user.to_dict(include_lockout_info=True)
                print(f"✓ Lockout to_dict() successful")
                print(f"  account_locked_until: {lockout_dict.get('account_locked_until')}")
                print(f"  last_failed_login: {lockout_dict.get('last_failed_login')}")
                
            except Exception as e:
                print(f"✗ Lockout to_dict() failed: {str(e)}")
                print(f"  Error type: {type(e).__name__}")
                
                # Print user attributes for debugging
                print(f"  User attributes:")
                print(f"    created_at: {user.created_at} (type: {type(user.created_at)})")
                print(f"    account_locked_until: {user.account_locked_until} (type: {type(user.account_locked_until)})")
                print(f"    last_failed_login: {user.last_failed_login} (type: {type(user.last_failed_login)})")
                
                # Try to isolate which field is causing the issue
                print("  Testing individual datetime fields...")
                
                try:
                    if user.created_at:
                        iso_created = user.created_at.isoformat()
                        print(f"    ✓ created_at.isoformat(): {iso_created}")
                    else:
                        print(f"    ✓ created_at is None")
                except Exception as field_e:
                    print(f"    ✗ created_at.isoformat() failed: {str(field_e)}")
                
                try:
                    if user.account_locked_until:
                        iso_locked = user.account_locked_until.isoformat()
                        print(f"    ✓ account_locked_until.isoformat(): {iso_locked}")
                    else:
                        print(f"    ✓ account_locked_until is None")
                except Exception as field_e:
                    print(f"    ✗ account_locked_until.isoformat() failed: {str(field_e)}")
                
                try:
                    if user.last_failed_login:
                        iso_failed = user.last_failed_login.isoformat()
                        print(f"    ✓ last_failed_login.isoformat(): {iso_failed}")
                    else:
                        print(f"    ✓ last_failed_login is None")
                except Exception as field_e:
                    print(f"    ✗ last_failed_login.isoformat() failed: {str(field_e)}")
                
                break  # Stop at first error for detailed analysis

if __name__ == "__main__":
    debug_user_serialization()
