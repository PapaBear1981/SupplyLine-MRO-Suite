#!/usr/bin/env python3
"""
Test if the frontend can properly proxy requests to the backend
"""

import requests
import json

def test_frontend_api_proxy():
    """Test if frontend properly proxies API requests to backend"""
    
    frontend_url = "https://supplyline-frontend-production-454313121816.us-west1.run.app"
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("🔗 Testing Frontend-Backend Connection")
    print("=" * 50)
    
    # Test if frontend can proxy API requests
    test_endpoints = [
        "/api/tools",
        "/api/auth/status", 
        "/api/users"
    ]
    
    print("Testing via Frontend Proxy:")
    for endpoint in test_endpoints:
        try:
            print(f"\nTesting {frontend_url}{endpoint}...")
            response = requests.get(f"{frontend_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 401]:
                print("✅ Frontend proxy working")
            else:
                print(f"⚠️  Unexpected status: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing Direct Backend:")
    for endpoint in test_endpoints:
        try:
            print(f"\nTesting {backend_url}{endpoint}...")
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 401]:
                print("✅ Backend working")
            else:
                print(f"⚠️  Unexpected status: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_login_via_frontend():
    """Test login via frontend proxy"""
    
    frontend_url = "https://supplyline-frontend-production-454313121816.us-west1.run.app"
    
    print("\n" + "=" * 50)
    print("Testing Login via Frontend Proxy")
    print("=" * 50)
    
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    # Test login via frontend proxy
    try:
        print(f"Testing {frontend_url}/api/auth/login...")
        response = requests.post(f"{frontend_url}/api/auth/login", json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login via frontend proxy SUCCESSFUL!")
            try:
                result = response.json()
                print(f"User: {result.get('name', 'Unknown')}")
                print(f"Admin: {result.get('is_admin', False)}")
                return True
            except:
                print(f"Response: {response.text}")
                return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main execution"""
    
    print("🌐 Frontend-Backend Connection Test")
    print("Testing if the frontend can properly communicate with the backend")
    
    # Test API proxy
    test_frontend_api_proxy()
    
    # Test login
    login_success = test_login_via_frontend()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if login_success:
        print("✅ Frontend-Backend connection: WORKING")
        print("✅ Login via frontend proxy: SUCCESSFUL")
        print("🎉 The issue might be in the frontend JavaScript configuration")
        
        print("\n📋 Next Steps:")
        print("1. Check browser developer tools for JavaScript errors")
        print("2. Verify frontend API configuration")
        print("3. Test login form submission in browser")
        
    else:
        print("❌ Frontend-Backend connection: ISSUES DETECTED")
        print("The frontend cannot properly proxy requests to the backend")
        
        print("\n📋 Next Steps:")
        print("1. Check frontend deployment configuration")
        print("2. Verify VITE_API_URL environment variable")
        print("3. Check CORS settings on backend")

if __name__ == "__main__":
    main()
