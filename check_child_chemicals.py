import requests
import json

# Check for child chemicals
response = requests.get('http://localhost:5000/api/chemicals')
chemicals_data = response.json()

print(f"Total chemicals: {len(chemicals_data['chemicals'])}")

# Check for chemicals with parent_lot_number
child_chems = [c for c in chemicals_data['chemicals'] if c.get('parent_lot_number')]
print(f"Child chemicals (with parent_lot_number): {len(child_chems)}")

if child_chems:
    print("\nChild chemicals:")
    for c in child_chems[:10]:
        print(f"  ID: {c['id']}, Part: {c['part_number']}, Lot: {c['lot_number']}, Parent: {c.get('parent_lot_number')}, Warehouse: {c.get('warehouse_id')}, Kit: {c.get('kit_name')}")

# Check for chemicals with lot numbers ending in -A, -B, etc (child pattern)
child_pattern_chems = [c for c in chemicals_data['chemicals'] if c.get('lot_number') and '-' in c.get('lot_number', '')]
print(f"\nChemicals with '-' in lot number: {len(child_pattern_chems)}")

if child_pattern_chems:
    print("\nChemicals with '-' in lot number:")
    for c in child_pattern_chems[:10]:
        print(f"  ID: {c['id']}, Part: {c['part_number']}, Lot: {c['lot_number']}, Warehouse: {c.get('warehouse_id')}, Kit: {c.get('kit_name')}")

