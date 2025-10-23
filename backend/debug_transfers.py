"""
Debug script to check kit transfers and items
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
        print("\n=== KITS ===")
        kits = Kit.query.all()
        for kit in kits:
            print(f"Kit ID: {kit.id}, Name: {kit.name}")
        
        print("\n=== KIT ITEMS (Tools/Chemicals) ===")
        kit_items = KitItem.query.all()
        for item in kit_items:
            print(f"KitItem ID: {item.id}, Kit: {item.kit_id}, Type: {item.item_type}, "
                  f"Item ID: {item.item_id}, Part#: {item.part_number}, "
                  f"Lot: {item.lot_number}, Serial: {item.serial_number}, Qty: {item.quantity}")
            
            # Get the actual item details
            if item.item_type == 'chemical':
                chem = Chemical.query.get(item.item_id)
                if chem:
                    print(f"  -> Chemical: {chem.part_number}, Lot: {chem.lot_number}, Warehouse: {chem.warehouse_id}")
            elif item.item_type == 'tool':
                tool = Tool.query.get(item.item_id)
                if tool:
                    print(f"  -> Tool: {tool.tool_number}, Serial: {tool.serial_number}, Warehouse: {tool.warehouse_id}")
        
        print("\n=== KIT EXPENDABLES ===")
        expendables = KitExpendable.query.all()
        for exp in expendables:
            print(f"Expendable ID: {exp.id}, Kit: {exp.kit_id}, Part#: {exp.part_number}, Qty: {exp.quantity}")
        
        print("\n=== RECENT TRANSFERS ===")
        transfers = KitTransfer.query.order_by(KitTransfer.transfer_date.desc()).limit(10).all()
        for transfer in transfers:
            print(f"Transfer ID: {transfer.id}, Type: {transfer.item_type}, Item ID: {transfer.item_id}")
            print(f"  From: {transfer.from_location_type} {transfer.from_location_id}")
            print(f"  To: {transfer.to_location_type} {transfer.to_location_id}")
            print(f"  Qty: {transfer.quantity}, Status: {transfer.status}, Date: {transfer.transfer_date}")
        
        print("\n=== CHEMICALS ===")
        chemicals = Chemical.query.all()
        for chem in chemicals:
            print(f"Chemical ID: {chem.id}, Part#: {chem.part_number}, Lot: {chem.lot_number}, "
                  f"Qty: {chem.quantity}, Warehouse: {chem.warehouse_id}")
        
        print("\n=== TOOLS ===")
        tools = Tool.query.all()
        for tool in tools:
            print(f"Tool ID: {tool.id}, Tool#: {tool.tool_number}, Serial: {tool.serial_number}, "
                  f"Warehouse: {tool.warehouse_id}")

if __name__ == '__main__':
    main()

