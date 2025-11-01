import requests
import json

# Wait a moment for backend to restart
import time
time.sleep(3)

# Fetch tools from API
response = requests.get('http://localhost:5000/api/tools?per_page=100')
data = response.json()

print(f"Total tools returned: {len(data['tools'])}")
print(f"Pagination info: {data['pagination']}")

# Count tools by location
in_warehouse = [t for t in data['tools'] if t.get('warehouse_id') is not None]
in_kits = [t for t in data['tools'] if t.get('kit_name') is not None]
unknown = [t for t in data['tools'] if t.get('warehouse_id') is None and t.get('kit_name') is None]

print(f"\nTools by location:")
print(f"  In warehouse: {len(in_warehouse)}")
print(f"  In kits: {len(in_kits)}")
print(f"  Unknown location: {len(unknown)}")

# Show sample of tools in kits
print(f"\nSample tools in kits:")
for tool in in_kits[:10]:
    print(f"  {tool['tool_number']}: Kit={tool.get('kit_name')}, Box={tool.get('box_number')}, Warehouse={tool.get('warehouse_id')}")

# Show sample of tools in warehouse
print(f"\nSample tools in warehouse:")
for tool in in_warehouse[:5]:
    print(f"  {tool['tool_number']}: Warehouse ID={tool.get('warehouse_id')}, Location={tool.get('location')}, Kit={tool.get('kit_name')}")

