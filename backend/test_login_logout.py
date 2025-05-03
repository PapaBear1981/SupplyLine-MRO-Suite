import requests
import json

# Base URL
base_url = "http://localhost:5000/api"

# Test login
def test_login():
    print("\n=== Testing Login ===")
    url = f"{base_url}/auth/login"
    payload = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Login
        print("Sending login request...")
        response = session.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.text}")
        
        # Check auth status
        print("\nChecking auth status...")
        status_response = session.get(f"{base_url}/auth/status")
        print(f"Status Code: {status_response.status_code}")
        print(f"Response Content: {status_response.text}")
        
        # Return the session for further testing
        return session
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test logout
def test_logout(session):
    print("\n=== Testing Logout ===")
    url = f"{base_url}/auth/logout"
    
    try:
        # Logout
        print("Sending logout request...")
        response = session.post(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.text}")
        
        # Check auth status after logout
        print("\nChecking auth status after logout...")
        status_response = session.get(f"{base_url}/auth/status")
        print(f"Status Code: {status_response.status_code}")
        print(f"Response Content: {status_response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test login
    session = test_login()
    
    if session:
        # Test logout
        test_logout(session)
