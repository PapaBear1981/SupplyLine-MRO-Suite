#!/usr/bin/env python3
"""
Test Database Connection Script

This script tests the database connection directly using the correct parameters.
"""

import requests
import json
import sys

def test_db_connection():
    """Test database connection by calling a simple endpoint."""
    
    backend_url = "https://supplyline-backend-test-454313121816.us-west1.run.app"
    
    print("Testing database connection...")
    
    try:
        # Test the health endpoint first
        print("1. Testing health endpoint...")
        response = requests.get(f"{backend_url}/api/health", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Health check passed: {result}")
        else:
            print(f"✗ Health check failed: {response.status_code} - {response.text}")
            return False
        
        # Test the debug environment endpoint
        print("\n2. Testing debug environment endpoint...")
        response = requests.get(f"{backend_url}/api/debug/env", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Environment debug successful:")
            print(json.dumps(result, indent=2))
        else:
            print(f"✗ Environment debug failed: {response.status_code} - {response.text}")
        
        # Test the database inspection endpoint
        print("\n3. Testing database inspection endpoint...")
        response = requests.get(f"{backend_url}/api/db-inspect", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Database inspection successful:")
            print(json.dumps(result, indent=2))
        else:
            print(f"✗ Database inspection failed: {response.status_code} - {response.text}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response - {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("SupplyLine MRO Suite - Database Connection Test")
    print("=" * 60)
    
    if test_db_connection():
        print("\n✓ Database connection test completed successfully!")
    else:
        print("\n✗ Database connection test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test completed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
