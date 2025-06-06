from app import create_app
from models import db
import sqlite3

def add_expected_return_date_column():
    # Connect to the database
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        print("Connected to app.db")
    except Exception as e:
        print(f"Error connecting to app.db: {e}")
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            print("Connected to database.db")
        except Exception as e:
            print(f"Error connecting to database.db: {e}")
            return

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(checkouts)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'expected_return_date' not in columns:
        print("Adding expected_return_date column to checkouts table...")
        cursor.execute("ALTER TABLE checkouts ADD COLUMN expected_return_date TIMESTAMP")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column expected_return_date already exists.")

    conn.close()

if __name__ == '__main__':
    # Create the app context
    app = create_app()
    with app.app_context():
        add_expected_return_date_column()
