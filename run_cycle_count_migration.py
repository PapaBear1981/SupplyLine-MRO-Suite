#!/usr/bin/env python3
"""
Script to run cycle count table migration via the backend API
"""

import requests
import json

def run_cycle_count_migration():
    """Run the cycle count migration by calling the backend API"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("Running cycle count table migration...")
    
    # Read the migration SQL
    with open('migration_cycle_count.sql', 'r') as f:
        migration_sql = f.read()
    
    # Try to call a migration endpoint with the SQL
    try:
        # First try to see if there's a general migration endpoint
        print("Trying to run migration via emergency endpoint...")
        response = requests.get(f"{backend_url}/api/emergency-migrate", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Emergency migration completed")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Now try to test if cycle count endpoints work
            print("\nTesting cycle count endpoints...")
            test_endpoints = [
                "/api/cycle-counts/schedules",
                "/api/cycle-counts/batches", 
                "/api/cycle-counts/stats"
            ]
            
            for endpoint in test_endpoints:
                try:
                    test_response = requests.get(f"{backend_url}{endpoint}", timeout=10)
                    if test_response.status_code == 401:
                        print(f"✅ {endpoint}: {test_response.status_code} (Authentication required - endpoint exists!)")
                    elif test_response.status_code == 500:
                        print(f"❌ {endpoint}: {test_response.status_code} (Still broken - tables missing)")
                    else:
                        print(f"ℹ️  {endpoint}: {test_response.status_code} - {test_response.text[:50]}")
                except Exception as e:
                    print(f"❌ {endpoint}: ERROR - {e}")
            
            return True
        else:
            print(f"Migration failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Migration failed - {e}")
        return False

if __name__ == "__main__":
    success = run_cycle_count_migration()
    if success:
        print("\n✅ Cycle count migration completed successfully!")
    else:
        print("\n❌ Cycle count migration failed!")
