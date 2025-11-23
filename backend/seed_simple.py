"""Simple Aircraft MRO Database Seed Script"""

from app import create_app
from models import db, Tool, Chemical
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("\\n========== SEEDING AIRCRAFT MRO DATABASE ==========\\n")

    # Clear existing
    Tool.query.delete()
    Chemical.query.delete()
    db.session.commit()
    print("Cleared existing data")

    # Aircraft Tools - Using manufacturer part numbers
    tools = [
        ("TECH3FR250", "SN-TW-12345", 'Snap-On 3/8" Torque Wrench (10-150 ft-lbs)', "Torque Tools", "available", True),
        ("2503MRMH", "SN-TW-12346", 'CDI 1/2" Torque Wrench (30-250 ft-lbs)', "Torque Tools", "available", True),
        ("C3FR250F", "SN-TW-12347", "Precision Instruments 3/8\" Torque Wrench", "Torque Tools", "checked_out", True),
        ("J6168F", "SN-TW-12348", 'Proto 1/4" Torque Wrench (20-200 in-lbs)', "Torque Tools", "maintenance", True),
        ("64-560", "SN-TW-12349", 'Armstrong 3/4" Torque Wrench (150-750 ft-lbs)', "Torque Tools", "available", True),
        ("1423", "SN-DM-45001", 'Sioux 1/4" Pneumatic Right Angle Drill', "Power Tools", "available", False),
        ("10L2000", "SN-DM-45002", "Dotco Inline Pneumatic Drill Motor", "Power Tools", "available", False),
        ("CP9789", "SN-DM-45003", 'Chicago Pneumatic 3/8" Reversible Air Drill', "Power Tools", "checked_out", False),
        ("2804-22", "SN-DM-45004", "Milwaukee M18 Cordless Drill/Driver Kit", "Power Tools", "available", False),
        ("CP714", "SN-RG-78001", "Chicago Pneumatic .401 Rivet Gun", "Rivet Tools", "available", False),
        ("2120", "SN-RG-78002", "Sioux .498 Heavy Duty Rivet Gun", "Rivet Tools", "available", False),
        ("G84", "SN-RG-78003", "Cherry Aerospace Hand Rivet Tool", "Rivet Tools", "checked_out", False),
        ("FIREBIRD", "SN-RG-78004", "Gesipa 14.4V Cordless Rivet Gun", "Rivet Tools", "available", False),
        ("500-196-30", "SN-IT-99001", 'Mitutoyo Digital Caliper (0-6" / 0.0005")', "Measuring Tools", "available", True),
        ("T230XRL-1", "SN-IT-99002", 'Starrett Digital Micrometer (0-1" / 0.00005")', "Measuring Tools", "available", True),
        ("599-281", "SN-IT-99003", 'Brown & Sharpe Bore Gauge Set (2-6")', "Measuring Tools", "checked_out", True),
        ("IPLEX-NX", "SN-IT-99004", "Olympus IPLEX NX Videoscope", "NDT Equipment", "available", True),
        ("MENTOR-IQ", "SN-IT-99005", "GE Mentor Visual iQ Borescope", "NDT Equipment", "available", True),
        ("BB-UNIV-6", "N/A", "Cleveland Universal Bucking Bar Set (6-piece)", "Hand Tools", "available", False),
        ("TB-1", "N/A", "Avery Tungsten Bucking Bar - 1 lb", "Hand Tools", "available", False),
        ("FB-2", "N/A", "Avery Flat Bucking Bar - 2 lb", "Hand Tools", "available", False),
        ("MS20995C41", "SN-SW-55001", 'Milbar Safety Wire Pliers (0.020-0.041")', "Hand Tools", "available", False),
        ("SW-1", "SN-SW-55002", "American Beauty Safety Wire Twister", "Hand Tools", "available", False),
        ("SCO10S250A", "SN-PG-33001", 'Sioux 1/4" Die Grinder (25,000 RPM)', "Power Tools", "available", False),
        ("10-25", "SN-PG-33002", "Dotco Right Angle Die Grinder", "Power Tools", "checked_out", False),
        ("AFM8", "SN-CT-66001", "Daniels AFM8 Hand Crimp Tool", "Electrical Tools", "available", True),
        ("HX4", "SN-CT-66002", "Daniels HX4 Pneumatic Crimp Tool", "Electrical Tools", "available", True),
        ("SCR-106H", "SN-HT-88001", "Enerpac 10-Ton Hydraulic Porta-Power Set", "Hydraulic Tools", "available", False),
        ("R506", "SN-HT-88002", "Simplex 50-Ton Hydraulic Cylinder", "Hydraulic Tools", "available", False),
        ("87V", "SN-TE-77001", "Fluke 87V Industrial Multimeter", "Test Equipment", "available", True),
        ("DPS-300", "SN-TE-77002", "Barfield DPS-300 Pitot Static Tester", "Test Equipment", "available", True),
        ("MODEL-500", "SN-TE-77003", "Testronix Model 500 Circuit Analyzer", "Test Equipment", "maintenance", True),
        ("02-7810-0000", "SN-JS-11001", 'Tronair 15-Ton Axle Jack (25-44" Range)', "Jacking Equipment", "available", False),
        ("02-8800-0010", "SN-JS-11002", "Tronair 25-Ton Wing Jack", "Jacking Equipment", "available", False),
        ("02-4300-0000", "SN-JS-11003", "Tronair 30-Ton Jack Stand Set (4-piece)", "Jacking Equipment", "available", False),
        ("DBT-100", "N/A", "Royal Deburring Tool Set with Blades", "Hand Tools", "available", False),
        ("S100", "N/A", "Noga Deburring Tool with Carbide Blade", "Hand Tools", "available", False),
    ]

    for i, (num, serial, desc, cat, status, cal) in enumerate(tools):
        last_cal = datetime.now() - timedelta(days=random.randint(30, 300)) if cal else None
        next_cal = last_cal + timedelta(days=365) if cal and last_cal else None

        tool = Tool(
            tool_number=num,
            serial_number=serial,
            description=desc,
            category=cat,
            status=status,
            condition="Good" if status != "maintenance" else "Fair",
            location=f"Shelf {(i % 20) + 1}-{chr(65 + (i % 5))}",
            requires_calibration=cal,
            calibration_frequency_days=365 if cal else None,
            last_calibration_date=last_cal,
            next_calibration_date=next_cal
        )
        db.session.add(tool)
    db.session.commit()
    print(f"Created {len(tools)} aircraft tools")

    # Aircraft Chemicals
    chemicals = [
        ("MIL-PRF-5606H", "LOT-5606-2024A", "MIL-PRF-5606H Hydraulic Fluid (Red) - Eastman", "Hydraulic Fluids", 208, "L"),
        ("MIL-PRF-83282", "LOT-83282-2024B", "MIL-PRF-83282 Fire Resistant Hydraulic Fluid", "Hydraulic Fluids", 208, "L"),
        ("SKYDROL-500B-4", "LOT-SKY-2024C", "Skydrol 500B-4 Aviation Hydraulic Fluid", "Hydraulic Fluids", 156, "L"),
        ("SKYDROL-LD-4", "LOT-SKYLD-2024A", "Skydrol LD-4 Low Density Hydraulic Fluid", "Hydraulic Fluids", 104, "L"),
        ("MIL-PRF-23827", "LOT-23827-2024D", "MIL-PRF-23827 Grease, Aircraft & Instrument - Aeroshell", "Lubricants", 25, "kg"),
        ("MIL-PRF-81322", "LOT-81322-2024E", "MIL-PRF-81322 Synthetic Grease - Aeroshell", "Lubricants", 15, "kg"),
        ("ROYCO-782", "LOT-782-2024F", "Royco 782 Synthetic Turbine Engine Oil", "Lubricants", 208, "L"),
        ("AEROSHELL-W100", "LOT-W100-2024G", "Aeroshell W100 Piston Engine Oil", "Lubricants", 156, "L"),
        ("MIL-PRF-680", "LOT-680-2024J", "MIL-PRF-680 Type II Degreasing Compound - Turco", "Cleaners", 76, "L"),
        ("SKYDROL-CLEANER", "LOT-SKYCLEAN-2024K", "Skydrol Cleaner (Phosphate Ester Safe)", "Cleaners", 38, "L"),
        ("MEK-AIRCRAFT", "LOT-MEK-2024L", "Methyl Ethyl Ketone (MEK) - Aircraft Grade", "Solvents", 114, "L"),
        ("ACETONE-PURE", "LOT-ACE-2024M", "Acetone - 99.5% Pure (Aircraft Grade)", "Solvents", 95, "L"),
        ("IPA-99", "LOT-IPA-2024N", "Isopropyl Alcohol 99% (IPA)", "Solvents", 76, "L"),
        ("STODDARD-SOLVENT", "LOT-STOD-2024P", "Stoddard Solvent (Mineral Spirits)", "Solvents", 152, "L"),
        ("MIL-PRF-16173", "LOT-16173-2024Q", "MIL-PRF-16173 Grade 4 Corrosion Preventive - ACF-50", "Corrosion Prevention", 28, "L"),
        ("MIL-PRF-81309", "LOT-81309-2024R", "MIL-PRF-81309 Type II & III Preservative - LPS", "Corrosion Prevention", 45, "L"),
        ("LPS-3", "LOT-LPS3-2024S", "LPS-3 Heavy Duty Rust Inhibitor", "Corrosion Prevention", 32, "L"),
        ("ACF-50", "LOT-ACF-2024T", "ACF-50 Anti-Corrosion Formula", "Corrosion Prevention", 18, "L"),
        ("PR-1440-B2", "LOT-PR1440-2024U", "PR-1440 Class B-2 Fuel Tank Sealant - PPG", "Sealants", 12, "kg"),
        ("PR-1422-B2", "LOT-PR1422-2024V", "PR-1422 Class B-2 Fay Surface Sealant - PPG", "Sealants", 8, "kg"),
        ("EA-9394", "LOT-EA9394-2024W", "Hysol EA-9394 Epoxy Adhesive - Henkel", "Adhesives", 5, "kg"),
        ("MIL-PRF-23377", "LOT-23377-2024Y", "MIL-PRF-23377 Epoxy Primer - Gray", "Primers", 38, "L"),
        ("ALODINE-1200S", "LOT-ALOD-2024AA", "Alodine 1200S Chromate Conversion Coating", "Surface Treatment", 22, "L"),
        ("ZL-60D", "LOT-ZL60-2024AB", "Zyglo ZL-60D Fluorescent Penetrant - Magnaflux", "NDT Materials", 15, "L"),
        ("SKC-S", "LOT-SKC-2024AC", "Spotcheck SKC-S Penetrant Cleaner - Magnaflux", "NDT Materials", 18, "L"),
    ]

    for part, lot, desc, cat, qty, unit in chemicals:
        chem = Chemical(
            part_number=part,
            lot_number=lot,
            description=desc,
            manufacturer="Various",
            category=cat,
            quantity=int(qty),
            unit=unit,
            status="available",
            location=f"Cabinet {random.randint(1, 10)}-{chr(65 + random.randint(0, 3))}",
            minimum_stock_level=int(qty * 0.2),
            expiration_date=datetime.now() + timedelta(days=random.randint(730, 1825))
        )
        db.session.add(chem)
    db.session.commit()
    print(f"Created {len(chemicals)} aircraft chemicals")

    print(f"\\n========== SEEDING COMPLETE ==========")
    print(f"Tools: {Tool.query.count()}")
    print(f"Chemicals: {Chemical.query.count()}")
    print("Login: ADMIN001 / admin123\\n")
