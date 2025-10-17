#!/usr/bin/env python3
"""
E2E Test Endpoint Verification Script

This script verifies that all API endpoints required by E2E tests are responding correctly.
It tests endpoints without authentication to ensure they return proper error codes,
and with authentication to ensure they return expected data.

Usage:
    python verify_e2e_endpoints.py
"""

import requests
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Base URL for the API
BASE_URL = 'http://localhost:5000/api'

# Test credentials
TEST_CREDENTIALS = {
    'admin': {'employee_number': 'ADMIN001', 'password': 'admin123'},
    'user': {'employee_number': 'USER001', 'password': 'user123'}
}

# Endpoints to test
ENDPOINTS_TO_TEST = [
    # Auth endpoints
    {'path': '/auth/login', 'method': 'POST', 'requires_auth': False, 'expected_status': [200, 400, 401]},
    {'path': '/auth/me', 'method': 'GET', 'requires_auth': True, 'expected_status': [200]},
    {'path': '/auth/logout', 'method': 'POST', 'requires_auth': True, 'expected_status': [200]},
    
    # Tools endpoints
    {'path': '/tools', 'method': 'GET', 'requires_auth': False, 'expected_status': [200]},
    {'path': '/tools/new', 'method': 'GET', 'requires_auth': True, 'expected_status': [200, 403]},
    
    # Checkouts endpoints
    {'path': '/checkouts', 'method': 'GET', 'requires_auth': False, 'expected_status': [200]},
    {'path': '/checkouts/user', 'method': 'GET', 'requires_auth': True, 'expected_status': [200]},
    
    # Kits endpoints
    {'path': '/kits', 'method': 'GET', 'requires_auth': False, 'expected_status': [200]},
    {'path': '/kits/aircraft-types', 'method': 'GET', 'requires_auth': False, 'expected_status': [200]},
    
    # Dashboard endpoints
    {'path': '/user/activity', 'method': 'GET', 'requires_auth': True, 'expected_status': [200]},
    
    # Admin endpoints (should fail for non-admin)
    {'path': '/admin/dashboard/stats', 'method': 'GET', 'requires_auth': True, 'expected_status': [200, 403]},
]


def login(credentials):
    """Login and return session cookies"""
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            json=credentials,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"✓ Login successful for {credentials['employee_number']}")
            return response.cookies
        else:
            logger.error(f"✗ Login failed for {credentials['employee_number']}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"✗ Login error for {credentials['employee_number']}: {str(e)}")
        return None


def test_endpoint(endpoint, cookies=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint['path']}"
    method = endpoint['method']
    expected_status = endpoint['expected_status']
    
    try:
        if method == 'GET':
            response = requests.get(url, cookies=cookies, timeout=5)
        elif method == 'POST':
            response = requests.post(url, cookies=cookies, timeout=5)
        else:
            logger.warning(f"⚠ Unsupported method {method} for {endpoint['path']}")
            return False
        
        if response.status_code in expected_status:
            logger.info(f"✓ {method} {endpoint['path']} - Status: {response.status_code}")
            return True
        else:
            logger.error(f"✗ {method} {endpoint['path']} - Expected: {expected_status}, Got: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ {method} {endpoint['path']} - Connection refused. Is the backend running?")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"✗ {method} {endpoint['path']} - Request timed out")
        return False
    except Exception as e:
        logger.error(f"✗ {method} {endpoint['path']} - Error: {str(e)}")
        return False


def main():
    """Main function to verify all endpoints"""
    logger.info("=" * 60)
    logger.info("E2E Test Endpoint Verification")
    logger.info("=" * 60)
    logger.info(f"Testing endpoints at: {BASE_URL}")
    logger.info("")
    
    # Test if backend is running
    try:
        response = requests.get(f'{BASE_URL}/auth/login', timeout=2)
        logger.info("✓ Backend is running")
    except requests.exceptions.ConnectionError:
        logger.error("✗ Backend is not running. Please start the backend server first.")
        logger.error("  Run: cd backend && python run.py")
        return False
    except Exception as e:
        logger.error(f"✗ Error connecting to backend: {str(e)}")
        return False
    
    logger.info("")
    logger.info("Testing endpoints without authentication...")
    logger.info("-" * 60)
    
    # Test endpoints without auth
    results_no_auth = []
    for endpoint in ENDPOINTS_TO_TEST:
        if not endpoint['requires_auth']:
            result = test_endpoint(endpoint)
            results_no_auth.append(result)
    
    logger.info("")
    logger.info("Testing endpoints with authentication...")
    logger.info("-" * 60)
    
    # Login as admin
    admin_cookies = login(TEST_CREDENTIALS['admin'])
    
    if not admin_cookies:
        logger.error("✗ Failed to login as admin. Cannot test authenticated endpoints.")
        logger.error("  Make sure test data is seeded: python backend/seed_e2e_test_data.py")
        return False
    
    # Test endpoints with auth
    results_with_auth = []
    for endpoint in ENDPOINTS_TO_TEST:
        if endpoint['requires_auth']:
            result = test_endpoint(endpoint, admin_cookies)
            results_with_auth.append(result)
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    
    total_tests = len(results_no_auth) + len(results_with_auth)
    passed_tests = sum(results_no_auth) + sum(results_with_auth)
    failed_tests = total_tests - passed_tests
    
    logger.info(f"Total endpoints tested: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {failed_tests}")
    
    if failed_tests == 0:
        logger.info("")
        logger.info("✓ All endpoints are responding correctly!")
        return True
    else:
        logger.error("")
        logger.error(f"✗ {failed_tests} endpoint(s) failed verification")
        logger.error("  Please check the backend logs and fix the failing endpoints")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

