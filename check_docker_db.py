from app import create_app
from models_kits import KitTransfer, KitItem
from models import Chemical

app = create_app()
app.app_context().push()

print(f"Transfers: {KitTransfer.query.count()}")
print(f"Kit items (chemical): {KitItem.query.filter_by(item_type='chemical').count()}")
print(f"Chemicals with parent_lot_number: {Chemical.query.filter(Chemical.parent_lot_number.isnot(None)).count()}")
print(f"Chemicals with warehouse_id=None: {Chemical.query.filter_by(warehouse_id=None).count()}")

# Show recent transfers
transfers = KitTransfer.query.order_by(KitTransfer.transfer_date.desc()).limit(5).all()
print(f"\nRecent transfers:")
for t in transfers:
    print(f"  ID: {t.id}, Status: {t.status}, From: {t.from_location_type}/{t.from_location_id}, To: {t.to_location_type}/{t.to_location_id}")

# Show kit items
kit_items = KitItem.query.filter_by(item_type='chemical').all()
print(f"\nKit items (chemical):")
for ki in kit_items:
    print(f"  Kit: {ki.kit_id}, Item ID: {ki.item_id}, Part: {ki.part_number}, Lot: {ki.lot_number}")

# Show child chemicals
child_chems = Chemical.query.filter(Chemical.parent_lot_number.isnot(None)).all()
print(f"\nChild chemicals:")
for c in child_chems:
    print(f"  ID: {c.id}, Part: {c.part_number}, Lot: {c.lot_number}, Parent: {c.parent_lot_number}, Warehouse: {c.warehouse_id}")

