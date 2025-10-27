import sqlite3


conn = sqlite3.connect("../database/tools.db")
cursor = conn.cursor()

print("=== All kit_expendables (including quantity 0) ===")
cursor.execute("SELECT id, kit_id, part_number, lot_number, quantity, unit, status FROM kit_expendables ORDER BY id")
rows = cursor.fetchall()
print(f"Total kit_expendables: {len(rows)}")
for row in rows:
    print(row)

print("\n=== Kit issuances for CHEM001 ===")
cursor.execute('SELECT * FROM kit_issuances WHERE part_number = "CHEM001" ORDER BY issued_date DESC LIMIT 10')
rows = cursor.fetchall()
print(f"Total issuances: {len(rows)}")
for row in rows:
    print(row)

print("\n=== CHEM001 LOT001-A in chemicals table ===")
cursor.execute('SELECT id, part_number, lot_number, quantity, location FROM chemicals WHERE part_number = "CHEM001" AND lot_number = "LOT001-A"')
row = cursor.fetchone()
if row:
    print(f"Chemical ID: {row[0]}, Part: {row[1]}, Lot: {row[2]}, Qty: {row[3]}, Location: {row[4]}")
else:
    print("Not found")

conn.close()

