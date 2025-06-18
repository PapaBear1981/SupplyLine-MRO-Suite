#!/usr/bin/env python3
"""
Test script to check if the API endpoints are working properly.
This will help us determine if the database migration was successful.
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://supplylinemrosuite-454313121816.us-west1.run.app"

def test_login():
    """Test login functionality"""
    print("Testing login...")

    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            timeout=30
        )

        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text[:200]}...")

        if response.status_code == 200:
            # Extract JWT token from response
            response_data = response.json()
            jwt_token = response_data.get('token')
            session_cookie = response.cookies.get('session')

            print(f"JWT token: {jwt_token[:50] if jwt_token else 'None'}...")
            print(f"Session cookie: {session_cookie}")

            return jwt_token, session_cookie
        else:
            print(f"Login failed with status {response.status_code}")
            return None, None

    except Exception as e:
        print(f"Login error: {e}")
        return None, None

def test_endpoints_without_auth():
    """Test the problematic endpoints without authentication to see error types"""
    endpoints = [
        "/api/checkouts/overdue",
        "/api/checkouts/user", 
        "/api/user/activity",
        "/api/announcements"
    ]
    
    print("\nTesting endpoints without authentication:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            print(f"{endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_endpoints_with_auth(jwt_token, session_cookie):
    """Test endpoints with authentication"""
    if not jwt_token and not session_cookie:
        print("No authentication available, skipping authenticated tests")
        return

    endpoints = [
        "/api/checkouts/overdue",
        "/api/checkouts/user",
        "/api/user/activity",
        "/api/announcements"
    ]

    print(f"\nTesting endpoints with authentication:")

    # Prepare headers and cookies
    headers = {}
    cookies = {}

    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    if session_cookie:
        cookies['session'] = session_cookie

    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{BACKEND_URL}{endpoint}",
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            print(f"{endpoint}: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

def test_migration_endpoint(jwt_token, session_cookie):
    """Test the migration endpoint"""
    if not jwt_token and not session_cookie:
        print("No authentication available, skipping migration test")
        return

    print(f"\nTesting migration endpoint:")

    headers = {}
    cookies = {}

    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    if session_cookie:
        cookies['session'] = session_cookie

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/admin/migrate-database",
            headers=headers,
            cookies=cookies,
            timeout=60
        )
        print(f"Migration endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Migration endpoint ERROR: {e}")

def main():
    print("=== API Endpoint Testing ===")
    print(f"Backend URL: {BACKEND_URL}")

    # Test endpoints without authentication first
    test_endpoints_without_auth()

    # Try to login
    jwt_token, session_cookie = test_login()

    # Test endpoints with authentication
    test_endpoints_with_auth(jwt_token, session_cookie)

    # Test migration endpoint
    test_migration_endpoint(jwt_token, session_cookie)

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
