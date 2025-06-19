#!/usr/bin/env python3
"""
Test database initialization endpoints
"""

import requests
import json

def test_db_init():
    """Test database initialization endpoints"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("Testing database initialization endpoints...")
    
    endpoints = [
        ("/api/db-init-simple", "POST"),
        ("/api/init-db", "POST"),
        ("/api/db-reset", "POST")
    ]
    
    for endpoint, method in endpoints:
        try:
            print(f"\nTrying {method} {endpoint}...")
            if method == "POST":
                response = requests.post(f"{backend_url}{endpoint}", timeout=60)
            else:
                response = requests.get(f"{backend_url}{endpoint}", timeout=60)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"SUCCESS: {json.dumps(result, indent=2)}")
                except:
                    print(f"Response: {response.text}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_db_init()
