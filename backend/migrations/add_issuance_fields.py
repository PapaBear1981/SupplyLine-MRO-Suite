"""
Migration script to add new fields to kit_issuances table.
Adds: issued_to, part_number, serial_number, lot_number, description
"""
import sqlite3
import os

def migrate_kit_issuances():
    """Add new fields to kit_issuances table"""
    # Get database path
    if os.path.exists('/database'):
        db_path = os.path.join('/database', 'tools.db')
    else:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database', 'tools.db'))

    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(kit_issuances)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add issued_to column
        if 'issued_to' not in columns:
            print("Adding issued_to column...")
            cursor.execute("""
                ALTER TABLE kit_issuances 
                ADD COLUMN issued_to INTEGER REFERENCES users(id)
            """)
            print("✓ Added issued_to column")
        else:
            print("✓ issued_to column already exists")
        
        # Add part_number column
        if 'part_number' not in columns:
            print("Adding part_number column...")
            cursor.execute("""
                ALTER TABLE kit_issuances 
                ADD COLUMN part_number VARCHAR(100)
            """)
            print("✓ Added part_number column")
        else:
            print("✓ part_number column already exists")
        
        # Add serial_number column
        if 'serial_number' not in columns:
            print("Adding serial_number column...")
            cursor.execute("""
                ALTER TABLE kit_issuances 
                ADD COLUMN serial_number VARCHAR(100)
            """)
            print("✓ Added serial_number column")
        else:
            print("✓ serial_number column already exists")
        
        # Add lot_number column
        if 'lot_number' not in columns:
            print("Adding lot_number column...")
            cursor.execute("""
                ALTER TABLE kit_issuances 
                ADD COLUMN lot_number VARCHAR(100)
            """)
            print("✓ Added lot_number column")
        else:
            print("✓ lot_number column already exists")
        
        # Add description column
        if 'description' not in columns:
            print("Adding description column...")
            cursor.execute("""
                ALTER TABLE kit_issuances 
                ADD COLUMN description VARCHAR(500)
            """)
            print("✓ Added description column")
        else:
            print("✓ description column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_kit_issuances()

