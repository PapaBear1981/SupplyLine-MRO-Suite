"""
Check kit item quantities in the database.
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
db_path = os.path.abspath(db_path)

print(f"Connecting to database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check kit_items table
    print("\nKit Items for Kit ID 2:")
    cursor.execute("SELECT id, part_number, description, quantity FROM kit_items WHERE kit_id = 2")
    items = cursor.fetchall()
    
    for item_id, part_number, description, quantity in items:
        print(f"  ID: {item_id}, Part: {part_number}, Desc: {description}, Qty: {quantity} (type: {type(quantity).__name__})")
    
    # Check kit_expendables table
    print("\nKit Expendables for Kit ID 2:")
    cursor.execute("SELECT id, part_number, description, quantity FROM kit_expendables WHERE kit_id = 2")
    expendables = cursor.fetchall()
    
    for expendable_id, part_number, description, quantity in expendables:
        print(f"  ID: {expendable_id}, Part: {part_number}, Desc: {description}, Qty: {quantity} (type: {type(quantity).__name__})")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    
finally:
    conn.close()

