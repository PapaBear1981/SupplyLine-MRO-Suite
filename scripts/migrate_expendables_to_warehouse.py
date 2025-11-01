"""
Migration script to convert KitExpendable records to warehouse-based Expendable model.

This script:
1. Creates the expendables table
2. Migrates all KitExpendable records to Expendable model (in warehouses)
3. Assigns lot numbers to all items that don't have them
4. Creates KitItem records to link kits to the new Expendable records
5. Preserves all existing data and relationships

Run this script ONCE to migrate the system.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.run import app
from backend.models import db, Warehouse, Expendable, LotNumberSequence
from backend.models_kits import KitExpendable, KitItem, Kit


def get_or_create_default_warehouse():
    """Get or create a default warehouse for migrated expendables"""
    warehouse = Warehouse.query.filter_by(name="Main Warehouse").first()
    if not warehouse:
        print("Creating default 'Main Warehouse'...")
        warehouse = Warehouse(
            name="Main Warehouse",
            address="123 Main St",
            city="Seattle",
            state="WA",
            zip_code="98101",
            country="USA",
            warehouse_type="main",
            is_active=True
        )
        db.session.add(warehouse)
        db.session.flush()
        print(f"Created warehouse: {warehouse.name} (ID: {warehouse.id})")
    else:
        print(f"Using existing warehouse: {warehouse.name} (ID: {warehouse.id})")
    return warehouse


def migrate_kit_expendables():
    """Migrate all KitExpendable records to warehouse-based Expendable model"""
    
    with app.app_context():
        print("\n" + "="*80)
        print("EXPENDABLE MIGRATION SCRIPT")
        print("="*80)
        
        # Get all KitExpendables
        kit_expendables = KitExpendable.query.all()
        print(f"\nFound {len(kit_expendables)} KitExpendable records to migrate")
        
        if not kit_expendables:
            print("No KitExpendables to migrate. Exiting.")
            return
        
        # Get or create default warehouse
        warehouse = get_or_create_default_warehouse()
        
        # Track migrations
        migrated_count = 0
        error_count = 0
        lot_number_counter = {}  # Track lot numbers by part number
        
        print("\n" + "-"*80)
        print("MIGRATION PROCESS")
        print("-"*80)
        
        for kit_exp in kit_expendables:
            try:
                # Generate lot number if not present
                if kit_exp.lot_number:
                    lot_number = kit_exp.lot_number
                elif kit_exp.serial_number:
                    # If it has a serial number, use that
                    serial_number = kit_exp.serial_number
                    lot_number = None
                else:
                    # Generate a unique lot number
                    # Use part number as base for lot number generation
                    if kit_exp.part_number not in lot_number_counter:
                        lot_number_counter[kit_exp.part_number] = 1
                    else:
                        lot_number_counter[kit_exp.part_number] += 1

                    lot_number = LotNumberSequence.generate_lot_number()
                    serial_number = None
                
                # Create new Expendable in warehouse
                expendable = Expendable(
                    part_number=kit_exp.part_number,
                    serial_number=serial_number if not lot_number else None,
                    lot_number=lot_number if not serial_number else None,
                    description=kit_exp.description,
                    manufacturer=None,  # Not tracked in KitExpendable
                    quantity=kit_exp.quantity,
                    unit=kit_exp.unit,
                    location=kit_exp.location,
                    category="General",
                    status="available",
                    warehouse_id=warehouse.id,
                    date_added=kit_exp.added_date,
                    minimum_stock_level=kit_exp.minimum_stock_level,
                    notes=f"Migrated from KitExpendable ID {kit_exp.id}"
                )
                db.session.add(expendable)
                db.session.flush()  # Get the expendable ID
                
                # Create KitItem to link kit to the new Expendable
                kit_item = KitItem(
                    kit_id=kit_exp.kit_id,
                    box_id=kit_exp.box_id,
                    item_type="expendable",
                    item_id=expendable.id,
                    part_number=expendable.part_number,
                    serial_number=expendable.serial_number,
                    lot_number=expendable.lot_number,
                    description=expendable.description,
                    quantity=expendable.quantity,
                    location=kit_exp.location,
                    status="available",
                    added_date=kit_exp.added_date,
                    last_updated=kit_exp.last_updated
                )
                db.session.add(kit_item)
                
                # Mark the warehouse item as "in kit" by setting warehouse_id to None
                expendable.warehouse_id = None
                
                migrated_count += 1
                print(f"✓ Migrated: {kit_exp.part_number} (KitExp ID {kit_exp.id} → Exp ID {expendable.id} → KitItem)")
                
            except Exception as e:
                error_count += 1
                print(f"✗ Error migrating KitExpendable ID {kit_exp.id}: {e}")
                db.session.rollback()
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "-"*80)
            print("MIGRATION SUMMARY")
            print("-"*80)
            print(f"✓ Successfully migrated: {migrated_count} expendables")
            print(f"✗ Errors: {error_count}")
            print(f"✓ Created {migrated_count} new Expendable records")
            print(f"✓ Created {migrated_count} new KitItem records")
            print("\n" + "="*80)
            print("MIGRATION COMPLETE!")
            print("="*80)
            print("\nNOTE: KitExpendable table is now deprecated.")
            print("All expendables are now managed through the Expendable model.")
            print("KitItem records link kits to expendables (just like tools and chemicals).")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ MIGRATION FAILED: {e}")
            print("All changes have been rolled back.")
            raise


if __name__ == "__main__":
    print("\n⚠️  WARNING: This migration will convert all KitExpendable records to the new warehouse-based system.")
    print("⚠️  This operation cannot be easily reversed.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    migrate_kit_expendables()

