#!/usr/bin/env python3
"""
Create admin user via API
"""

import requests
import json

def create_admin_user():
    """Create admin user via the backend API"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("Creating admin user...")
    
    try:
        # Try to create admin user
        print("Trying /api/init-admin endpoint...")
        response = requests.post(f"{backend_url}/api/init-admin", timeout=60)
        
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                print(f"SUCCESS: {json.dumps(result, indent=2)}")
                return True
            except:
                print(f"Response: {response.text}")
                return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_login():
    """Test login with admin credentials"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("\nTesting login...")
    
    try:
        login_data = {
            "employee_number": "ADMIN001",
            "password": "admin123"
        }
        
        response = requests.post(f"{backend_url}/api/login", json=login_data, timeout=30)
        
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"LOGIN SUCCESS: {json.dumps(result, indent=2)}")
                return True
            except:
                print(f"Login response: {response.text}")
                return True
        else:
            print(f"Login error: {response.text}")
            return False
            
    except Exception as e:
        print(f"LOGIN ERROR: {e}")
        return False

if __name__ == "__main__":
    admin_created = create_admin_user()
    if admin_created:
        print("\n✅ Admin user creation completed!")
        login_success = test_login()
        if login_success:
            print("✅ Login test successful!")
        else:
            print("❌ Login test failed!")
    else:
        print("\n❌ Admin user creation failed!")
