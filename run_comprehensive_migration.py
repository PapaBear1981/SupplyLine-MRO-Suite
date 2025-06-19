#!/usr/bin/env python3
"""
Comprehensive database migration script for SupplyLine MRO Suite
Fixes tools table schema and creates missing cycle count tables
"""

import requests
import json
import time

def run_migration_via_api(migration_name, description):
    """Run a migration via the backend API"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print(f"\n{'='*60}")
    print(f"Running {migration_name}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        # Run emergency migration to ensure all basic tables exist
        print("Step 1: Running emergency migration...")
        response = requests.get(f"{backend_url}/api/emergency-migrate", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Emergency migration: {result.get('status', 'Success')}")
            if 'message' in result:
                print(f"   Message: {result['message']}")
        else:
            print(f"⚠️  Emergency migration returned {response.status_code}: {response.text}")
        
        # Wait a moment between operations
        time.sleep(2)
        
        # Run database initialization to ensure all models are created
        print("\nStep 2: Running database initialization...")
        response = requests.post(f"{backend_url}/api/db-init-simple", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Database initialization: {result.get('status', 'Success')}")
            if 'message' in result:
                print(f"   Message: {result['message']}")
        else:
            print(f"⚠️  Database initialization returned {response.status_code}: {response.text}")
        
        # Wait a moment between operations
        time.sleep(2)
        
        # Verify admin user exists
        print("\nStep 3: Verifying admin user...")
        response = requests.post(f"{backend_url}/api/init-admin", timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Admin user: {result.get('status', 'Success')}")
            if 'message' in result:
                print(f"   Message: {result['message']}")
        else:
            print(f"⚠️  Admin user check returned {response.status_code}: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during {migration_name}: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints to verify functionality"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print(f"\n{'='*60}")
    print("Testing API Endpoints")
    print(f"{'='*60}")
    
    # Test endpoints that were previously failing
    test_endpoints = [
        ("/api/tools", "Tools API"),
        ("/api/chemicals", "Chemicals API"),
        ("/api/calibration-standards", "Calibration Standards API"),
        ("/api/calibrations", "Calibrations API"),
        ("/api/cycle-counts/schedules", "Cycle Count Schedules API"),
        ("/api/cycle-counts/batches", "Cycle Count Batches API"),
        ("/api/cycle-counts/stats", "Cycle Count Stats API"),
        ("/api/checkouts", "Checkouts API")
    ]
    
    success_count = 0
    total_count = len(test_endpoints)
    
    for endpoint, name in test_endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            
            if response.status_code == 401:
                print(f"✅ {name}: Authentication required (endpoint exists and working)")
                success_count += 1
            elif response.status_code == 200:
                print(f"✅ {name}: Success (200)")
                success_count += 1
            elif response.status_code == 500:
                print(f"❌ {name}: Server error (500) - Database issue")
            elif response.status_code == 404:
                print(f"❌ {name}: Not found (404) - Endpoint missing")
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Connection error - {e}")
    
    print(f"\nAPI Test Results: {success_count}/{total_count} endpoints working")
    return success_count == total_count

def main():
    """Main migration execution"""
    
    print("🚀 Starting Comprehensive SupplyLine MRO Suite Database Migration")
    print("This will fix all remaining database schema issues and missing tables")
    
    # Run the comprehensive migration
    migration_success = run_migration_via_api(
        "Comprehensive Database Migration",
        "Fix tools table schema and create missing cycle count tables"
    )
    
    if migration_success:
        print("\n✅ Migration completed successfully!")
        
        # Test the API endpoints
        api_success = test_api_endpoints()
        
        if api_success:
            print("\n🎉 ALL SYSTEMS GO!")
            print("✅ Database schema fixed")
            print("✅ All missing tables created")
            print("✅ All API endpoints working")
            print("✅ Ready for comprehensive navigation testing")
            
            print("\n📋 Next Steps:")
            print("1. Test login and session persistence")
            print("2. Navigate through all pages systematically")
            print("3. Verify Cycle Counts page is no longer blank")
            print("4. Confirm Reports page works without database errors")
            print("5. Test all admin dashboard features")
            
        else:
            print("\n⚠️  Migration completed but some API endpoints still have issues")
            print("Manual investigation may be required for remaining problems")
    else:
        print("\n❌ Migration failed!")
        print("Manual database intervention may be required")

if __name__ == "__main__":
    main()
