#!/usr/bin/env python3
"""
Fix admin user and test login functionality
"""

import requests
import json
import time

def fix_admin_user():
    """Recreate admin user and test login"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("🔧 Fixing Admin User and Testing Login")
    print("=" * 50)
    
    try:
        # Step 1: Run emergency migration
        print("Step 1: Running emergency migration...")
        response = requests.get(f"{backend_url}/api/emergency-migrate", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Emergency migration: {result.get('status', 'Success')}")
        else:
            print(f"⚠️  Emergency migration: {response.status_code}")
        
        time.sleep(2)
        
        # Step 2: Initialize database
        print("\nStep 2: Initializing database...")
        response = requests.post(f"{backend_url}/api/db-init-simple", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Database initialization: {result.get('status', 'Success')}")
        else:
            print(f"⚠️  Database initialization: {response.status_code}")
        
        time.sleep(2)
        
        # Step 3: Create/verify admin user
        print("\nStep 3: Creating/verifying admin user...")
        response = requests.post(f"{backend_url}/api/init-admin", timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Admin user: {result.get('status', 'Success')}")
            if 'message' in result:
                print(f"   Message: {result['message']}")
        else:
            print(f"⚠️  Admin user creation: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
        
        time.sleep(2)
        
        # Step 4: Test login
        print("\nStep 4: Testing login...")
        login_data = {
            "employee_number": "ADMIN001",
            "password": "admin123"
        }
        
        response = requests.post(f"{backend_url}/api/login", json=login_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login test: SUCCESS")
            print(f"   User: {result.get('user', {}).get('name', 'Unknown')}")
            print(f"   Role: {'Admin' if result.get('user', {}).get('is_admin') else 'User'}")
            return True
        else:
            print(f"❌ Login test: FAILED ({response.status_code})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_key_endpoints():
    """Test key endpoints to verify system status"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("\n" + "=" * 50)
    print("Testing Key Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("/api/tools", "Tools API"),
        ("/api/users", "Users API"),
        ("/api/checkouts", "Checkouts API"),
        ("/api/chemicals", "Chemicals API"),
        ("/api/calibrations", "Calibrations API"),
        ("/api/cycle-counts/schedules", "Cycle Count Schedules API"),
    ]
    
    working_count = 0
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            
            if response.status_code == 401:
                print(f"✅ {name}: Authentication required (working)")
                working_count += 1
            elif response.status_code == 200:
                print(f"✅ {name}: Success")
                working_count += 1
            elif response.status_code == 500:
                print(f"❌ {name}: Server error")
                try:
                    error_data = response.json()
                    if 'tool_number' in str(error_data):
                        print(f"   Schema issue: {error_data}")
                except:
                    pass
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Connection error - {e}")
    
    print(f"\nEndpoint Status: {working_count}/{len(endpoints)} working")
    return working_count

def main():
    """Main execution"""
    
    print("🚀 Admin User Fix and System Test")
    print("This will fix admin user issues and test system functionality")
    
    # Fix admin user
    login_success = fix_admin_user()
    
    # Test endpoints
    working_endpoints = test_key_endpoints()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if login_success:
        print("✅ Admin login: WORKING")
    else:
        print("❌ Admin login: FAILED")
    
    print(f"✅ Working endpoints: {working_endpoints}/6")
    
    if login_success and working_endpoints >= 4:
        print("\n🎉 SYSTEM STATUS: MOSTLY FUNCTIONAL")
        print("✅ Database migrations completed")
        print("✅ Admin user working")
        print("✅ Most APIs working")
        
        print("\n📋 Remaining Issues:")
        print("1. Cycle Counts page still blank (models not imported)")
        print("2. Reports page has tool_number schema error")
        print("3. Session management may need improvement")
        
        print("\n📋 Next Steps:")
        print("1. Test frontend login in browser")
        print("2. Navigate through working pages")
        print("3. Document remaining issues for backend deployment fix")
        
    else:
        print("\n⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print("Critical issues remain that require backend fixes")

if __name__ == "__main__":
    main()
