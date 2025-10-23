"""
Diagnostic script to check kit API endpoints.

Required environment variables:
- API_URL: Base URL for the API (default: http://localhost:5000)
- ADMIN_EMAIL: Admin email for authentication
- ADMIN_PASSWORD: Admin password for authentication
"""
import requests
import json
import os

# Configuration from environment variables
API_URL = os.getenv('API_URL', 'http://localhost:5000')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_EMAIL and ADMIN_PASSWORD environment variables must be set. "
        "Example: export ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=yourpassword"
    )

# Login first to get token
login_url = f"{API_URL}/api/auth/login"
login_data = {
    "email": ADMIN_EMAIL,
    "password": ADMIN_PASSWORD
}

try:
    response = requests.post(login_url, json=login_data, timeout=10)
    if response.status_code == 200:
        token = response.json().get('access_token')
        # Mask token in logs for security
        print(f"✓ Login successful, token: {token[:10]}...{token[-5:]}")

        # Get kit items for kit 1 (Boeing 737)
        headers = {"Authorization": f"Bearer {token}"}
        kit_items_url = f"{API_URL}/api/kits/1/items"

        response = requests.get(kit_items_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n=== Kit 1 (Boeing 737) Items ===")
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
except requests.Timeout:
    print("✗ Request timed out - server may be unresponsive")
except requests.RequestException as e:
    print(f"✗ Network error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

