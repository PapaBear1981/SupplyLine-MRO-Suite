import sqlite3

conn = sqlite3.connect('../database/tools.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, kit_id, part_number, quantity, unit, minimum_stock_level 
    FROM kit_expendables 
    WHERE part_number = 'NAS1104-5D'
""")

results = cursor.fetchall()
for row in results:
    print(f"ID: {row[0]}, Kit: {row[1]}, Part: {row[2]}, Qty: {row[3]}, Unit: {row[4]}, Min: {row[5]}")

conn.close()

