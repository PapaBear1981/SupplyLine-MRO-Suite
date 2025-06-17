#!/usr/bin/env python3
"""
Performance Testing Suite for SupplyLine MRO Suite
Tests response times, load handling, and database performance
"""

import requests
import time
import threading
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

class PerformanceTester:
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
        """Authenticate to get session token"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", 
                json={"employee_number": "ADMIN001", "password": "admin123"})
            if response.status_code == 200:
                self.auth_token = response.json().get('token')
                return True
        except Exception as e:
            print(f"Authentication failed: {e}")
        return False
    
    def measure_response_time(self, url, method='GET', data=None, headers=None):
        """Measure response time for a single request"""
        start_time = time.time()
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                'response_time': response_time,
                'status_code': response.status_code,
                'success': response.status_code < 400
            }
        except Exception as e:
            end_time = time.time()
            return {
                'response_time': (end_time - start_time) * 1000,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
    
    def test_api_response_times(self):
        """Test API endpoint response times"""
        print("\n⚡ API RESPONSE TIME TESTS")
        
        if not self.authenticate():
            self.log_test("Authentication for performance tests", False, "Could not authenticate")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test endpoints with target response times
        endpoints = [
            (f"{API_BASE}/auth/session-info", "GET", None, 500, "Authentication"),
            (f"{API_BASE}/tools", "GET", None, 300, "Tool operations"),
            (f"{API_BASE}/chemicals", "GET", None, 300, "Chemical operations"),
            (f"{API_BASE}/user/activity", "GET", None, 500, "User activity"),
        ]
        
        for url, method, data, target_ms, description in endpoints:
            result = self.measure_response_time(url, method, data, headers)
            
            if result['success']:
                passed = result['response_time'] <= target_ms
                self.log_test(f"{description} response time", passed,
                             f"{result['response_time']:.1f}ms (target: {target_ms}ms)")
            else:
                self.log_test(f"{description} response time", False,
                             f"Request failed: {result.get('error', 'Unknown error')}")
    
    def test_concurrent_users(self, num_users=10):
        """Test concurrent user load"""
        print(f"\n👥 CONCURRENT USERS TEST ({num_users} users)")
        
        def simulate_user():
            """Simulate a single user session"""
            session = requests.Session()
            results = []
            
            # Login
            login_result = self.measure_response_time(
                f"{API_BASE}/auth/login", 
                'POST', 
                {"employee_number": "ADMIN001", "password": "admin123"}
            )
            results.append(login_result)
            
            if login_result['success']:
                # Simulate user activities
                activities = [
                    f"{API_BASE}/auth/session-info",
                    f"{API_BASE}/tools",
                    f"{API_BASE}/chemicals",
                ]
                
                for url in activities:
                    result = self.measure_response_time(url)
                    results.append(result)
            
            return results
        
        # Run concurrent user simulations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(simulate_user) for _ in range(num_users)]
            all_results = []
            
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"User simulation failed: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_requests = [r for r in all_results if r['success']]
        failed_requests = [r for r in all_results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            success_rate = len(successful_requests) / len(all_results) * 100
            
            self.log_test(f"Concurrent users ({num_users}) handled", 
                         success_rate >= 95,
                         f"Success rate: {success_rate:.1f}%, Avg response: {avg_response_time:.1f}ms")
            
            self.log_test(f"Response times under load acceptable", 
                         avg_response_time <= 2000,
                         f"Avg: {avg_response_time:.1f}ms, Max: {max_response_time:.1f}ms")
        else:
            self.log_test(f"Concurrent users test", False, "All requests failed")
    
    def test_database_performance(self):
        """Test database performance"""
        print("\n🗄️ DATABASE PERFORMANCE TESTS")
        
        if not self.auth_token:
            if not self.authenticate():
                self.log_test("Database performance tests", False, "Authentication failed")
                return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test database-heavy operations
        db_operations = [
            (f"{API_BASE}/tools", "Tools query"),
            (f"{API_BASE}/chemicals", "Chemicals query"),
            (f"{API_BASE}/user/activity", "Activity query"),
            (f"{API_BASE}/audit/logs", "Audit logs query"),
        ]
        
        for url, description in db_operations:
            # Run multiple times to get average
            times = []
            for _ in range(5):
                result = self.measure_response_time(url, headers=headers)
                if result['success']:
                    times.append(result['response_time'])
            
            if times:
                avg_time = statistics.mean(times)
                self.log_test(f"{description} performance", 
                             avg_time <= 1000,
                             f"Average: {avg_time:.1f}ms over 5 requests")
            else:
                self.log_test(f"{description} performance", False, "All requests failed")
    
    def test_memory_usage(self):
        """Test for memory leaks by making repeated requests"""
        print("\n🧠 MEMORY USAGE TEST")
        
        if not self.auth_token:
            if not self.authenticate():
                self.log_test("Memory usage test", False, "Authentication failed")
                return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Make many requests to check for memory leaks
        num_requests = 50
        response_times = []
        
        for i in range(num_requests):
            result = self.measure_response_time(f"{API_BASE}/tools", headers=headers)
            if result['success']:
                response_times.append(result['response_time'])
        
        if len(response_times) >= num_requests * 0.8:  # At least 80% success
            # Check if response times are increasing (potential memory leak)
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            
            # Response times shouldn't increase by more than 50%
            performance_degradation = (avg_second - avg_first) / avg_first * 100
            
            self.log_test("Memory usage stable", 
                         performance_degradation <= 50,
                         f"Performance change: {performance_degradation:.1f}%")
        else:
            self.log_test("Memory usage test", False, "Too many failed requests")
    
    def run_all_tests(self):
        """Run all performance tests"""
        print("⚡ SUPPLYLINE MRO SUITE - PERFORMANCE TESTING")
        print("=" * 50)
        
        self.test_api_response_times()
        self.test_concurrent_users(10)
        self.test_database_performance()
        self.test_memory_usage()
        
        # Summary
        print("\n📊 PERFORMANCE TEST SUMMARY")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL PERFORMANCE TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME PERFORMANCE TESTS FAILED")
            failed_tests = [r for r in self.test_results if not r['passed']]
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
            return False

if __name__ == "__main__":
    tester = PerformanceTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
