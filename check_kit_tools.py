import sqlite3

conn = sqlite3.connect('database/tools.db')
cursor = conn.cursor()

# Count by kit
cursor.execute('''
    SELECT ki.kit_id, k.name, COUNT(*) as tool_count
    FROM kit_items ki
    LEFT JOIN kits k ON ki.kit_id = k.id
    WHERE ki.item_type = "tool"
    GROUP BY ki.kit_id
''')

print('Summary by Kit:')
print('-' * 100)
for row in cursor.fetchall():
    print(f'Kit {row[0]} ({row[1]}): {row[2]} tool items')

# Check if tools have kit_id set
cursor.execute('''
    SELECT COUNT(*) FROM tools WHERE warehouse_id IS NULL
''')
tools_without_warehouse = cursor.fetchone()[0]
print(f'\nTools without warehouse_id: {tools_without_warehouse}')

# Check tool locations
cursor.execute('''
    SELECT 
        CASE 
            WHEN warehouse_id IS NOT NULL THEN 'In Warehouse'
            ELSE 'Not in Warehouse'
        END as location_type,
        COUNT(*) as count
    FROM tools
    GROUP BY location_type
''')
print('\nTool locations:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()

