#!/usr/bin/env python3
"""
Test script to reproduce the users API datetime parsing issue
"""
import requests
import json

def test_users_api():
    """Test the users API endpoint after logging in"""
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing Users API endpoint...")
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        'employee_number': 'ADMIN001',
        'password': 'admin123'
    }
    
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Login response status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✓ Login successful")
        login_result = login_response.json()
        print(f"Login result: {json.dumps(login_result, indent=2)}")
    else:
        print(f"✗ Login failed: {login_response.text}")
        return False
    
    # Step 2: Test users API endpoint
    print("\n2. Testing /api/users endpoint...")
    users_response = session.get(f"{base_url}/api/users")
    print(f"Users API response status: {users_response.status_code}")
    
    if users_response.status_code == 200:
        print("✓ Users API successful")
        users_data = users_response.json()
        print(f"Number of users returned: {len(users_data)}")
        
        # Print first user for debugging
        if users_data:
            print(f"First user data: {json.dumps(users_data[0], indent=2)}")
        return True
    else:
        print(f"✗ Users API failed: {users_response.text}")
        return False

if __name__ == "__main__":
    success = test_users_api()
    if success:
        print("\n✓ Test completed successfully!")
    else:
        print("\n✗ Test failed!")
