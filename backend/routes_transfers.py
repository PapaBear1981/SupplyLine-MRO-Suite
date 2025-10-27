"""
Warehouse transfer routes.
Handles transfers between warehouses and kits.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Chemical, Tool, Warehouse, WarehouseTransfer, db
from models_kits import Kit, KitBox, KitItem
from utils.transaction_helper import record_transaction


transfers_bp = Blueprint("transfers", __name__)


@transfers_bp.route("/transfers/warehouse-to-kit", methods=["POST"])
@jwt_required()
def transfer_warehouse_to_kit():
    """
    Transfer a tool or chemical from warehouse to kit.
    Required fields:
        - from_warehouse_id: Source warehouse ID
        - to_kit_id: Destination kit ID
        - box_id: Destination box ID within the kit
        - item_type: 'tool' or 'chemical'
        - item_id: ID of the tool or chemical
        - quantity: Quantity to transfer (default: 1)
        - location: Optional location within the box
        - notes: Optional transfer notes
    """
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # Validate required fields
        required_fields = ["from_warehouse_id", "to_kit_id", "box_id", "item_type", "item_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate item_type
        if data["item_type"] not in ["tool", "chemical"]:
            return jsonify({"error": 'item_type must be "tool" or "chemical"'}), 400

        # Get warehouse, kit, and box
        warehouse = Warehouse.query.get(data["from_warehouse_id"])
        kit = Kit.query.get(data["to_kit_id"])
        box = KitBox.query.get(data["box_id"])

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404
        if not kit:
            return jsonify({"error": "Kit not found"}), 404
        if not box:
            return jsonify({"error": "Box not found"}), 404
        if box.kit_id != kit.id:
            return jsonify({"error": "Box does not belong to the specified kit"}), 400

        # Get the item
        if data["item_type"] == "tool":
            item = Tool.query.get(data["item_id"])
            if not item:
                return jsonify({"error": "Tool not found"}), 404
            if item.warehouse_id != warehouse.id:
                return jsonify({"error": "Tool is not in the specified warehouse"}), 400

            # Create kit item
            kit_item = KitItem(
                kit_id=kit.id,
                box_id=box.id,
                item_type="tool",
                item_id=item.id,
                part_number=item.tool_number,
                serial_number=item.serial_number,
                description=item.description,
                quantity=data.get("quantity", 1),
                location=data.get("location"),
                status="available",
                added_date=datetime.now(),
                last_updated=datetime.now()
            )

            # Remove from warehouse
            item.warehouse_id = None

        else:  # chemical
            item = Chemical.query.get(data["item_id"])
            if not item:
                return jsonify({"error": "Chemical not found"}), 404
            if item.warehouse_id != warehouse.id:
                return jsonify({"error": "Chemical is not in the specified warehouse"}), 400

            # Create kit item
            kit_item = KitItem(
                kit_id=kit.id,
                box_id=box.id,
                item_type="chemical",
                item_id=item.id,
                part_number=item.part_number,
                lot_number=item.lot_number,
                description=item.description,
                quantity=data.get("quantity", 1),
                location=data.get("location"),
                status="available",
                added_date=datetime.now(),
                last_updated=datetime.now()
            )

            # Remove from warehouse
            item.warehouse_id = None

        # Create transfer record
        transfer = WarehouseTransfer(
            from_warehouse_id=warehouse.id,
            to_kit_id=kit.id,
            item_type=data["item_type"],
            item_id=data["item_id"],
            quantity=data.get("quantity", 1),
            transfer_date=datetime.now(),
            transferred_by_id=current_user_id,
            notes=data.get("notes"),
            status="completed"
        )

        # Record transaction
        record_transaction(
            db=db,
            item_type=data["item_type"],
            item_id=data["item_id"],
            transaction_type="transfer",
            quantity=data.get("quantity", 1),
            user_id=current_user_id,
            from_location=warehouse.name,
            to_location=f"{kit.name} - {box.box_number}",
            notes=data.get("notes", f"Transferred from {warehouse.name} to kit {kit.name}")
        )

        db.session.add(kit_item)
        db.session.add(transfer)
        db.session.commit()

        return jsonify({
            "message": "Transfer completed successfully",
            "transfer": transfer.to_dict(),
            "kit_item": kit_item.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@transfers_bp.route("/transfers/kit-to-warehouse", methods=["POST"])
@jwt_required()
def transfer_kit_to_warehouse():
    """
    Transfer a tool or chemical from kit back to warehouse.
    Required fields:
        - from_kit_id: Source kit ID
        - kit_item_id: ID of the kit item to transfer
        - to_warehouse_id: Destination warehouse ID
        - notes: Optional transfer notes
    """
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # Validate required fields
        required_fields = ["from_kit_id", "kit_item_id", "to_warehouse_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Get kit, kit item, and warehouse
        kit = Kit.query.get(data["from_kit_id"])
        kit_item = KitItem.query.get(data["kit_item_id"])
        warehouse = Warehouse.query.get(data["to_warehouse_id"])

        if not kit:
            return jsonify({"error": "Kit not found"}), 404
        if not kit_item:
            return jsonify({"error": "Kit item not found"}), 404
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404
        if kit_item.kit_id != kit.id:
            return jsonify({"error": "Kit item does not belong to the specified kit"}), 400

        # Get the actual item and move it to warehouse
        if kit_item.item_type == "tool":
            item = Tool.query.get(kit_item.item_id)
            if item:
                item.warehouse_id = warehouse.id
        else:  # chemical
            item = Chemical.query.get(kit_item.item_id)
            if item:
                item.warehouse_id = warehouse.id

        # Create transfer record
        transfer = WarehouseTransfer(
            from_kit_id=kit.id,
            to_warehouse_id=warehouse.id,
            item_type=kit_item.item_type,
            item_id=kit_item.item_id,
            quantity=kit_item.quantity,
            transfer_date=datetime.now(),
            transferred_by_id=current_user_id,
            notes=data.get("notes"),
            status="completed"
        )

        # Record transaction
        record_transaction(
            db=db,
            item_type=kit_item.item_type,
            item_id=kit_item.item_id,
            transaction_type="transfer",
            quantity=kit_item.quantity,
            user_id=current_user_id,
            from_location=f"{kit.name} - {kit_item.box.box_number if kit_item.box else 'Unknown'}",
            to_location=warehouse.name,
            notes=data.get("notes", f"Returned from kit {kit.name} to {warehouse.name}")
        )

        # Remove kit item
        db.session.delete(kit_item)
        db.session.add(transfer)
        db.session.commit()

        return jsonify({
            "message": "Transfer completed successfully",
            "transfer": transfer.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@transfers_bp.route("/transfers/warehouse-to-warehouse", methods=["POST"])
@jwt_required()
def transfer_warehouse_to_warehouse():
    """
    Transfer a tool or chemical between warehouses.
    Required fields:
        - from_warehouse_id: Source warehouse ID
        - to_warehouse_id: Destination warehouse ID
        - item_type: 'tool' or 'chemical'
        - item_id: ID of the tool or chemical
        - quantity: Quantity to transfer (default: 1)
        - notes: Optional transfer notes
    """
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # Validate required fields
        required_fields = ["from_warehouse_id", "to_warehouse_id", "item_type", "item_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate item_type
        if data["item_type"] not in ["tool", "chemical"]:
            return jsonify({"error": 'item_type must be "tool" or "chemical"'}), 400

        # Get warehouses
        from_warehouse = Warehouse.query.get(data["from_warehouse_id"])
        to_warehouse = Warehouse.query.get(data["to_warehouse_id"])

        if not from_warehouse:
            return jsonify({"error": "Source warehouse not found"}), 404
        if not to_warehouse:
            return jsonify({"error": "Destination warehouse not found"}), 404
        if from_warehouse.id == to_warehouse.id:
            return jsonify({"error": "Source and destination warehouses must be different"}), 400

        # Get the item and transfer it
        if data["item_type"] == "tool":
            item = Tool.query.get(data["item_id"])
            if not item:
                return jsonify({"error": "Tool not found"}), 404
            if item.warehouse_id != from_warehouse.id:
                return jsonify({"error": "Tool is not in the source warehouse"}), 400

            item.warehouse_id = to_warehouse.id

        else:  # chemical
            item = Chemical.query.get(data["item_id"])
            if not item:
                return jsonify({"error": "Chemical not found"}), 404
            if item.warehouse_id != from_warehouse.id:
                return jsonify({"error": "Chemical is not in the source warehouse"}), 400

            item.warehouse_id = to_warehouse.id

        # Create transfer record
        transfer = WarehouseTransfer(
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            item_type=data["item_type"],
            item_id=data["item_id"],
            quantity=data.get("quantity", 1),
            transfer_date=datetime.now(),
            transferred_by_id=current_user_id,
            notes=data.get("notes"),
            status="completed"
        )

        # Record transaction
        record_transaction(
            db=db,
            item_type=data["item_type"],
            item_id=data["item_id"],
            transaction_type="transfer",
            quantity=data.get("quantity", 1),
            user_id=current_user_id,
            from_location=from_warehouse.name,
            to_location=to_warehouse.name,
            notes=data.get("notes", f"Transferred from {from_warehouse.name} to {to_warehouse.name}")
        )

        db.session.add(transfer)
        db.session.commit()

        return jsonify({
            "message": "Transfer completed successfully",
            "transfer": transfer.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@transfers_bp.route("/transfers", methods=["GET"])
@jwt_required()
def get_transfers():
    """
    Get transfer history with filters.
    Query params:
        - warehouse_id: Filter by warehouse (from or to)
        - kit_id: Filter by kit (from or to)
        - item_type: Filter by item type (tool/chemical)
        - item_id: Filter by specific item
        - status: Filter by status
        - start_date: Filter by start date (ISO format)
        - end_date: Filter by end date (ISO format)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
    """
    try:
        # Get query parameters
        warehouse_id = request.args.get("warehouse_id", type=int)
        kit_id = request.args.get("kit_id", type=int)
        item_type = request.args.get("item_type")
        item_id = request.args.get("item_id", type=int)
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        # Build query
        query = WarehouseTransfer.query

        # Apply filters
        if warehouse_id:
            query = query.filter(
                db.or_(
                    WarehouseTransfer.from_warehouse_id == warehouse_id,
                    WarehouseTransfer.to_warehouse_id == warehouse_id
                )
            )

        if kit_id:
            query = query.filter(
                db.or_(
                    WarehouseTransfer.from_kit_id == kit_id,
                    WarehouseTransfer.to_kit_id == kit_id
                )
            )

        if item_type:
            query = query.filter_by(item_type=item_type)

        if item_id:
            query = query.filter_by(item_id=item_id)

        if status:
            query = query.filter_by(status=status)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(WarehouseTransfer.transfer_date >= start_dt)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use ISO format."}), 400

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(WarehouseTransfer.transfer_date <= end_dt)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use ISO format."}), 400

        # Paginate
        pagination = query.order_by(WarehouseTransfer.transfer_date.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "transfers": [transfer.to_dict() for transfer in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
