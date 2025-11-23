"""
Aircraft MRO Database Seed Script
Populates database with realistic aircraft maintenance tools, parts, and chemicals
"""

from app import create_app
from models import db, User, Tool, Chemical, Warehouse
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random


def clear_database():
    """Clear existing data"""
    print("Clearing existing data...")
    Tool.query.delete()
    Chemical.query.delete()
    # Keep users and warehouses
    db.session.commit()
    print("Database cleared")


def seed_warehouses():
    """Create warehouses if they don't exist"""
    if Warehouse.query.count() == 0:
        warehouses = [
            Warehouse(name="Main Tool Crib", address="Hangar 1", city="Seattle", state="WA", warehouse_type="main"),
            Warehouse(name="Chemical Storage", address="Building B", city="Seattle", state="WA", warehouse_type="satellite"),
            Warehouse(name="Spokane Facility", address="123 Airport Way", city="Spokane", state="WA", warehouse_type="satellite"),
        ]
        for wh in warehouses:
            db.session.add(wh)
        db.session.commit()
        print(f"Created {len(warehouses)} warehouses")
    return Warehouse.query.all()


def seed_aircraft_tools(warehouses):
    """Seed realistic aircraft maintenance tools"""
    print("Seeding aircraft maintenance tools...")

    tools_data = [
        # Torque Wrenches
        {"tool_number": "TW-001", "serial": "SN-TW-12345", "desc": "Snap-On 3/8\" Drive Torque Wrench (10-150 ft-lbs) - TECH3FR250", "category": "Torque Tools", "requires_cal": True, "status": "available"},
        {"tool_number": "TW-002", "serial": "SN-TW-12346", "desc": "CDI 1/2\" Drive Torque Wrench (30-250 ft-lbs) - 2503MRMH", "category": "Torque Tools", "requires_cal": True, "status": "available"},
        {"tool_number": "TW-003", "serial": "SN-TW-12347", "desc": "Precision Instruments 3/8\" Micro-Adjustable Torque Wrench", "category": "Torque Tools", "mfg": "Precision Instruments", "model": "C3FR250F", "requires_cal": True, "status": "checked_out"},
        {"tool_number": "TW-004", "serial": "SN-TW-12348", "desc": "Proto 1/4\" Drive Torque Wrench (20-200 in-lbs)", "category": "Torque Tools", "mfg": "Proto", "model": "J6168F", "requires_cal": True, "status": "maintenance"},
        {"tool_number": "TW-005", "serial": "SN-TW-12349", "desc": "Armstrong 3/4\" Drive Torque Wrench (150-750 ft-lbs)", "category": "Torque Tools", "mfg": "Armstrong", "model": "64-560", "requires_cal": True, "status": "available"},

        # Drill Motors & Accessories
        {"tool_number": "DM-001", "serial": "SN-DM-45001", "desc": "Sioux 1/4\" Pneumatic Right Angle Drill", "category": "Power Tools", "mfg": "Sioux Tools", "model": "1423", "requires_cal": False, "status": "available"},
        {"tool_number": "DM-002", "serial": "SN-DM-45002", "desc": "Dotco Inline Pneumatic Drill Motor", "category": "Power Tools", "mfg": "Dotco", "model": "10L2000", "requires_cal": False, "status": "available"},
        {"tool_number": "DM-003", "serial": "SN-DM-45003", "desc": "Chicago Pneumatic 3/8\" Reversible Air Drill", "category": "Power Tools", "mfg": "Chicago Pneumatic", "model": "CP9789", "requires_cal": False, "status": "checked_out"},
        {"tool_number": "DM-004", "serial": "SN-DM-45004", "desc": "Milwaukee Cordless 18V Drill/Driver Kit", "category": "Power Tools", "mfg": "Milwaukee", "model": "2804-22", "requires_cal": False, "status": "available"},

        # Rivet Guns
        {"tool_number": "RG-001", "serial": "SN-RG-78001", "desc": "Chicago Pneumatic .401 Rivet Gun", "category": "Rivet Tools", "mfg": "Chicago Pneumatic", "model": "CP714", "requires_cal": False, "status": "available"},
        {"tool_number": "RG-002", "serial": "SN-RG-78002", "desc": "Sioux .498 Heavy Duty Rivet Gun", "category": "Rivet Tools", "mfg": "Sioux Tools", "model": "2120", "requires_cal": False, "status": "available"},
        {"tool_number": "RG-003", "serial": "SN-RG-78003", "desc": "Cherry Aerospace Hand Rivet Tool", "category": "Rivet Tools", "mfg": "Cherry Aerospace", "model": "G84", "requires_cal": False, "status": "checked_out"},
        {"tool_number": "RG-004", "serial": "SN-RG-78004", "desc": "Gesipa Cordless Rivet Gun 14.4V", "category": "Rivet Tools", "mfg": "Gesipa", "model": "FireBird", "requires_cal": False, "status": "available"},

        # Inspection Tools
        {"tool_number": "IT-001", "serial": "SN-IT-99001", "desc": "Mitutoyo Digital Caliper 0-6\" (0.0005\" Resolution)", "category": "Measuring Tools", "mfg": "Mitutoyo", "model": "500-196-30", "requires_cal": True, "status": "available"},
        {"tool_number": "IT-002", "serial": "SN-IT-99002", "desc": "Starrett Digital Micrometer 0-1\" (0.00005\")", "category": "Measuring Tools", "mfg": "Starrett", "model": "T230XRL-1", "requires_cal": True, "status": "available"},
        {"tool_number": "IT-003", "serial": "SN-IT-99003", "desc": "Brown & Sharpe Bore Gauge Set (2-6\")", "category": "Measuring Tools", "mfg": "Brown & Sharpe", "model": "599-281", "requires_cal": True, "status": "checked_out"},
        {"tool_number": "IT-004", "serial": "SN-IT-99004", "desc": "Olympus IPLEX NX Videoscope", "category": "NDT Equipment", "mfg": "Olympus", "model": "IPLEX-NX", "requires_cal": True, "status": "available"},
        {"tool_number": "IT-005", "serial": "SN-IT-99005", "desc": "GE Mentor Visual iQ Borescope", "category": "NDT Equipment", "mfg": "GE Inspection", "model": "Mentor-iQ", "requires_cal": True, "status": "available"},

        # Bucking Bars
        {"tool_number": "BB-001", "serial": "N/A", "desc": "Universal Bucking Bar Set (6-piece)", "category": "Hand Tools", "mfg": "Cleveland", "model": "BB-UNIV-6", "requires_cal": False, "status": "available"},
        {"tool_number": "BB-002", "serial": "N/A", "desc": "Tungsten Bucking Bar - 1 lb", "category": "Hand Tools", "mfg": "Avery Tools", "model": "TB-1", "requires_cal": False, "status": "available"},
        {"tool_number": "BB-003", "serial": "N/A", "desc": "Flat Bucking Bar - 2 lb", "category": "Hand Tools", "mfg": "Avery Tools", "model": "FB-2", "requires_cal": False, "status": "available"},

        # Safety Wire Tools
        {"tool_number": "SW-001", "serial": "SN-SW-55001", "desc": "Milbar Safety Wire Pliers (0.020-0.041\")", "category": "Hand Tools", "mfg": "Milbar", "model": "MS20995C41", "requires_cal": False, "status": "available"},
        {"tool_number": "SW-002", "serial": "SN-SW-55002", "desc": "American Beauty Safety Wire Twister", "category": "Hand Tools", "mfg": "American Beauty", "model": "SW-1", "requires_cal": False, "status": "available"},

        # Pneumatic Grinders
        {"tool_number": "PG-001", "serial": "SN-PG-33001", "desc": "Sioux 1/4\" Die Grinder (25,000 RPM)", "category": "Power Tools", "mfg": "Sioux Tools", "model": "SCO10S250A", "requires_cal": False, "status": "available"},
        {"tool_number": "PG-002", "serial": "SN-PG-33002", "desc": "Dotco Right Angle Die Grinder", "category": "Power Tools", "mfg": "Dotco", "model": "10-25", "requires_cal": False, "status": "checked_out"},

        # Crimp Tools
        {"tool_number": "CT-001", "serial": "SN-CT-66001", "desc": "Daniels AFM8 Hand Crimp Tool", "category": "Electrical Tools", "mfg": "Daniels Manufacturing", "model": "AFM8", "requires_cal": True, "status": "available"},
        {"tool_number": "CT-002", "serial": "SN-CT-66002", "desc": "DMC HX4 Pneumatic Crimp Tool", "category": "Electrical Tools", "mfg": "Daniels Manufacturing", "model": "HX4", "requires_cal": True, "status": "available"},

        # Hydraulic Tools
        {"tool_number": "HT-001", "serial": "SN-HT-88001", "desc": "Enerpac 10-Ton Hydraulic Porta-Power Set", "category": "Hydraulic Tools", "mfg": "Enerpac", "model": "SCR-106H", "requires_cal": False, "status": "available"},
        {"tool_number": "HT-002", "serial": "SN-HT-88002", "desc": "Simplex 50-Ton Hydraulic Cylinder", "category": "Hydraulic Tools", "mfg": "Simplex", "model": "R506", "requires_cal": False, "status": "available"},

        # Test Equipment
        {"tool_number": "TE-001", "serial": "SN-TE-77001", "desc": "Fluke 87V Industrial Multimeter", "category": "Test Equipment", "mfg": "Fluke", "model": "87V", "requires_cal": True, "status": "available"},
        {"tool_number": "TE-002", "serial": "SN-TE-77002", "desc": "Barfield DPS-300 Pitot Static Tester", "category": "Test Equipment", "mfg": "Barfield", "model": "DPS300", "requires_cal": True, "status": "available"},
        {"tool_number": "TE-003", "serial": "SN-TE-77003", "desc": "Testronix Model 500 Circuit Analyzer", "category": "Test Equipment", "mfg": "Testronix", "model": "500", "requires_cal": True, "status": "maintenance"},

        # Jacks & Stands
        {"tool_number": "JS-001", "serial": "SN-JS-11001", "desc": "Tronair 15-Ton Axle Jack (25-44\" Range)", "category": "Jacking Equipment", "mfg": "Tronair", "model": "02-7810-0000", "requires_cal": False, "status": "available"},
        {"tool_number": "JS-002", "serial": "SN-JS-11002", "desc": "Tronair 25-Ton Wing Jack", "category": "Jacking Equipment", "mfg": "Tronair", "model": "02-8800-0010", "requires_cal": False, "status": "available"},
        {"tool_number": "JS-003", "serial": "SN-JS-11003", "desc": "Tronair 30-Ton Jack Stand Set (4-piece)", "category": "Jacking Equipment", "mfg": "Tronair", "model": "02-4300-0000", "requires_cal": False, "status": "available"},

        # Deburring Tools
        {"tool_number": "DB-001", "serial": "N/A", "desc": "Royal Deburring Tool Set with Blades", "category": "Hand Tools", "mfg": "Royal Products", "model": "DBT-100", "requires_cal": False, "status": "available"},
        {"tool_number": "DB-002", "serial": "N/A", "desc": "Noga Deburring Tool with Carbide Blade", "category": "Hand Tools", "mfg": "Noga", "model": "S100", "requires_cal": False, "status": "available"},
    ]

    for i, tool_data in enumerate(tools_data):
        # Calculate calibration dates for tools requiring calibration
        if tool_data["requires_cal"]:
            days_since_cal = random.randint(30, 300)
            last_cal = datetime.now() - timedelta(days=days_since_cal)
            next_cal = last_cal + timedelta(days=365)
        else:
            last_cal = None
            next_cal = None

        tool = Tool(
            tool_number=tool_data["tool_number"],
            serial_number=tool_data["serial"],
            description=tool_data["desc"],
            category=tool_data["category"],
            status=tool_data["status"],
            condition="Good" if tool_data["status"] != "maintenance" else "Fair",
            location=f"Shelf {(i % 20) + 1}-{chr(65 + (i % 5))}",
            requires_calibration=tool_data["requires_cal"],
            calibration_frequency_days=365 if tool_data["requires_cal"] else None,
            last_calibration_date=last_cal,
            next_calibration_date=next_cal,
            warehouse_id=warehouses[i % len(warehouses)].id if i % 4 == 0 else None
        )
        db.session.add(tool)

    db.session.commit()
    print(f"Created {len(tools_data)} aircraft maintenance tools")


def seed_aircraft_chemicals(warehouses):
    """Seed realistic aircraft chemicals and consumables"""
    print("Seeding aircraft chemicals...")

    chemicals_data = [
        # Hydraulic Fluids
        {"part": "MIL-PRF-5606H", "lot": "LOT-5606-2024A", "desc": "MIL-PRF-5606H Hydraulic Fluid (Red)", "mfg": "Eastman", "qty": 208, "unit": "L", "cat": "Hydraulic Fluids", "status": "available"},
        {"part": "MIL-PRF-83282", "lot": "LOT-83282-2024B", "desc": "MIL-PRF-83282 Fire Resistant Hydraulic Fluid", "mfg": "Eastman", "qty": 208, "unit": "L", "cat": "Hydraulic Fluids", "status": "available"},
        {"part": "SKYDROL-500B-4", "lot": "LOT-SKY-2024C", "desc": "Skydrol 500B-4 Aviation Hydraulic Fluid", "mfg": "Eastman", "qty": 156, "unit": "L", "cat": "Hydraulic Fluids", "status": "available"},
        {"part": "SKYDROL-LD-4", "lot": "LOT-SKYLD-2024A", "desc": "Skydrol LD-4 Low Density Hydraulic Fluid", "mfg": "Eastman", "qty": 104, "unit": "L", "cat": "Hydraulic Fluids", "status": "low_stock"},

        # Lubricants
        {"part": "MIL-PRF-23827", "lot": "LOT-23827-2024D", "desc": "MIL-PRF-23827 Grease, Aircraft & Instrument", "mfg": "Aeroshell", "qty": 25, "unit": "kg", "cat": "Lubricants", "status": "available"},
        {"part": "MIL-PRF-81322", "lot": "LOT-81322-2024E", "desc": "MIL-PRF-81322 Grease, Synthetic", "mfg": "Aeroshell", "qty": 15, "unit": "kg", "cat": "Lubricants", "status": "available"},
        {"part": "ROYCO-782", "lot": "LOT-782-2024F", "desc": "Royco 782 Synthetic Turbine Engine Oil", "mfg": "Royco", "qty": 208, "unit": "L", "cat": "Lubricants", "status": "available"},
        {"part": "AEROSHELL-W100", "lot": "LOT-W100-2024G", "desc": "Aeroshell W100 Piston Engine Oil", "mfg": "Shell", "qty": 156, "unit": "L", "cat": "Lubricants", "status": "available"},
        {"part": "AEROSHELL-560", "lot": "LOT-560-2024H", "desc": "Aeroshell Fluid 560 Synthetic Hydraulic/Instrument", "mfg": "Shell", "qty": 52, "unit": "L", "cat": "Lubricants", "status": "available"},

        # Cleaners & Solvents
        {"part": "MIL-PRF-680", "lot": "LOT-680-2024J", "desc": "MIL-PRF-680 Type II Degreasing Compound", "mfg": "Turco", "qty": 76, "unit": "L", "cat": "Cleaners", "status": "available"},
        {"part": "SKYDROL-CLEANER", "lot": "LOT-SKYCLEAN-2024K", "desc": "Skydrol Cleaner (Phosphate Ester Safe)", "mfg": "Eastman", "qty": 38, "unit": "L", "cat": "Cleaners", "status": "available"},
        {"part": "METHYL-ETHYL-KETONE", "lot": "LOT-MEK-2024L", "desc": "Methyl Ethyl Ketone (MEK) - Aircraft Grade", "mfg": "Sherwin-Williams", "qty": 114, "unit": "L", "cat": "Solvents", "status": "available"},
        {"part": "ACETONE-PURE", "lot": "LOT-ACE-2024M", "desc": "Acetone - 99.5% Pure (Aircraft Grade)", "mfg": "Sherwin-Williams", "qty": 95, "unit": "L", "cat": "Solvents", "status": "available"},
        {"part": "ISOPROPYL-ALCOHOL", "lot": "LOT-IPA-2024N", "desc": "Isopropyl Alcohol 99% (IPA)", "mfg": "VWR", "qty": 76, "unit": "L", "cat": "Solvents", "status": "available"},
        {"part": "STODDARD-SOLVENT", "lot": "LOT-STOD-2024P", "desc": "Stoddard Solvent (Mineral Spirits)", "mfg": "Sherwin-Williams", "qty": 152, "unit": "L", "cat": "Solvents", "status": "available"},

        # Corrosion Prevention
        {"part": "MIL-PRF-16173", "lot": "LOT-16173-2024Q", "desc": "MIL-PRF-16173 Grade 4 Corrosion Preventive", "mfg": "ACF-50", "qty": 28, "unit": "L", "cat": "Corrosion Prevention", "status": "available"},
        {"part": "MIL-PRF-81309", "lot": "LOT-81309-2024R", "desc": "MIL-PRF-81309 Type II & III Preservative", "mfg": "LPS", "qty": 45, "unit": "L", "cat": "Corrosion Prevention", "status": "available"},
        {"part": "LPS-3", "lot": "LOT-LPS3-2024S", "desc": "LPS-3 Heavy Duty Rust Inhibitor", "mfg": "LPS", "qty": 32, "unit": "L", "cat": "Corrosion Prevention", "status": "available"},
        {"part": "ACF-50", "lot": "LOT-ACF-2024T", "desc": "ACF-50 Anti-Corrosion Formula", "mfg": "ACF-50", "qty": 18, "unit": "L", "cat": "Corrosion Prevention", "status": "low_stock"},

        # Sealants & Adhesives
        {"part": "PR-1440-B2", "lot": "LOT-PR1440-2024U", "desc": "PR-1440 Class B-2 Fuel Tank Sealant", "mfg": "PPG Aerospace", "qty": 12, "unit": "kg", "cat": "Sealants", "status": "available"},
        {"part": "PR-1422-B2", "lot": "LOT-PR1422-2024V", "desc": "PR-1422 Class B-2 Fay Surface Sealant", "mfg": "PPG Aerospace", "qty": 8, "unit": "kg", "cat": "Sealants", "status": "available"},
        {"part": "EA-9394", "lot": "LOT-EA9394-2024W", "desc": "Hysol EA-9394 Epoxy Adhesive", "mfg": "Henkel", "qty": 5, "unit": "kg", "cat": "Adhesives", "status": "available"},
        {"part": "EA-9309", "lot": "LOT-EA9309-2024X", "desc": "Hysol EA-9309 Paste Adhesive", "mfg": "Henkel", "qty": 6, "unit": "kg", "cat": "Adhesives", "status": "available"},

        # Primers & Paints
        {"part": "MIL-PRF-23377", "lot": "LOT-23377-2024Y", "desc": "MIL-PRF-23377 Epoxy Primer - Gray", "mfg": "Sherwin-Williams", "qty": 38, "unit": "L", "cat": "Primers", "status": "available"},
        {"part": "MIL-PRF-85285", "lot": "LOT-85285-2024Z", "desc": "MIL-PRF-85285 Polyurethane Topcoat - White", "mfg": "Akzo Nobel", "qty": 45, "unit": "L", "cat": "Paints", "status": "available"},
        {"part": "ALODINE-1200S", "lot": "LOT-ALOD-2024AA", "desc": "Alodine 1200S Chromate Conversion Coating", "mfg": "Henkel", "qty": 22, "unit": "L", "cat": "Surface Treatment", "status": "available"},

        # Penetrants & Inspection Materials
        {"part": "ZL-60D", "lot": "LOT-ZL60-2024AB", "desc": "Zyglo ZL-60D Fluorescent Penetrant", "mfg": "Magnaflux", "qty": 15, "unit": "L", "cat": "NDT Materials", "status": "available"},
        {"part": "SKC-S", "lot": "LOT-SKC-2024AC", "desc": "Spotcheck SKC-S Penetrant Cleaner", "mfg": "Magnaflux", "qty": 18, "unit": "L", "cat": "NDT Materials", "status": "available"},
        {"part": "ZP-9F", "lot": "LOT-ZP9-2024AD", "desc": "Zyglo ZP-9F Developer (Aerosol)", "mfg": "Magnaflux", "qty": 24, "unit": "cans", "cat": "NDT Materials", "status": "available"},

        # Specialty Chemicals
        {"part": "AQUA-CLEAN", "lot": "LOT-AQ-2024AE", "desc": "Aqua-Clean Aqueous Cleaner (Biodegradable)", "mfg": "Brulin", "qty": 95, "unit": "L", "cat": "Cleaners", "status": "available"},
        {"part": "TURCO-5948", "lot": "LOT-5948-2024AF", "desc": "Turco 5948 Paint Stripper", "mfg": "Henkel", "qty": 57, "unit": "L", "cat": "Specialty", "status": "available"},
        {"part": "PURPLE-POWER", "lot": "LOT-PP-2024AG", "desc": "Purple Power Industrial Degreaser", "mfg": "Aiken Chemical", "qty": 114, "unit": "L", "cat": "Cleaners", "status": "available"},
    ]

    for i, chem_data in enumerate(chemicals_data):
        # Set expiration dates (2-5 years from now for most chemicals)
        exp_days = random.randint(730, 1825)  # 2-5 years
        expiration = datetime.now() + timedelta(days=exp_days)

        chemical = Chemical(
            part_number=chem_data["part"],
            lot_number=chem_data["lot"],
            description=chem_data["desc"],
            manufacturer=chem_data["mfg"],
            quantity=chem_data["qty"],
            unit=chem_data["unit"],
            category=chem_data["cat"],
            status=chem_data["status"],
            location=f"Cabinet {(i % 10) + 1}-{chr(65 + (i % 4))}",
            minimum_quantity=chem_data["qty"] * 0.2,  # 20% minimum
            expiration_date=expiration,
            warehouse_id=warehouses[i % len(warehouses)].id if i % 3 == 0 else None
        )
        db.session.add(chemical)

    db.session.commit()
    print(f"Created {len(chemicals_data)} aircraft chemicals")


def seed_database():
    """Main seeding function"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("AIRCRAFT MRO DATABASE SEEDING")
        print("="*60 + "\n")

        # Clear existing data
        clear_database()

        # Seed warehouses
        warehouses = seed_warehouses()

        # Seed tools and chemicals
        seed_aircraft_tools(warehouses)
        seed_aircraft_chemicals(warehouses)

        # Summary
        print("\n" + "="*60)
        print("DATABASE SEEDING COMPLETE")
        print("="*60)
        print(f"Users:      {User.query.count()}")
        print(f"Warehouses: {Warehouse.query.count()}")
        print(f"Tools:      {Tool.query.count()}")
        print(f"Chemicals:  {Chemical.query.count()}")
        print("\nLogin credentials:")
        print("  Admin: ADMIN001 / admin123")
        print("\nRealistic aircraft maintenance data loaded!")
        print("="*60 + "\n")


if __name__ == "__main__":
    seed_database()
