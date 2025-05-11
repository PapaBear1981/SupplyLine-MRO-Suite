import sqlite3

# Connect to the database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Add a tool with a category
cursor.execute('''
    INSERT INTO tools (tool_number, serial_number, description, condition, location, category, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
''', ('T001', 'S001', 'Test Tool', 'Good', 'Storage', 'General'))

# Commit the changes and close the connection
conn.commit()
conn.close()

print('Tool added successfully')
