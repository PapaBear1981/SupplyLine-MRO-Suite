import os
import sqlite3

# Find the database file
def find_database():
    possible_paths = [
        'database/tools.db',
        '../database/tools.db',
        'backend/database/tools.db',
        './database/tools.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found database at: {path}")
            return path
    
    print("Database not found in common locations")
    return None

# Connect to the database
db_path = find_database()
if db_path:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in database: {[table[0] for table in tables]}")
        
        # Check tools
        print("\nTools:")
        cursor.execute("SELECT id, tool_number, serial_number, description FROM tools LIMIT 5")
        tools = cursor.fetchall()
        for tool in tools:
            print(f"Tool ID: {tool[0]}, Number: {tool[1]}, Serial: {tool[2]}, Description: {tool[3]}")
            
            # Check if tool is checked out
            cursor.execute("SELECT id FROM checkouts WHERE tool_id = ? AND return_date IS NULL", (tool[0],))
            checkout = cursor.fetchone()
            status = 'checked_out' if checkout else 'available'
            print(f"  Status: {status}")
        
        # Check active checkouts
        print("\nActive Checkouts:")
        cursor.execute("""
            SELECT c.id, c.tool_id, t.tool_number, c.user_id, u.name, c.checkout_date
            FROM checkouts c
            JOIN tools t ON c.tool_id = t.id
            JOIN users u ON c.user_id = u.id
            WHERE c.return_date IS NULL
        """)
        checkouts = cursor.fetchall()
        if checkouts:
            for checkout in checkouts:
                print(f"Checkout ID: {checkout[0]}, Tool: {checkout[2]} (ID: {checkout[1]}), User: {checkout[4]} (ID: {checkout[3]})")
                print(f"  Checkout Date: {checkout[5]}")
        else:
            print("  No active checkouts found")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
else:
    print("Cannot proceed without database file")
