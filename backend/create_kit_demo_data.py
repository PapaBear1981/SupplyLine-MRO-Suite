"""
Create demo data for Mobile Warehouse (Kits) system.

This script generates sample kits, items, transfers, reorders, and messages
for testing and demonstration purposes.

Usage:
    python create_kit_demo_data.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    User, AircraftType, Kit, KitBox, KitItem, KitExpendable,
    KitIssuance, KitTransfer, KitReorderRequest, KitMessage
)


def create_demo_data():
    """Create comprehensive demo data for kits system."""
    
    with app.app_context():
        print("🚀 Creating Mobile Warehouse (Kits) Demo Data...")
        print("=" * 60)
        
        # Get or create users
        admin = User.query.filter_by(employee_number='ADMIN001').first()
        if not admin:
            print("❌ Admin user not found. Please run the application first.")
            return
        
        # Create test users if they don't exist
        mechanic1 = User.query.filter_by(employee_number='MECH001').first()
        if not mechanic1:
            mechanic1 = User(
                employee_number='MECH001',
                name='John Mechanic',
                email='john.mechanic@example.com',
                department='Maintenance',
                role='user'
            )
            mechanic1.set_password('password123')
            db.session.add(mechanic1)
        
        mechanic2 = User.query.filter_by(employee_number='MECH002').first()
        if not mechanic2:
            mechanic2 = User(
                employee_number='MECH002',
                name='Jane Technician',
                email='jane.tech@example.com',
                department='Maintenance',
                role='user'
            )
            mechanic2.set_password('password123')
            db.session.add(mechanic2)
        
        materials_user = User.query.filter_by(employee_number='MAT001').first()
        if not materials_user:
            materials_user = User(
                employee_number='MAT001',
                name='Bob Materials',
                email='bob.materials@example.com',
                department='Materials',
                role='admin'
            )
            materials_user.set_password('password123')
            db.session.add(materials_user)
        
        db.session.commit()
        print("✅ Users created/verified")
        
        # Get aircraft types
        q400 = AircraftType.query.filter_by(name='Q400').first()
        rj85 = AircraftType.query.filter_by(name='RJ85').first()
        cl415 = AircraftType.query.filter_by(name='CL415').first()
        
        if not all([q400, rj85, cl415]):
            print("❌ Aircraft types not found. Please run migrations first.")
            return
        
        print("✅ Aircraft types verified")
        
        # Create kits
        kits_data = [
            {
                'name': 'Q400-Kit-Alpha',
                'aircraft_type': q400,
                'description': 'Primary maintenance kit for Q400 fleet',
                'status': 'active'
            },
            {
                'name': 'Q400-Kit-Bravo',
                'aircraft_type': q400,
                'description': 'Secondary Q400 kit for remote operations',
                'status': 'active'
            },
            {
                'name': 'RJ85-Kit-Main',
                'aircraft_type': rj85,
                'description': 'Main RJ85 maintenance kit',
                'status': 'active'
            },
            {
                'name': 'CL415-Kit-Fire',
                'aircraft_type': cl415,
                'description': 'CL415 water bomber maintenance kit',
                'status': 'active'
            },
            {
                'name': 'Q400-Kit-Retired',
                'aircraft_type': q400,
                'description': 'Retired kit for reference',
                'status': 'inactive'
            }
        ]
        
        kits = []
        for kit_data in kits_data:
            existing_kit = Kit.query.filter_by(name=kit_data['name']).first()
            if not existing_kit:
                kit = Kit(
                    name=kit_data['name'],
                    aircraft_type_id=kit_data['aircraft_type'].id,
                    description=kit_data['description'],
                    status=kit_data['status'],
                    created_by=admin.id
                )
                db.session.add(kit)
                kits.append(kit)
            else:
                kits.append(existing_kit)
        
        db.session.commit()
        print(f"✅ Created {len(kits)} kits")
        
        # Create boxes for each kit
        box_types = ['expendable', 'tooling', 'consumable', 'loose', 'floor']
        boxes_created = 0
        
        for kit in kits:
            if kit.status == 'active':
                for i, box_type in enumerate(box_types, 1):
                    existing_box = KitBox.query.filter_by(
                        kit_id=kit.id,
                        box_type=box_type
                    ).first()
                    
                    if not existing_box:
                        box = KitBox(
                            kit_id=kit.id,
                            box_number=i,
                            box_type=box_type,
                            description=f'{box_type.capitalize()} box for {kit.name}'
                        )
                        db.session.add(box)
                        boxes_created += 1
        
        db.session.commit()
        print(f"✅ Created {boxes_created} kit boxes")
        
        # Create expendables for active kits
        expendables_created = 0
        sample_expendables = [
            {'part_number': 'EXP-001', 'description': 'Safety Wire', 'quantity': 100, 'unit': 'ft'},
            {'part_number': 'EXP-002', 'description': 'Cleaning Rags', 'quantity': 50, 'unit': 'ea'},
            {'part_number': 'EXP-003', 'description': 'Zip Ties', 'quantity': 200, 'unit': 'ea'},
            {'part_number': 'EXP-004', 'description': 'Masking Tape', 'quantity': 10, 'unit': 'roll'},
            {'part_number': 'EXP-005', 'description': 'Gloves', 'quantity': 25, 'unit': 'pair'},
        ]
        
        for kit in kits:
            if kit.status == 'active':
                expendable_box = KitBox.query.filter_by(
                    kit_id=kit.id,
                    box_type='expendable'
                ).first()
                
                if expendable_box:
                    for exp_data in sample_expendables:
                        existing_exp = KitExpendable.query.filter_by(
                            kit_id=kit.id,
                            part_number=exp_data['part_number']
                        ).first()
                        
                        if not existing_exp:
                            expendable = KitExpendable(
                                kit_id=kit.id,
                                box_id=expendable_box.id,
                                part_number=exp_data['part_number'],
                                description=exp_data['description'],
                                quantity=exp_data['quantity'],
                                unit=exp_data['unit'],
                                location=f'Box {expendable_box.box_number}',
                                status='available',
                                minimum_stock_level=exp_data['quantity'] // 4
                            )
                            db.session.add(expendable)
                            expendables_created += 1
        
        db.session.commit()
        print(f"✅ Created {expendables_created} expendable items")
        
        # Create issuances
        issuances_created = 0
        for kit in kits[:3]:  # Only for first 3 active kits
            if kit.status == 'active':
                expendables = KitExpendable.query.filter_by(kit_id=kit.id).limit(3).all()
                
                for expendable in expendables:
                    # Create 2-3 issuances per item
                    for i in range(random.randint(2, 3)):
                        issuance = KitIssuance(
                            kit_id=kit.id,
                            item_type='expendable',
                            item_id=expendable.id,
                            issued_by=random.choice([mechanic1.id, mechanic2.id]),
                            quantity=random.randint(1, 5),
                            purpose='Maintenance',
                            work_order=f'WO-{random.randint(1000, 9999)}',
                            issued_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        )
                        db.session.add(issuance)
                        issuances_created += 1
        
        db.session.commit()
        print(f"✅ Created {issuances_created} issuances")
        
        # Create transfers
        transfers_created = 0
        if len(kits) >= 2:
            for i in range(5):
                source_kit = random.choice(kits[:3])
                dest_kit = random.choice([k for k in kits[:3] if k.id != source_kit.id])
                
                expendable = KitExpendable.query.filter_by(kit_id=source_kit.id).first()
                
                if expendable:
                    transfer = KitTransfer(
                        item_type='expendable',
                        item_id=expendable.id,
                        from_location_type='kit',
                        from_location_id=source_kit.id,
                        to_location_type='kit',
                        to_location_id=dest_kit.id,
                        quantity=random.randint(1, 3),
                        transferred_by=mechanic1.id,
                        transfer_date=datetime.utcnow() - timedelta(days=random.randint(1, 15)),
                        status=random.choice(['pending', 'completed', 'completed', 'completed'])
                    )
                    db.session.add(transfer)
                    transfers_created += 1
        
        db.session.commit()
        print(f"✅ Created {transfers_created} transfers")
        
        # Create reorder requests
        reorders_created = 0
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['pending', 'approved', 'fulfilled']
        
        for kit in kits[:3]:
            if kit.status == 'active':
                expendables = KitExpendable.query.filter_by(kit_id=kit.id).limit(3).all()
                
                for expendable in expendables:
                    reorder = KitReorderRequest(
                        kit_id=kit.id,
                        item_type='expendable',
                        item_id=expendable.id,
                        part_number=expendable.part_number,
                        description=expendable.description,
                        quantity_requested=random.randint(10, 50),
                        priority=random.choice(priorities),
                        requested_by=random.choice([mechanic1.id, mechanic2.id]),
                        requested_date=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                        status=random.choice(statuses),
                        notes=f'Restock needed for {kit.name}'
                    )
                    db.session.add(reorder)
                    reorders_created += 1
        
        db.session.commit()
        print(f"✅ Created {reorders_created} reorder requests")
        
        # Create messages
        messages_created = 0
        for kit in kits[:3]:
            if kit.status == 'active':
                # Create a few messages per kit
                for i in range(random.randint(2, 4)):
                    message = KitMessage(
                        kit_id=kit.id,
                        sender_id=random.choice([mechanic1.id, mechanic2.id, materials_user.id]),
                        recipient_id=materials_user.id if random.random() > 0.5 else None,
                        subject=random.choice([
                            'Low stock alert',
                            'Transfer request',
                            'Reorder status',
                            'Kit maintenance needed'
                        ]),
                        message=f'This is a demo message regarding {kit.name}. Please review and respond.',
                        is_read=random.choice([True, False]),
                        sent_date=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    )
                    db.session.add(message)
                    messages_created += 1
        
        db.session.commit()
        print(f"✅ Created {messages_created} messages")
        
        print("=" * 60)
        print("🎉 Demo data creation complete!")
        print("\nSummary:")
        print(f"  - Kits: {len(kits)}")
        print(f"  - Boxes: {boxes_created}")
        print(f"  - Expendables: {expendables_created}")
        print(f"  - Issuances: {issuances_created}")
        print(f"  - Transfers: {transfers_created}")
        print(f"  - Reorder Requests: {reorders_created}")
        print(f"  - Messages: {messages_created}")
        print("\nTest Users:")
        print("  - MECH001 / password123 (Mechanic)")
        print("  - MECH002 / password123 (Mechanic)")
        print("  - MAT001 / password123 (Materials)")


if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"\n❌ Error creating demo data: {str(e)}")
        import traceback
        traceback.print_exc()

