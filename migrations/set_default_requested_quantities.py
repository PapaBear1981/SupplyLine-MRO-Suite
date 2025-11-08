#!/usr/bin/env python3
"""
Set default requested quantities for chemicals that need reorder but don't have a requested quantity.
"""
import os
import sqlite3

def get_db_path():
    """Get the database path, checking both local and Docker environments."""
    # Check if running in Docker (volume mounted at /database)
    docker_db_path = "/database/tools.db"
    if os.path.exists(docker_db_path):
        return docker_db_path
    
    # Local development path
    local_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "tools.db")
    if os.path.exists(local_db_path):
        return local_db_path
    
    raise FileNotFoundError("Database file not found in expected locations")

def set_default_requested_quantities():
    """Set default requested quantities for chemicals needing reorder."""
    db_path = get_db_path()
    print(f"Using database: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get chemicals needing reorder without requested quantity
        cursor.execute("""
            SELECT id, part_number, lot_number, description, quantity, minimum_stock_level, unit
            FROM chemicals
            WHERE needs_reorder = 1 
            AND reorder_status = 'needed' 
            AND requested_quantity IS NULL
        """)
        chemicals = cursor.fetchall()
        
        print(f"Found {len(chemicals)} chemicals needing reorder without requested quantity\n")
        
        updated_count = 0
        for chem_id, part_number, lot_number, description, current_qty, min_stock, unit in chemicals:
            print(f"Processing Chemical ID {chem_id}: {part_number} - {lot_number}")
            print(f"  Description: {description}")
            print(f"  Current Quantity: {current_qty} {unit}")
            print(f"  Minimum Stock Level: {min_stock} {unit}")
            
            # Calculate a sensible default requested quantity
            if min_stock and min_stock > 0:
                # Request enough to get back to 2x minimum stock level
                requested_qty = max(min_stock * 2 - current_qty, min_stock)
            else:
                # If no minimum stock level, request 5 units
                requested_qty = 5
            
            print(f"  Setting requested quantity to: {requested_qty} {unit}")
            
            # Update the chemical
            cursor.execute("""
                UPDATE chemicals
                SET requested_quantity = ?
                WHERE id = ?
            """, (requested_qty, chem_id))
            
            updated_count += 1
            print(f"  ✓ Updated\n")
        
        if updated_count > 0:
            conn.commit()
            print(f"✓ Successfully updated {updated_count} chemicals")
        else:
            print("No chemicals needed updating")
        
        # Verify the updates
        print("\n--- Verification ---")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chemicals 
            WHERE needs_reorder = 1 AND reorder_status = 'needed'
        """)
        total_count = cursor.fetchone()[0]
        print(f"Total chemicals needing reorder: {total_count}")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chemicals 
            WHERE needs_reorder = 1 
            AND reorder_status = 'needed' 
            AND requested_quantity IS NOT NULL
        """)
        with_qty_count = cursor.fetchone()[0]
        print(f"Chemicals with requested quantity: {with_qty_count}")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chemicals 
            WHERE needs_reorder = 1 
            AND reorder_status = 'needed' 
            AND requested_quantity IS NULL
        """)
        without_qty_count = cursor.fetchone()[0]
        print(f"Chemicals without requested quantity: {without_qty_count}")
        
        if with_qty_count > 0:
            print("\nChemicals with requested quantity:")
            cursor.execute("""
                SELECT part_number, lot_number, requested_quantity, unit
                FROM chemicals
                WHERE needs_reorder = 1 
                AND reorder_status = 'needed' 
                AND requested_quantity IS NOT NULL
            """)
            for part_number, lot_number, requested_qty, unit in cursor.fetchall():
                print(f"  - {part_number} ({lot_number}): {requested_qty} {unit}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    set_default_requested_quantities()

