#!/usr/bin/env python3
"""
Performance Test Script for SupplyLine MRO Suite

Tests API endpoint response times to verify pre-deployment optimizations.
"""

import requests
import time
import json
import sys
from datetime import datetime

# Disable SSL warnings for local testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_CREDENTIALS = {
    "employee_number": "ADMIN001",
    "password": "Yxqs5AMldhs-9PzjktSVqg"  # Generated admin password from init
}

def measure_response_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        return result, duration_ms
    return wrapper

@measure_response_time
def test_endpoint(session, endpoint, method='GET', data=None):
    """Test an API endpoint and return response and timing"""
    url = f"{BASE_URL}{endpoint}"

    # Use timeout to prevent hanging
    timeout = 10

    if method == 'GET':
        response = session.get(url, timeout=timeout)
    elif method == 'POST':
        response = session.post(url, json=data, timeout=timeout)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return response

def login_and_get_session():
    """Login and return authenticated session with JWT token"""
    session = requests.Session()

    # Login
    login_response = session.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS)

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return None

    # Get JWT token from response
    try:
        login_data = login_response.json()
        token = login_data.get('token')

        if token:
            # Set Authorization header for all future requests
            session.headers.update({'Authorization': f'Bearer {token}'})
            print("✅ Login successful - JWT token received")
            return session
        else:
            print("⚠️  Login successful but no JWT token in response")
            print(f"Response data keys: {list(login_data.keys())}")
            return None

    except Exception as e:
        print(f"Error parsing login response: {e}")
        return None

def run_performance_tests():
    """Run performance tests on critical API endpoints"""
    print("🚀 Starting Performance Tests")
    print("=" * 50)
    
    # Login first
    session = login_and_get_session()
    if not session:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Test endpoints that were slow in the original issue
    test_endpoints = [
        ("/api/health", "GET"),
        ("/api/tools", "GET"),
        ("/api/chemicals", "GET"),
        ("/api/checkouts", "GET"),
        ("/api/users", "GET"),
        ("/api/announcements", "GET"),
        ("/api/admin/dashboard/stats", "GET"),
        ("/api/cycle-count/schedules", "GET"),  # Test the fixed endpoint
    ]
    
    results = []
    total_tests = len(test_endpoints)
    passed_tests = 0
    
    print(f"\nTesting {total_tests} endpoints...")
    print("-" * 50)
    
    for endpoint, method in test_endpoints:
        try:
            response, duration_ms = test_endpoint(session, endpoint, method)
            
            # Determine status
            if response.status_code == 200:
                if duration_ms < 500:  # Target: < 500ms
                    status = "✅ EXCELLENT"
                    passed_tests += 1
                elif duration_ms < 1000:  # Acceptable: < 1000ms
                    status = "✅ GOOD"
                    passed_tests += 1
                elif duration_ms < 2000:  # Improved but not ideal
                    status = "⚠️  IMPROVED"
                else:
                    status = "❌ STILL SLOW"
            else:
                status = f"❌ ERROR ({response.status_code})"
            
            results.append({
                'endpoint': endpoint,
                'method': method,
                'duration_ms': duration_ms,
                'status_code': response.status_code,
                'status': status
            })
            
            print(f"{endpoint:<30} {duration_ms:>8.1f}ms  {status}")
            
        except Exception as e:
            print(f"{endpoint:<30} {'ERROR':>8}     ❌ {str(e)}")
            results.append({
                'endpoint': endpoint,
                'method': method,
                'duration_ms': None,
                'status_code': None,
                'status': f"❌ ERROR: {str(e)}"
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 50)
    
    avg_time = sum(r['duration_ms'] for r in results if r['duration_ms']) / len([r for r in results if r['duration_ms']])
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Average Response Time: {avg_time:.1f}ms")
    print(f"Target: <500ms | Acceptable: <1000ms")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for result in results:
        if result['duration_ms']:
            print(f"  {result['endpoint']}: {result['duration_ms']:.1f}ms ({result['status_code']})")
        else:
            print(f"  {result['endpoint']}: {result['status']}")
    
    # Overall assessment
    if passed_tests == total_tests and avg_time < 500:
        print("\n🎉 EXCELLENT: All tests passed with optimal performance!")
        return True
    elif passed_tests >= total_tests * 0.8 and avg_time < 1000:
        print("\n✅ GOOD: Most tests passed with acceptable performance!")
        return True
    else:
        print("\n⚠️  NEEDS IMPROVEMENT: Some endpoints still need optimization")
        return False

if __name__ == "__main__":
    print(f"Performance Test Started: {datetime.now()}")
    success = run_performance_tests()
    print(f"\nPerformance Test Completed: {datetime.now()}")
    
    if success:
        print("\n🚀 Ready for deployment!")
        sys.exit(0)
    else:
        print("\n⚠️  Additional optimization needed")
        sys.exit(1)
