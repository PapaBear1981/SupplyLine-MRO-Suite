"""
Fix tool locations - tools in kits should not have warehouse_id set
"""
import sqlite3

conn = sqlite3.connect('database/tools.db')
cursor = conn.cursor()

# Get all tools that are in kit_items
cursor.execute('''
    SELECT DISTINCT item_id 
    FROM kit_items 
    WHERE item_type = "tool"
''')
tools_in_kits = [row[0] for row in cursor.fetchall()]
print(f'Found {len(tools_in_kits)} tools in kits')

# Update these tools to remove warehouse_id
if tools_in_kits:
    placeholders = ','.join('?' * len(tools_in_kits))
    cursor.execute(f'''
        UPDATE tools 
        SET warehouse_id = NULL 
        WHERE id IN ({placeholders})
    ''', tools_in_kits)
    
    print(f'Updated {cursor.rowcount} tools to remove warehouse_id')

# Verify the changes
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN warehouse_id IS NOT NULL THEN 1 ELSE 0 END) as in_warehouse,
        SUM(CASE WHEN warehouse_id IS NULL THEN 1 ELSE 0 END) as not_in_warehouse
    FROM tools
''')
stats = cursor.fetchone()
print(f'\nTool location stats:')
print(f'  Total tools: {stats[0]}')
print(f'  In warehouse: {stats[1]}')
print(f'  Not in warehouse (should be in kits): {stats[2]}')

conn.commit()
conn.close()

print('\n✅ Tool locations fixed!')

