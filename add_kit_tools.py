"""
Script to add 125 tools to kits (25 per kit for 5 kits)
These tools will be created as separate Tool records and transferred to kits
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from extensions import db
from models import Tool
from models_kits import Kit, KitItem, Box
from datetime import datetime

app = create_app()

with app.app_context():
    # Get all kits
    kits = Kit.query.all()
    print(f"Found {len(kits)} kits")
    
    # Get the warehouse
    warehouse_id = 1
    
    # Tool categories for variety
    categories = [
        "Hand Tools",
        "Power Tools", 
        "Measuring Tools",
        "Testing Equipment",
        "Fastening Tools"
    ]
    
    tool_counter = 51  # Start after the existing 50 tools
    
    for kit in kits:
        print(f"\nProcessing Kit: {kit.name} (ID: {kit.id})")
        
        # Get or create a box for this kit
        box = Box.query.filter_by(kit_id=kit.id).first()
        if not box:
            box = Box(
                kit_id=kit.id,
                box_number=f"BOX-{kit.id}-001",
                description=f"Main box for {kit.name}",
                created_at=datetime.utcnow()
            )
            db.session.add(box)
            db.session.flush()
            print(f"  Created box: {box.box_number}")
        
        # Create 25 tools for this kit
        for i in range(25):
            tool_number = f"KIT-TOOL-{tool_counter:04d}"
            serial_number = f"SN{tool_counter:05d}"
            category = categories[i % len(categories)]
            
            # Create the tool
            tool = Tool(
                tool_number=tool_number,
                serial_number=serial_number,
                description=f"{category} for {kit.name}",
                condition="Good",
                location=f"Kit {kit.id} - Box {box.box_number}",
                category=category,
                status="available",
                warehouse_id=None,  # Not in warehouse, in kit
                created_at=datetime.utcnow()
            )
            db.session.add(tool)
            db.session.flush()  # Get the tool ID
            
            # Create kit item linking tool to kit
            kit_item = KitItem(
                kit_id=kit.id,
                box_id=box.id,
                item_type="tool",
                item_id=tool.id,
                part_number=tool_number,
                description=tool.description,
                quantity=1,
                status="active",
                created_at=datetime.utcnow()
            )
            db.session.add(kit_item)
            
            tool_counter += 1
        
        print(f"  Added 25 tools to kit {kit.name}")
    
    # Commit all changes
    db.session.commit()
    print(f"\n✅ Successfully added {tool_counter - 51} tools to kits")
    print(f"Total tools in database should now be: {Tool.query.count()}")

