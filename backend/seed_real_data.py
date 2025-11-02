"""
Seed database with real aircraft maintenance tools, chemicals, and kits.
This script creates realistic data for Boeing 737, RJ85, and Q400 aircraft.
"""
import os
import sys
from datetime import datetime


# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask

from models import Chemical, Expendable, LotNumberSequence, Tool, User, Warehouse, db
from models_kits import AircraftType, Kit, KitBox, KitExpendable, KitItem


# Create Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    os.path.dirname(__file__), "..", "database", "tools.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Real aircraft tools (50 items)
AIRCRAFT_TOOLS = [
    # Hand Tools
    ("MS25171-3", "Torque Wrench 0-150 in-lbs", "Precision torque wrench for aircraft fasteners"),
    ("MS25171-4", "Torque Wrench 0-600 in-lbs", "Heavy duty torque wrench"),
    ("MS25171-5", "Torque Wrench 0-1000 in-lbs", "High torque wrench for large fasteners"),
    ("AN960-10", "Flat Washer Set", "Assorted AN960 flat washers"),
    ("MS20470AD4-6", "Rivet Set", "Universal head rivets assortment"),
    ("BACC30AM3D", "Safety Wire Pliers", "Milbar safety wire pliers"),
    ("MS20995C32", "Safety Wire Dispenser", "0.032 inch safety wire"),
    ("AN3-5A", "Bolt Assortment", "AN3 bolts various lengths"),
    ("AN4-10A", "Bolt Assortment", "AN4 bolts various lengths"),
    ("AN5-20A", "Bolt Assortment", "AN5 bolts various lengths"),

    # Measuring Tools
    ("MS35769-3", "Dial Indicator 0.001", "Precision dial indicator"),
    ("MS35338-1", "Micrometer 0-1 inch", "Outside micrometer"),
    ("MS35338-2", "Micrometer 1-2 inch", "Outside micrometer"),
    ("MS35338-3", "Micrometer 2-3 inch", "Outside micrometer"),
    ("GGG-R-791", "Steel Rule 6 inch", "Precision steel rule"),
    ("GGG-R-791-12", "Steel Rule 12 inch", "Precision steel rule"),
    ("MS35769-5", "Depth Gauge", "Precision depth gauge"),
    ("MS35338-10", "Telescoping Gauge Set", "Bore measurement gauges"),

    # Specialized Tools
    ("BACC13AK3-1", "Swaging Tool", "Cable swaging tool"),
    ("MS25171-10", "Crimping Tool", "Wire terminal crimper"),
    ("MS25171-12", "Pin Removal Tool", "Connector pin extraction"),
    ("BACC45FT3", "Cable Tension Meter", "Control cable tension gauge"),
    ("MS25171-15", "Rivet Gun", "Pneumatic rivet gun"),
    ("MS25171-16", "Bucking Bar Set", "Rivet bucking bars"),
    ("MS25171-18", "Drill Motor", "Pneumatic drill motor"),
    ("MS25171-20", "Countersink Cutter", "100° countersink"),
    ("MS25171-22", "Deburring Tool", "Edge deburring tool"),
    ("MS25171-24", "Reamer Set", "Precision reamers"),

    # Inspection Tools
    ("MS25171-30", "Borescope", "Flexible inspection scope"),
    ("MS25171-32", "Magnifying Glass 10x", "Inspection magnifier"),
    ("MS25171-34", "Flashlight LED", "High intensity LED light"),
    ("MS25171-36", "Mirror Inspection Set", "Telescoping mirrors"),
    ("MS25171-38", "Feeler Gauge Set", "Precision feeler gauges"),
    ("MS25171-40", "Thread Pitch Gauge", "Thread identification"),
    ("MS25171-42", "Radius Gauge Set", "Fillet radius gauges"),

    # Power Tools
    ("MS25171-50", "Impact Wrench 1/2", "Pneumatic impact wrench"),
    ("MS25171-52", "Grinder 4 inch", "Angle grinder"),
    ("MS25171-54", "Sander Orbital", "Pneumatic orbital sander"),
    ("MS25171-56", "Polisher 6 inch", "Pneumatic polisher"),
    ("MS25171-58", "Shear Pneumatic", "Sheet metal shear"),

    # Electrical Tools
    ("MS25171-60", "Multimeter Digital", "Fluke digital multimeter"),
    ("MS25171-62", "Wire Stripper", "Automatic wire stripper"),
    ("MS25171-64", "Crimper Electrical", "Electrical terminal crimper"),
    ("MS25171-66", "Soldering Iron", "Temperature controlled iron"),
    ("MS25171-68", "Heat Gun", "Variable temperature heat gun"),

    # Hydraulic Tools
    ("MS25171-70", "Pressure Gauge 0-3000 PSI", "Hydraulic pressure gauge"),
    ("MS25171-72", "Hydraulic Hand Pump", "Manual hydraulic pump"),
    ("MS25171-74", "Flaring Tool", "Hydraulic line flaring tool"),
    ("MS25171-76", "Tube Bender", "Hydraulic tube bender"),
    ("MS25171-78", "Tube Cutter", "Precision tube cutter"),
]


# Real aircraft chemicals (50 items)
AIRCRAFT_CHEMICALS = [
    # Cleaners
    ("MIL-PRF-680", "Type II Degreaser", "Stoddard solvent cleaner", "Gallon"),
    ("MIL-PRF-87937", "Type I Cleaner", "General purpose cleaner", "Quart"),
    ("MIL-PRF-25769", "Type II Cleaner", "Heavy duty cleaner", "Gallon"),
    ("AMS-1526", "Oxygen System Cleaner", "Non-flammable cleaner", "Pint"),
    ("AMS-1550", "Hydraulic System Cleaner", "Flushing fluid", "Gallon"),
    ("MIL-PRF-81309", "Type III Cleaner", "Precision cleaner", "Quart"),
    ("SAE-AMS-1428", "Dry Cleaning Solvent", "Spot remover", "Pint"),
    ("MIL-PRF-32295", "Aqueous Cleaner", "Water-based cleaner", "Gallon"),

    # Lubricants
    ("MIL-PRF-23827", "Type I Grease", "General purpose grease", "Tube"),
    ("MIL-PRF-81322", "Type II Grease", "High temp grease", "Tube"),
    ("MIL-PRF-32014", "Type III Grease", "Extreme pressure grease", "Cartridge"),
    ("MIL-PRF-7870", "Type I Oil", "Hydraulic fluid", "Quart"),
    ("MIL-PRF-5606", "Type II Oil", "Aircraft hydraulic fluid", "Gallon"),
    ("MIL-PRF-83282", "Type III Oil", "Synthetic hydraulic fluid", "Quart"),
    ("MIL-PRF-6085", "Turbine Oil", "Gas turbine lubricant", "Quart"),
    ("MIL-PRF-23699", "Synthetic Oil", "Jet engine oil", "Quart"),

    # Sealants
    ("MIL-PRF-81733", "Class A Sealant", "Fuel tank sealant", "Cartridge"),
    ("MIL-PRF-81733", "Class B Sealant", "Faying surface sealant", "Cartridge"),
    ("MIL-PRF-81733", "Class C Sealant", "Brush-on sealant", "Pint"),
    ("AMS-S-8802", "Polysulfide Sealant", "Two-part sealant", "Kit"),
    ("AMS-3277", "Silicone Sealant", "RTV sealant", "Tube"),
    ("MIL-PRF-46010", "Corrosion Inhibitor", "Protective coating", "Quart"),

    # Adhesives
    ("MMM-AF-163-2", "Film Adhesive", "Structural adhesive", "Roll"),
    ("MIL-PRF-25463", "Epoxy Adhesive", "Two-part epoxy", "Kit"),
    ("AMS-3832", "Acrylic Adhesive", "Fast-cure adhesive", "Tube"),
    ("MIL-PRF-46147", "Cyanoacrylate", "Super glue", "Bottle"),

    # Paints & Coatings
    ("MIL-PRF-85285", "Type I Primer", "Epoxy primer", "Quart"),
    ("MIL-PRF-85285", "Type II Primer", "Polyurethane primer", "Quart"),
    ("TT-E-489", "Enamel Paint", "Topcoat enamel", "Quart"),
    ("MIL-PRF-23377", "Polyurethane Topcoat", "Exterior paint", "Quart"),
    ("TT-P-645", "Zinc Chromate Primer", "Corrosion resistant", "Pint"),

    # Specialty Chemicals
    ("MIL-PRF-16173", "Corrosion Remover", "Rust remover", "Quart"),
    ("MIL-PRF-680", "Penetrating Oil", "Rust penetrant", "Can"),
    ("AMS-2644", "Passivation Solution", "Stainless treatment", "Gallon"),
    ("MIL-PRF-81309", "Deicing Fluid", "Type I deicing", "Gallon"),
    ("AMS-1424", "Anti-Seize Compound", "Thread lubricant", "Tube"),
    ("MIL-PRF-16173", "Paint Stripper", "Aircraft stripper", "Gallon"),
    ("AMS-3155", "Mold Release", "Composite release", "Can"),

    # Inspection Materials
    ("AMS-2644", "Penetrant Dye", "NDT penetrant", "Can"),
    ("AMS-2647", "Developer Powder", "NDT developer", "Can"),
    ("AMS-3155", "Magnetic Particles", "Mag particle inspection", "Can"),
    ("AMS-2644", "Ultrasonic Couplant", "UT gel", "Bottle"),

    # Consumables
    ("MIL-PRF-680", "Shop Towels", "Lint-free towels", "Box"),
    ("AMS-3155", "Masking Tape 2 inch", "High-temp tape", "Roll"),
    ("MIL-PRF-16173", "Aluminum Tape", "Foil tape", "Roll"),
    ("AMS-2644", "Abrasive Paper 220 grit", "Sandpaper", "Sheet"),
    ("AMS-2647", "Abrasive Paper 400 grit", "Sandpaper", "Sheet"),
    ("AMS-3155", "Steel Wool Fine", "Polishing wool", "Pad"),
    ("MIL-PRF-680", "Cotton Swabs", "Cleaning swabs", "Box"),
]


def clear_existing_data():
    """Remove all existing tools, chemicals, and kits."""
    print("Clearing existing data...")

    # Clear kit-related data first (foreign key constraints)
    KitExpendable.query.delete()
    KitItem.query.delete()
    KitBox.query.delete()
    Kit.query.delete()

    # Clear tools and chemicals
    Tool.query.delete()
    Chemical.query.delete()

    db.session.commit()
    print("✓ Existing data cleared")


def create_warehouses():
    """Create warehouses if they don't exist."""
    print("Creating warehouses...")

    warehouse = Warehouse.query.filter_by(name="Main Warehouse").first()
    if not warehouse:
        warehouse = Warehouse(
            name="Main Warehouse",
            address="123 Airport Way",
            city="Seattle",
            state="WA",
            zip_code="98101"
        )
        db.session.add(warehouse)
        db.session.commit()
        print("✓ Created Main Warehouse")
    else:
        print("✓ Main Warehouse already exists")

    return warehouse


def create_aircraft_types():
    """Create aircraft types if they don't exist."""
    print("Creating aircraft types...")

    aircraft_types = {}

    for name in ["Boeing 737", "RJ85", "Q400"]:
        aircraft_type = AircraftType.query.filter_by(name=name).first()
        if not aircraft_type:
            aircraft_type = AircraftType(name=name)
            db.session.add(aircraft_type)
        aircraft_types[name] = aircraft_type

    db.session.commit()
    print(f"✓ Created {len(aircraft_types)} aircraft types")

    return aircraft_types


def seed_tools(warehouse):
    """Seed 50 real aircraft tools."""
    print("Seeding 50 aircraft tools...")

    tools = []
    for i, (tool_num, name, desc) in enumerate(AIRCRAFT_TOOLS, 1):
        # Measuring tools (11-18) need calibration
        needs_calibration = (i >= 11 and i <= 18)

        tool = Tool(
            tool_number=tool_num,
            serial_number=f"SN{10000 + i:05d}",
            description=f"{name} - {desc}",
            condition="Good",
            location=warehouse.name,
            warehouse_id=warehouse.id,
            category="Hand Tool" if i <= 10 else "Power Tool" if i > 35 else "Measuring Tool",
            requires_calibration=needs_calibration,
            next_calibration_date=datetime(2025, 12, 31) if needs_calibration else None,
            calibration_status="current" if needs_calibration else "not_applicable"
        )
        tools.append(tool)
        db.session.add(tool)

    db.session.commit()
    print(f"✓ Created {len(tools)} tools")

    return tools


def seed_chemicals(warehouse):
    """Seed 50 real aircraft chemicals."""
    print("Seeding 50 aircraft chemicals...")

    chemicals = []
    for i, (part_num, name, desc, unit) in enumerate(AIRCRAFT_CHEMICALS, 1):
        chemical = Chemical(
            part_number=part_num,
            lot_number=f"LOT{20250000 + i:05d}",
            description=f"{name} - {desc}",
            manufacturer="Boeing Approved",
            quantity=10,  # Integer only
            unit=unit,
            location=warehouse.name,
            warehouse_id=warehouse.id,
            category="Cleaner" if i <= 8 else "Lubricant" if i <= 16 else "Sealant" if i <= 23 else "Adhesive" if i <= 27 else "Paint" if i <= 32 else "Specialty",
            expiration_date=datetime(2026, 12, 31),
            minimum_stock_level=5
        )
        chemicals.append(chemical)
        db.session.add(chemical)

    db.session.commit()
    print(f"✓ Created {len(chemicals)} chemicals")

    return chemicals


def create_kit_boxes(kit, box_types):
    """Create 9 boxes for a kit (4 expendables, 3 tools, 2 consumables)."""
    boxes = []

    for box_type, count in box_types.items():
        for i in range(count):
            box = KitBox(
                kit_id=kit.id,
                box_number=f"{box_type[0].upper()}{i+1:02d}",
                box_type=box_type,
                description=f"{box_type.title()} Box {i+1}"
            )
            boxes.append(box)
            db.session.add(box)

    db.session.flush()  # Get IDs without committing
    return boxes


def populate_kit_with_items(kit, boxes, tools, chemicals):
    """Populate kit boxes with tools, expendables, and chemicals."""

    # Separate boxes by type
    tool_boxes = [b for b in boxes if b.box_type == "tools"]
    expendable_boxes = [b for b in boxes if b.box_type == "expendables"]
    consumable_boxes = [b for b in boxes if b.box_type == "consumables"]

    # Add tools to tool boxes (distribute evenly)
    tools_per_box = len(tools) // len(tool_boxes) if tool_boxes else 0
    tool_idx = 0

    for box in tool_boxes:
        for _ in range(tools_per_box):
            if tool_idx < len(tools):
                tool = tools[tool_idx]
                kit_item = KitItem(
                    kit_id=kit.id,
                    box_id=box.id,
                    item_type="tool",
                    item_id=tool.id,
                    part_number=tool.tool_number,
                    serial_number=tool.serial_number,
                    description=tool.description,
                    quantity=1.0,
                    status="available"
                )
                db.session.add(kit_item)
                tool_idx += 1

    # Add chemicals to consumable boxes
    chems_per_box = len(chemicals) // len(consumable_boxes) if consumable_boxes else 0
    chem_idx = 0

    for box in consumable_boxes:
        for _ in range(chems_per_box):
            if chem_idx < len(chemicals):
                chemical = chemicals[chem_idx]
                kit_item = KitItem(
                    kit_id=kit.id,
                    box_id=box.id,
                    item_type="chemical",
                    item_id=chemical.id,
                    part_number=chemical.part_number,
                    lot_number=chemical.lot_number,
                    description=chemical.description,
                    quantity=2.0,
                    status="available"
                )
                db.session.add(kit_item)
                chem_idx += 1

    # Add expendables to expendable boxes
    # Create some common expendables using the new Expendable + KitItem architecture
    expendables_data = [
        ("EXP-001", "Nitrile Gloves - Box of 100", "Box"),
        ("EXP-002", "Safety Glasses - Clear lens", "Each"),
        ("EXP-003", "Ear Plugs - Foam disposable", "Pair"),
        ("EXP-004", "Face Masks - Disposable", "Box"),
        ("EXP-005", "Shop Rags - Cotton rags", "Box"),
        ("EXP-006", "Zip Ties 8 inch - Black nylon", "Bag"),
        ("EXP-007", "Electrical Tape - 3/4 inch black", "Roll"),
        ("EXP-008", "Duct Tape - 2 inch silver", "Roll"),
    ]

    exp_idx = 0
    for box in expendable_boxes:
        for _ in range(2):  # 2 expendables per box
            if exp_idx < len(expendables_data):
                part_num, desc, unit = expendables_data[exp_idx]

                # Generate lot number for this expendable
                lot_number = LotNumberSequence.generate_lot_number()

                # Create Expendable record (warehouse_id will be None for kit-only items)
                expendable = Expendable(
                    part_number=part_num,
                    serial_number=None,  # Using lot tracking, not serial
                    lot_number=lot_number,
                    description=desc,
                    manufacturer=None,
                    quantity=10,
                    unit=unit,
                    location="",
                    category="General",
                    status="available",
                    warehouse_id=None  # Kit-only expendables don't have warehouse_id
                )
                db.session.add(expendable)
                db.session.flush()  # Get expendable ID

                # Create KitItem to link expendable to kit
                kit_item = KitItem(
                    kit_id=kit.id,
                    box_id=box.id,
                    item_type="expendable",
                    item_id=expendable.id,
                    part_number=part_num,
                    serial_number=None,
                    lot_number=lot_number,
                    description=desc,
                    quantity=10,
                    location="",
                    status="available"
                )
                db.session.add(kit_item)
                exp_idx += 1


def seed_kits(aircraft_types, tools, chemicals):
    """Create 5 kits: 2 Boeing 737, 2 RJ85, 1 Q400."""
    print("Creating 5 aircraft kits...")

    # Get admin user for created_by field
    admin = User.query.filter_by(employee_number="ADMIN001").first()
    if not admin:
        print("ERROR: Admin user not found. Please create admin user first.")
        return []

    kit_configs = [
        ("Boeing 737", "Boeing 737 Maintenance Kit #1"),
        ("Boeing 737", "Boeing 737 Maintenance Kit #2"),
        ("RJ85", "RJ85 Maintenance Kit #1"),
        ("RJ85", "RJ85 Maintenance Kit #2"),
        ("Q400", "Q400 Maintenance Kit #1"),
    ]

    # Box configuration: 4 expendables, 3 tools, 2 consumables
    box_types = {
        "expendables": 4,
        "tools": 3,
        "consumables": 2
    }

    kits = []
    tools_per_kit = len(tools) // 5  # Distribute tools across kits
    chems_per_kit = len(chemicals) // 5  # Distribute chemicals across kits

    for i, (aircraft_name, kit_name) in enumerate(kit_configs):
        aircraft_type = aircraft_types[aircraft_name]

        kit = Kit(
            name=kit_name,
            aircraft_type_id=aircraft_type.id,
            description=f"Complete maintenance kit for {aircraft_name}",
            status="available",
            created_by=admin.id
        )
        db.session.add(kit)
        db.session.flush()  # Get kit ID

        # Create boxes for this kit
        boxes = create_kit_boxes(kit, box_types)

        # Get subset of tools and chemicals for this kit
        kit_tools = tools[i * tools_per_kit:(i + 1) * tools_per_kit]
        kit_chemicals = chemicals[i * chems_per_kit:(i + 1) * chems_per_kit]

        # Populate kit with items
        populate_kit_with_items(kit, boxes, kit_tools, kit_chemicals)

        kits.append(kit)
        print(f"  ✓ Created {kit_name} with {len(boxes)} boxes")

    db.session.commit()
    print(f"✓ Created {len(kits)} kits with all items")

    return kits


def main():
    """Main seeding function."""
    with app.app_context():
        print("\n" + "="*60)
        print("SEEDING DATABASE WITH REAL AIRCRAFT DATA")
        print("="*60 + "\n")

        # Step 1: Clear existing data
        clear_existing_data()

        # Step 2: Create warehouses
        warehouse = create_warehouses()

        # Step 3: Create aircraft types
        aircraft_types = create_aircraft_types()

        # Step 4: Seed tools
        tools = seed_tools(warehouse)

        # Step 5: Seed chemicals
        chemicals = seed_chemicals(warehouse)

        # Step 6: Create kits with boxes and items
        kits = seed_kits(aircraft_types, tools, chemicals)

        print("\n" + "="*60)
        print("DATABASE SEEDING COMPLETE!")
        print("="*60)
        print("\nSummary:")
        print(f"  • {len(tools)} aircraft tools")
        print(f"  • {len(chemicals)} aircraft chemicals")
        print(f"  • {len(kits)} kits (2 Boeing 737, 2 RJ85, 1 Q400)")
        print("  • Each kit has 9 boxes (4 expendables, 3 tools, 2 consumables)")
        print("  • All kits populated with tools, chemicals, and expendables")
        print("\n")


if __name__ == "__main__":
    main()


