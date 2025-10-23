"""
Comprehensive test script for kit-to-kit transfers

Required environment variables:
- TEST_EMPLOYEE_NUMBER: Employee number for authentication
- TEST_PASSWORD: Password for authentication
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Login credentials from environment variables
LOGIN_DATA = {
    "employee_number": os.getenv("TEST_EMPLOYEE_NUMBER", ""),
    "password": os.getenv("TEST_PASSWORD", "")
}

if not LOGIN_DATA["employee_number"] or not LOGIN_DATA["password"]:
    raise RuntimeError(
        "TEST_EMPLOYEE_NUMBER and TEST_PASSWORD environment variables must be set. "
        "Example: export TEST_EMPLOYEE_NUMBER=ADMIN001 TEST_PASSWORD=yourpassword"
    )

def login():
    """Login and get auth token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if response.status_code == 200:
        token = response.json()['access_token']
        print("✓ Logged in successfully")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def get_headers(token):
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_kits(token):
    """Get all kits"""
    response = requests.get(f"{BASE_URL}/kits", headers=get_headers(token))
    if response.status_code == 200:
        kits = response.json()
        print(f"\n✓ Found {len(kits)} kits:")
        for kit in kits:
            print(f"  - Kit {kit['id']}: {kit['name']}")
        return kits
    else:
        print(f"✗ Failed to get kits: {response.text}")
        return []

def get_kit_items(token, kit_id):
    """Get items in a kit"""
    response = requests.get(f"{BASE_URL}/kits/{kit_id}/items", headers=get_headers(token))
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        expendables = data.get('expendables', [])
        print(f"\n✓ Kit {kit_id} has {len(items)} items and {len(expendables)} expendables:")
        for item in items:
            print(f"  - {item['part_number']} (Lot: {item.get('lot_number', 'N/A')}, "
                  f"Serial: {item.get('serial_number', 'N/A')}, Qty: {item['quantity']})")
        for exp in expendables:
            print(f"  - {exp['part_number']} (Expendable, Qty: {exp['quantity']})")
        return items, expendables
    else:
        print(f"✗ Failed to get kit items: {response.text}")
        return [], []

def transfer_item(token, from_kit_id, to_kit_id, item_type, item_id, quantity, box_id=None):
    """Transfer an item between kits"""
    transfer_data = {
        "from_location_type": "kit",
        "from_location_id": from_kit_id,
        "to_location_type": "kit",
        "to_location_id": to_kit_id,
        "item_type": item_type,
        "item_id": item_id,
        "quantity": quantity,
        "notes": "Test transfer"
    }
    if box_id:
        transfer_data["box_id"] = box_id
    
    response = requests.post(f"{BASE_URL}/transfers", 
                            headers=get_headers(token), 
                            json=transfer_data)
    if response.status_code == 201:
        transfer = response.json()
        print(f"\n✓ Transfer created successfully (ID: {transfer['id']})")
        return transfer
    else:
        print(f"\n✗ Transfer failed: {response.text}")
        return None

def verify_chemical_warehouse(token, chemical_id):
    """Verify a chemical's warehouse status"""
    # We'll need to query the database directly for this
    # For now, just return True
    return True

def main():
    print("=" * 60)
    print("KIT-TO-KIT TRANSFER TEST")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        return
    
    # Get kits
    kits = get_kits(token)
    if len(kits) < 2:
        print("\n✗ Need at least 2 kits for testing")
        return
    
    kit1_id = kits[0]['id']
    kit2_id = kits[1]['id']
    kit1_name = kits[0]['name']
    kit2_name = kits[1]['name']
    
    print(f"\n{'=' * 60}")
    print(f"TEST 1: Transfer chemical from {kit1_name} to {kit2_name}")
    print(f"{'=' * 60}")
    
    # Get items in kit 1
    items1_before, exp1_before = get_kit_items(token, kit1_id)
    items2_before, exp2_before = get_kit_items(token, kit2_id)
    
    if not items1_before:
        print("\n✗ No items in kit 1 to transfer")
        return
    
    # Select first chemical item
    chemical_item = None
    for item in items1_before:
        if item.get('item_type') == 'chemical':
            chemical_item = item
            break
    
    if not chemical_item:
        print("\n✗ No chemical items in kit 1")
        return
    
    print(f"\nTransferring: {chemical_item['part_number']} (Lot: {chemical_item.get('lot_number')})")
    print(f"  KitItem ID: {chemical_item['id']}")
    print(f"  Actual Chemical ID: {chemical_item.get('item_id')}")
    print(f"  Quantity: {chemical_item['quantity']}")
    
    # Perform transfer
    transfer = transfer_item(token, kit1_id, kit2_id, 'chemical', 
                            chemical_item['id'], 1)
    
    if not transfer:
        return
    
    # Verify results
    print(f"\n{'=' * 60}")
    print("VERIFICATION")
    print(f"{'=' * 60}")
    
    items1_after, exp1_after = get_kit_items(token, kit1_id)
    items2_after, exp2_after = get_kit_items(token, kit2_id)
    
    print(f"\n{kit1_name} items: {len(items1_before)} → {len(items1_after)}")
    print(f"{kit2_name} items: {len(items2_before)} → {len(items2_after)}")
    
    # Check if item appears in kit 2
    found_in_kit2 = False
    for item in items2_after:
        if (item.get('part_number') == chemical_item['part_number'] and 
            item.get('lot_number') == chemical_item.get('lot_number')):
            found_in_kit2 = True
            print(f"\n✓ Item found in {kit2_name}:")
            print(f"  Part#: {item['part_number']}")
            print(f"  Lot: {item.get('lot_number')}")
            print(f"  KitItem ID: {item['id']}")
            print(f"  Actual Chemical ID: {item.get('item_id')}")
            break
    
    if found_in_kit2:
        print("\n✓ TEST PASSED: Item successfully transferred!")
    else:
        print("\n✗ TEST FAILED: Item not found in destination kit!")
    
    print(f"\n{'=' * 60}")
    print("TEST COMPLETE")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    main()

