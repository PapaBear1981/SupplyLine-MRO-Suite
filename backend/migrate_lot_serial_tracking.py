"""
Database Migration Script for Lot/Serial Number Tracking

This script adds comprehensive lot and serial number tracking across all inventory types:
- Adds lot_number field to tools table (for consumables)
- Adds tracking_type field to kit_expendables table
- Creates inventory_transactions table for complete audit trail
- Creates lot_number_sequences table for auto-generation
- Adds indexes for performance

Usage:
    python migrate_lot_serial_tracking.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Tool, Chemical, InventoryTransaction, LotNumberSequence
from models_kits import KitExpendable, KitItem
from sqlalchemy import text, inspect


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()


def migrate_database():
    """Execute the migration"""
    print("=" * 80)
    print("LOT/SERIAL NUMBER TRACKING MIGRATION")
    print("=" * 80)
    print()

    app = create_app()
    with app.app_context():
        try:
            # Step 1: Add lot_number to tools table
            print("Step 1: Adding lot_number field to tools table...")
            if not check_column_exists('tools', 'lot_number'):
                db.session.execute(text(
                    "ALTER TABLE tools ADD COLUMN lot_number VARCHAR(100)"
                ))
                db.session.commit()
                print("✅ Added lot_number column to tools table")
            else:
                print("⏭️  lot_number column already exists in tools table")
            
            # Step 2: Verify chemicals table has lot_number
            print("\nStep 2: Verifying chemicals table has lot_number...")
            if check_column_exists('chemicals', 'lot_number'):
                print("✅ Chemicals table already has lot_number field")
            else:
                print("⚠️  WARNING: Chemicals table missing lot_number field!")
                print("   This should already exist. Please check your database.")
            
            # Step 3: Add tracking_type to kit_expendables table
            print("\nStep 3: Adding tracking_type field to kit_expendables table...")
            if not check_column_exists('kit_expendables', 'tracking_type'):
                db.session.execute(text(
                    "ALTER TABLE kit_expendables ADD COLUMN tracking_type VARCHAR(20) DEFAULT 'lot'"
                ))
                db.session.commit()
                print("✅ Added tracking_type column to kit_expendables table")
                
                # Update existing records to have tracking_type based on what they have
                print("   Updating existing expendables with appropriate tracking_type...")
                expendables = KitExpendable.query.all()
                for exp in expendables:
                    if exp.serial_number and exp.lot_number:
                        exp.tracking_type = 'both'
                    elif exp.serial_number:
                        exp.tracking_type = 'serial'
                    else:
                        exp.tracking_type = 'lot'
                db.session.commit()
                print(f"   ✅ Updated {len(expendables)} existing expendables")
            else:
                print("⏭️  tracking_type column already exists in kit_expendables table")
            
            # Step 4: Create inventory_transactions table
            print("\nStep 4: Creating inventory_transactions table...")
            if not check_table_exists('inventory_transactions'):
                # Use SQLAlchemy model to create table for database portability
                InventoryTransaction.__table__.create(bind=db.engine, checkfirst=True)
                db.session.commit()
                print("✅ Created inventory_transactions table")
            else:
                print("⏭️  inventory_transactions table already exists")

            # Step 5: Create lot_number_sequences table
            print("\nStep 5: Creating lot_number_sequences table...")
            if not check_table_exists('lot_number_sequences'):
                # Use SQLAlchemy model to create table for database portability
                LotNumberSequence.__table__.create(bind=db.engine, checkfirst=True)
                db.session.commit()
                print("✅ Created lot_number_sequences table")
            else:
                print("⏭️  lot_number_sequences table already exists")
            
            # Step 6: Create indexes for performance
            print("\nStep 6: Creating indexes for performance...")
            
            indexes = [
                ("idx_tools_lot_number", "tools", "lot_number"),
                ("idx_tools_serial_number", "tools", "serial_number"),
                ("idx_chemicals_lot_number", "chemicals", "lot_number"),
                ("idx_kit_items_lot_number", "kit_items", "lot_number"),
                ("idx_kit_items_serial_number", "kit_items", "serial_number"),
                ("idx_kit_expendables_lot_number", "kit_expendables", "lot_number"),
                ("idx_kit_expendables_serial_number", "kit_expendables", "serial_number"),
                ("idx_inventory_transactions_item", "inventory_transactions", "item_type, item_id"),
                ("idx_inventory_transactions_timestamp", "inventory_transactions", "timestamp"),
                ("idx_lot_number_sequences_date", "lot_number_sequences", "date"),
            ]
            
            for index_name, table_name, columns in indexes:
                try:
                    db.session.execute(text(
                        f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})"
                    ))
                    print(f"   ✅ Created index {index_name}")
                except Exception as e:
                    print(f"   ⏭️  Index {index_name} may already exist or error: {str(e)}")
            
            db.session.commit()
            
            # Step 7: Create initial transaction records for existing inventory
            print("\nStep 7: Creating initial transaction records for existing inventory...")
            
            # Get admin user for initial transactions
            from models import User
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = User.query.first()
            
            if admin_user:
                transaction_count = 0
                
                # Create transactions for existing tools
                tools = Tool.query.all()
                for tool in tools:
                    existing = InventoryTransaction.query.filter_by(
                        item_type='tool',
                        item_id=tool.id,
                        transaction_type='initial_inventory'
                    ).first()
                    
                    if not existing:
                        transaction = InventoryTransaction(
                            item_type='tool',
                            item_id=tool.id,
                            transaction_type='initial_inventory',
                            user_id=admin_user.id,
                            quantity_change=1.0,
                            location_to=tool.location,
                            notes='Initial inventory record created during migration',
                            lot_number=tool.lot_number,
                            serial_number=tool.serial_number,
                            timestamp=tool.created_at
                        )
                        db.session.add(transaction)
                        transaction_count += 1
                
                # Create transactions for existing chemicals
                chemicals = Chemical.query.all()
                for chemical in chemicals:
                    existing = InventoryTransaction.query.filter_by(
                        item_type='chemical',
                        item_id=chemical.id,
                        transaction_type='initial_inventory'
                    ).first()
                    
                    if not existing:
                        transaction = InventoryTransaction(
                            item_type='chemical',
                            item_id=chemical.id,
                            transaction_type='initial_inventory',
                            user_id=admin_user.id,
                            quantity_change=chemical.quantity,
                            location_to=chemical.location,
                            notes='Initial inventory record created during migration',
                            lot_number=chemical.lot_number,
                            timestamp=chemical.date_added
                        )
                        db.session.add(transaction)
                        transaction_count += 1
                
                # Create transactions for existing kit expendables
                expendables = KitExpendable.query.all()
                for exp in expendables:
                    existing = InventoryTransaction.query.filter_by(
                        item_type='expendable',
                        item_id=exp.id,
                        transaction_type='initial_inventory'
                    ).first()
                    
                    if not existing:
                        transaction = InventoryTransaction(
                            item_type='expendable',
                            item_id=exp.id,
                            transaction_type='initial_inventory',
                            user_id=admin_user.id,
                            quantity_change=exp.quantity,
                            location_to=exp.location,
                            notes='Initial inventory record created during migration',
                            lot_number=exp.lot_number,
                            serial_number=exp.serial_number,
                            timestamp=exp.added_date
                        )
                        db.session.add(transaction)
                        transaction_count += 1
                
                db.session.commit()
                print(f"   ✅ Created {transaction_count} initial transaction records")
            else:
                print("   ⚠️  No admin user found, skipping initial transaction creation")
            
            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("\nSummary:")
            print("  - Added lot_number field to tools table")
            print("  - Added tracking_type field to kit_expendables table")
            print("  - Created inventory_transactions table")
            print("  - Created lot_number_sequences table")
            print("  - Created performance indexes")
            print("  - Created initial transaction records")
            print("\nNext steps:")
            print("  1. Test the application to ensure all features work correctly")
            print("  2. Update API endpoints to use new transaction tracking")
            print("  3. Update frontend to display lot/serial numbers")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    migrate_database()

