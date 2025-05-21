import sqlite3
import os
import sys

# Get the database path from the environment or use the default
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join('..', 'database', 'tools.db'))

def create_announcements_tables():
    """Create the announcements and announcement_reads tables if they don't exist."""
    print(f"Using database path: {os.path.abspath(DB_PATH)}")

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if the announcements table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='announcements'")
        if not cursor.fetchone():
            print("Creating announcements table...")
            cursor.execute('''
                CREATE TABLE announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expiration_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            ''')
            print("Announcements table created successfully.")
        else:
            print("Announcements table already exists.")

        # Check if the announcement_reads table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='announcement_reads'")
        if not cursor.fetchone():
            print("Creating announcement_reads table...")
            cursor.execute('''
                CREATE TABLE announcement_reads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    announcement_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (announcement_id) REFERENCES announcements(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(announcement_id, user_id)
                )
            ''')
            print("Announcement_reads table created successfully.")
        else:
            print("Announcement_reads table already exists.")

        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    create_announcements_tables()
