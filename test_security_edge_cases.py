#!/usr/bin/env python3
"""
Security and Edge Case Testing for SupplyLine MRO Suite
Tests authentication edge cases, token expiration, unauthorized access, and security measures
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:5173"
TEST_CREDENTIALS = {
    "employee_number": "ADMIN001",
    "password": "admin123"
}

class SecurityTester:
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
    
    def test_invalid_credentials(self):
        """Test various invalid credential combinations"""
        invalid_creds = [
            {"employee_number": "", "password": ""},
            {"employee_number": "INVALID", "password": "wrong"},
            {"employee_number": "ADMIN001", "password": "wrongpassword"},
            {"employee_number": "admin001", "password": "admin123"},  # Case sensitivity
            {"employee_number": "ADMIN001", "password": ""},
            {"employee_number": "", "password": "admin123"},
        ]
        
        passed = 0
        total = len(invalid_creds)
        
        for i, creds in enumerate(invalid_creds):
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json=creds,
                    headers={"Content-Type": "application/json"}
                )
                
                success = response.status_code in [400, 401]  # Should be rejected
                details = f"Creds {i+1}: Status {response.status_code} (expected 400/401)"
                
                if success:
                    passed += 1
                    
                self.log_test(f"Invalid Credentials Test {i+1}", success, details)
            except Exception as e:
                self.log_test(f"Invalid Credentials Test {i+1}", False, f"Exception: {str(e)}")
        
        overall_success = passed == total
        self.log_test("Overall Invalid Credentials Protection", overall_success, f"{passed}/{total} tests passed")
        return overall_success
    
    def test_sql_injection_attempts(self):
        """Test SQL injection attempts in login"""
        injection_attempts = [
            {"employee_number": "' OR '1'='1", "password": "anything"},
            {"employee_number": "ADMIN001'; DROP TABLE users; --", "password": "admin123"},
            {"employee_number": "ADMIN001", "password": "' OR '1'='1"},
            {"employee_number": "admin' UNION SELECT * FROM users --", "password": "test"},
        ]
        
        passed = 0
        total = len(injection_attempts)
        
        for i, creds in enumerate(injection_attempts):
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json=creds,
                    headers={"Content-Type": "application/json"}
                )
                
                success = response.status_code in [400, 401, 500]  # Should be rejected
                details = f"Injection {i+1}: Status {response.status_code}"
                
                if success:
                    passed += 1
                    
                self.log_test(f"SQL Injection Test {i+1}", success, details)
            except Exception as e:
                self.log_test(f"SQL Injection Test {i+1}", False, f"Exception: {str(e)}")
        
        overall_success = passed == total
        self.log_test("Overall SQL Injection Protection", overall_success, f"{passed}/{total} tests passed")
        return overall_success
    
    def test_malformed_requests(self):
        """Test malformed and malicious requests"""
        malformed_requests = [
            # Missing content type
            ({"employee_number": "ADMIN001", "password": "admin123"}, {}),
            # Invalid JSON
            ('{"employee_number": "ADMIN001", "password":}', {"Content-Type": "application/json"}),
            # Extra fields
            ({"employee_number": "ADMIN001", "password": "admin123", "admin": True}, {"Content-Type": "application/json"}),
            # Wrong data types
            ({"employee_number": 123, "password": ["admin123"]}, {"Content-Type": "application/json"}),
        ]
        
        passed = 0
        total = len(malformed_requests)
        
        for i, (data, headers) in enumerate(malformed_requests):
            try:
                if isinstance(data, str):
                    response = requests.post(f"{BASE_URL}/api/auth/login", data=data, headers=headers)
                else:
                    response = requests.post(f"{BASE_URL}/api/auth/login", json=data, headers=headers)
                
                success = response.status_code in [400, 401, 422, 500]  # Should be rejected
                details = f"Malformed {i+1}: Status {response.status_code}"
                
                if success:
                    passed += 1
                    
                self.log_test(f"Malformed Request Test {i+1}", success, details)
            except Exception as e:
                # Network/parsing errors are also acceptable for malformed requests
                passed += 1
                self.log_test(f"Malformed Request Test {i+1}", True, f"Properly rejected: {str(e)}")
        
        overall_success = passed == total
        self.log_test("Overall Malformed Request Protection", overall_success, f"{passed}/{total} tests passed")
        return overall_success
    
    def test_unauthorized_api_access(self):
        """Test access to protected endpoints without authentication"""
        protected_endpoints = [
            "/api/tools",
            "/api/chemicals", 
            "/api/checkouts",
            "/api/users",
            "/api/admin/dashboard/stats",
            "/api/announcements",
        ]
        
        passed = 0
        total = len(protected_endpoints)
        
        # Clear any existing auth
        session = requests.Session()
        
        for endpoint in protected_endpoints:
            try:
                response = session.get(f"{BASE_URL}{endpoint}")
                success = response.status_code == 401  # Should require auth
                details = f"Status: {response.status_code} (expected 401)"
                
                if success:
                    passed += 1
                    
                self.log_test(f"Unauthorized Access: {endpoint}", success, details)
            except Exception as e:
                self.log_test(f"Unauthorized Access: {endpoint}", False, f"Exception: {str(e)}")
        
        overall_success = passed == total
        self.log_test("Overall Unauthorized Access Protection", overall_success, f"{passed}/{total} endpoints protected")
        return overall_success
    
    def test_invalid_token_access(self):
        """Test access with invalid/malformed tokens"""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "expired_token_here",
            "",
            "null",
        ]
        
        passed = 0
        total = len(invalid_tokens)
        
        for i, token in enumerate(invalid_tokens):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/api/tools", headers=headers)
                
                success = response.status_code == 401  # Should be rejected
                details = f"Token {i+1}: Status {response.status_code} (expected 401)"
                
                if success:
                    passed += 1
                    
                self.log_test(f"Invalid Token Test {i+1}", success, details)
            except Exception as e:
                self.log_test(f"Invalid Token Test {i+1}", False, f"Exception: {str(e)}")
        
        overall_success = passed == total
        self.log_test("Overall Invalid Token Protection", overall_success, f"{passed}/{total} tests passed")
        return overall_success
    
    def test_rate_limiting(self):
        """Test if there's basic rate limiting on login attempts"""
        print("Testing rate limiting (this may take a moment)...")
        
        # Make rapid login attempts
        attempts = 10
        responses = []
        
        for i in range(attempts):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"employee_number": "INVALID", "password": "wrong"},
                    headers={"Content-Type": "application/json"}
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            except Exception as e:
                responses.append(0)  # Connection error
        
        # Check if any requests were rate limited (429) or blocked
        rate_limited = any(status in [429, 503] for status in responses)
        success = rate_limited or len(set(responses)) > 1  # Some variation in responses
        
        details = f"Responses: {responses[:5]}... (Rate limited: {rate_limited})"
        self.log_test("Rate Limiting Test", success, details)
        return success
    
    def run_all_security_tests(self):
        """Run comprehensive security test suite"""
        print("🔒 Starting Security and Edge Case Testing")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_invalid_credentials,
            self.test_sql_injection_attempts,
            self.test_malformed_requests,
            self.test_unauthorized_api_access,
            self.test_invalid_token_access,
            self.test_rate_limiting,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"🔒 Security Test Results: {passed}/{total} test categories passed")
        
        if passed == total:
            print("🎉 All security tests passed! Application has good security measures.")
            return True
        else:
            print("⚠️  Some security tests failed. Review security measures.")
            return False

def main():
    """Main test execution"""
    tester = SecurityTester()
    success = tester.run_all_security_tests()
    
    # Save detailed results
    with open('security_test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_success": success,
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to security_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
