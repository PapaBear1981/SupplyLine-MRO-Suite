import requests
import json

response = requests.get('http://localhost:5000/api/chemicals')
data = response.json()

print(f"Total chemicals: {len(data['chemicals'])}")

kit_chems = [c for c in data['chemicals'] if c.get('kit_name')]
print(f"Chemicals in kits: {len(kit_chems)}")

if kit_chems:
    print("\nChemicals in kits:")
    for c in kit_chems[:10]:
        print(f"  {c['part_number']}: Kit={c.get('kit_name')}, Box={c.get('box_number')}, Warehouse={c.get('warehouse_id')}")
else:
    print("\nNo chemicals found in kits!")

