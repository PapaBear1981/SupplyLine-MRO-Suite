import requests
import json

response = requests.get('http://localhost:5000/api/chemicals?per_page=500')
data = response.json()

print(f"Total from pagination: {data['pagination']['total']}")
print(f"Chemicals returned: {len(data['chemicals'])}")

# Check for chemicals with kit_id
kit_chems = [c for c in data['chemicals'] if c.get('kit_id')]
print(f"Chemicals with kit_id: {len(kit_chems)}")

if kit_chems:
    print("\nChemicals with kit_id:")
    for c in kit_chems[:10]:
        print(f"  ID: {c['id']}, Part: {c['part_number']}, Lot: {c['lot_number']}, Kit ID: {c.get('kit_id')}, Kit Name: {c.get('kit_name')}, Warehouse: {c.get('warehouse_id')}")
else:
    print("\nNo chemicals with kit_id found!")
    
# Check for chemicals with warehouse_id = None
no_warehouse = [c for c in data['chemicals'] if c.get('warehouse_id') is None]
print(f"\nChemicals with warehouse_id=None: {len(no_warehouse)}")

if no_warehouse:
    print("\nChemicals with warehouse_id=None:")
    for c in no_warehouse[:10]:
        print(f"  ID: {c['id']}, Part: {c['part_number']}, Lot: {c['lot_number']}, Kit ID: {c.get('kit_id')}, Kit Name: {c.get('kit_name')}")

