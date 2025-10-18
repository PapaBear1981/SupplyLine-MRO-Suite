import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'tools.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(chemicals)")
columns = cursor.fetchall()

print("Chemicals table columns:")
print("-" * 60)
for col in columns:
    print(f"{col[0]:3d}. {col[1]:25s} {col[2]:10s} {'NOT NULL' if col[3] else ''}")

print("\n" + "=" * 60)
print("Checking for partial transfer columns:")
print("=" * 60)

column_names = [col[1] for col in columns]
if 'parent_lot_number' in column_names:
    print("✅ parent_lot_number column exists")
else:
    print("❌ parent_lot_number column NOT found")

if 'lot_sequence' in column_names:
    print("✅ lot_sequence column exists")
else:
    print("❌ lot_sequence column NOT found")

conn.close()

