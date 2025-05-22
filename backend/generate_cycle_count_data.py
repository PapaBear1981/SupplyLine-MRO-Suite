import os
import sys
import random
from datetime import datetime, timedelta
import sqlite3

# Add the parent directory to the path so we can import the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the models
from models import db, Tool, Chemical, User
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment
)

def generate_sample_data():
    """Generate sample data for cycle count functionality"""
    print("Generating sample cycle count data...")

    # Get admin user for created_by fields
    admin_user = User.query.filter_by(employee_number='ADMIN001').first()
    if not admin_user:
        print("Admin user not found. Using first user in database.")
        admin_user = User.query.first()

    if not admin_user:
        print("No users found in database. Cannot generate sample data.")
        return

    # Create sample schedules
    schedules = []
    schedule_data = [
        {
            'name': 'Monthly Tool Count',
            'description': 'Monthly count of tools using random sampling method',
            'frequency': 'monthly',
            'method': 'random'
        },
        {
            'name': 'Quarterly Chemical Inventory',
            'description': 'Quarterly count of chemicals using ABC analysis',
            'frequency': 'quarterly',
            'method': 'abc'
        },
        {
            'name': 'Annual Full Inventory',
            'description': 'Annual count of all inventory items',
            'frequency': 'annual',
            'method': 'location'
        }
    ]

    for data in schedule_data:
        schedule = CycleCountSchedule(
            name=data['name'],
            description=data['description'],
            frequency=data['frequency'],
            method=data['method'],
            created_by=admin_user.id,
            is_active=True
        )
        db.session.add(schedule)
        schedules.append(schedule)

    db.session.commit()
    print(f"Created {len(schedules)} sample schedules")

    # Create sample batches
    batches = []
    batch_data = [
        {
            'schedule': schedules[0],
            'name': 'May 2025 Tool Count',
            'status': 'in_progress',
            'start_date': datetime.now() - timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=5),
            'notes': 'Monthly count of tools for May 2025'
        },
        {
            'schedule': schedules[1],
            'name': 'Q2 2025 Chemical Inventory',
            'status': 'pending',
            'start_date': datetime.now() + timedelta(days=10),
            'end_date': datetime.now() + timedelta(days=15),
            'notes': 'Quarterly count of chemicals for Q2 2025'
        },
        {
            'schedule': schedules[2],
            'name': 'Annual Inventory 2025',
            'status': 'completed',
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now() - timedelta(days=25),
            'notes': 'Annual count of all inventory items for 2025'
        }
    ]

    for data in batch_data:
        batch = CycleCountBatch(
            schedule_id=data['schedule'].id,
            name=data['name'],
            status=data['status'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            created_by=admin_user.id,
            notes=data['notes']
        )
        db.session.add(batch)
        batches.append(batch)

    db.session.commit()
    print(f"Created {len(batches)} sample batches")

    # Get tools and chemicals for items
    tools = Tool.query.limit(10).all()
    chemicals = Chemical.query.limit(10).all()

    if not tools:
        print("No tools found in database. Skipping tool items.")

    if not chemicals:
        print("No chemicals found in database. Skipping chemical items.")

    # Create sample items
    items = []

    # Add tool items to the first batch
    for tool in tools:
        item = CycleCountItem(
            batch_id=batches[0].id,
            item_type='tool',
            item_id=tool.id,
            expected_quantity=1,
            expected_location=tool.location,
            status=random.choice(['pending', 'counted', 'counted', 'counted'])
        )
        db.session.add(item)
        items.append(item)

    # Add chemical items to the second batch
    for chemical in chemicals:
        item = CycleCountItem(
            batch_id=batches[1].id,
            item_type='chemical',
            item_id=chemical.id,
            expected_quantity=chemical.quantity,
            expected_location=chemical.location,
            status='pending'
        )
        db.session.add(item)
        items.append(item)

    # Add both tool and chemical items to the third batch
    for tool in tools[:5]:
        item = CycleCountItem(
            batch_id=batches[2].id,
            item_type='tool',
            item_id=tool.id,
            expected_quantity=1,
            expected_location=tool.location,
            status='counted'
        )
        db.session.add(item)
        items.append(item)

    for chemical in chemicals[:5]:
        item = CycleCountItem(
            batch_id=batches[2].id,
            item_type='chemical',
            item_id=chemical.id,
            expected_quantity=chemical.quantity,
            expected_location=chemical.location,
            status='counted'
        )
        db.session.add(item)
        items.append(item)

    db.session.commit()
    print(f"Created {len(items)} sample items")

    # Create sample results for counted items
    results = []
    for item in items:
        if item.status == 'counted':
            # Randomly decide if there's a discrepancy
            has_discrepancy = random.choice([True, False, False, False])

            # Determine discrepancy type and values
            discrepancy_type = None
            actual_quantity = item.expected_quantity
            actual_location = item.expected_location
            condition = 'good'

            if has_discrepancy:
                discrepancy_type = random.choice(['quantity', 'location', 'condition'])

                if discrepancy_type == 'quantity':
                    # Adjust quantity by +/- 10-50%
                    adjustment = random.uniform(0.5, 1.5)
                    actual_quantity = round(item.expected_quantity * adjustment, 2)
                elif discrepancy_type == 'location':
                    locations = ['Shelf A', 'Shelf B', 'Drawer 1', 'Drawer 2', 'Cabinet 3']
                    actual_location = random.choice([loc for loc in locations if loc != item.expected_location])
                elif discrepancy_type == 'condition':
                    condition = random.choice(['damaged', 'expired', 'missing'])

            result = CycleCountResult(
                item_id=item.id,
                counted_by=admin_user.id,
                counted_at=datetime.now() - timedelta(days=random.randint(1, 5)),
                actual_quantity=actual_quantity,
                actual_location=actual_location,
                condition=condition,
                notes=f"Count performed by {admin_user.name}",
                has_discrepancy=has_discrepancy,
                discrepancy_type=discrepancy_type,
                discrepancy_notes="Discrepancy found during count" if has_discrepancy else None
            )
            db.session.add(result)
            results.append(result)

    db.session.commit()
    print(f"Created {len(results)} sample results")

    # Create sample adjustments for some results with discrepancies
    adjustments = []
    for result in results:
        if result.has_discrepancy and random.choice([True, False]):
            adjustment_type = result.discrepancy_type
            old_value = None
            new_value = None

            if adjustment_type == 'quantity':
                old_value = str(result.item.expected_quantity)
                new_value = str(result.actual_quantity)
            elif adjustment_type == 'location':
                old_value = result.item.expected_location
                new_value = result.actual_location
            elif adjustment_type == 'condition':
                old_value = 'good'
                new_value = result.condition

            adjustment = CycleCountAdjustment(
                result_id=result.id,
                approved_by=admin_user.id,
                adjustment_type=adjustment_type,
                old_value=old_value,
                new_value=new_value,
                notes="Adjustment approved after verification"
            )
            db.session.add(adjustment)
            adjustments.append(adjustment)

    db.session.commit()
    print(f"Created {len(adjustments)} sample adjustments")

    print("Sample data generation complete!")

if __name__ == "__main__":
    # Import app context
    from app import create_app
    app = create_app()

    with app.app_context():
        generate_sample_data()
