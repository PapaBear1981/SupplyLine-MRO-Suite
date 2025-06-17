#!/usr/bin/env python3
"""
Comprehensive Functionality Testing Suite for SupplyLine MRO Suite
Tests all core business workflows and user interactions
"""

import requests
import sys
import os
import uuid

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

class FunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.created_items = {'tools': [], 'chemicals': [], 'users': []}
        
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
    
    def test_user_authentication_workflows(self):
        """Test user authentication workflows"""
        print("\n🔐 USER AUTHENTICATION WORKFLOWS")
        
        # Test 1: Admin login
        if self.authenticate():
            self.log_test("Admin user login", True, "Authentication successful")
        else:
            self.log_test("Admin user login", False, "Authentication failed")
        
        # Test 2: Session info
        if self.auth_token:
            try:
                response = self.session.get(f"{API_BASE}/auth/session-info", 
                                          headers=self.get_headers())
                self.log_test("Session info retrieval", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Session info test", False, f"Error: {e}")
        
        # Test 3: User profile access
        if self.auth_token:
            try:
                response = self.session.get(f"{API_BASE}/auth/user", 
                                          headers=self.get_headers())
                self.log_test("User profile access", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("User profile test", False, f"Error: {e}")
    
    def test_tool_management_workflows(self):
        """Test tool management workflows"""
        print("\n🔧 TOOL MANAGEMENT WORKFLOWS")
        
        if not self.auth_token:
            self.log_test("Tool management tests", False, "Not authenticated")
            return
        
        # Test 1: List tools
        try:
            response = self.session.get(f"{API_BASE}/tools", headers=self.get_headers())
            self.log_test("List tools", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("List tools test", False, f"Error: {e}")
        
        # Test 2: Create tool
        unique_id = uuid.uuid4().hex[:8]
        tool_data = {
            "tool_number": f"TEST-{unique_id}",
            "serial_number": f"SN{unique_id}",
            "description": "Test Tool for Functionality Testing",
            "category": "Testing",
            "location": "Test Lab",
            "status": "Available"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/tools", 
                                       json=tool_data, 
                                       headers=self.get_headers())
            if response.status_code == 201:
                tool_id = response.json().get('id')
                self.created_items['tools'].append(tool_id)
                self.log_test("Create tool", True, f"Tool ID: {tool_id}")
            else:
                self.log_test("Create tool", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create tool test", False, f"Error: {e}")
        
        # Test 3: Get tool details
        if self.created_items['tools']:
            try:
                tool_id = self.created_items['tools'][0]
                response = self.session.get(f"{API_BASE}/tools/{tool_id}", 
                                          headers=self.get_headers())
                self.log_test("Get tool details", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get tool details test", False, f"Error: {e}")
    
    def test_chemical_management_workflows(self):
        """Test chemical management workflows"""
        print("\n⚗️ CHEMICAL MANAGEMENT WORKFLOWS")
        
        if not self.auth_token:
            self.log_test("Chemical management tests", False, "Not authenticated")
            return
        
        # Test 1: List chemicals
        try:
            response = self.session.get(f"{API_BASE}/chemicals", headers=self.get_headers())
            self.log_test("List chemicals", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("List chemicals test", False, f"Error: {e}")
        
        # Test 2: Create chemical
        unique_id = uuid.uuid4().hex[:8]
        chemical_data = {
            "part_number": f"CHEM-{unique_id}",
            "lot_number": f"LOT{unique_id}",
            "description": "Test Chemical for Functionality Testing",
            "manufacturer": "Test Manufacturer",
            "category": "Testing",
            "quantity": 100,
            "unit": "ml",
            "expiration_date": "2025-12-31"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/chemicals", 
                                       json=chemical_data, 
                                       headers=self.get_headers())
            if response.status_code == 201:
                chemical_id = response.json().get('id')
                self.created_items['chemicals'].append(chemical_id)
                self.log_test("Create chemical", True, f"Chemical ID: {chemical_id}")
            else:
                self.log_test("Create chemical", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create chemical test", False, f"Error: {e}")
        
        # Test 3: Get chemical details
        if self.created_items['chemicals']:
            try:
                chemical_id = self.created_items['chemicals'][0]
                response = self.session.get(f"{API_BASE}/chemicals/{chemical_id}", 
                                          headers=self.get_headers())
                self.log_test("Get chemical details", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get chemical details test", False, f"Error: {e}")
    
    def test_dashboard_workflows(self):
        """Test dashboard and reporting workflows"""
        print("\n📊 DASHBOARD & REPORTING WORKFLOWS")
        
        if not self.auth_token:
            self.log_test("Dashboard tests", False, "Not authenticated")
            return
        
        # Test dashboard endpoints
        dashboard_endpoints = [
            ("/user/activity", "User activity"),
            ("/checkouts/user", "User checkouts"),
            ("/checkouts/overdue", "Overdue checkouts"),
            ("/calibrations/due", "Calibrations due"),
            ("/calibrations/overdue", "Overdue calibrations"),
            ("/chemicals/on-order", "Chemicals on order"),
            ("/announcements", "Announcements")
        ]
        
        for endpoint, description in dashboard_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", 
                                          headers=self.get_headers())
                self.log_test(f"Dashboard: {description}", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Dashboard {description} test", False, f"Error: {e}")
    
    def test_admin_workflows(self):
        """Test admin-specific workflows"""
        print("\n👑 ADMIN WORKFLOWS")
        
        if not self.auth_token:
            self.log_test("Admin tests", False, "Not authenticated")
            return
        
        # Test admin endpoints
        admin_endpoints = [
            ("/admin/dashboard/stats", "Admin dashboard stats"),
            ("/admin/settings", "System settings"),
            ("/admin/registration-requests", "Registration requests"),
            ("/audit/logs", "Audit logs"),
            ("/admin/system-resources", "System resources")
        ]
        
        for endpoint, description in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", 
                                          headers=self.get_headers())
                self.log_test(f"Admin: {description}", 
                             response.status_code == 200,
                             f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Admin {description} test", False, f"Error: {e}")
    
    def test_data_integrity(self):
        """Test data integrity and consistency"""
        print("\n🔍 DATA INTEGRITY TESTS")
        
        if not self.auth_token:
            self.log_test("Data integrity tests", False, "Not authenticated")
            return
        
        # Test 1: Verify created tools exist
        if self.created_items['tools']:
            try:
                response = self.session.get(f"{API_BASE}/tools", headers=self.get_headers())
                if response.status_code == 200:
                    tools = response.json().get('tools', [])
                    created_tool_found = any(tool['id'] in self.created_items['tools'] for tool in tools)
                    self.log_test("Created tool data integrity",
                                 created_tool_found,
                                 "Found created tool in list")
                else:
                    self.log_test("Tool data integrity", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Tool data integrity test", False, f"Error: {e}")
        
        # Test 2: Verify created chemicals exist
        if self.created_items['chemicals']:
            try:
                response = self.session.get(f"{API_BASE}/chemicals", headers=self.get_headers())
                if response.status_code == 200:
                    chemicals = response.json().get('chemicals', [])
                    created_chemical_found = any(chem['id'] in self.created_items['chemicals'] for chem in chemicals)
                    self.log_test("Created chemical data integrity",
                                 created_chemical_found,
                                 "Found created chemical in list")
                else:
                    self.log_test("Chemical data integrity", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Chemical data integrity test", False, f"Error: {e}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 CLEANING UP TEST DATA")
        
        # Clean up tools
        for tool_id in self.created_items['tools']:
            try:
                response = self.session.delete(f"{API_BASE}/tools/{tool_id}", 
                                             headers=self.get_headers())
                if response.status_code in [200, 204]:
                    print(f"    ✅ Deleted tool {tool_id}")
                else:
                    print(f"    ⚠️ Could not delete tool {tool_id}: {response.status_code}")
            except Exception as e:
                print(f"    ❌ Error deleting tool {tool_id}: {e}")
        
        # Clean up chemicals
        for chemical_id in self.created_items['chemicals']:
            try:
                response = self.session.delete(f"{API_BASE}/chemicals/{chemical_id}", 
                                             headers=self.get_headers())
                if response.status_code in [200, 204]:
                    print(f"    ✅ Deleted chemical {chemical_id}")
                else:
                    print(f"    ⚠️ Could not delete chemical {chemical_id}: {response.status_code}")
            except Exception as e:
                print(f"    ❌ Error deleting chemical {chemical_id}: {e}")
    
    def run_all_tests(self):
        """Run all functionality tests"""
        print("📋 SUPPLYLINE MRO SUITE - FUNCTIONALITY TESTING")
        print("=" * 50)

        # Authenticate once at the beginning
        if not self.authenticate():
            print("❌ Admin authentication failed – aborting test run")
            sys.exit(1)

        self.test_user_authentication_workflows()
        self.test_tool_management_workflows()
        self.test_chemical_management_workflows()
        self.test_dashboard_workflows()
        self.test_admin_workflows()
        self.test_data_integrity()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n📊 FUNCTIONALITY TEST SUMMARY")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL FUNCTIONALITY TESTS PASSED!")
            return True

        print("⚠️  SOME FUNCTIONALITY TESTS FAILED")
        failed_tests = [r for r in self.test_results if not r['passed']]
        for test in failed_tests:
            print(f"   ❌ {test['test']}: {test['details']}")
        return False

if __name__ == "__main__":
    tester = FunctionalityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
