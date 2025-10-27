#!/usr/bin/env python3
"""Check transfers directly in the database"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models_kits import KitTransfer, KitItem
from models import db, Chemical
from app import create_app

app = create_app()

with app.app_context():
    # Check for all transfers
    all_transfers = KitTransfer.query.all()
    print(f"Total transfers: {len(all_transfers)}")
    
    # Check for pending transfers
    pending_transfers = KitTransfer.query.filter_by(status='pending').all()
    print(f"Pending transfers: {len(pending_transfers)}")
    
    # Check for completed transfers
    completed_transfers = KitTransfer.query.filter_by(status='completed').all()
    print(f"Completed transfers: {len(completed_transfers)}")
    
    # Show recent transfers
    recent_transfers = KitTransfer.query.order_by(KitTransfer.transfer_date.desc()).limit(10).all()
    print(f"\nRecent transfers:")
    for t in recent_transfers:
        print(f"  ID: {t.id}, Type: {t.item_type}, From: {t.from_location_type}/{t.from_location_id}, To: {t.to_location_type}/{t.to_location_id}, Qty: {t.quantity}, Status: {t.status}")
    
    # Check for kit items
    kit_items = KitItem.query.filter_by(item_type='chemical').all()
    print(f"\nChemical kit items: {len(kit_items)}")
    
    if kit_items:
        print("\nChemical kit items:")
        for ki in kit_items[:10]:
            print(f"  Kit: {ki.kit_id}, Item ID: {ki.item_id}, Part: {ki.part_number}, Lot: {ki.lot_number}, Qty: {ki.quantity}")
    
    # Check for chemicals with warehouse_id = None
    no_warehouse_chems = Chemical.query.filter_by(warehouse_id=None).all()
    print(f"\nChemicals with warehouse_id=None: {len(no_warehouse_chems)}")
    
    if no_warehouse_chems:
        print("\nChemicals with no warehouse:")
        for c in no_warehouse_chems[:10]:
            print(f"  ID: {c.id}, Part: {c.part_number}, Lot: {c.lot_number}, Qty: {c.quantity}, Parent: {c.parent_lot_number}")

