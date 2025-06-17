#!/usr/bin/env python3
"""
Remote Database Initialization Script

This script calls the backend API to initialize the database remotely.
"""

import requests
import json
import sys

def init_database():
    """Initialize the database by calling the backend API."""
    
    backend_url = "https://supplyline-backend-production-sukn4msdrq-uc.a.run.app"
    
    print("Initializing database via backend API...")
    
    try:
        # First try the init-db endpoint
        print("Trying /api/init-db endpoint...")
        response = requests.post(f"{backend_url}/api/init-db", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Database initialization completed")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Init-db failed with status {response.status_code}: {response.text}")
            
            # Try the db-reset endpoint as fallback
            print("Trying /api/db-reset endpoint...")
            response = requests.post(f"{backend_url}/api/db-reset", timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print("SUCCESS: Database reset and initialization completed")
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"DB-reset failed with status {response.status_code}: {response.text}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response - {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        return False

def test_login():
    """Test login functionality after database initialization."""
    
    backend_url = "https://supplyline-backend-production-sukn4msdrq-uc.a.run.app"
    
    print("Testing login functionality...")
    
    try:
        login_data = {
            "employee_number": "ADMIN001",
            "password": "admin123"
        }
        
        response = requests.post(f"{backend_url}/api/login", json=login_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Login test passed")
            print(f"Login response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Login test failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Login test failed - {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("SupplyLine MRO Suite - Remote Database Initialization")
    print("=" * 60)
    
    # Initialize database
    if init_database():
        print("\nDatabase initialization successful!")
        
        # Test login
        print("\n" + "-" * 40)
        if test_login():
            print("\nAll tests passed! The application should now be working.")
        else:
            print("\nDatabase initialized but login test failed.")
            print("You may need to check the admin user creation.")
    else:
        print("\nDatabase initialization failed!")
        print("Please check the backend logs for more details.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Database initialization process completed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
