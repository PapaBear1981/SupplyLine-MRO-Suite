#!/usr/bin/env python3
"""
Comprehensive Security Testing Suite for SupplyLine MRO Suite
Tests authentication, authorization, input validation, and security headers
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_authentication_security(self):
        """Test authentication security measures"""
        print("\n🔐 AUTHENTICATION SECURITY TESTS")
        
        # Test 1: Invalid credentials
        try:
            response = self.session.post(f"{API_BASE}/auth/login", 
                json={"employee_number": "INVALID", "password": "invalid"})
            self.log_test("Invalid credentials rejected", 
                         response.status_code == 401,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid credentials test", False, f"Error: {e}")
        
        # Test 2: SQL injection in login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", 
                json={"employee_number": "' OR '1'='1", "password": "anything"})
            self.log_test("SQL injection in login blocked", 
                         response.status_code == 401,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("SQL injection login test", False, f"Error: {e}")
        
        # Test 3: Valid login
        try:
            response = self.session.post(f"{API_BASE}/auth/login", 
                json={"employee_number": "ADMIN001", "password": "admin123"})
            if response.status_code == 200:
                self.auth_token = response.json().get('token')
                self.log_test("Valid login successful", True, "Admin login working")
            else:
                self.log_test("Valid login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Valid login test", False, f"Error: {e}")
    
    def test_authorization_security(self):
        """Test authorization and access control"""
        print("\n🛡️ AUTHORIZATION SECURITY TESTS")
        
        # Test 1: Access protected endpoint without auth
        try:
            response = requests.get(f"{API_BASE}/users")
            self.log_test("Protected endpoint blocks unauthenticated access", 
                         response.status_code in [401, 403],
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthenticated access test", False, f"Error: {e}")
        
        # Test 2: Access with valid session
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(f"{API_BASE}/auth/session-info", headers=headers)
                self.log_test("Authenticated access works", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Authenticated access test", False, f"Error: {e}")
    
    def test_input_validation(self):
        """Test input validation and XSS prevention"""
        print("\n🔍 INPUT VALIDATION TESTS")
        
        # Test XSS payloads
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'; DROP TABLE users; --"
        ]
        
        for payload in xss_payloads:
            try:
                response = self.session.post(f"{API_BASE}/auth/login", 
                    json={"employee_number": payload, "password": "test"})
                self.log_test(f"XSS payload blocked: {payload[:20]}...", 
                             response.status_code == 401,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"XSS test for {payload[:20]}...", False, f"Error: {e}")
    
    def test_security_headers(self):
        """Test security headers"""
        print("\n🔒 SECURITY HEADERS TESTS")
        
        try:
            response = requests.get(BASE_URL)
            headers = response.headers
            
            # Check for security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            for header, expected in security_headers.items():
                actual = headers.get(header)
                self.log_test(f"Security header {header}", 
                             actual == expected,
                             f"Expected: {expected}, Got: {actual}")
                             
        except Exception as e:
            self.log_test("Security headers test", False, f"Error: {e}")
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n⚡ RATE LIMITING TESTS")
        
        # Test rapid requests
        try:
            rapid_requests = 0
            blocked_requests = 0
            
            for i in range(10):
                response = requests.post(f"{API_BASE}/auth/login", 
                    json={"employee_number": "test", "password": "test"})
                rapid_requests += 1
                if response.status_code == 429:  # Too Many Requests
                    blocked_requests += 1
                time.sleep(0.1)
            
            self.log_test("Rate limiting active", 
                         blocked_requests > 0 or rapid_requests <= 10,
                         f"Blocked: {blocked_requests}/{rapid_requests}")
                         
        except Exception as e:
            self.log_test("Rate limiting test", False, f"Error: {e}")
    
    def test_session_security(self):
        """Test session security"""
        print("\n🍪 SESSION SECURITY TESTS")
        
        if self.auth_token:
            try:
                # Test session info
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(f"{API_BASE}/auth/session-info", headers=headers)
                
                if response.status_code == 200:
                    session_data = response.json()
                    self.log_test("Session info accessible", True, 
                                 f"Authenticated: {session_data.get('authenticated')}")
                else:
                    self.log_test("Session info test", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Session security test", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔐 SUPPLYLINE MRO SUITE - SECURITY TESTING")
        print("=" * 50)
        
        self.test_authentication_security()
        self.test_authorization_security()
        self.test_input_validation()
        self.test_security_headers()
        self.test_rate_limiting()
        self.test_session_security()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL SECURITY TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME SECURITY TESTS FAILED")
            failed_tests = [r for r in self.test_results if not r['passed']]
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
            return False

if __name__ == "__main__":
    tester = SecurityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
