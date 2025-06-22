#!/usr/bin/env python3
"""
Test script to verify the authentication fix for reports page
"""
import requests
import json

# Test login and reports access
def test_auth_fix():
    base_url = "http://localhost"
    
    print("Testing authentication fix...")
    
    # Step 1: Login
    print("1. Attempting login...")
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            print("✅ Login successful!")
            print(f"Access token received: {access_token[:50]}...")

            # Decode the JWT token to see what's in it
            import base64
            import json
            try:
                # Split the token and decode the payload
                parts = access_token.split('.')
                if len(parts) == 3:
                    # Add padding if needed
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.b64decode(payload)
                    token_data = json.loads(decoded)
                    print(f"Token payload: {token_data}")
            except Exception as e:
                print(f"Could not decode token: {e}")

            # Step 2: Test reports API
            print("\n2. Testing reports API access...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            reports_response = requests.get(
                f"{base_url}/api/reports/tools",
                headers=headers
            )

            print(f"Reports API response status: {reports_response.status_code}")
            print(f"Request headers: {headers}")

            if reports_response.status_code == 200:
                print("✅ Reports API access successful!")
                print("🎉 Fix verified: Reports page should now work!")
                return True
            else:
                print(f"❌ Reports API failed: {reports_response.text}")
                print("Let me check the backend logs for more details...")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_auth_fix()
    if success:
        print("\n🎉 SUCCESS: The authentication fix is working!")
    else:
        print("\n❌ FAILED: The authentication fix needs more work.")
