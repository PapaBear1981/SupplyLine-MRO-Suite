import requests
import json

# Check kit_items table
response = requests.get('http://localhost:5000/api/kits')
kits_data = response.json()

print("=== KITS ===")
for kit in kits_data.get('kits', [])[:5]:
    print(f"Kit ID {kit['id']}: {kit['name']}")
    if kit.get('items'):
        print(f"  Items in kit: {len(kit['items'])}")
        for item in kit['items'][:5]:
            print(f"    - {item.get('item_type')}: {item.get('part_number')} (ID: {item.get('item_id')})")

# Check chemicals API
response = requests.get('http://localhost:5000/api/chemicals')
chemicals_data = response.json()

print(f"\n=== CHEMICALS API ===")
print(f"Total chemicals returned: {len(chemicals_data['chemicals'])}")

# Check for chemicals with kit info
kit_chems = [c for c in chemicals_data['chemicals'] if c.get('kit_name')]
print(f"Chemicals with kit_name: {len(kit_chems)}")

# Check for chemicals with warehouse_id = None
no_warehouse = [c for c in chemicals_data['chemicals'] if c.get('warehouse_id') is None]
print(f"Chemicals with warehouse_id=None: {len(no_warehouse)}")

if no_warehouse:
    print("\nChemicals with no warehouse_id:")
    for c in no_warehouse[:10]:
        print(f"  {c['part_number']}: kit_name={c.get('kit_name')}, warehouse_id={c.get('warehouse_id')}, lot={c.get('lot_number')}")

