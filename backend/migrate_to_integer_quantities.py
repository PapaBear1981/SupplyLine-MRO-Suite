#!/usr/bin/env python3
"""
Migration script to convert chemical quantities from Float to Integer.

This script:
1. Rounds all existing decimal quantities to whole numbers
2. Updates the database schema to use Integer columns
3. Validates the migration was successful

Run this script once to migrate existing data.
"""

import sys
from run import app
from models import db, Chemical, ChemicalIssuance
from sqlalchemy import text

def migrate_quantities():
    """Migrate chemical quantities from Float to Integer."""
    
    with app.app_context():
        print("=" * 60)
        print("CHEMICAL QUANTITY MIGRATION: Float → Integer")
        print("=" * 60)
        
        # Step 1: Show current state
        print("\n[STEP 1] Current database state:")
        chemicals = Chemical.query.all()
        print(f"  Found {len(chemicals)} chemicals")
        for chem in chemicals:
            print(f"    {chem.part_number}: {chem.quantity} {chem.unit} (type: {type(chem.quantity).__name__})")
        
        issuances = ChemicalIssuance.query.all()
        print(f"\n  Found {len(issuances)} chemical issuances")
        for iss in issuances:
            print(f"    Issuance #{iss.id}: {iss.quantity} (type: {type(iss.quantity).__name__})")
        
        # Step 2: Round all decimal quantities to integers
        print("\n[STEP 2] Rounding decimal quantities to whole numbers...")
        
        # Update chemicals
        for chem in chemicals:
            old_qty = chem.quantity
            new_qty = round(old_qty)
            if old_qty != new_qty:
                print(f"  {chem.part_number}: {old_qty} → {new_qty}")
                chem.quantity = new_qty
            
            if chem.minimum_stock_level is not None:
                old_min = chem.minimum_stock_level
                new_min = round(old_min)
                if old_min != new_min:
                    print(f"  {chem.part_number} min stock: {old_min} → {new_min}")
                    chem.minimum_stock_level = new_min
        
        # Update issuances
        for iss in issuances:
            old_qty = iss.quantity
            new_qty = round(old_qty)
            if old_qty != new_qty:
                print(f"  Issuance #{iss.id}: {old_qty} → {new_qty}")
                iss.quantity = new_qty
        
        # Commit the changes
        try:
            db.session.commit()
            print("  ✓ All quantities rounded successfully")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error rounding quantities: {e}")
            return False
        
        # Step 3: Recreate tables with Integer columns
        print("\n[STEP 3] Recreating database schema with Integer columns...")
        print("  WARNING: This will drop and recreate the chemicals and chemical_issuances tables")
        
        response = input("  Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("  Migration cancelled by user")
            return False
        
        try:
            # Save all data
            chemicals_data = []
            for chem in Chemical.query.all():
                chemicals_data.append({
                    'id': chem.id,
                    'part_number': chem.part_number,
                    'lot_number': chem.lot_number,
                    'description': chem.description,
                    'manufacturer': chem.manufacturer,
                    'quantity': int(round(chem.quantity)),
                    'unit': chem.unit,
                    'location': chem.location,
                    'category': chem.category,
                    'warehouse_id': chem.warehouse_id,
                    'date_added': chem.date_added,
                    'expiration_date': chem.expiration_date,
                    'minimum_stock_level': int(round(chem.minimum_stock_level)) if chem.minimum_stock_level else None,
                    'notes': chem.notes,
                    'status': chem.status,
                    'is_archived': chem.is_archived
                })
            
            issuances_data = []
            for iss in ChemicalIssuance.query.all():
                issuances_data.append({
                    'id': iss.id,
                    'chemical_id': iss.chemical_id,
                    'quantity': int(round(iss.quantity)),
                    'user_id': iss.user_id,
                    'hangar': iss.hangar,
                    'purpose': iss.purpose,
                    'issue_date': iss.issue_date
                })
            
            print(f"  Saved {len(chemicals_data)} chemicals and {len(issuances_data)} issuances")
            
            # Drop and recreate tables
            db.session.execute(text('DROP TABLE IF EXISTS chemical_issuances'))
            db.session.execute(text('DROP TABLE IF EXISTS chemicals'))
            db.session.commit()
            print("  ✓ Old tables dropped")
            
            # Create new tables with Integer columns
            db.create_all()
            print("  ✓ New tables created with Integer columns")
            
            # Restore data
            for chem_data in chemicals_data:
                db.session.execute(
                    text("""
                        INSERT INTO chemicals (
                            id, part_number, lot_number, description, manufacturer,
                            quantity, unit, location, category, warehouse_id,
                            date_added, expiration_date, minimum_stock_level,
                            notes, status, is_archived
                        ) VALUES (
                            :id, :part_number, :lot_number, :description, :manufacturer,
                            :quantity, :unit, :location, :category, :warehouse_id,
                            :date_added, :expiration_date, :minimum_stock_level,
                            :notes, :status, :is_archived
                        )
                    """),
                    chem_data
                )
            
            for iss_data in issuances_data:
                db.session.execute(
                    text("""
                        INSERT INTO chemical_issuances (
                            id, chemical_id, quantity, user_id,
                            hangar, purpose, issue_date
                        ) VALUES (
                            :id, :chemical_id, :quantity, :user_id,
                            :hangar, :purpose, :issue_date
                        )
                    """),
                    iss_data
                )
            
            db.session.commit()
            print(f"  ✓ Restored {len(chemicals_data)} chemicals and {len(issuances_data)} issuances")
            
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error recreating schema: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 4: Verify migration
        print("\n[STEP 4] Verifying migration...")
        chemicals = Chemical.query.all()
        print(f"  Found {len(chemicals)} chemicals")
        all_integers = True
        for chem in chemicals:
            qty_type = type(chem.quantity).__name__
            min_type = type(chem.minimum_stock_level).__name__ if chem.minimum_stock_level else "None"
            print(f"    {chem.part_number}: {chem.quantity} (type: {qty_type}), min: {chem.minimum_stock_level} (type: {min_type})")
            if qty_type != 'int':
                all_integers = False
                print(f"      ✗ ERROR: Quantity is still {qty_type}, not int!")
        
        issuances = ChemicalIssuance.query.all()
        print(f"\n  Found {len(issuances)} chemical issuances")
        for iss in issuances:
            qty_type = type(iss.quantity).__name__
            print(f"    Issuance #{iss.id}: {iss.quantity} (type: {qty_type})")
            if qty_type != 'int':
                all_integers = False
                print(f"      ✗ ERROR: Quantity is still {qty_type}, not int!")
        
        if all_integers:
            print("\n" + "=" * 60)
            print("✓ MIGRATION SUCCESSFUL!")
            print("  All quantities are now integers")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ MIGRATION FAILED!")
            print("  Some quantities are still not integers")
            print("=" * 60)
            return False

if __name__ == '__main__':
    success = migrate_quantities()
    sys.exit(0 if success else 1)

