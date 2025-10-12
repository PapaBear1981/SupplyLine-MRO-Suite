"""
Simple API test script for Mobile Warehouse/Kits system
Run this to verify the backend APIs are working correctly

Usage:
    python test_kits_api.py

Requirements:
    - Backend server must be running
    - Valid JWT token required
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# You'll need to get a valid JWT token by logging in first
# Replace this with your actual token
JWT_TOKEN = None


def get_headers():
    """Get headers with JWT token"""
    if not JWT_TOKEN:
        print("❌ ERROR: JWT_TOKEN not set. Please login first and set the token.")
        print("\nTo get a token:")
        print("1. Login via the UI or POST to /api/auth/login")
        print("2. Copy the access_token from the response")
        print("3. Set JWT_TOKEN variable in this script")
        return None
    
    return {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }


def test_aircraft_types():
    """Test aircraft types endpoint"""
    print("\n" + "="*60)
    print("Testing Aircraft Types API")
    print("="*60)
    
    headers = get_headers()
    if not headers:
        return False
    
    # GET aircraft types
    print("\n1. GET /api/aircraft-types")
    response = requests.get(f"{API_BASE}/aircraft-types", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {len(data.get('aircraft_types', []))} aircraft types")
        for at in data.get('aircraft_types', []):
            print(f"      - {at['name']}: {at['description']}")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False


def test_kits():
    """Test kits endpoint"""
    print("\n" + "="*60)
    print("Testing Kits API")
    print("="*60)
    
    headers = get_headers()
    if not headers:
        return False
    
    # GET kits
    print("\n1. GET /api/kits")
    response = requests.get(f"{API_BASE}/kits", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {data.get('total', 0)} kits")
        for kit in data.get('kits', [])[:3]:  # Show first 3
            print(f"      - {kit['name']} ({kit['aircraft_type']['name']})")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False


def test_create_kit():
    """Test creating a kit"""
    print("\n" + "="*60)
    print("Testing Kit Creation")
    print("="*60)
    
    headers = get_headers()
    if not headers:
        return False
    
    # First get an aircraft type ID
    response = requests.get(f"{API_BASE}/aircraft-types", headers=headers)
    if response.status_code != 200:
        print("   ❌ Cannot get aircraft types")
        return False
    
    aircraft_types = response.json().get('aircraft_types', [])
    if not aircraft_types:
        print("   ❌ No aircraft types available")
        return False
    
    aircraft_type_id = aircraft_types[0]['id']
    
    # Create a test kit
    print(f"\n1. POST /api/kits (Test Kit)")
    test_kit = {
        "name": f"Test Kit {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "aircraft_type_id": aircraft_type_id,
        "description": "Automated test kit",
        "status": "active"
    }
    
    response = requests.post(
        f"{API_BASE}/kits",
        headers=headers,
        json=test_kit
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        kit_id = data['kit']['id']
        print(f"   ✅ Created kit ID: {kit_id}")
        print(f"      Name: {data['kit']['name']}")
        return kit_id
    else:
        print(f"   ❌ Error: {response.text}")
        return None


def test_kit_boxes(kit_id):
    """Test kit boxes endpoint"""
    print("\n" + "="*60)
    print("Testing Kit Boxes API")
    print("="*60)
    
    headers = get_headers()
    if not headers:
        return False
    
    # Add a box
    print(f"\n1. POST /api/kits/{kit_id}/boxes")
    test_box = {
        "box_number": "Box1",
        "box_type": "tooling",
        "description": "Test tooling box"
    }
    
    response = requests.post(
        f"{API_BASE}/kits/{kit_id}/boxes",
        headers=headers,
        json=test_box
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✅ Created box: {data['box']['box_number']}")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False


def test_kit_analytics(kit_id):
    """Test kit analytics endpoint"""
    print("\n" + "="*60)
    print("Testing Kit Analytics API")
    print("="*60)
    
    headers = get_headers()
    if not headers:
        return False
    
    print(f"\n1. GET /api/kits/{kit_id}/analytics")
    response = requests.get(f"{API_BASE}/kits/{kit_id}/analytics", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Analytics retrieved")
        print(f"      Total Items: {data.get('total_items', 0)}")
        print(f"      Total Issuances: {data.get('total_issuances', 0)}")
        print(f"      Total Transfers: {data.get('total_transfers', 0)}")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("MOBILE WAREHOUSE/KITS API TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not JWT_TOKEN:
        print("\n❌ CANNOT RUN TESTS: JWT_TOKEN not set")
        print("\nPlease:")
        print("1. Start the backend server: python backend/app.py")
        print("2. Login to get a JWT token")
        print("3. Set JWT_TOKEN in this script")
        print("4. Run this script again")
        return
    
    results = []
    
    # Test 1: Aircraft Types
    results.append(("Aircraft Types", test_aircraft_types()))
    
    # Test 2: Kits List
    results.append(("Kits List", test_kits()))
    
    # Test 3: Create Kit
    kit_id = test_create_kit()
    results.append(("Create Kit", kit_id is not None))
    
    if kit_id:
        # Test 4: Kit Boxes
        results.append(("Kit Boxes", test_kit_boxes(kit_id)))
        
        # Test 5: Kit Analytics
        results.append(("Kit Analytics", test_kit_analytics(kit_id)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()

