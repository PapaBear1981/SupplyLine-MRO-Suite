#!/usr/bin/env python3
"""
Test script to verify app startup without full deployment
"""

import os
import sys

# Set environment variables for Cloud SQL
os.environ['DB_HOST'] = '/cloudsql/gen-lang-client-0819985982:us-west1:supplyline-db'
os.environ['DB_USER'] = 'supplyline_user'
os.environ['DB_NAME'] = 'supplyline'
os.environ['DB_PASSWORD'] = 'test_password'  # This will be replaced by actual secret
os.environ['FLASK_ENV'] = 'production'

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        print("  - Testing Flask import...")
        from flask import Flask
        print("    ✓ Flask imported successfully")
    except Exception as e:
        print(f"    ✗ Flask import failed: {e}")
        return False
    
    try:
        print("  - Testing config import...")
        from config import Config
        print("    ✓ Config imported successfully")
    except Exception as e:
        print(f"    ✗ Config import failed: {e}")
        return False
    
    try:
        print("  - Testing models import...")
        from models import db
        print("    ✓ Models imported successfully")
    except Exception as e:
        print(f"    ✗ Models import failed: {e}")
        return False
    
    try:
        print("  - Testing utils imports...")
        from utils.error_handler import setup_global_error_handlers
        print("    ✓ Error handler imported successfully")
    except Exception as e:
        print(f"    ✗ Error handler import failed: {e}")
        return False
    
    try:
        print("  - Testing routes import...")
        from routes import register_routes
        print("    ✓ Routes imported successfully")
    except Exception as e:
        print(f"    ✗ Routes import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test app creation"""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        print("  - Creating app...")
        app = create_app()
        print("    ✓ App created successfully")
        
        print("  - Testing app context...")
        with app.app_context():
            print("    ✓ App context works")
        
        return True
    except Exception as e:
        print(f"    ✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("SupplyLine Backend Startup Test")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation tests failed")
        return False
    
    print("\n✅ All tests passed! App should start successfully.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
