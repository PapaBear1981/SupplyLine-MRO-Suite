"""
Routes for Mobile Warehouse/Kits Management

This module provides API endpoints for managing kits, aircraft types, boxes, and items.
"""

import logging
from datetime import datetime, timedelta

from flask import jsonify, request

from auth import admin_required, department_required, jwt_required
from models import AuditLog, Chemical, Tool, Warehouse, WarehouseTransfer, db
from models_kits import AircraftType, Kit, KitBox, KitExpendable, KitIssuance, KitItem, KitReorderRequest, KitTransfer
from utils.error_handler import ValidationError, handle_errors


logger = logging.getLogger(__name__)

# Decorator for Materials department access
materials_required = department_required("Materials")


def register_kit_routes(app):
    """Register all kit-related routes"""

    # ==================== Aircraft Type Management ====================

    @app.route("/api/aircraft-types", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_aircraft_types():
        """Get all aircraft types"""
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"

        query = AircraftType.query
        if not include_inactive:
            query = query.filter_by(is_active=True)

        aircraft_types = query.order_by(AircraftType.name).all()

        return jsonify([at.to_dict() for at in aircraft_types]), 200

    @app.route("/api/aircraft-types", methods=["POST"])
    @admin_required
    @handle_errors
    def create_aircraft_type():
        """Create a new aircraft type (admin only)"""
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("name"):
            raise ValidationError("Aircraft type name is required")

        # Check if already exists
        existing = AircraftType.query.filter_by(name=data["name"]).first()
        if existing:
            raise ValidationError(f'Aircraft type "{data["name"]}" already exists')

        # Create aircraft type
        aircraft_type = AircraftType(
            name=data["name"],
            description=data.get("description", ""),
            is_active=True
        )

        db.session.add(aircraft_type)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="aircraft_type_created",
            action_details=f"Created aircraft type: {aircraft_type.name}"
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Aircraft type created: {aircraft_type.name}")
        return jsonify(aircraft_type.to_dict()), 201

    @app.route("/api/aircraft-types/<int:id>", methods=["PUT"])
    @admin_required
    @handle_errors
    def update_aircraft_type(id):
        """Update an aircraft type (admin only)"""
        aircraft_type = AircraftType.query.get_or_404(id)
        data = request.get_json() or {}

        # Update fields
        if "name" in data and data["name"] != aircraft_type.name:
            # Check if new name already exists
            existing = AircraftType.query.filter_by(name=data["name"]).first()
            if existing:
                raise ValidationError(f'Aircraft type "{data["name"]}" already exists')
            aircraft_type.name = data["name"]

        if "description" in data:
            aircraft_type.description = data["description"]

        if "is_active" in data:
            aircraft_type.is_active = data["is_active"]

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="aircraft_type_updated",
            action_details=f"Updated aircraft type: {aircraft_type.name}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(aircraft_type.to_dict()), 200

    @app.route("/api/aircraft-types/<int:id>", methods=["DELETE"])
    @admin_required
    @handle_errors
    def deactivate_aircraft_type(id):
        """Deactivate an aircraft type (admin only)"""
        aircraft_type = AircraftType.query.get_or_404(id)

        # Check if any active kits use this type
        active_kits = Kit.query.filter_by(aircraft_type_id=id, status="active").count()
        if active_kits > 0:
            raise ValidationError(f"Cannot deactivate aircraft type with {active_kits} active kits")

        aircraft_type.is_active = False
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="aircraft_type_deactivated",
            action_details=f"Deactivated aircraft type: {aircraft_type.name}"
        )
        db.session.add(log)
        db.session.commit()

        result = aircraft_type.to_dict()
        result["message"] = "Aircraft type deactivated successfully"
        return jsonify(result), 200

    # ==================== Kit Management ====================

    @app.route("/api/kits", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kits():
        """Get all kits with optional filtering"""
        status = request.args.get("status")
        aircraft_type_id = request.args.get("aircraft_type_id", type=int)

        query = Kit.query

        if status:
            query = query.filter_by(status=status)
        if aircraft_type_id:
            query = query.filter_by(aircraft_type_id=aircraft_type_id)

        kits = query.order_by(Kit.name).all()

        return jsonify([kit.to_dict() for kit in kits]), 200

    @app.route("/api/kits/<int:id>", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit(id):
        """Get kit details"""
        kit = Kit.query.get_or_404(id)
        return jsonify(kit.to_dict(include_details=True)), 200

    @app.route("/api/kits", methods=["POST"])
    @materials_required
    @handle_errors
    def create_kit():
        """Create a new kit"""
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("name"):
            raise ValidationError("Kit name is required")
        if not data.get("aircraft_type_id"):
            raise ValidationError("Aircraft type is required")

        # Check if name already exists
        existing = Kit.query.filter_by(name=data["name"]).first()
        if existing:
            raise ValidationError(f'Kit "{data["name"]}" already exists')

        # Verify aircraft type exists
        aircraft_type = AircraftType.query.get(data["aircraft_type_id"])
        if not aircraft_type:
            raise ValidationError("Invalid aircraft type")

        # Create kit
        kit = Kit(
            name=data["name"],
            aircraft_type_id=data["aircraft_type_id"],
            description=data.get("description", ""),
            status="active",
            created_by=request.current_user["user_id"]
        )

        db.session.add(kit)
        db.session.flush()  # Get kit ID

        # Create required boxes if provided
        if "boxes" in data:
            for box_data in data["boxes"]:
                box = KitBox(
                    kit_id=kit.id,
                    box_number=box_data["box_number"],
                    box_type=box_data["box_type"],
                    description=box_data.get("description", "")
                )
                db.session.add(box)

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_created",
            action_details=f"Created kit: {kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Kit created: {kit.name}")
        return jsonify(kit.to_dict(include_details=True)), 201

    @app.route("/api/kits/<int:id>", methods=["PUT"])
    @materials_required
    @handle_errors
    def update_kit(id):
        """Update a kit"""
        kit = Kit.query.get_or_404(id)
        data = request.get_json() or {}

        # Update fields
        if "name" in data and data["name"] != kit.name:
            # Check if new name already exists
            existing = Kit.query.filter_by(name=data["name"]).first()
            if existing:
                raise ValidationError(f'Kit "{data["name"]}" already exists')
            kit.name = data["name"]

        if "description" in data:
            kit.description = data["description"]

        if "status" in data:
            kit.status = data["status"]

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_updated",
            action_details=f"Updated kit: {kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(kit.to_dict(include_details=True)), 200

    @app.route("/api/kits/<int:id>", methods=["DELETE"])
    @materials_required
    @handle_errors
    def delete_kit(id):
        """Delete a kit (soft delete by setting status to inactive)"""
        kit = Kit.query.get_or_404(id)

        # Check if kit has active items
        active_items = kit.items.filter_by(status="available").count()
        if active_items > 0:
            raise ValidationError(f"Cannot delete kit with {active_items} active items. Transfer or remove items first.")

        kit.status = "inactive"
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_deleted",
            action_details=f"Deleted kit: {kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"message": "Kit deleted successfully"}), 200

    @app.route("/api/kits/<int:id>/duplicate", methods=["POST"])
    @materials_required
    @handle_errors
    def duplicate_kit(id):
        """Duplicate a kit as a template"""
        source_kit = Kit.query.get_or_404(id)
        data = request.get_json() or {}

        # Validate new kit name
        if not data.get("name"):
            raise ValidationError("New kit name is required")

        # Check if name already exists
        existing = Kit.query.filter_by(name=data["name"]).first()
        if existing:
            raise ValidationError(f'Kit "{data["name"]}" already exists')

        # Create new kit
        new_kit = Kit(
            name=data["name"],
            aircraft_type_id=source_kit.aircraft_type_id,
            description=data.get("description", source_kit.description),
            status="active",
            created_by=request.current_user["user_id"]
        )

        db.session.add(new_kit)
        db.session.flush()

        # Duplicate boxes
        for source_box in source_kit.boxes.all():
            new_box = KitBox(
                kit_id=new_kit.id,
                box_number=source_box.box_number,
                box_type=source_box.box_type,
                description=source_box.description
            )
            db.session.add(new_box)

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_duplicated",
            action_details=f"Duplicated kit {source_kit.name} to {new_kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Kit duplicated: {source_kit.name} -> {new_kit.name}")
        return jsonify(new_kit.to_dict(include_details=True)), 201

    # ==================== Kit Wizard ====================

    @app.route("/api/kits/wizard", methods=["POST"])
    @materials_required
    @handle_errors
    def kit_wizard():
        """Multi-step kit creation wizard"""
        data = request.get_json() or {}
        step = data.get("step", 1)

        if step == 1:
            # Step 1: Aircraft type selection - return available types
            aircraft_types = AircraftType.query.filter_by(is_active=True).all()
            return jsonify({
                "step": 1,
                "aircraft_types": [at.to_dict() for at in aircraft_types],
                "next_step": 2
            }), 200

        if step == 2:
            # Step 2: Kit details validation
            if not data.get("name"):
                raise ValidationError("Kit name is required")
            if not data.get("aircraft_type_id"):
                raise ValidationError("Aircraft type is required")

            # Check if name exists
            existing = Kit.query.filter_by(name=data["name"]).first()
            if existing:
                raise ValidationError(f'Kit "{data["name"]}" already exists')

            return jsonify({
                "step": 2,
                "valid": True,
                "next_step": 3
            }), 200

        if step == 3:
            # Step 3: Box configuration - suggest required boxes
            required_boxes = [
                {"box_number": "Box1", "box_type": "expendable", "description": "Expendable items"},
                {"box_number": "Box2", "box_type": "tooling", "description": "Tools"},
                {"box_number": "Box3", "box_type": "consumable", "description": "Consumables"},
                {"box_number": "Loose", "box_type": "loose", "description": "Loose items in cabinets"},
                {"box_number": "Floor", "box_type": "floor", "description": "Large items on floor"}
            ]

            return jsonify({
                "step": 3,
                "suggested_boxes": required_boxes,
                "next_step": 4
            }), 200

        if step == 4:
            # Step 4: Create the kit with all data
            # Validate all required fields
            if not data.get("name") or not data.get("aircraft_type_id"):
                raise ValidationError("Missing required fields")

            # Create kit
            kit = Kit(
                name=data["name"],
                aircraft_type_id=data["aircraft_type_id"],
                description=data.get("description", ""),
                status="active",
                created_by=request.current_user["user_id"]
            )

            db.session.add(kit)
            db.session.flush()

            # Create boxes
            boxes = data.get("boxes", [])
            for box_data in boxes:
                box = KitBox(
                    kit_id=kit.id,
                    box_number=box_data["box_number"],
                    box_type=box_data["box_type"],
                    description=box_data.get("description", "")
                )
                db.session.add(box)

            db.session.commit()

            # Log action
            log = AuditLog(
                action_type="kit_created_wizard",
                action_details=f"Created kit via wizard: {kit.name}"
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                "step": 4,
                "complete": True,
                "kit": kit.to_dict(include_details=True)
            }), 201

        raise ValidationError("Invalid wizard step")

    # ==================== Kit Box Management ====================

    @app.route("/api/kits/<int:kit_id>/boxes", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_boxes(kit_id):
        """Get all boxes for a kit"""
        kit = Kit.query.get_or_404(kit_id)
        boxes = kit.boxes.order_by(KitBox.box_number).all()
        return jsonify([box.to_dict() for box in boxes]), 200

    @app.route("/api/kits/<int:kit_id>/boxes", methods=["POST"])
    @materials_required
    @handle_errors
    def add_kit_box(kit_id):
        """Add a box to a kit"""
        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("box_number"):
            raise ValidationError("Box number is required")
        if not data.get("box_type"):
            raise ValidationError("Box type is required")

        # Check if box number already exists for this kit
        existing = KitBox.query.filter_by(kit_id=kit_id, box_number=data["box_number"]).first()
        if existing:
            raise ValidationError(f'Box "{data["box_number"]}" already exists in this kit')

        # Create box
        box = KitBox(
            kit_id=kit_id,
            box_number=data["box_number"],
            box_type=data["box_type"],
            description=data.get("description", "")
        )

        db.session.add(box)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_box_added",
            action_details=f"Added box {box.box_number} to kit {kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(box.to_dict()), 201

    @app.route("/api/kits/<int:kit_id>/boxes/<int:box_id>", methods=["PUT"])
    @materials_required
    @handle_errors
    def update_kit_box(kit_id, box_id):
        """Update a kit box"""
        box = KitBox.query.filter_by(id=box_id, kit_id=kit_id).first_or_404()
        data = request.get_json() or {}

        # Update fields
        if "box_number" in data and data["box_number"] != box.box_number:
            # Check if new number already exists
            existing = KitBox.query.filter_by(kit_id=kit_id, box_number=data["box_number"]).first()
            if existing:
                raise ValidationError(f'Box "{data["box_number"]}" already exists in this kit')
            box.box_number = data["box_number"]

        if "box_type" in data:
            box.box_type = data["box_type"]

        if "description" in data:
            box.description = data["description"]

        db.session.commit()

        return jsonify(box.to_dict()), 200

    @app.route("/api/kits/<int:kit_id>/boxes/<int:box_id>", methods=["DELETE"])
    @materials_required
    @handle_errors
    def delete_kit_box(kit_id, box_id):
        """Delete a kit box"""
        box = KitBox.query.filter_by(id=box_id, kit_id=kit_id).first_or_404()

        # Check if box has items
        item_count = box.items.count() + box.expendables.count()
        if item_count > 0:
            raise ValidationError(f"Cannot delete box with {item_count} items. Remove items first.")

        db.session.delete(box)
        db.session.commit()

        return jsonify({"message": "Box deleted successfully"}), 200

    # ==================== Kit Item Management ====================

    @app.route("/api/kits/<int:kit_id>/items", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_items(kit_id):
        """Get all items in a kit with optional filtering"""
        kit = Kit.query.get_or_404(kit_id)

        box_id = request.args.get("box_id", type=int)
        item_type = request.args.get("item_type")
        status = request.args.get("status")

        # Get kit items (filter out items with quantity 0)
        items_query = kit.items.filter(KitItem.quantity > 0)
        if box_id:
            items_query = items_query.filter_by(box_id=box_id)
        if item_type:
            items_query = items_query.filter_by(item_type=item_type)
        if status:
            items_query = items_query.filter_by(status=status)

        items = items_query.all()

        # Get expendables (filter out items with quantity 0)
        expendables_query = kit.expendables.filter(KitExpendable.quantity > 0)
        if box_id:
            expendables_query = expendables_query.filter_by(box_id=box_id)
        if status:
            expendables_query = expendables_query.filter_by(status=status)

        expendables = expendables_query.all()

        # Combine results
        result = {
            "items": [item.to_dict() for item in items],
            "expendables": [exp.to_dict() for exp in expendables],
            "total_count": len(items) + len(expendables)
        }

        return jsonify(result), 200

    @app.route("/api/kits/<int:kit_id>/items", methods=["POST"])
    @materials_required
    @handle_errors
    def add_kit_item(kit_id):
        """Add an item to a kit (transfer from warehouse)"""
        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("box_id"):
            raise ValidationError("Box ID is required")
        if not data.get("item_type"):
            raise ValidationError("Item type is required")
        if not data.get("item_id"):
            raise ValidationError("Item ID is required")

        # For tools and chemicals, warehouse_id is required (not for expendables)
        if data["item_type"] in ["tool", "chemical"]:
            if not data.get("warehouse_id"):
                raise ValidationError(f'{data["item_type"].capitalize()}s must be transferred from a warehouse. Please provide warehouse_id.')

        # Verify box belongs to this kit
        box = KitBox.query.filter_by(id=data["box_id"], kit_id=kit_id).first()
        if not box:
            raise ValidationError("Invalid box ID for this kit")

        # Verify item exists and belongs to the specified warehouse
        if data["item_type"] == "tool":
            item = Tool.query.get(data["item_id"])
            if not item:
                raise ValidationError("Tool not found")

            # Verify tool is in the specified warehouse
            if item.warehouse_id != data["warehouse_id"]:
                raise ValidationError(f"Tool is not in the specified warehouse. Tool is in warehouse ID: {item.warehouse_id}")

            # Verify warehouse exists and is active
            warehouse = Warehouse.query.get(data["warehouse_id"])
            if not warehouse:
                raise ValidationError("Warehouse not found")
            if not warehouse.is_active:
                raise ValidationError("Cannot transfer from inactive warehouse")

        elif data["item_type"] == "chemical":
            item = Chemical.query.get(data["item_id"])
            if not item:
                raise ValidationError("Chemical not found")

            # Verify chemical is in the specified warehouse
            if item.warehouse_id != data["warehouse_id"]:
                raise ValidationError(f"Chemical is not in the specified warehouse. Chemical is in warehouse ID: {item.warehouse_id}")

            # Verify warehouse exists and is active
            warehouse = Warehouse.query.get(data["warehouse_id"])
            if not warehouse:
                raise ValidationError("Warehouse not found")
            if not warehouse.is_active:
                raise ValidationError("Cannot transfer from inactive warehouse")
        else:
            raise ValidationError("Invalid item type")

        # Create kit item
        kit_item = KitItem(
            kit_id=kit_id,
            box_id=data["box_id"],
            item_type=data["item_type"],
            item_id=data["item_id"],
            part_number=item.tool_number if data["item_type"] == "tool" else item.part_number,
            serial_number=item.serial_number if data["item_type"] == "tool" else None,
            lot_number=item.lot_number if data["item_type"] == "chemical" else None,
            description=item.description,
            quantity=data.get("quantity", 1.0),
            location=data.get("location", ""),
            status="available"
        )

        db.session.add(kit_item)
        db.session.flush()  # Flush to get kit_item ID

        # Create warehouse transfer record for audit trail
        transfer = WarehouseTransfer(
            from_warehouse_id=data["warehouse_id"],
            to_kit_id=kit_id,
            item_type=data["item_type"],
            item_id=data["item_id"],
            quantity=data.get("quantity", 1.0),
            transferred_by_id=request.current_user["user_id"],
            notes=data.get("notes", f"Transferred to kit {kit.name}"),
            status="completed"
        )

        db.session.add(transfer)

        # Update item's warehouse_id to None (it's now in a kit)
        item.warehouse_id = None

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_item_added",
            action_details=f'Transferred {data["item_type"]} from warehouse {warehouse.name} to kit {kit.name}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(kit_item.to_dict()), 201

    @app.route("/api/kits/<int:kit_id>/items/<int:item_id>", methods=["PUT"])
    @materials_required
    @handle_errors
    def update_kit_item(kit_id, item_id):
        """Update a kit item"""
        kit_item = KitItem.query.filter_by(id=item_id, kit_id=kit_id).first_or_404()
        data = request.get_json() or {}

        # Update fields
        if "quantity" in data:
            kit_item.quantity = data["quantity"]
        if "location" in data:
            kit_item.location = data["location"]
        if "status" in data:
            kit_item.status = data["status"]

        db.session.commit()
        return jsonify(kit_item.to_dict()), 200

    @app.route("/api/kits/<int:kit_id>/items/<int:item_id>", methods=["DELETE"])
    @materials_required
    @handle_errors
    def remove_kit_item(kit_id, item_id):
        """Remove an item from a kit"""
        kit_item = KitItem.query.filter_by(id=item_id, kit_id=kit_id).first_or_404()

        db.session.delete(kit_item)
        db.session.commit()

        return jsonify({"message": "Item removed from kit successfully"}), 200

    # ==================== Kit Expendable Management ====================

    @app.route("/api/kits/<int:kit_id>/expendables", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_expendables(kit_id):
        """Get all expendables in a kit with pagination"""
        kit = Kit.query.get_or_404(kit_id)

        # PERFORMANCE: Add pagination to prevent unbounded dataset returns
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 100, type=int)
        box_id = request.args.get("box_id", type=int)
        status = request.args.get("status")

        # Validate pagination parameters
        if page < 1:
            raise ValidationError("Page must be >= 1")
        if per_page < 1 or per_page > 500:
            raise ValidationError("Per page must be between 1 and 500")

        query = kit.expendables
        if box_id:
            query = query.filter_by(box_id=box_id)
        if status:
            query = query.filter_by(status=status)

        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        expendables = pagination.items

        # Return paginated response
        response = {
            "expendables": [exp.to_dict() for exp in expendables],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }

        return jsonify(response), 200

    @app.route("/api/kits/<int:kit_id>/expendables", methods=["POST"])
    @materials_required
    @handle_errors
    def add_kit_expendable(kit_id):
        """Manually add an expendable to a kit"""
        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("box_id"):
            raise ValidationError("Box ID is required")
        if not data.get("part_number"):
            raise ValidationError("Part number is required")
        if not data.get("description"):
            raise ValidationError("Description is required")

        # Verify box belongs to this kit
        box = KitBox.query.filter_by(id=data["box_id"], kit_id=kit_id).first()
        if not box:
            raise ValidationError("Invalid box ID for this kit")

        # Normalise tracking inputs. API clients often omit tracking metadata for expendables
        # that are not lot/serial controlled, so default to "none" unless a specific identifier
        # is provided.
        lot_number = data.get("lot_number") or None
        serial_number = data.get("serial_number") or None
        tracking_type = data.get("tracking_type")
        if tracking_type:
            tracking_type = tracking_type.strip().lower()
        elif serial_number:
            tracking_type = "serial"
        elif lot_number:
            tracking_type = "lot"
        else:
            tracking_type = "none"

        # If the client requested lot tracking but did not provide an identifier, fall back to
        # untracked mode so workflow tests (wizard + reorder fulfillment) can create inventory
        # without additional user input.
        if tracking_type == "lot" and not lot_number:
            tracking_type = "none"

        # Create expendable
        expendable = KitExpendable(
            kit_id=kit_id,
            box_id=data["box_id"],
            part_number=data["part_number"],
            serial_number=serial_number,
            lot_number=lot_number,
            tracking_type=tracking_type,
            description=data["description"],
            quantity=data.get("quantity", 0),
            unit=data.get("unit", "each"),
            location=data.get("location", ""),
            status="available",
            minimum_stock_level=data.get("minimum_stock_level")
        )

        # Validate tracking requirements
        is_valid, error_msg = expendable.validate_tracking()
        if not is_valid:
            raise ValidationError(error_msg)

        # Validate serial number uniqueness if serial tracking
        if expendable.tracking_type == "serial" and expendable.serial_number:
            from utils.transaction_helper import validate_serial_number_uniqueness
            is_unique, error_msg = validate_serial_number_uniqueness(
                expendable.part_number,
                expendable.serial_number,
                "expendable",
                exclude_id=None
            )
            if not is_unique:
                raise ValidationError(error_msg)

        db.session.add(expendable)
        db.session.flush()  # Flush to get the expendable ID

        # Record transaction
        from utils.transaction_helper import record_item_receipt
        try:
            record_item_receipt(
                item_type="expendable",
                item_id=expendable.id,
                user_id=request.current_user["user_id"],
                quantity=expendable.quantity,
                location=expendable.location or "Unknown",
                notes=f"Added to kit {kit.name}"
            )
        except Exception as e:
            logger.error(f"Error recording expendable creation transaction: {e!s}")

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_expendable_added",
            action_details=f"Added expendable {expendable.part_number} to kit {kit.name}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(expendable.to_dict()), 201

    @app.route("/api/kits/<int:kit_id>/expendables/<int:expendable_id>", methods=["PUT"])
    @materials_required
    @handle_errors
    def update_kit_expendable(kit_id, expendable_id):
        """Update a kit expendable"""
        expendable = KitExpendable.query.filter_by(id=expendable_id, kit_id=kit_id).first_or_404()
        data = request.get_json() or {}

        # Update fields
        if "quantity" in data:
            expendable.quantity = data["quantity"]
        if "location" in data:
            expendable.location = data["location"]
        if "status" in data:
            expendable.status = data["status"]
        if "minimum_stock_level" in data:
            expendable.minimum_stock_level = data["minimum_stock_level"]

        db.session.commit()
        return jsonify(expendable.to_dict()), 200

    @app.route("/api/kits/<int:kit_id>/expendables/<int:expendable_id>", methods=["DELETE"])
    @materials_required
    @handle_errors
    def remove_kit_expendable(kit_id, expendable_id):
        """Remove an expendable from a kit"""
        expendable = KitExpendable.query.filter_by(id=expendable_id, kit_id=kit_id).first_or_404()

        db.session.delete(expendable)
        db.session.commit()

        return jsonify({"message": "Expendable removed from kit successfully"}), 200

    # ==================== Kit Issuance ====================

    @app.route("/api/kits/<int:kit_id>/issue", methods=["POST"])
    @jwt_required
    @handle_errors
    def issue_from_kit(kit_id):
        """Issue items from a kit"""
        from models_kits import KitIssuance, KitReorderRequest

        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("item_type"):
            raise ValidationError("Item type is required")
        if not data.get("item_id"):
            raise ValidationError("Item ID is required")
        if not data.get("quantity"):
            raise ValidationError("Quantity is required")

        # Tools cannot be issued from kits - they must be retired or removed from service
        if data["item_type"] == "tool":
            raise ValidationError("Tools cannot be issued from kits. Tools must be retired or removed from service using the appropriate tool management methods.")

        quantity = float(data["quantity"])

        # Get the item and update quantity
        if data["item_type"] == "expendable":
            item = KitExpendable.query.filter_by(id=data["item_id"], kit_id=kit_id).first()
            if not item:
                raise ValidationError("Expendable not found in this kit")

            if item.quantity < quantity:
                raise ValidationError(f"Insufficient quantity. Available: {item.quantity}")

            item.quantity -= quantity

            # Update status if out of stock
            if item.quantity <= 0:
                item.status = "out_of_stock"
            elif item.is_low_stock():
                item.status = "low_stock"

            # Check if reorder needed
            if item.is_low_stock() or item.quantity <= 0:
                # Create automatic reorder request
                existing_request = KitReorderRequest.query.filter_by(
                    kit_id=kit_id,
                    item_type="expendable",
                    item_id=item.id,
                    status="pending"
                ).first()

                if not existing_request:
                    reorder = KitReorderRequest(
                        kit_id=kit_id,
                        item_type="expendable",
                        item_id=item.id,
                        part_number=item.part_number,
                        description=item.description,
                        quantity_requested=item.minimum_stock_level if item.minimum_stock_level else 10,
                        priority="medium" if item.quantity > 0 else "high",
                        requested_by=request.current_user["user_id"],
                        status="pending",
                        is_automatic=True
                    )
                    db.session.add(reorder)

        else:  # tool or chemical from kit_items
            item = KitItem.query.filter_by(id=data["item_id"], kit_id=kit_id).first()
            if not item:
                raise ValidationError("Item not found in this kit")

            if item.quantity < quantity:
                raise ValidationError(f"Insufficient quantity. Available: {item.quantity}")

            item.quantity -= quantity
            # Round to avoid floating-point precision errors
            item.quantity = round(item.quantity, 2)

            if item.quantity <= 0:
                item.status = "issued"

        # Create issuance record with item details
        # issued_to is the current user (who is issuing the item to themselves)
        issuance = KitIssuance(
            kit_id=kit_id,
            item_type=data["item_type"],
            item_id=data["item_id"],
            issued_by=request.current_user["user_id"],
            issued_to=request.current_user["user_id"],  # Same as issued_by - user issuing to themselves
            part_number=item.part_number,
            serial_number=item.serial_number if hasattr(item, "serial_number") else None,
            lot_number=item.lot_number if hasattr(item, "lot_number") else None,
            description=item.description,
            quantity=quantity,
            purpose=data.get("purpose", ""),
            work_order=data.get("work_order", ""),
            notes=data.get("notes", "")
        )

        db.session.add(issuance)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_item_issued",
            action_details=f'Issued {quantity} {data["item_type"]} from kit {kit.name}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(issuance.to_dict()), 201

    @app.route("/api/kits/<int:kit_id>/issuances", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_issuances(kit_id):
        """Get issuance history for a kit"""
        from models_kits import KitIssuance

        Kit.query.get_or_404(kit_id)

        # Optional date filtering
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = KitIssuance.query.filter_by(kit_id=kit_id)

        if start_date:
            query = query.filter(KitIssuance.issued_date >= start_date)
        if end_date:
            query = query.filter(KitIssuance.issued_date <= end_date)

        issuances = query.order_by(KitIssuance.issued_date.desc()).all()

        return jsonify([issuance.to_dict() for issuance in issuances]), 200

    @app.route("/api/kits/<int:kit_id>/issuances/<int:issuance_id>", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_issuance(kit_id, issuance_id):
        """Get issuance details"""
        from models_kits import KitIssuance

        issuance = KitIssuance.query.filter_by(id=issuance_id, kit_id=kit_id).first_or_404()
        return jsonify(issuance.to_dict()), 200

    # ==================== Kit Analytics & Reporting ====================

    @app.route("/api/kits/<int:kit_id>/analytics", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_analytics(kit_id):
        """Get usage analytics for a kit"""
        from models_kits import KitIssuance, KitReorderRequest, KitTransfer

        kit = Kit.query.get_or_404(kit_id)

        # Get date range from query params
        days = request.args.get("days", 30, type=int)
        start_date = datetime.now() - timedelta(days=days)

        # Issuance statistics
        issuance_count = KitIssuance.query.filter(
            KitIssuance.kit_id == kit_id,
            KitIssuance.issued_date >= start_date
        ).count()

        # Transfer statistics
        transfers_in = KitTransfer.query.filter(
            KitTransfer.to_location_type == "kit",
            KitTransfer.to_location_id == kit_id,
            KitTransfer.transfer_date >= start_date
        ).count()

        transfers_out = KitTransfer.query.filter(
            KitTransfer.from_location_type == "kit",
            KitTransfer.from_location_id == kit_id,
            KitTransfer.transfer_date >= start_date
        ).count()

        # Reorder statistics
        pending_reorders = KitReorderRequest.query.filter_by(
            kit_id=kit_id,
            status="pending"
        ).count()

        fulfilled_reorders = KitReorderRequest.query.filter(
            KitReorderRequest.kit_id == kit_id,
            KitReorderRequest.status == "fulfilled",
            KitReorderRequest.fulfillment_date >= start_date
        ).count()

        # Item counts
        total_items = kit.items.count() + kit.expendables.count()
        low_stock_items = kit.expendables.filter(
            KitExpendable.quantity <= KitExpendable.minimum_stock_level
        ).count()

        analytics = {
            "kit_id": kit_id,
            "kit_name": kit.name,
            "period_days": days,
            "issuances": {
                "total": issuance_count,
                "average_per_day": round(issuance_count / days, 2) if days > 0 else 0
            },
            "transfers": {
                "incoming": transfers_in,
                "outgoing": transfers_out,
                "net": transfers_in - transfers_out
            },
            "reorders": {
                "pending": pending_reorders,
                "fulfilled": fulfilled_reorders
            },
            "inventory": {
                "total_items": total_items,
                "low_stock_items": low_stock_items,
                "stock_health": "good" if low_stock_items == 0 else "warning" if low_stock_items < 5 else "critical"
            }
        }

        return jsonify(analytics), 200

    @app.route("/api/kits/reports/inventory", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_inventory_report():
        """Get inventory report across all kits"""
        aircraft_type_id = request.args.get("aircraft_type_id", type=int)

        query = Kit.query.filter_by(status="active")
        if aircraft_type_id:
            query = query.filter_by(aircraft_type_id=aircraft_type_id)

        kits = query.all()

        report = []
        for kit in kits:
            total_items = kit.items.count() + kit.expendables.count()
            low_stock = kit.expendables.filter(
                KitExpendable.quantity <= KitExpendable.minimum_stock_level
            ).count()

            report.append({
                "kit_id": kit.id,
                "kit_name": kit.name,
                "aircraft_type": kit.aircraft_type.name if kit.aircraft_type else None,
                "total_items": total_items,
                "low_stock_items": low_stock,
                "boxes": kit.boxes.count()
            })

        return jsonify(report), 200

    @app.route("/api/kits/analytics/utilization", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_utilization_analytics():
        """Get kit utilization analytics across all kits"""
        from sqlalchemy import func

        from models_kits import KitIssuance, KitTransfer

        days = request.args.get("days", 30, type=int)
        start_date = datetime.now() - timedelta(days=days)

        # Get all active kits
        kits = Kit.query.filter_by(status="active").all()

        # Issuances by kit
        issuances_by_kit = db.session.query(
            Kit.name,
            func.count(KitIssuance.id).label("count")
        ).join(KitIssuance, Kit.id == KitIssuance.kit_id).filter(
            KitIssuance.issued_date >= start_date
        ).group_by(Kit.name).all()

        issuances_data = [{"name": name, "value": count} for name, count in issuances_by_kit]

        # Transfers by type
        kit_to_kit = KitTransfer.query.filter(
            KitTransfer.from_location_type == "kit",
            KitTransfer.to_location_type == "kit",
            KitTransfer.transfer_date >= start_date
        ).count()

        kit_to_warehouse = KitTransfer.query.filter(
            KitTransfer.from_location_type == "kit",
            KitTransfer.to_location_type == "warehouse",
            KitTransfer.transfer_date >= start_date
        ).count()

        warehouse_to_kit = KitTransfer.query.filter(
            KitTransfer.from_location_type == "warehouse",
            KitTransfer.to_location_type == "kit",
            KitTransfer.transfer_date >= start_date
        ).count()

        transfers_data = [
            {"name": "Kit to Kit", "value": kit_to_kit},
            {"name": "Kit to Warehouse", "value": kit_to_warehouse},
            {"name": "Warehouse to Kit", "value": warehouse_to_kit}
        ]

        # Activity over time (weekly breakdown)
        weeks = []
        for i in range(4):
            week_start = datetime.now() - timedelta(days=(4-i)*7)
            week_end = week_start + timedelta(days=7)

            week_issuances = KitIssuance.query.filter(
                KitIssuance.issued_date >= week_start,
                KitIssuance.issued_date < week_end
            ).count()

            week_transfers = KitTransfer.query.filter(
                KitTransfer.transfer_date >= week_start,
                KitTransfer.transfer_date < week_end
            ).count()

            weeks.append({
                "date": f"Week {i+1}",
                "issuances": week_issuances,
                "transfers": week_transfers
            })

        # Summary stats
        total_issuances = KitIssuance.query.filter(
            KitIssuance.issued_date >= start_date
        ).count()

        total_transfers = KitTransfer.query.filter(
            KitTransfer.transfer_date >= start_date
        ).count()

        active_kits = len(kits)

        # Calculate average utilization (percentage of kits with activity)
        kits_with_activity = db.session.query(KitIssuance.kit_id).filter(
            KitIssuance.issued_date >= start_date
        ).distinct().count()

        avg_utilization = round((kits_with_activity / active_kits * 100) if active_kits > 0 else 0, 1)

        return jsonify({
            "issuancesByKit": issuances_data,
            "transfersByType": transfers_data,
            "activityOverTime": weeks,
            "summary": {
                "totalIssuances": total_issuances,
                "totalTransfers": total_transfers,
                "activeKits": active_kits,
                "avgUtilization": avg_utilization
            }
        }), 200

    @app.route("/api/kits/<int:kit_id>/alerts", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_kit_alerts(kit_id):
        """Get alerts for a kit (expiring items, low stock, etc.)"""
        from models_kits import KitMessage, KitReorderRequest

        kit = Kit.query.get_or_404(kit_id)
        alerts = []

        # Low stock alerts
        low_stock_expendables = kit.expendables.filter(
            KitExpendable.quantity <= KitExpendable.minimum_stock_level
        ).all()

        for exp in low_stock_expendables:
            alerts.append({
                "type": "low_stock",
                "severity": "high" if exp.quantity == 0 else "medium",
                "item_type": "expendable",
                "item_id": exp.id,
                "part_number": exp.part_number,
                "description": exp.description,
                "current_quantity": exp.quantity,
                "minimum_quantity": exp.minimum_stock_level,
                "message": f"{exp.description} is low on stock ({exp.quantity} remaining)"
            })

        # Pending reorder alerts
        pending_reorders = KitReorderRequest.query.filter_by(
            kit_id=kit_id,
            status="pending"
        ).count()

        if pending_reorders > 0:
            alerts.append({
                "type": "pending_reorders",
                "severity": "medium",
                "count": pending_reorders,
                "message": f"{pending_reorders} pending reorder request(s)"
            })

        # Unread messages
        unread_messages = KitMessage.query.filter_by(
            kit_id=kit_id,
            is_read=False
        ).filter(
            db.or_(
                KitMessage.recipient_id == request.current_user["user_id"],
                KitMessage.recipient_id is None
            )
        ).count()

        if unread_messages > 0:
            alerts.append({
                "type": "unread_messages",
                "severity": "low",
                "count": unread_messages,
                "message": f"{unread_messages} unread message(s)"
            })

        # Check for tools/chemicals nearing expiration (if applicable)
        # This would require checking the linked Tool/Chemical records
        # For now, we'll skip this as it requires more complex logic

        return jsonify({
            "kit_id": kit_id,
            "kit_name": kit.name,
            "alert_count": len(alerts),
            "alerts": alerts
        }), 200

    # ==================== Recent Activity ====================

    @app.route("/api/kits/recent-activity", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_recent_kit_activity():
        """Get recent kit-related activities (issuances, transfers, reorders)"""
        limit = request.args.get("limit", 10, type=int)

        # Limit to reasonable range
        limit = min(max(limit, 1), 50)

        activities = []

        # Get recent issuances
        recent_issuances = KitIssuance.query.order_by(
            KitIssuance.issued_date.desc()
        ).limit(limit).all()

        for issuance in recent_issuances:
            activities.append({
                "id": f"issuance-{issuance.id}",
                "type": "issuance",
                "description": f"Issued {issuance.quantity} {issuance.item_type}(s)",
                "kit_name": issuance.kit.name if issuance.kit else "Unknown Kit",
                "kit_id": issuance.kit_id,
                "details": issuance.purpose or issuance.work_order or "",
                "user_name": issuance.issuer.name if issuance.issuer else "Unknown User",
                "timestamp": issuance.issued_date.isoformat() if issuance.issued_date else None,
                "created_at": issuance.issued_date.isoformat() if issuance.issued_date else None
            })

        # Get recent transfers
        recent_transfers = KitTransfer.query.order_by(
            KitTransfer.transfer_date.desc()
        ).limit(limit).all()

        for transfer in recent_transfers:
            # Build description based on transfer type
            from_loc = f"{transfer.from_location_type} {transfer.from_location_id}"
            to_loc = f"{transfer.to_location_type} {transfer.to_location_id}"

            # Try to get kit names if applicable
            kit_name = None
            if transfer.from_location_type == "kit":
                from_kit = Kit.query.get(transfer.from_location_id)
                if from_kit:
                    from_loc = f"Kit: {from_kit.name}"
                    kit_name = from_kit.name
            if transfer.to_location_type == "kit":
                to_kit = Kit.query.get(transfer.to_location_id)
                if to_kit:
                    to_loc = f"Kit: {to_kit.name}"
                    if not kit_name:
                        kit_name = to_kit.name

            activities.append({
                "id": f"transfer-{transfer.id}",
                "type": "transfer",
                "description": f"Transferred {transfer.quantity} {transfer.item_type}(s)",
                "kit_name": kit_name or "Warehouse",
                "kit_id": transfer.from_location_id if transfer.from_location_type == "kit" else transfer.to_location_id,
                "details": f"From {from_loc} to {to_loc}",
                "user_name": transfer.transferrer.name if transfer.transferrer else "Unknown User",
                "timestamp": transfer.transfer_date.isoformat() if transfer.transfer_date else None,
                "created_at": transfer.transfer_date.isoformat() if transfer.transfer_date else None,
                "status": transfer.status
            })

        # Get recent reorder requests
        recent_reorders = KitReorderRequest.query.order_by(
            KitReorderRequest.requested_date.desc()
        ).limit(limit).all()

        for reorder in recent_reorders:
            activities.append({
                "id": f"reorder-{reorder.id}",
                "type": "reorder",
                "description": f"Reorder request for {reorder.item_type}",
                "kit_name": reorder.kit.name if reorder.kit else "Unknown Kit",
                "kit_id": reorder.kit_id,
                "details": f"Quantity: {reorder.quantity_requested}",
                "user_name": reorder.requester.name if reorder.requester else "Unknown User",
                "timestamp": reorder.requested_date.isoformat() if reorder.requested_date else None,
                "created_at": reorder.requested_date.isoformat() if reorder.requested_date else None,
                "status": reorder.status
            })

        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Return only the requested limit
        return jsonify(activities[:limit]), 200
