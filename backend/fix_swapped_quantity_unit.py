"""
Fix swapped quantity and unit values in kit_expendables table.

This script identifies and fixes records where the quantity and unit fields
have been accidentally swapped (e.g., quantity='EA', unit='23').
"""
import sqlite3
import os
import sys

def get_db_path():
    """Get the database path"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database',
            'tools.db'
        ))

def fix_swapped_values():
    """Fix swapped quantity and unit values"""
    db_path = get_db_path()
    print(f"Connecting to database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find records where quantity appears to be a string (unit) and unit appears to be a number
        # Use GLOB for pattern matching in SQLite (LIKE doesn't support character classes)
        cursor.execute("""
            SELECT id, part_number, description, quantity, unit
            FROM kit_expendables
            WHERE
              -- quantity looks non-numeric (contains letters)
              CAST(quantity AS TEXT) GLOB '*[A-Za-z]*'
              OR
              -- unit looks numeric (contains digits but no letters)
              (CAST(unit AS TEXT) GLOB '*[0-9]*' AND CAST(unit AS TEXT) NOT GLOB '*[A-Za-z]*')
        """)
        
        swapped_records = cursor.fetchall()
        
        if not swapped_records:
            print("✅ No swapped records found!")
            return True
        
        print(f"\n🔍 Found {len(swapped_records)} record(s) with potentially swapped values:\n")
        
        for record in swapped_records:
            id, part_number, description, quantity, unit = record
            print(f"ID: {id}")
            print(f"  Part Number: {part_number}")
            print(f"  Description: {description}")
            print(f"  Current Quantity: {quantity} (type: {type(quantity).__name__})")
            print(f"  Current Unit: {unit} (type: {type(unit).__name__})")
            print()
        
        # Ask for confirmation
        response = input("Do you want to swap these values? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Operation cancelled")
            return False
        
        # Perform the swap
        fixed_count = 0
        for record in swapped_records:
            id, part_number, description, quantity, unit = record
            
            # Swap the values
            cursor.execute("""
                UPDATE kit_expendables
                SET quantity = ?, unit = ?
                WHERE id = ?
            """, (unit, quantity, id))
            
            fixed_count += 1
            print(f"✅ Fixed record {id}: quantity={unit}, unit={quantity}")
        
        conn.commit()
        print(f"\n✅ Successfully fixed {fixed_count} record(s)!")
        
        # Verify the fix
        print("\n🔍 Verifying fixes...")
        for record in swapped_records:
            id = record[0]
            cursor.execute("""
                SELECT id, part_number, quantity, unit
                FROM kit_expendables
                WHERE id = ?
            """, (id,))
            
            fixed_record = cursor.fetchone()
            if fixed_record:
                print(f"  ID {fixed_record[0]}: {fixed_record[1]} - Quantity: {fixed_record[2]}, Unit: {fixed_record[3]}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Swapped Quantity/Unit Values in kit_expendables")
    print("=" * 60)
    print()
    
    success = fix_swapped_values()
    
    if success:
        print("\n✅ Fix completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Fix failed or was cancelled")
        sys.exit(1)

