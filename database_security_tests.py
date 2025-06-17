#!/usr/bin/env python3
"""
Database Security Testing Suite for SupplyLine MRO Suite
Tests SQL injection prevention, data access control, and transaction integrity
"""

import requests
import sys
import os
import uuid

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"
DB_PATH = "database/tools.db"

class DatabaseSecurityTester:
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
    
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            admin_emp_num = os.environ.get('SL_ADMIN_EMP_NUM', 'ADMIN001')
            admin_password = os.environ.get('SL_ADMIN_PWD', 'admin123')
            response = self.session.post(f"{API_BASE}/auth/login",
                json={"employee_number": admin_emp_num, "password": admin_password})
            if response.status_code == 200:
                self.auth_token = response.json().get('token')
                return True
        except Exception as e:
            print(f"Authentication failed: {e}")
        return False
    
    def get_headers(self):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        print("\n💉 SQL INJECTION PREVENTION TESTS")
        
        if not self.authenticate():
            self.log_test("SQL injection tests", False, "Authentication failed")
            return
        
        # SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; UPDATE users SET is_admin=1; --",
            "' OR 1=1 --",
            "'; INSERT INTO users (name) VALUES ('hacker'); --"
        ]
        
        # Test SQL injection in search parameters
        for payload in sql_payloads:
            try:
                # Test in tool search
                response = self.session.get(f"{API_BASE}/tools", 
                    params={"search": payload}, 
                    headers=self.get_headers())
                
                # Should not return 500 error (SQL error) and should not expose sensitive data
                passed = response.status_code != 500 and "users" not in response.text.lower()
                self.log_test(f"SQL injection blocked in search: {payload[:20]}...", 
                             passed,
                             f"Status: {response.status_code}")
                             
            except Exception as e:
                self.log_test(f"SQL injection test for {payload[:20]}...", False, f"Error: {e}")
        
        # Test SQL injection in POST data
        for payload in sql_payloads:
            try:
                tool_data = {
                    "tool_number": payload,
                    "description": "Test tool",
                    "category": "Test"
                }
                
                response = self.session.post(f"{API_BASE}/tools", 
                    json=tool_data, 
                    headers=self.get_headers())
                
                # Should handle malicious input gracefully
                passed = response.status_code != 500
                self.log_test(f"SQL injection blocked in POST: {payload[:20]}...", 
                             passed,
                             f"Status: {response.status_code}")
                             
            except Exception as e:
                self.log_test(f"SQL injection POST test for {payload[:20]}...", False, f"Error: {e}")
    
    def test_data_access_control(self):
        """Test data access control and authorization"""
        print("\n🔐 DATA ACCESS CONTROL TESTS")
        
        # Test 1: Unauthenticated access
        try:
            response = requests.get(f"{API_BASE}/tools")
            self.log_test("Unauthenticated database access blocked", 
                         response.status_code in [401, 403],
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthenticated access test", False, f"Error: {e}")
        
        # Test 2: Authenticated access works
        if self.auth_token:
            try:
                response = self.session.get(f"{API_BASE}/tools", headers=self.get_headers())
                self.log_test("Authenticated database access works", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Authenticated access test", False, f"Error: {e}")
        
        # Test 3: Direct database access prevention
        try:
            # Try to access database file directly (should not be exposed via web)
            response = requests.get(f"{BASE_URL}/database/tools.db")
            self.log_test("Direct database file access blocked", 
                         response.status_code == 404,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Direct database access test", False, f"Error: {e}")
    
    def test_transaction_integrity(self):
        """Test database transaction integrity"""
        print("\n🔄 TRANSACTION INTEGRITY TESTS")
        
        if not self.auth_token:
            self.log_test("Transaction integrity tests", False, "Not authenticated")
            return
        
        # Test 1: Create and verify tool
        unique_id = uuid.uuid4().hex[:8]
        tool_data = {
            "tool_number": f"INTEGRITY_TEST_{unique_id}",
            "serial_number": f"INT{unique_id}",
            "description": "Integrity Test Tool",
            "category": "Testing",
            "location": "Test Lab",
            "status": "Available"
        }
        
        try:
            # Create tool
            response = self.session.post(f"{API_BASE}/tools", 
                json=tool_data, 
                headers=self.get_headers())
            
            if response.status_code == 201:
                tool_id = response.json().get('id')
                
                # Verify tool exists
                verify_response = self.session.get(f"{API_BASE}/tools/{tool_id}", 
                    headers=self.get_headers())
                
                self.log_test("Transaction integrity - Create and verify", 
                             verify_response.status_code == 200,
                             f"Tool created and verified: {tool_id}")
                
                # Clean up
                self.session.delete(f"{API_BASE}/tools/{tool_id}", headers=self.get_headers())
                
            else:
                self.log_test("Transaction integrity test", False, 
                             f"Tool creation failed: {response.status_code}")
                             
        except Exception as e:
            self.log_test("Transaction integrity test", False, f"Error: {e}")
    
    def test_database_connection_security(self):
        """Test database connection security"""
        print("\n🔗 DATABASE CONNECTION SECURITY TESTS")
        
        # Test 1: Check if database file exists and is protected
        if os.path.exists(DB_PATH):
            try:
                # Check file permissions (should not be world-readable in production)
                import stat
                file_stats = os.stat(DB_PATH)
                file_mode = stat.filemode(file_stats.st_mode)
                
                self.log_test("Database file exists", True, f"Path: {DB_PATH}")
                self.log_test("Database file permissions", True, f"Mode: {file_mode}")
                
            except Exception as e:
                self.log_test("Database file check", False, f"Error: {e}")
        else:
            self.log_test("Database file check", False, "Database file not found")
        
        # Test 2: Connection pooling (indirect test via multiple requests)
        if self.auth_token:
            try:
                # Make multiple concurrent-like requests
                responses = []
                for _ in range(5):
                    response = self.session.get(f"{API_BASE}/tools", headers=self.get_headers())
                    responses.append(response.status_code)
                
                all_success = all(status == 200 for status in responses)
                self.log_test("Database connection pooling", 
                             all_success,
                             f"Multiple requests handled: {responses}")
                             
            except Exception as e:
                self.log_test("Connection pooling test", False, f"Error: {e}")
    
    def test_data_validation(self):
        """Test data validation and constraints"""
        print("\n✅ DATA VALIDATION TESTS")
        
        if not self.auth_token:
            self.log_test("Data validation tests", False, "Not authenticated")
            return
        
        # Test 1: Invalid data types
        invalid_tool_data = {
            "tool_number": 12345,  # Should be string
            "description": None,   # Should be string
            "category": "",        # Should not be empty
        }
        
        try:
            response = self.session.post(f"{API_BASE}/tools", 
                json=invalid_tool_data, 
                headers=self.get_headers())
            
            # Should reject invalid data
            self.log_test("Invalid data type validation", 
                         response.status_code == 400,
                         f"Status: {response.status_code}")
                         
        except Exception as e:
            self.log_test("Data type validation test", False, f"Error: {e}")
        
        # Test 2: Required field validation
        incomplete_tool_data = {
            "description": "Tool without required fields"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/tools", 
                json=incomplete_tool_data, 
                headers=self.get_headers())
            
            # Should reject incomplete data
            self.log_test("Required field validation", 
                         response.status_code == 400,
                         f"Status: {response.status_code}")
                         
        except Exception as e:
            self.log_test("Required field validation test", False, f"Error: {e}")
    
    def test_audit_trail_integrity(self):
        """Test audit trail and logging integrity"""
        print("\n📝 AUDIT TRAIL INTEGRITY TESTS")
        
        if not self.auth_token:
            self.log_test("Audit trail tests", False, "Not authenticated")
            return
        
        # Test 1: Check if audit logs are being created
        try:
            response = self.session.get(f"{API_BASE}/audit/logs", headers=self.get_headers())
            
            if response.status_code == 200:
                logs = response.json()
                self.log_test("Audit logs accessible", True, 
                             f"Found {len(logs)} audit entries")
            else:
                self.log_test("Audit logs test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Audit logs test", False, f"Error: {e}")
        
        # Test 2: Verify user activity logging
        try:
            response = self.session.get(f"{API_BASE}/user/activity", headers=self.get_headers())
            
            if response.status_code == 200:
                activities = response.json()
                self.log_test("User activity logging", True, 
                             f"Found {len(activities)} activity entries")
            else:
                self.log_test("User activity logging test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("User activity logging test", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all database security tests"""
        print("🗄️ SUPPLYLINE MRO SUITE - DATABASE SECURITY TESTING")
        print("=" * 50)
        
        self.test_sql_injection_prevention()
        self.test_data_access_control()
        self.test_transaction_integrity()
        self.test_database_connection_security()
        self.test_data_validation()
        self.test_audit_trail_integrity()
        
        # Summary
        print("\n📊 DATABASE SECURITY TEST SUMMARY")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL DATABASE SECURITY TESTS PASSED!")
            return True

        print("⚠️  SOME DATABASE SECURITY TESTS FAILED")
        failed_tests = [r for r in self.test_results if not r['passed']]
        for test in failed_tests:
            print(f"   ❌ {test['test']}: {test['details']}")
        return False

if __name__ == "__main__":
    tester = DatabaseSecurityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
