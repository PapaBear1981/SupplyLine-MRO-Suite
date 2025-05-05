import os
import sqlite3

# Define the database path
# Check if we're in Docker environment (look for /database volume)
if os.path.exists('/database'):
    db_path = os.path.join('/database', 'tools.db')
else:
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'tools.db'))
print(f"Database path: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if category column already exists
cursor.execute("PRAGMA table_info(tools)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
print(f"Current columns in tools table: {column_names}")

# Add category column if it doesn't exist
if 'category' not in column_names:
    print("Adding 'category' column to tools table...")
    cursor.execute("ALTER TABLE tools ADD COLUMN category TEXT DEFAULT 'General'")
    print("Category column added")
else:
    print("Category column already exists")

# Add status column if it doesn't exist
if 'status' not in column_names:
    print("Adding 'status' column to tools table...")
    cursor.execute("ALTER TABLE tools ADD COLUMN status TEXT NOT NULL DEFAULT 'available'")
    print("Status column added")
else:
    print("Status column already exists")

# Add status_reason column if it doesn't exist
if 'status_reason' not in column_names:
    print("Adding 'status_reason' column to tools table...")
    cursor.execute("ALTER TABLE tools ADD COLUMN status_reason TEXT")
    print("Status reason column added")
else:
    print("Status reason column already exists")

# Create tool_service_records table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS tool_service_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')
print("Created or verified tool_service_records table")

# Commit the changes
conn.commit()
print("Schema changes committed successfully")

# Close the connection
conn.close()
print("Database update completed successfully")
