#!/usr/bin/env python3
"""
Test the correct login endpoint that the frontend actually uses
"""

import requests
import json
import time

def test_auth_endpoints():
    """Test various authentication endpoints"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("🔍 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test different possible auth endpoints
    auth_endpoints = [
        "/auth/login",
        "/api/auth/login", 
        "/api/login",
        "/login"
    ]
    
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    for endpoint in auth_endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.post(f"{backend_url}{endpoint}", json=login_data, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Login endpoint found and working")
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                    return endpoint, True
                except:
                    print(f"Response: {response.text}")
                    return endpoint, True
            elif response.status_code == 401:
                print("⚠️  Endpoint exists but credentials invalid")
                return endpoint, False
            elif response.status_code == 404:
                print("❌ Endpoint not found")
            elif response.status_code == 500:
                print("❌ Server error")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Raw error: {response.text}")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    return None, False

def test_auth_status_endpoints():
    """Test authentication status endpoints"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("\n" + "=" * 50)
    print("Testing Auth Status Endpoints")
    print("=" * 50)
    
    status_endpoints = [
        "/auth/status",
        "/api/auth/status",
        "/auth/user",
        "/api/auth/user"
    ]
    
    for endpoint in status_endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Endpoint working")
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                except:
                    print(f"Response: {response.text}")
            elif response.status_code == 401:
                print("✅ Endpoint exists (authentication required)")
            elif response.status_code == 404:
                print("❌ Endpoint not found")
            else:
                print(f"⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

def main():
    """Main execution"""
    
    print("🔐 Authentication Endpoint Discovery")
    print("Finding the correct login endpoint that the frontend uses")
    
    # Test login endpoints
    working_endpoint, login_success = test_auth_endpoints()
    
    # Test status endpoints
    test_auth_status_endpoints()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if working_endpoint:
        if login_success:
            print(f"✅ Working login endpoint found: {working_endpoint}")
            print("✅ Login credentials are valid")
            print("🎉 Authentication system is functional!")
        else:
            print(f"⚠️  Login endpoint found: {working_endpoint}")
            print("❌ Login credentials are invalid")
            print("Need to check admin user creation")
    else:
        print("❌ No working login endpoint found")
        print("Backend deployment may be missing authentication routes")
    
    print("\n📋 Next Steps:")
    if working_endpoint and login_success:
        print("1. Test login in browser")
        print("2. Verify session persistence")
        print("3. Test all protected routes")
    elif working_endpoint:
        print("1. Recreate admin user with correct credentials")
        print("2. Test login again")
    else:
        print("1. Check backend route registration")
        print("2. Verify authentication module is loaded")
        print("3. Consider backend restart/redeploy")

if __name__ == "__main__":
    main()
