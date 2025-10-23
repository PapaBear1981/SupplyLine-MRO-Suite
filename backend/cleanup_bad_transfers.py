"""
Cleanup script to remove bad kit items that point to warehouse chemicals
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from models import db, Chemical, Tool
from models_kits import Kit, KitItem, KitExpendable, KitTransfer
from config import Config

# Create app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def main():
    with app.app_context():
        print("\n=== CLEANING UP BAD KIT ITEMS ===")
        
        # Find kit items that point to chemicals still in warehouses
        bad_items = []
        kit_items = KitItem.query.filter_by(item_type='chemical').all()
        
        for item in kit_items:
            chem = Chemical.query.get(item.item_id)
            if chem and chem.warehouse_id is not None:
                print(f"Found bad KitItem {item.id} in Kit {item.kit_id}: "
                      f"Points to Chemical {chem.id} ({chem.part_number} {chem.lot_number}) "
                      f"still in Warehouse {chem.warehouse_id}")
                bad_items.append(item)
        
        if bad_items:
            print(f"\nFound {len(bad_items)} bad kit items to remove")
            for item in bad_items:
                print(f"  Removing KitItem {item.id} from Kit {item.kit_id}")
                db.session.delete(item)
            
            db.session.commit()
            print("\nCleanup complete!")
        else:
            print("\nNo bad kit items found - database is clean!")
        
        # Show current state
        print("\n=== CURRENT KIT ITEMS ===")
        kit_items = KitItem.query.all()
        for item in kit_items:
            if item.item_type == 'chemical':
                chem = Chemical.query.get(item.item_id)
                if chem:
                    print(f"KitItem {item.id} in Kit {item.kit_id}: "
                          f"Chemical {chem.id} ({chem.part_number} {chem.lot_number}) "
                          f"Warehouse: {chem.warehouse_id}")

if __name__ == '__main__':
    main()

