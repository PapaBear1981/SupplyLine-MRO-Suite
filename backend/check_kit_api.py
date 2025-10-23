import requests
import json

# Login first to get token
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "email": "admin@example.com",
    "password": "admin123"
}

try:
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"✓ Login successful, token: {token[:20]}...")
        
        # Get kit items for kit 1 (Boeing 737)
        headers = {"Authorization": f"Bearer {token}"}
        kit_items_url = "http://localhost:5000/api/kits/1/items"
        
        response = requests.get(kit_items_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n=== Kit 1 (Boeing 737) Items ===")
            print(f"Total items: {data.get('total_count')}")
            print(f"\nKit Items (tools/chemicals): {len(data.get('items', []))}")
            for item in data.get('items', []):
                print(f"  - {item.get('part_number')} {item.get('lot_number', '')} - Qty: {item.get('quantity')}")
            
            print(f"\nKit Expendables: {len(data.get('expendables', []))}")
            for exp in data.get('expendables', []):
                print(f"  - {exp.get('part_number')} {exp.get('lot_number', '')} - Qty: {exp.get('quantity')} {exp.get('unit', '')}")
        else:
            print(f"✗ Failed to get kit items: {response.status_code}")
            print(response.text)
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}")

