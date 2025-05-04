import sqlite3
import os

def update_user_schema():
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'tools.db')

    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    # Check if is_active column exists
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if 'is_active' not in column_names:
        print("Adding is_active column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
        conn.commit()
        print("Column added successfully!")
    else:
        print("is_active column already exists in users table.")

    # Set all users to active
    cursor.execute("UPDATE users SET is_active = 1")
    conn.commit()
    print(f"Updated all users to be active.")

    conn.close()

if __name__ == "__main__":
    update_user_schema()
