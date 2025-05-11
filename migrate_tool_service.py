import sqlite3
import os

print("Starting database migration for tool service functionality...")

# Define the database path
db_path = os.path.join(os.path.dirname(__file__), 'database', 'tools.db')
# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(db_path), exist_ok=True)
print(f"Database path: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if status column already exists
    cursor.execute("PRAGMA table_info(tools)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Add status column if it doesn't exist
    if 'status' not in column_names:
        print("Adding 'status' column to tools table...")
        cursor.execute("ALTER TABLE tools ADD COLUMN status TEXT NOT NULL DEFAULT 'available'")
    else:
        print("'status' column already exists in tools table")

    # Add status_reason column if it doesn't exist
    if 'status_reason' not in column_names:
        print("Adding 'status_reason' column to tools table...")
        cursor.execute("ALTER TABLE tools ADD COLUMN status_reason TEXT")
    else:
        print("'status_reason' column already exists in tools table")

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

    print("Migration completed successfully!")

except Exception as e:
    print(f"Error during migration: {str(e)}")
    if 'conn' in locals():
        conn.close()
