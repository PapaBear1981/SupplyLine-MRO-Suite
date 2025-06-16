"""
Test script to verify role management endpoints are working
"""
import requests
import json

def test_role_endpoints():
    """Test role management endpoints"""
    base_url = "http://localhost:5000"
    
    # First login as admin
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        # Login
        print("Testing login...")
        login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return False
        
        print("Login successful!")
        
        # Test roles endpoint
        print("\nTesting /api/roles endpoint...")
        roles_response = session.get(f"{base_url}/api/roles")
        print(f"Roles endpoint status: {roles_response.status_code}")
        
        if roles_response.status_code == 200:
            roles_data = roles_response.json()
            print(f"Roles data: {json.dumps(roles_data, indent=2)}")
        else:
            print(f"Roles endpoint error: {roles_response.text}")
        
        # Test users endpoint
        print("\nTesting /api/users endpoint...")
        users_response = session.get(f"{base_url}/api/users")
        print(f"Users endpoint status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"Found {len(users_data)} users")
        else:
            print(f"Users endpoint error: {users_response.text}")
        
        # Test permissions categories endpoint
        print("\nTesting /api/permissions/categories endpoint...")
        perms_response = session.get(f"{base_url}/api/permissions/categories")
        print(f"Permissions endpoint status: {perms_response.status_code}")
        
        if perms_response.status_code == 200:
            perms_data = perms_response.json()
            print(f"Permissions categories: {json.dumps(perms_data, indent=2)}")
        else:
            print(f"Permissions endpoint error: {perms_response.text}")
        
        return True
        
    except Exception as e:
        print(f"Error testing endpoints: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_role_endpoints()
    if success:
        print("\nRole management endpoints test completed!")
    else:
        print("\nRole management endpoints test failed!")
