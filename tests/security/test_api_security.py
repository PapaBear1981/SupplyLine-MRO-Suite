#!/usr/bin/env python3
"""
API Security Test Suite
Tests that all API endpoints are properly protected with authentication
"""

import requests
import json
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

BASE_URL = 'http://localhost:5000'

# Test credentials
ADMIN_CREDENTIALS = {
    'employee_number': 'ADMIN001',
    'password': 'admin123'
}

class APISecurityTester:
    def __init__(self):
        self.token = None
        self.test_results = []
    
    def log_result(self, test_name, expected, actual, passed):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'passed': passed
        })
        print(f"{status} {test_name}: Expected {expected}, Got {actual}")
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are properly blocked"""
        print("\n🔒 Testing Unauthenticated Access (should all return 401)")
        
        endpoints_to_test = [
            # Tools endpoints
            ('GET', '/api/tools', 'Tools list'),
            ('GET', '/api/tools/1', 'Tool details'),
            ('GET', '/api/calibrations/notifications', 'Calibration notifications'),
            
            # Chemicals endpoints
            ('GET', '/api/chemicals', 'Chemicals list'),
            ('GET', '/api/chemicals/1', 'Chemical details'),
            ('GET', '/api/chemicals/1/barcode', 'Chemical barcode'),
            ('GET', '/api/chemicals/1/issuances', 'Chemical issuances'),
            
            # Checkouts endpoints (already secured)
            ('GET', '/api/checkouts', 'Checkouts list'),
            ('GET', '/api/checkouts/user', 'User checkouts'),
        ]
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}")
                elif method == 'POST':
                    response = requests.post(f"{BASE_URL}{endpoint}", json={})
                
                expected = 401
                actual = response.status_code
                passed = actual == expected
                
                self.log_result(f"Unauthenticated {description}", expected, actual, passed)
                
            except Exception as e:
                self.log_result(f"Unauthenticated {description}", 401, f"Error: {e}", False)
    
    def authenticate(self):
        """Get authentication token"""
        print("\n🔑 Authenticating...")
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ Authentication successful, token obtained")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_authenticated_access(self):
        """Test that authenticated requests work properly"""
        if not self.token:
            print("❌ No authentication token available")
            return
        
        print("\n🔓 Testing Authenticated Access (should all return 200 or appropriate success codes)")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        endpoints_to_test = [
            # Tools endpoints
            ('GET', '/api/tools', 'Tools list', 200),
            ('GET', '/api/calibrations/notifications', 'Calibration notifications', 200),
            
            # Chemicals endpoints
            ('GET', '/api/chemicals', 'Chemicals list', 200),
            
            # Checkouts endpoints
            ('GET', '/api/checkouts', 'Checkouts list', 200),
            ('GET', '/api/checkouts/user', 'User checkouts', 200),
        ]
        
        for method, endpoint, description, expected_code in endpoints_to_test:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                elif method == 'POST':
                    response = requests.post(f"{BASE_URL}{endpoint}", json={}, headers=headers)
                
                expected = expected_code
                actual = response.status_code
                passed = actual == expected
                
                self.log_result(f"Authenticated {description}", expected, actual, passed)
                
            except Exception as e:
                self.log_result(f"Authenticated {description}", expected_code, f"Error: {e}", False)
    
    def test_invalid_token_access(self):
        """Test that invalid tokens are properly rejected"""
        print("\n🚫 Testing Invalid Token Access (should all return 401)")
        
        invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
        
        endpoints_to_test = [
            ('GET', '/api/tools', 'Tools list with invalid token'),
            ('GET', '/api/chemicals', 'Chemicals list with invalid token'),
        ]
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=invalid_headers)
                
                expected = 401
                actual = response.status_code
                passed = actual == expected
                
                self.log_result(description, expected, actual, passed)
                
            except Exception as e:
                self.log_result(description, 401, f"Error: {e}", False)
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🛡️  API Security Test Suite")
        print("=" * 50)
        
        # Test unauthenticated access
        self.test_unauthenticated_access()
        
        # Authenticate
        if self.authenticate():
            # Test authenticated access
            self.test_authenticated_access()
        
        # Test invalid token access
        self.test_invalid_token_access()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: Expected {result['expected']}, Got {result['actual']}")
        
        if failed_tests == 0:
            print("\n🎉 ALL SECURITY TESTS PASSED!")
            print("✅ API endpoints are properly secured")
        else:
            print(f"\n⚠️  {failed_tests} security issues found")
            return False
        
        return True

def main():
    """Main function"""
    tester = APISecurityTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
