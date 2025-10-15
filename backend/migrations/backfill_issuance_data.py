"""
Migration script to backfill existing kit issuances with item data.
Populates: part_number, serial_number, lot_number, description, issued_to
"""
import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backfill_issuance_data():
    """Backfill existing issuances with item data"""
    # Get database path
    if os.path.exists('/database'):
        db_path = os.path.join('/database', 'tools.db')
    else:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database', 'tools.db'))
    
    print(f"Backfilling issuance data in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all issuances
        cursor.execute("""
            SELECT id, item_type, item_id, issued_by
            FROM kit_issuances
            WHERE part_number IS NULL OR description IS NULL
        """)
        issuances = cursor.fetchall()
        
        print(f"Found {len(issuances)} issuances to backfill")
        
        updated_count = 0
        for issuance_id, item_type, item_id, issued_by in issuances:
            part_number = None
            serial_number = None
            lot_number = None
            description = None

            # Get item data based on type
            if item_type in ('tool', 'chemical'):
                # Get from kit_items (which stores data for both tools and chemicals)
                cursor.execute("""
                    SELECT part_number, serial_number, lot_number, description
                    FROM kit_items
                    WHERE id = ?
                """, (item_id,))
                result = cursor.fetchone()
                if result:
                    part_number, serial_number, lot_number, description = result

            elif item_type == 'expendable':
                # Get from kit_expendables
                cursor.execute("""
                    SELECT part_number, lot_number, description
                    FROM kit_expendables
                    WHERE id = ?
                """, (item_id,))
                result = cursor.fetchone()
                if result:
                    part_number, lot_number, description = result
            
            # Update the issuance with the item data
            # Set issued_to to the same as issued_by (user who issued it)
            cursor.execute("""
                UPDATE kit_issuances
                SET part_number = ?,
                    serial_number = ?,
                    lot_number = ?,
                    description = ?,
                    issued_to = ?
                WHERE id = ?
            """, (part_number, serial_number, lot_number, description, issued_by, issuance_id))
            
            updated_count += 1
            print(f"  Updated issuance {issuance_id}: {item_type} - {description or 'N/A'}")
        
        conn.commit()
        print(f"\n✅ Successfully backfilled {updated_count} issuances!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Backfill failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    backfill_issuance_data()

