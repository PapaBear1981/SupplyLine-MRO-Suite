#!/usr/bin/env python3
"""
Full database initialization
"""

import requests
import json

def full_db_init():
    """Run full database initialization"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("Running full database initialization...")
    
    # Try all initialization endpoints
    endpoints = [
        "/api/db-init-simple",
        "/api/init-db", 
        "/api/db-reset"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTrying POST {endpoint}...")
            response = requests.post(f"{backend_url}{endpoint}", timeout=120)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"SUCCESS: {json.dumps(result, indent=2)}")
                    
                    # If this endpoint succeeded, try to create admin user
                    if "success" in result.get("status", "").lower():
                        print("\nTrying to create admin user...")
                        admin_response = requests.post(f"{backend_url}/api/init-admin", timeout=60)
                        print(f"Admin creation status: {admin_response.status_code}")
                        if admin_response.status_code in [200, 201]:
                            admin_result = admin_response.json()
                            print(f"Admin creation: {json.dumps(admin_result, indent=2)}")
                        else:
                            print(f"Admin creation error: {admin_response.text}")
                    
                    return True
                except Exception as e:
                    print(f"Response parsing error: {e}")
                    print(f"Raw response: {response.text}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    return False

if __name__ == "__main__":
    success = full_db_init()
    if success:
        print("\n✅ Database initialization completed!")
    else:
        print("\n❌ Database initialization failed!")
