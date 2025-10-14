"""
Migration script for Warehouse Management System.

This script:
1. Creates the warehouses, warehouse_transfers tables
2. Adds warehouse_id columns to tools and chemicals tables
3. Creates a 'Main Warehouse' with default address
4. Moves all existing tools and chemicals to Main Warehouse
5. Ensures all tools have serial numbers (generates if missing)
6. Ensures all chemicals have lot numbers (generates if missing)
7. Updates all kit items to have proper lot/serial numbers

Run this script ONCE to migrate the database to the new warehouse system.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Tool, Chemical, Warehouse, WarehouseTransfer, LotNumberSequence
from models_kits import KitItem, KitExpendable
from sqlalchemy import text
from datetime import datetime

# Create the Flask app
app = create_app()


def create_tables():
    """Create new tables for warehouse system."""
    print("Creating warehouse system tables...")
    
    with app.app_context():
        # Create warehouses table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS warehouses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL UNIQUE,
                address VARCHAR(500),
                city VARCHAR(100),
                state VARCHAR(50),
                zip_code VARCHAR(20),
                country VARCHAR(100) DEFAULT 'USA',
                warehouse_type VARCHAR(50) NOT NULL DEFAULT 'satellite',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                created_by_id INTEGER,
                FOREIGN KEY (created_by_id) REFERENCES users(id)
            )
        """))
        
        # Create indexes for warehouses
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouses_name ON warehouses(name)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouses_is_active ON warehouses(is_active)
        """))
        
        # Create warehouse_transfers table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS warehouse_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_warehouse_id INTEGER,
                to_warehouse_id INTEGER,
                to_kit_id INTEGER,
                from_kit_id INTEGER,
                item_type VARCHAR(50) NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                transfer_date DATETIME NOT NULL,
                transferred_by_id INTEGER NOT NULL,
                notes TEXT,
                status VARCHAR(50) NOT NULL DEFAULT 'completed',
                FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id),
                FOREIGN KEY (to_warehouse_id) REFERENCES warehouses(id),
                FOREIGN KEY (to_kit_id) REFERENCES kits(id),
                FOREIGN KEY (from_kit_id) REFERENCES kits(id),
                FOREIGN KEY (transferred_by_id) REFERENCES users(id)
            )
        """))
        
        # Create indexes for warehouse_transfers
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_from_warehouse ON warehouse_transfers(from_warehouse_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_to_warehouse ON warehouse_transfers(to_warehouse_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_to_kit ON warehouse_transfers(to_kit_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_from_kit ON warehouse_transfers(from_kit_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_item_type ON warehouse_transfers(item_type)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_item_id ON warehouse_transfers(item_id)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_transfer_date ON warehouse_transfers(transfer_date)
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_warehouse_transfers_status ON warehouse_transfers(status)
        """))
        
        db.session.commit()
        print("✓ Warehouse system tables created successfully")


def add_warehouse_columns():
    """Add warehouse_id columns to tools and chemicals tables."""
    print("Adding warehouse_id columns to tools and chemicals...")
    
    with app.app_context():
        # Check if warehouse_id column exists in tools table
        result = db.session.execute(text("PRAGMA table_info(tools)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'warehouse_id' not in columns:
            db.session.execute(text("""
                ALTER TABLE tools ADD COLUMN warehouse_id INTEGER REFERENCES warehouses(id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tools_warehouse_id ON tools(warehouse_id)
            """))
            print("✓ Added warehouse_id to tools table")
        else:
            print("✓ warehouse_id already exists in tools table")
        
        # Check if warehouse_id column exists in chemicals table
        result = db.session.execute(text("PRAGMA table_info(chemicals)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'warehouse_id' not in columns:
            db.session.execute(text("""
                ALTER TABLE chemicals ADD COLUMN warehouse_id INTEGER REFERENCES warehouses(id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chemicals_warehouse_id ON chemicals(warehouse_id)
            """))
            print("✓ Added warehouse_id to chemicals table")
        else:
            print("✓ warehouse_id already exists in chemicals table")
        
        db.session.commit()


def create_main_warehouse():
    """Create the Main Warehouse."""
    print("Creating Main Warehouse...")
    
    with app.app_context():
        # Check if Main Warehouse already exists
        main_warehouse = Warehouse.query.filter_by(name='Main Warehouse').first()
        
        if not main_warehouse:
            main_warehouse = Warehouse(
                name='Main Warehouse',
                address='123 Main Street',
                city='Aviation City',
                state='CA',
                zip_code='90001',
                country='USA',
                warehouse_type='main',
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(main_warehouse)
            db.session.commit()
            print(f"✓ Created Main Warehouse (ID: {main_warehouse.id})")
        else:
            print(f"✓ Main Warehouse already exists (ID: {main_warehouse.id})")
        
        return main_warehouse


def migrate_tools_to_warehouse(main_warehouse):
    """Move all tools not in kits to Main Warehouse and ensure serial numbers."""
    print("Migrating tools to Main Warehouse...")

    with app.app_context():
        # Get all tools
        tools = Tool.query.all()
        tools_migrated = 0
        serial_numbers_generated = 0

        # Get all tool IDs that are in kits
        kit_tool_ids = set([ki.item_id for ki in KitItem.query.filter(KitItem.item_type == 'tool').all()])

        for tool in tools:
            # Only migrate tools not in kits
            if tool.id not in kit_tool_ids:
                if not tool.warehouse_id:
                    tool.warehouse_id = main_warehouse.id
                    tools_migrated += 1

            # Ensure tool has a serial number
            if not tool.serial_number or tool.serial_number.strip() == '':
                # Generate serial number based on tool_number
                tool.serial_number = f"{tool.tool_number}-{str(tool.id).zfill(3)}"
                serial_numbers_generated += 1

        db.session.commit()
        print(f"✓ Migrated {tools_migrated} tools to Main Warehouse")
        print(f"✓ Generated {serial_numbers_generated} serial numbers for tools")


def migrate_chemicals_to_warehouse(main_warehouse):
    """Move all chemicals not in kits to Main Warehouse and ensure lot numbers."""
    print("Migrating chemicals to Main Warehouse...")

    with app.app_context():
        # Get all chemicals
        chemicals = Chemical.query.all()
        chemicals_migrated = 0
        lot_numbers_generated = 0

        # Get all chemical IDs that are in kits
        kit_chemical_ids = set([ki.item_id for ki in KitItem.query.filter(KitItem.item_type == 'chemical').all()])

        for chemical in chemicals:
            # Only migrate chemicals not in kits
            if chemical.id not in kit_chemical_ids:
                if not chemical.warehouse_id:
                    chemical.warehouse_id = main_warehouse.id
                    chemicals_migrated += 1

            # Ensure chemical has a lot number
            if not chemical.lot_number or chemical.lot_number.strip() == '':
                # Generate lot number using the LotNumberSequence
                chemical.lot_number = LotNumberSequence.generate_lot_number()
                lot_numbers_generated += 1

        db.session.commit()
        print(f"✓ Migrated {chemicals_migrated} chemicals to Main Warehouse")
        print(f"✓ Generated {lot_numbers_generated} lot numbers for chemicals")


def ensure_kit_items_have_tracking():
    """Ensure all kit items have proper lot/serial numbers."""
    print("Ensuring kit items have proper tracking numbers...")

    with app.app_context():
        # Update kit items (tools and chemicals) to have serial/lot numbers
        kit_items = KitItem.query.all()
        tools_updated = 0
        chemicals_updated = 0

        for ki in kit_items:
            # Update tools to have serial numbers
            if ki.item_type == 'tool':
                tool = Tool.query.get(ki.item_id)
                if tool and (not tool.serial_number or tool.serial_number.strip() == ''):
                    tool.serial_number = f"{tool.tool_number}-{str(tool.id).zfill(3)}"
                    tools_updated += 1
                # Update kit item's serial number field
                if tool and not ki.serial_number:
                    ki.serial_number = tool.serial_number

            # Update chemicals to have lot numbers
            if ki.item_type == 'chemical':
                chemical = Chemical.query.get(ki.item_id)
                if chemical and (not chemical.lot_number or chemical.lot_number.strip() == ''):
                    chemical.lot_number = LotNumberSequence.generate_lot_number()
                    chemicals_updated += 1
                # Update kit item's lot number field
                if chemical and not ki.lot_number:
                    ki.lot_number = chemical.lot_number

        # Update kit expendables to have lot numbers and tracking type
        kit_expendables = KitExpendable.query.all()
        for ke in kit_expendables:
            # Set tracking type if not set
            if not ke.tracking_type:
                ke.tracking_type = 'lot'

            # Ensure lot number exists
            if not ke.lot_number or ke.lot_number.strip() == '':
                ke.lot_number = LotNumberSequence.generate_lot_number()

        db.session.commit()
        print(f"✓ Updated {tools_updated} kit tools with serial numbers")
        print(f"✓ Updated {chemicals_updated} kit chemicals with lot numbers")
        print(f"✓ Updated {len(kit_expendables)} kit expendables with lot numbers")


def main():
    """Run the complete migration."""
    print("=" * 60)
    print("WAREHOUSE MANAGEMENT SYSTEM MIGRATION")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Create tables
        create_tables()
        print()
        
        # Step 2: Add warehouse columns
        add_warehouse_columns()
        print()
        
        # Step 3: Create Main Warehouse
        main_warehouse = create_main_warehouse()
        print()
        
        # Step 4: Migrate tools
        migrate_tools_to_warehouse(main_warehouse)
        print()
        
        # Step 5: Migrate chemicals
        migrate_chemicals_to_warehouse(main_warehouse)
        print()
        
        # Step 6: Ensure kit items have tracking
        ensure_kit_items_have_tracking()
        print()
        
        print("=" * 60)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Warehouse system tables created")
        print("- Main Warehouse created")
        print("- All tools and chemicals migrated to Main Warehouse")
        print("- All items now have proper lot/serial numbers")
        print()
        
    except Exception as e:
        print(f"\n✗ MIGRATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

