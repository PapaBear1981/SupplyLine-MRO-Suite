"""
Routes for Expendable Management (Kit-Only Consumables)

This module provides API endpoints for managing expendables - consumable items
that are added directly to kits without warehouse management.

Key features:
- Add expendables directly to kits with auto-generated lot/serial numbers
- Update expendable quantities and details
- Transfer expendables between kits
- Generate barcodes for lot/serial tracking
- Full audit trail via AuditLog
"""

import logging
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from auth import department_required, jwt_required
from models import AuditLog, Expendable, LotNumberSequence, db
from models_kits import Kit, KitBox, KitItem
from utils.error_handler import ValidationError, handle_errors


logger = logging.getLogger(__name__)

expendables_bp = Blueprint("expendables", __name__)

# Decorator for Materials department access
materials_required = department_required("Materials")


def generate_serial_number(part_number):
    """
    Generate a unique serial number for an expendable.
    Format: SN-{part_number}-{timestamp}

    Args:
        part_number (str): Part number of the expendable

    Returns:
        str: Generated serial number
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"SN-{part_number}-{timestamp}"


@expendables_bp.route("/kits/<int:kit_id>/expendables", methods=["POST"])
@materials_required
@handle_errors
def add_expendable_to_kit(kit_id):
    """
    Add a new expendable directly to a kit.

    Required fields:
        - box_id: ID of the box within the kit
        - part_number: Part number of the expendable
        - description: Description of the expendable
        - quantity: Quantity to add
        - unit: Unit of measurement (each, oz, ml, ft, etc.)
        - tracking_type: 'lot' or 'serial'

    Optional fields:
        - lot_number: Lot number (auto-generated if not provided and tracking_type='lot')
        - serial_number: Serial number (auto-generated if not provided and tracking_type='serial')
        - manufacturer: Manufacturer name
        - location: Location within the box
        - category: Category (default: 'General')
        - minimum_stock_level: Minimum stock level for reorder alerts
        - notes: Additional notes
    """
    kit = Kit.query.get_or_404(kit_id)
    data = request.get_json() or {}

    # Validate required fields
    required_fields = ["box_id", "part_number", "description", "quantity", "unit", "tracking_type"]
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Missing required field: {field}")

    # Validate box belongs to kit
    box = KitBox.query.get_or_404(data["box_id"])
    if box.kit_id != kit_id:
        raise ValidationError("Box does not belong to this kit")

    # Validate tracking type
    tracking_type = data["tracking_type"].lower()
    if tracking_type not in ["lot", "serial"]:
        raise ValidationError("tracking_type must be 'lot' or 'serial'")

    # Auto-generate lot or serial number if not provided
    if tracking_type == "lot":
        lot_number = data.get("lot_number")
        if not lot_number:
            lot_number = LotNumberSequence.generate_lot_number()
        serial_number = None
    else:  # serial
        serial_number = data.get("serial_number")
        if not serial_number:
            serial_number = generate_serial_number(data["part_number"])
        lot_number = None

    logger.info(f"Creating expendable {data['part_number']} with {tracking_type}={lot_number or serial_number}")

    try:
        # Create expendable (warehouse_id will be forced to None in __init__)
        expendable = Expendable(
            part_number=data["part_number"],
            serial_number=serial_number,
            lot_number=lot_number,
            description=data["description"],
            manufacturer=data.get("manufacturer"),
            quantity=float(data["quantity"]),
            unit=data["unit"],
            location=data.get("location"),
            category=data.get("category", "General"),
            status="available",
            minimum_stock_level=data.get("minimum_stock_level"),
            notes=data.get("notes")
        )

        db.session.add(expendable)
        db.session.flush()  # Get expendable ID

        # Create KitItem to link expendable to kit
        kit_item = KitItem(
            kit_id=kit_id,
            box_id=data["box_id"],
            item_type="expendable",
            item_id=expendable.id,
            part_number=expendable.part_number,
            serial_number=expendable.serial_number,
            lot_number=expendable.lot_number,
            description=expendable.description,
            quantity=expendable.quantity,
            location=expendable.location,
            status="available",
            added_date=datetime.now(),
            last_updated=datetime.now()
        )

        db.session.add(kit_item)

        # Log action
        log = AuditLog(
            action_type="expendable_added_to_kit",
            action_details=f"Added expendable {expendable.part_number} ({tracking_type}={lot_number or serial_number}) to kit {kit.name}, box {box.box_number}"
        )
        db.session.add(log)

        db.session.commit()

        logger.info(f"Successfully added expendable {expendable.id} to kit {kit_id}")

        return jsonify({
            "message": "Expendable added to kit successfully",
            "expendable": expendable.to_dict(),
            "kit_item": kit_item.to_dict()
        }), 201

    except ValueError as e:
        db.session.rollback()
        raise ValidationError(str(e))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding expendable to kit: {e}")
        raise


@expendables_bp.route("/kits/<int:kit_id>/expendables/<int:expendable_id>", methods=["PUT"])
@materials_required
@handle_errors
def update_expendable(kit_id, expendable_id):
    """
    Update an expendable in a kit.

    Updatable fields:
        - quantity: Update quantity
        - location: Update location within box
        - status: Update status (available, low_stock, out_of_stock)
        - minimum_stock_level: Update minimum stock level
        - notes: Update notes
    """
    kit = Kit.query.get_or_404(kit_id)
    expendable = Expendable.query.get_or_404(expendable_id)

    # Verify expendable is in this kit
    kit_item = KitItem.query.filter_by(
        kit_id=kit_id,
        item_type="expendable",
        item_id=expendable_id
    ).first()

    if not kit_item:
        raise ValidationError("Expendable not found in this kit")

    data = request.get_json() or {}

    # Update allowed fields
    if "quantity" in data:
        old_quantity = expendable.quantity
        expendable.quantity = float(data["quantity"])
        kit_item.quantity = expendable.quantity
        logger.info(f"Updated expendable {expendable_id} quantity from {old_quantity} to {expendable.quantity}")

    if "location" in data:
        expendable.location = data["location"]
        kit_item.location = data["location"]

    if "status" in data:
        expendable.status = data["status"]
        kit_item.status = data["status"]

    if "minimum_stock_level" in data:
        expendable.minimum_stock_level = data.get("minimum_stock_level")

    if "notes" in data:
        expendable.notes = data["notes"]

    kit_item.last_updated = datetime.now()

    # Log action
    log = AuditLog(
        action_type="expendable_updated",
        action_details=f"Updated expendable {expendable.part_number} in kit {kit.name}"
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({
        "message": "Expendable updated successfully",
        "expendable": expendable.to_dict(),
        "kit_item": kit_item.to_dict()
    }), 200


@expendables_bp.route("/kits/<int:kit_id>/expendables/<int:expendable_id>", methods=["DELETE"])
@materials_required
@handle_errors
def remove_expendable_from_kit(kit_id, expendable_id):
    """
    Remove an expendable from a kit.
    This deletes both the KitItem and the Expendable record.
    """
    kit = Kit.query.get_or_404(kit_id)
    expendable = Expendable.query.get_or_404(expendable_id)

    # Verify expendable is in this kit
    kit_item = KitItem.query.filter_by(
        kit_id=kit_id,
        item_type="expendable",
        item_id=expendable_id
    ).first()

    if not kit_item:
        raise ValidationError("Expendable not found in this kit")

    # Log action before deletion
    log = AuditLog(
        action_type="expendable_removed_from_kit",
        action_details=f"Removed expendable {expendable.part_number} from kit {kit.name}"
    )
    db.session.add(log)

    # Delete KitItem and Expendable
    db.session.delete(kit_item)
    db.session.delete(expendable)

    db.session.commit()

    logger.info(f"Removed expendable {expendable_id} from kit {kit_id}")

    return jsonify({"message": "Expendable removed from kit successfully"}), 200



@expendables_bp.route("/inventory/expendable/<int:expendable_id>/detail", methods=["GET"])
@jwt_required
def get_expendable_detail(expendable_id):
    """
    Get detailed information about an expendable.

    Args:
        expendable_id (int): ID of the expendable

    Returns:
        JSON response with expendable details
    """
    expendable = Expendable.query.get_or_404(expendable_id)

    # Get all kit items that reference this expendable
    kit_items = KitItem.query.filter_by(item_type="expendable", item_id=expendable.id).all()

    # Build kit locations list
    kit_locations = []
    for kit_item in kit_items:
        kit = Kit.query.get(kit_item.kit_id)
        box = KitBox.query.get(kit_item.box_id) if kit_item.box_id else None
        kit_locations.append({
            "kit_id": kit.id,
            "kit_name": kit.name,
            "box_id": box.id if box else None,
            "box_number": box.box_number if box else None,
            "quantity": kit_item.quantity,
            "status": kit_item.status
        })

    return jsonify({
        "id": expendable.id,
        "part_number": expendable.part_number,
        "description": expendable.description,
        "manufacturer": expendable.manufacturer,
        "serial_number": expendable.serial_number,
        "lot_number": expendable.lot_number,
        "tracking_type": "serial" if expendable.serial_number else "lot",
        "quantity": expendable.quantity,
        "unit": expendable.unit,
        "location": expendable.location,
        "category": expendable.category,
        "status": expendable.status,
        "warehouse_id": expendable.warehouse_id,
        "date_added": expendable.date_added.isoformat() if expendable.date_added else None,
        "minimum_stock_level": expendable.minimum_stock_level,
        "notes": expendable.notes,
        "kit_locations": kit_locations
    }), 200


@expendables_bp.route("/expendables/<int:expendable_id>/barcode", methods=["GET"])
@jwt_required
def get_expendable_barcode(expendable_id):
    """
    Get barcode data for an expendable.
    Returns barcode string and QR code URL for printing labels.
    """
    expendable = Expendable.query.get_or_404(expendable_id)

    # Create barcode data - use lot_number or serial_number
    if expendable.lot_number:
        barcode_data = f"{expendable.part_number}-LOT-{expendable.lot_number}"
    else:
        barcode_data = f"{expendable.part_number}-{expendable.serial_number}"

    # Get the base URL for QR code
    base_url = current_app.config.get("PUBLIC_URL")
    base_url = request.host_url.rstrip("/") if not base_url else base_url.rstrip("/")

    # Create QR code URL that points to the expendable view page
    qr_url = f"{base_url}/expendable-view/{expendable.id}"

    return jsonify({
        "barcode_data": barcode_data,
        "qr_url": qr_url,
        "part_number": expendable.part_number,
        "lot_number": expendable.lot_number,
        "serial_number": expendable.serial_number,
        "description": expendable.description,
        "quantity": expendable.quantity,
        "unit": expendable.unit,
        "location": expendable.location,
        "category": expendable.category,
        "date_added": expendable.date_added.isoformat() if expendable.date_added else None
    }), 200


@expendables_bp.route("/transfers/kit-to-kit/expendable", methods=["POST"])
@materials_required
@handle_errors
def transfer_expendable_between_kits():
    """
    Transfer an expendable from one kit to another.

    Required fields:
        - from_kit_id: Source kit ID
        - to_kit_id: Destination kit ID
        - to_box_id: Destination box ID within the destination kit
        - expendable_id: ID of the expendable to transfer

    Optional fields:
        - location: New location within the destination box
        - notes: Transfer notes
    """
    data = request.get_json() or {}

    # Validate required fields
    required_fields = ["from_kit_id", "to_kit_id", "to_box_id", "expendable_id"]
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Missing required field: {field}")

    # Get kits and box
    from_kit = Kit.query.get_or_404(data["from_kit_id"])
    to_kit = Kit.query.get_or_404(data["to_kit_id"])
    to_box = KitBox.query.get_or_404(data["to_box_id"])

    # Validate box belongs to destination kit
    if to_box.kit_id != to_kit.id:
        raise ValidationError("Box does not belong to the destination kit")

    # Get expendable and verify it's in the source kit
    expendable = Expendable.query.get_or_404(data["expendable_id"])

    from_kit_item = KitItem.query.filter_by(
        kit_id=from_kit.id,
        item_type="expendable",
        item_id=expendable.id
    ).first()

    if not from_kit_item:
        raise ValidationError("Expendable not found in source kit")

    # Remove from source kit
    db.session.delete(from_kit_item)

    # Add to destination kit
    to_kit_item = KitItem(
        kit_id=to_kit.id,
        box_id=to_box.id,
        item_type="expendable",
        item_id=expendable.id,
        part_number=expendable.part_number,
        serial_number=expendable.serial_number,
        lot_number=expendable.lot_number,
        description=expendable.description,
        quantity=expendable.quantity,
        location=data.get("location", expendable.location),
        status="available",
        added_date=datetime.now(),
        last_updated=datetime.now()
    )

    db.session.add(to_kit_item)

    # Update expendable location if provided
    if "location" in data:
        expendable.location = data["location"]

    # Log action
    tracking_id = expendable.lot_number or expendable.serial_number
    tracking_type = "lot" if expendable.lot_number else "serial"
    log = AuditLog(
        action_type="expendable_transferred_between_kits",
        action_details=f"Transferred expendable {expendable.part_number} ({tracking_type}={tracking_id}) from kit {from_kit.name} to kit {to_kit.name}, box {to_box.box_number}"
    )
    db.session.add(log)

    db.session.commit()

    logger.info(f"Transferred expendable {expendable.id} from kit {from_kit.id} to kit {to_kit.id}")

    return jsonify({
        "message": "Expendable transferred successfully",
        "expendable": expendable.to_dict(),
        "from_kit": from_kit.name,
        "to_kit": to_kit.name,
        "to_box": to_box.box_number
    }), 200

