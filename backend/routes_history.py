"""
Routes for Item History Lookup

This module provides API endpoints for comprehensive item history tracking.
Supports lookup by part/tool number and lot/serial number for all item types.
"""

import logging
from datetime import timedelta

from flask import jsonify, request
from sqlalchemy import and_, or_

from auth import jwt_required
from models import (
    AuditLog,
    Checkout,
    Chemical,
    ChemicalIssuance,
    ChemicalReturn,
    InventoryTransaction,
    Tool,
    Warehouse,
    WarehouseTransfer,
    db,
)
from models_kits import Kit, KitExpendable, KitIssuance, KitItem, KitTransfer
from utils.error_handler import ValidationError, handle_errors


logger = logging.getLogger(__name__)


def register_history_routes(app):
    """Register all history-related routes"""

    @app.route("/api/history/lookup", methods=["POST"])
    @jwt_required
    @handle_errors
    def lookup_item_history():
        """
        Comprehensive item history lookup by part/tool number and lot/serial number.

        Request body:
            {
                "identifier": "T-12345" or "CHEM-001",  // part_number or tool_number
                "tracking_number": "SN-001" or "LOT-251014-0001"  // serial_number or lot_number
            }

        Returns:
            {
                "item_found": true,
                "item_type": "tool" | "chemical" | "expendable",
                "item_details": {...},
                "current_location": {...},
                "parent_lot": {...},  // If applicable
                "child_lots": [...],  // If applicable
                "history": [
                    {
                        "event_type": "warehouse_to_kit_transfer" | "kit_to_warehouse_transfer" |
                                     "kit_to_kit_transfer" | "issuance" | "checkout" | "return" |
                                     "retirement" | "status_change" | "creation",
                        "timestamp": "2025-01-15T10:30:00",
                        "description": "Transferred from Warehouse A to Kit Q400-001",
                        "user": "John Doe",
                        "details": {...}
                    },
                    ...
                ]
            }
        """
        data = request.get_json() or {}

        # Validate required fields
        if "identifier" not in data or "tracking_number" not in data:
            raise ValidationError("Both identifier (part/tool number) and tracking_number (lot/serial number) are required")

        identifier = data["identifier"].strip()
        tracking_number = data["tracking_number"].strip()

        # Search for the item across all types (case-insensitive)
        item = None
        item_type = None
        item_details = {}

        # Try to find as Tool (by tool_number and serial_number OR lot_number)
        # Using ilike for case-insensitive matching
        tool = Tool.query.filter(
            Tool.tool_number.ilike(identifier),
            or_(
                Tool.serial_number.ilike(tracking_number),
                Tool.lot_number.ilike(tracking_number)
            )
        ).first()

        if tool:
            item = tool
            item_type = "tool"
            item_details = {
                "id": tool.id,
                "tool_number": tool.tool_number,
                "serial_number": tool.serial_number,
                "lot_number": tool.lot_number,
                "description": tool.description,
                "condition": tool.condition,
                "category": tool.category,
                "status": tool.status,
                "status_reason": tool.status_reason,
                "warehouse_id": tool.warehouse_id,
                "warehouse_name": tool.warehouse.name if tool.warehouse else None,
                "created_at": tool.created_at.isoformat() if tool.created_at else None,
                "requires_calibration": tool.requires_calibration,
                "calibration_status": tool.calibration_status,
                "last_calibration_date": tool.last_calibration_date.isoformat() if tool.last_calibration_date else None,
                "next_calibration_date": tool.next_calibration_date.isoformat() if tool.next_calibration_date else None
            }

        # Try to find as Chemical (by part_number and lot_number)
        # Using ilike for case-insensitive matching
        if not item:
            chemical = Chemical.query.filter(
                Chemical.part_number.ilike(identifier),
                Chemical.lot_number.ilike(tracking_number)
            ).first()

            if chemical:
                item = chemical
                item_type = "chemical"
                item_details = {
                    "id": chemical.id,
                    "part_number": chemical.part_number,
                    "lot_number": chemical.lot_number,
                    "description": chemical.description,
                    "manufacturer": chemical.manufacturer,
                    "quantity": chemical.quantity,
                    "unit": chemical.unit,
                    "category": chemical.category,
                    "status": chemical.status,
                    "warehouse_id": chemical.warehouse_id,
                    "warehouse_name": chemical.warehouse.name if chemical.warehouse else None,
                    "date_added": chemical.date_added.isoformat() if chemical.date_added else None,
                    "expiration_date": chemical.expiration_date.isoformat() if chemical.expiration_date else None,
                    "parent_lot_number": chemical.parent_lot_number,
                    "lot_sequence": chemical.lot_sequence
                }

        # Try to find as KitExpendable (by part_number and lot_number OR serial_number)
        # Using ilike for case-insensitive matching
        if not item:
            expendable = KitExpendable.query.filter(
                KitExpendable.part_number.ilike(identifier),
                or_(
                    KitExpendable.lot_number.ilike(tracking_number),
                    KitExpendable.serial_number.ilike(tracking_number)
                )
            ).first()

            if expendable:
                item = expendable
                item_type = "expendable"
                kit = db.session.get(Kit, expendable.kit_id)
                item_details = {
                    "id": expendable.id,
                    "part_number": expendable.part_number,
                    "lot_number": expendable.lot_number,
                    "serial_number": expendable.serial_number,
                    "description": expendable.description,
                    "quantity": expendable.quantity,
                    "unit": expendable.unit,
                    "status": expendable.status,
                    "kit_id": expendable.kit_id,
                    "kit_name": kit.name if kit else None,
                    "added_date": expendable.added_date.isoformat() if expendable.added_date else None
                }

        if not item:
            return jsonify({
                "item_found": False,
                "message": f'No item found with identifier "{identifier}" and tracking number "{tracking_number}"'
            }), 404

        # Get current location
        current_location = _get_current_location(item, item_type)

        # Get parent lot information (for chemicals)
        # Using ilike for case-insensitive matching
        parent_lot = None
        if item_type == "chemical" and item.parent_lot_number:
            parent_chemical = Chemical.query.filter(
                Chemical.lot_number.ilike(item.parent_lot_number)
            ).first()
            if parent_chemical:
                parent_lot = {
                    "lot_number": parent_chemical.lot_number,
                    "part_number": parent_chemical.part_number,
                    "description": parent_chemical.description,
                    "quantity": parent_chemical.quantity,
                    "status": parent_chemical.status
                }

        # Get child lots (for chemicals)
        # Using ilike for case-insensitive matching
        child_lots = []
        if item_type == "chemical":
            child_chemicals = Chemical.query.filter(
                Chemical.parent_lot_number.ilike(item.lot_number)
            ).all()
            child_lots = [{
                "lot_number": child.lot_number,
                "part_number": child.part_number,
                "description": child.description,
                "quantity": child.quantity,
                "status": child.status,
                "date_added": child.date_added.isoformat() if child.date_added else None
            } for child in child_chemicals]

        # Build comprehensive history
        history = _build_item_history(item, item_type, identifier, tracking_number)

        return jsonify({
            "item_found": True,
            "item_type": item_type,
            "item_details": item_details,
            "current_location": current_location,
            "parent_lot": parent_lot,
            "child_lots": child_lots,
            "history": history
        }), 200


def _get_current_location(item, item_type):
    """Determine the current location of an item"""
    location = {
        "type": None,
        "name": None,
        "details": None
    }

    if item_type == "tool":
        if item.warehouse_id:
            location["type"] = "warehouse"
            location["name"] = item.warehouse.name if item.warehouse else "Unknown Warehouse"
            location["details"] = item.location
        else:
            # Check if in a kit
            kit_item = KitItem.query.filter_by(item_type="tool", item_id=item.id).first()
            if kit_item:
                kit = db.session.get(Kit, kit_item.kit_id)
                location["type"] = "kit"
                location["name"] = kit.name if kit else "Unknown Kit"
                location["details"] = kit_item.location
            else:
                location["type"] = "unknown"
                location["name"] = item.location or "Unknown"

    elif item_type == "chemical":
        if item.warehouse_id:
            location["type"] = "warehouse"
            location["name"] = item.warehouse.name if item.warehouse else "Unknown Warehouse"
            location["details"] = item.location
        else:
            # Check if in a kit
            kit_item = KitItem.query.filter_by(item_type="chemical", item_id=item.id).first()
            if kit_item:
                kit = db.session.get(Kit, kit_item.kit_id)
                location["type"] = "kit"
                location["name"] = kit.name if kit else "Unknown Kit"
                location["details"] = kit_item.location
            else:
                location["type"] = "unknown"
                location["name"] = item.location or "Unknown"

    elif item_type == "expendable":
        kit = db.session.get(Kit, item.kit_id)
        location["type"] = "kit"
        location["name"] = kit.name if kit else "Unknown Kit"
        location["details"] = item.location

    return location


def _build_item_history(item, item_type, identifier, tracking_number):
    """Build comprehensive history timeline for an item"""
    history_events = []

    # 1. Get creation/receipt event
    if item_type in ["tool", "chemical"]:
        history_events.append({
            "event_type": "creation",
            "timestamp": item.created_at.isoformat() if hasattr(item, "created_at") and item.created_at else (
                item.date_added.isoformat() if hasattr(item, "date_added") and item.date_added else None
            ),
            "description": f"{item_type.capitalize()} added to inventory",
            "user": "System",
            "details": {
                "identifier": identifier,
                "tracking_number": tracking_number
            }
        })
    elif item_type == "expendable":
        history_events.append({
            "event_type": "creation",
            "timestamp": item.added_date.isoformat() if item.added_date else None,
            "description": "Expendable added to kit",
            "user": "System",
            "details": {
                "identifier": identifier,
                "tracking_number": tracking_number
            }
        })

    # 2. Get inventory transactions
    if item_type in ["tool", "chemical"]:
        transactions = InventoryTransaction.query.filter_by(
            item_type=item_type,
            item_id=item.id
        ).order_by(InventoryTransaction.timestamp.asc()).all()

        for trans in transactions:
            from models import User
            user = db.session.get(User, trans.user_id)
            history_events.append({
                "event_type": trans.transaction_type,
                "timestamp": trans.timestamp.isoformat() if trans.timestamp else None,
                "description": _format_transaction_description(trans),
                "user": user.name if user else "Unknown User",
                "details": {
                    "quantity_change": trans.quantity_change,
                    "location_from": trans.location_from,
                    "location_to": trans.location_to,
                    "reference_number": trans.reference_number,
                    "notes": trans.notes
                }
            })

    # 3. Get warehouse transfers
    if item_type in ["tool", "chemical"]:
        warehouse_transfers = WarehouseTransfer.query.filter(
            WarehouseTransfer.item_type == item_type,
            WarehouseTransfer.item_id == item.id
        ).order_by(WarehouseTransfer.transfer_date.asc()).all()

        for transfer in warehouse_transfers:
            from models import User
            user = db.session.get(User, transfer.transferred_by_id)

            # Determine transfer type
            if transfer.from_warehouse_id and transfer.to_warehouse_id:
                event_type = "warehouse_to_warehouse_transfer"
                from_warehouse = db.session.get(Warehouse, transfer.from_warehouse_id)
                to_warehouse = db.session.get(Warehouse, transfer.to_warehouse_id)
                description = f'Transferred from {from_warehouse.name if from_warehouse else "Unknown"} to {to_warehouse.name if to_warehouse else "Unknown"}'
            elif transfer.from_warehouse_id and transfer.to_kit_id:
                event_type = "warehouse_to_kit_transfer"
                from_warehouse = db.session.get(Warehouse, transfer.from_warehouse_id)
                to_kit = db.session.get(Kit, transfer.to_kit_id)
                description = f'Transferred from {from_warehouse.name if from_warehouse else "Unknown"} to Kit {to_kit.name if to_kit else "Unknown"}'
            elif transfer.from_kit_id and transfer.to_warehouse_id:
                event_type = "kit_to_warehouse_transfer"
                from_kit = db.session.get(Kit, transfer.from_kit_id)
                to_warehouse = db.session.get(Warehouse, transfer.to_warehouse_id)
                description = f'Transferred from Kit {from_kit.name if from_kit else "Unknown"} to {to_warehouse.name if to_warehouse else "Unknown"}'
            else:
                event_type = "transfer"
                description = "Transfer"

            # Check if this transfer created a child lot (for partial chemical transfers)
            child_lot_number = None
            child_lot_status = None
            if item_type == "chemical" and transfer.quantity < item.quantity:
                # Look for child chemicals created around the same time
                child_chemicals = Chemical.query.filter(
                    Chemical.parent_lot_number.ilike(item.lot_number),
                    Chemical.date_added >= transfer.transfer_date - timedelta(seconds=5),
                    Chemical.date_added <= transfer.transfer_date + timedelta(seconds=5)
                ).all()
                if child_chemicals:
                    child_lot_number = child_chemicals[0].lot_number
                    child_lot_status = child_chemicals[0].status

            history_events.append({
                "event_type": event_type,
                "timestamp": transfer.transfer_date.isoformat() if transfer.transfer_date else None,
                "description": description,
                "user": user.name if user else "Unknown User",
                "details": {
                    "quantity": transfer.quantity,
                    "status": transfer.status,
                    "notes": transfer.notes,
                    "child_lot_number": child_lot_number,
                    "child_lot_status": child_lot_status
                }
            })

    # 4. Get kit transfers
    kit_transfers = KitTransfer.query.filter(
        KitTransfer.item_type == item_type,
        KitTransfer.item_id == item.id
    ).order_by(KitTransfer.transfer_date.asc()).all()

    for transfer in kit_transfers:
        from models import User
        user = db.session.get(User, transfer.transferred_by)

        # Determine transfer type
        if transfer.from_location_type == "kit" and transfer.to_location_type == "kit":
            event_type = "kit_to_kit_transfer"
            from_kit = db.session.get(Kit, transfer.from_location_id)
            to_kit = db.session.get(Kit, transfer.to_location_id)
            description = f'Transferred from Kit {from_kit.name if from_kit else "Unknown"} to Kit {to_kit.name if to_kit else "Unknown"}'
        elif transfer.from_location_type == "kit" and transfer.to_location_type == "warehouse":
            event_type = "kit_to_warehouse_transfer"
            from_kit = db.session.get(Kit, transfer.from_location_id)
            to_warehouse = db.session.get(Warehouse, transfer.to_location_id)
            description = f'Transferred from Kit {from_kit.name if from_kit else "Unknown"} to {to_warehouse.name if to_warehouse else "Unknown"}'
        elif transfer.from_location_type == "warehouse" and transfer.to_location_type == "kit":
            event_type = "warehouse_to_kit_transfer"
            from_warehouse = db.session.get(Warehouse, transfer.from_location_id)
            to_kit = db.session.get(Kit, transfer.to_location_id)
            description = f'Transferred from {from_warehouse.name if from_warehouse else "Unknown"} to Kit {to_kit.name if to_kit else "Unknown"}'
        else:
            event_type = "transfer"
            description = "Transfer"

        # Check if this transfer created a child lot (for partial chemical transfers)
        child_lot_number = None
        child_lot_status = None
        if item_type == "chemical" and transfer.quantity and item.quantity:
            # Look for child chemicals created around the same time
            child_chemicals = Chemical.query.filter(
                Chemical.parent_lot_number.ilike(item.lot_number),
                Chemical.date_added >= transfer.transfer_date - timedelta(seconds=5),
                Chemical.date_added <= transfer.transfer_date + timedelta(seconds=5)
            ).all()
            if child_chemicals:
                child_lot_number = child_chemicals[0].lot_number
                child_lot_status = child_chemicals[0].status

        history_events.append({
            "event_type": event_type,
            "timestamp": transfer.transfer_date.isoformat() if transfer.transfer_date else None,
            "description": description,
            "user": user.name if user else "Unknown User",
            "details": {
                "quantity": transfer.quantity,
                "status": transfer.status,
                "notes": transfer.notes,
                "child_lot_number": child_lot_number,
                "child_lot_status": child_lot_status
            }
        })

    # 5. Get checkouts (for tools)
    if item_type == "tool":
        checkouts = Checkout.query.filter_by(tool_id=item.id).order_by(Checkout.checkout_date.asc()).all()

        for checkout in checkouts:
            from models import User
            user = db.session.get(User, checkout.user_id)

            # Checkout event
            history_events.append({
                "event_type": "checkout",
                "timestamp": checkout.checkout_date.isoformat() if checkout.checkout_date else None,
                "description": f'Checked out to {user.name if user else "Unknown User"}',
                "user": user.name if user else "Unknown User",
                "details": {
                    "expected_return_date": checkout.expected_return_date.isoformat() if checkout.expected_return_date else None
                }
            })

            # Return event (if returned)
            if checkout.return_date:
                history_events.append({
                    "event_type": "return",
                    "timestamp": checkout.return_date.isoformat(),
                    "description": f'Returned by {user.name if user else "Unknown User"}',
                    "user": user.name if user else "Unknown User",
                    "details": {}
                })

    # 6. Get chemical issuances
    if item_type == "chemical":
        issuances = ChemicalIssuance.query.filter_by(chemical_id=item.id).order_by(ChemicalIssuance.issue_date.asc()).all()

        for issuance in issuances:
            from models import User
            user = db.session.get(User, issuance.user_id)

            history_events.append({
                "event_type": "issuance",
                "timestamp": issuance.issue_date.isoformat() if issuance.issue_date else None,
                "description": f'Issued {issuance.quantity} {item.unit} to {user.name if user else "Unknown User"} for {issuance.hangar}',
                "user": user.name if user else "Unknown User",
                "details": {
                    "quantity": issuance.quantity,
                    "hangar": issuance.hangar,
                    "purpose": issuance.purpose
                }
            })

        returns = ChemicalReturn.query.filter_by(chemical_id=item.id).order_by(ChemicalReturn.return_date.asc()).all()

        for chem_return in returns:
            from models import User

            user = db.session.get(User, chem_return.returned_by_id)

            history_events.append({
                "event_type": "return",
                "timestamp": chem_return.return_date.isoformat() if chem_return.return_date else None,
                "description": (
                    f'Returned {chem_return.quantity} {item.unit} to '
                    f'{chem_return.warehouse.name if chem_return.warehouse else chem_return.location or "Unknown Location"}'
                ),
                "user": user.name if user else "Unknown User",
                "details": {
                    "quantity": chem_return.quantity,
                    "warehouse": chem_return.warehouse.name if chem_return.warehouse else None,
                    "location": chem_return.location,
                    "notes": chem_return.notes,
                }
            })

    # 7. Get kit issuances
    kit_issuances = KitIssuance.query.filter(
        or_(
            and_(KitIssuance.part_number == identifier, KitIssuance.lot_number == tracking_number),
            and_(KitIssuance.part_number == identifier, KitIssuance.serial_number == tracking_number)
        )
    ).order_by(KitIssuance.issued_date.asc()).all()

    for issuance in kit_issuances:
        from models import User
        issuer = db.session.get(User, issuance.issued_by)
        recipient = db.session.get(User, issuance.issued_to) if issuance.issued_to else None

        history_events.append({
            "event_type": "kit_issuance",
            "timestamp": issuance.issued_date.isoformat() if issuance.issued_date else None,
            "description": f'Issued from kit {issuance.kit.name if issuance.kit else "Unknown"} - {issuance.purpose or "No purpose specified"}',
            "user": issuer.name if issuer else "Unknown User",
            "details": {
                "quantity": issuance.quantity,
                "purpose": issuance.purpose,
                "work_order": issuance.work_order,
                "recipient": recipient.name if recipient else None,
                "notes": issuance.notes
            }
        })

    # 8. Get status changes from audit log
    if item_type == "tool":
        # Look for retirement and status change events
        audit_logs = AuditLog.query.filter(
            or_(
                AuditLog.action_details.like(f"%{identifier}%"),
                AuditLog.action_details.like(f"%{tracking_number}%")
            ),
            or_(
                AuditLog.action_type == "tool_retired",
                AuditLog.action_type == "tool_status_changed",
                AuditLog.action_type == "tool_updated"
            )
        ).order_by(AuditLog.timestamp.asc()).all()

        for log in audit_logs:
            if "retired" in log.action_type.lower():
                event_type = "retirement"
                description = f"Tool retired - {log.action_details}"
            elif "status" in log.action_type.lower():
                event_type = "status_change"
                description = f"Status changed - {log.action_details}"
            else:
                event_type = "update"
                description = f"Updated - {log.action_details}"

            history_events.append({
                "event_type": event_type,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "description": description,
                "user": "System",
                "details": {
                    "action_details": log.action_details
                }
            })

    # Sort all events by timestamp
    history_events.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "", reverse=True)

    return history_events


def _format_transaction_description(transaction):
    """Format a transaction into a human-readable description"""
    trans_type = transaction.transaction_type

    if trans_type == "receipt":
        return "Received into inventory"
    if trans_type == "issuance":
        return f'Issued - {transaction.notes or "No notes"}'
    if trans_type == "transfer":
        return f'Transferred from {transaction.location_from or "Unknown"} to {transaction.location_to or "Unknown"}'
    if trans_type == "adjustment":
        return f'Inventory adjustment - {transaction.notes or "No notes"}'
    if trans_type == "checkout":
        return "Checked out"
    if trans_type == "return":
        return "Returned"
    if trans_type == "kit_issuance":
        return "Issued from kit"
    return f'{trans_type.replace("_", " ").title()}'

