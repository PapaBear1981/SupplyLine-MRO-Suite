#!/usr/bin/env python3
"""
Performance and Load Testing for SupplyLine MRO Suite
Tests API response times, concurrent requests, and basic load handling
"""

import requests
import json
import time
import sys
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CREDENTIALS = {
    "employee_number": "ADMIN001",
    "password": "admin123"
}

class PerformanceTester:
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
    
    def authenticate(self):
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def measure_response_time(self, endpoint, method="GET", data=None):
        """Measure response time for a single request"""
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{BASE_URL}{endpoint}", json=data)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response_time,
                "size": len(response.content) if response.content else 0
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "response_time": 0,
                "size": 0,
                "error": str(e)
            }
    
    def test_api_response_times(self):
        """Test response times for various API endpoints"""
        endpoints = [
            "/api/health",
            "/api/tools",
            "/api/chemicals",
            "/api/checkouts",
            "/api/users",
            "/api/announcements",
            "/api/admin/dashboard/stats",
        ]
        
        print("Testing API response times...")
        results = {}
        
        for endpoint in endpoints:
            times = []
            for i in range(5):  # Test each endpoint 5 times
                result = self.measure_response_time(endpoint)
                if result["success"]:
                    times.append(result["response_time"])
                time.sleep(0.1)  # Small delay between requests
            
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                
                # Consider under 500ms as good, under 1000ms as acceptable
                success = avg_time < 1000
                details = f"Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms"
                
                results[endpoint] = {
                    "avg": avg_time,
                    "min": min_time,
                    "max": max_time,
                    "success": success
                }
                
                self.log_test(f"Response Time: {endpoint}", success, details)
            else:
                self.log_test(f"Response Time: {endpoint}", False, "No successful responses")
                results[endpoint] = {"success": False}
        
        # Overall assessment
        successful_endpoints = sum(1 for r in results.values() if r.get("success", False))
        total_endpoints = len(endpoints)
        overall_success = successful_endpoints >= total_endpoints * 0.8  # 80% success rate
        
        self.log_test("Overall API Response Times", overall_success, 
                     f"{successful_endpoints}/{total_endpoints} endpoints under 1000ms")
        
        return overall_success
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("Testing concurrent request handling...")
        
        def make_request():
            return self.measure_response_time("/api/tools")
        
        # Test with different concurrency levels
        concurrency_levels = [5, 10, 20]
        results = {}
        
        for concurrency in concurrency_levels:
            print(f"  Testing {concurrency} concurrent requests...")
            
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrency)]
                responses = [future.result() for future in as_completed(futures)]
            end_time = time.time()
            
            successful_requests = sum(1 for r in responses if r["success"])
            total_time = (end_time - start_time) * 1000
            avg_response_time = statistics.mean([r["response_time"] for r in responses if r["success"]])
            
            success_rate = successful_requests / concurrency
            success = success_rate >= 0.9 and avg_response_time < 2000  # 90% success, under 2s
            
            details = f"Success: {successful_requests}/{concurrency} ({success_rate:.1%}), " \
                     f"Avg time: {avg_response_time:.1f}ms, Total: {total_time:.1f}ms"
            
            results[concurrency] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_time": total_time,
                "success": success
            }
            
            self.log_test(f"Concurrent Requests ({concurrency})", success, details)
        
        # Overall assessment
        overall_success = all(r["success"] for r in results.values())
        self.log_test("Overall Concurrent Request Handling", overall_success,
                     f"All concurrency levels handled successfully: {overall_success}")
        
        return overall_success
    
    def test_memory_usage_simulation(self):
        """Simulate memory usage with repeated requests"""
        print("Testing memory usage with repeated requests...")
        
        # Make 100 requests to simulate sustained load
        request_count = 100
        successful_requests = 0
        response_times = []
        
        start_time = time.time()
        
        for i in range(request_count):
            result = self.measure_response_time("/api/tools")
            if result["success"]:
                successful_requests += 1
                response_times.append(result["response_time"])
            
            if i % 20 == 0:
                print(f"  Completed {i}/{request_count} requests...")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            # Check if response times are stable (not increasing significantly)
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            
            first_avg = statistics.mean(first_half) if first_half else 0
            second_avg = statistics.mean(second_half) if second_half else 0
            
            # Response time shouldn't increase by more than 50%
            performance_degradation = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
            
            success_rate = successful_requests / request_count
            success = success_rate >= 0.95 and performance_degradation < 0.5
            
            details = f"Success: {successful_requests}/{request_count} ({success_rate:.1%}), " \
                     f"Avg time: {avg_response_time:.1f}ms, " \
                     f"Performance change: {performance_degradation:.1%}"
            
            self.log_test("Memory Usage Simulation", success, details)
            return success
        else:
            self.log_test("Memory Usage Simulation", False, "No successful requests")
            return False
    
    def test_database_performance(self):
        """Test database query performance"""
        print("Testing database performance...")
        
        # Test endpoints that involve database queries
        db_endpoints = [
            "/api/tools",
            "/api/users", 
            "/api/checkouts",
            "/api/admin/dashboard/stats"
        ]
        
        results = []
        
        for endpoint in db_endpoints:
            # Make multiple requests to test consistency
            times = []
            for _ in range(10):
                result = self.measure_response_time(endpoint)
                if result["success"]:
                    times.append(result["response_time"])
                time.sleep(0.05)
            
            if times:
                avg_time = statistics.mean(times)
                std_dev = statistics.stdev(times) if len(times) > 1 else 0
                
                # Database queries should be fast and consistent
                success = avg_time < 500 and std_dev < 200
                details = f"Avg: {avg_time:.1f}ms, StdDev: {std_dev:.1f}ms"
                
                results.append(success)
                self.log_test(f"DB Performance: {endpoint}", success, details)
            else:
                results.append(False)
                self.log_test(f"DB Performance: {endpoint}", False, "No successful responses")
        
        overall_success = sum(results) >= len(results) * 0.75  # 75% success rate
        self.log_test("Overall Database Performance", overall_success,
                     f"{sum(results)}/{len(results)} endpoints performed well")
        
        return overall_success
    
    def run_all_performance_tests(self):
        """Run comprehensive performance test suite"""
        print("⚡ Starting Performance and Load Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot run performance tests")
            return False
        
        # Test sequence
        tests = [
            self.test_api_response_times,
            self.test_concurrent_requests,
            self.test_memory_usage_simulation,
            self.test_database_performance,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"⚡ Performance Test Results: {passed}/{total} test categories passed")
        
        if passed == total:
            print("🎉 All performance tests passed! Application performs well under load.")
            return True
        else:
            print("⚠️  Some performance tests failed. Review performance optimizations.")
            return False

def main():
    """Main test execution"""
    tester = PerformanceTester()
    success = tester.run_all_performance_tests()
    
    # Save detailed results
    with open('performance_test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_success": success,
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to performance_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
