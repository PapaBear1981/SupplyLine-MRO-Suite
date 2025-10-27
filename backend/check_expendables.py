"""
Check kit_expendables table for NAS1104-5D records
"""
import os
import sqlite3


def get_db_path():
    """Get the database path"""
    if os.path.exists("/database"):
        return os.path.join("/database", "tools.db")
    return os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "database",
        "tools.db"
    ))

db_path = get_db_path()
print(f"Database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all NAS1104-5D records
cursor.execute("""
    SELECT id, kit_id, part_number, description, quantity, unit, location
    FROM kit_expendables
    WHERE part_number = 'NAS1104-5D'
    ORDER BY id
""")

records = cursor.fetchall()

print(f"Found {len(records)} NAS1104-5D record(s):\n")
print(f"{'ID':<5} {'Kit':<5} {'Part Number':<15} {'Quantity':<10} {'Unit':<10} {'Location':<20}")
print("=" * 80)

for record in records:
    id, kit_id, part_number, description, quantity, unit, location = record
    print(f"{id:<5} {kit_id:<5} {part_number:<15} {quantity:<10} {unit:<10} {location or 'N/A':<20}")
    print(f"      Description: {description}")
    print(f"      Quantity type: {type(quantity).__name__}, Unit type: {type(unit).__name__}")
    print()

conn.close()

