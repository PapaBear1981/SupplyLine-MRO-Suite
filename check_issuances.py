from app import create_app
from models import db, Chemical, ChemicalIssuance

app = create_app()
app.app_context().push()

print('=== CHEMICALS WITH ISSUANCES ===')
issuances = ChemicalIssuance.query.all()

if not issuances:
    print('No issuances found!')
else:
    for i in issuances:
        c = Chemical.query.get(i.chemical_id)
        if c:
            barcode = f'{c.part_number}-{c.lot_number}'
            print(f'Barcode: {barcode}, Issued Qty: {i.quantity}, Hangar: {i.hangar}')

