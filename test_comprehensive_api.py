#!/usr/bin/env python3
"""
Comprehensive API Testing for SupplyLine MRO Suite
Tests all authentication endpoints and protected routes
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CREDENTIALS = {
    "employee_number": "ADMIN001",
    "password": "admin123"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            self.log_test("Health Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_login_endpoint(self):
        """Test the login endpoint with valid credentials"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Login Endpoint", True, f"Token received: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test("Login Endpoint", False, "No token in response")
                    return False
            else:
                self.log_test("Login Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Login Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"employee_number": "INVALID", "password": "wrong"},
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401)"
            self.log_test("Invalid Login Rejection", success, details)
            return success
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_status(self):
        """Test the authentication status endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/status")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('authenticated', False)
                details = f"Authenticated: {success}, User: {data.get('user', {}).get('name', 'Unknown')}"
                self.log_test("Auth Status Check", success, details)
                return success
            else:
                self.log_test("Auth Status Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Status Check", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoints(self):
        """Test various protected endpoints"""
        endpoints = [
            ("/api/tools", "GET", "Tools List"),
            ("/api/chemicals", "GET", "Chemicals List"),
            ("/api/checkouts", "GET", "Checkouts List"),
            ("/api/users", "GET", "Users List"),
            ("/api/cycle-count/schedules", "GET", "Cycle Count Schedules"),
            ("/api/announcements", "GET", "Announcements List")
        ]
        
        results = []
        for endpoint, method, name in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.request(method, f"{BASE_URL}{endpoint}")
                
                # Accept both 200 (success) and 403 (forbidden but authenticated)
                success = response.status_code in [200, 403]
                details = f"Status: {response.status_code}"
                
                if response.status_code == 403:
                    details += " (Forbidden - role-based access working)"
                elif response.status_code == 401:
                    details += " (Unauthorized - auth required)"
                    success = False
                
                self.log_test(f"Protected Endpoint: {name}", success, details)
                results.append(success)
            except Exception as e:
                self.log_test(f"Protected Endpoint: {name}", False, f"Exception: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def test_unauthorized_access(self):
        """Test access without authentication token"""
        # Temporarily remove auth header
        original_headers = self.session.headers.copy()
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        try:
            response = self.session.get(f"{BASE_URL}/api/tools")
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401)"
            self.log_test("Unauthorized Access Blocked", success, details)
            
            # Restore headers
            self.session.headers.update(original_headers)
            return success
        except Exception as e:
            self.log_test("Unauthorized Access Blocked", False, f"Exception: {str(e)}")
            self.session.headers.update(original_headers)
            return False
    
    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 50)
        
        # Test sequence
        tests = [
            self.test_health_endpoint,
            self.test_invalid_login,
            self.test_login_endpoint,
            self.test_auth_status,
            self.test_unauthorized_access,
            self.test_protected_endpoints
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is ready for deployment.")
            return True
        else:
            print("⚠️  Some tests failed. Review issues before deployment.")
            return False

def main():
    """Main test execution"""
    tester = APITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('api_test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_success": success,
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to api_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
