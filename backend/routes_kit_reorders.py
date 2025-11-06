"""
Routes for Kit Reorder Request Management

This module provides API endpoints for managing reorder requests for kits.
"""

import logging
import os
from datetime import datetime

from flask import current_app, jsonify, request

from auth import department_required, jwt_required
from models import AuditLog, db
from models_kits import Kit, KitBox, KitExpendable, KitItem, KitReorderRequest
from utils.error_handler import ValidationError, handle_errors
from utils.file_validation import FileValidationError, validate_image_upload


logger = logging.getLogger(__name__)

materials_required = department_required("Materials")


def register_kit_reorder_routes(app):
    """Register all kit reorder routes"""

    @app.route("/api/kits/<int:kit_id>/reorder", methods=["POST"])
    @jwt_required
    @handle_errors
    def create_reorder_request(kit_id):
        """Create a reorder request for a kit (supports both JSON and multipart/form-data for image uploads)"""
        kit = Kit.query.get_or_404(kit_id)

        # Check if this is a multipart request (with image) or JSON
        if request.content_type and "multipart/form-data" in request.content_type:
            # Handle multipart form data (with image)
            data = request.form.to_dict()
            image_file = request.files.get("image")
        else:
            # Handle JSON data (no image)
            data = request.get_json() or {}
            image_file = None

        # Validate required fields
        if not data.get("part_number"):
            raise ValidationError("Part number is required")
        if not data.get("description"):
            raise ValidationError("Description is required")
        if not data.get("quantity_requested"):
            raise ValidationError("Quantity requested is required")

        # Handle image upload if provided
        image_path = None
        if image_file and image_file.filename:
            try:
                max_size = current_app.config.get("MAX_REORDER_IMAGE_SIZE", 5 * 1024 * 1024)  # 5MB default
                safe_filename = validate_image_upload(image_file, max_size=max_size)

                # Create reorder_images directory if it doesn't exist
                static_folder = current_app.static_folder or os.path.join(os.path.dirname(__file__), "static")
                upload_dir = os.path.join(static_folder, "reorder_images")
                os.makedirs(upload_dir, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_dir, safe_filename)
                image_file.save(file_path)

                # Store relative path
                image_path = f"/api/static/reorder_images/{safe_filename}"
                logger.info(f"Saved reorder request image: {image_path}")
            except FileValidationError as exc:
                raise ValidationError(f"Image upload failed: {exc!s}")

        # Create reorder request
        reorder = KitReorderRequest(
            kit_id=kit_id,
            item_type=data.get("item_type", "expendable"),
            item_id=data.get("item_id"),
            part_number=data["part_number"],
            description=data["description"],
            quantity_requested=float(data["quantity_requested"]),
            priority=data.get("priority", "medium"),
            requested_by=request.current_user["user_id"],
            status="pending",
            notes=data.get("notes", ""),
            is_automatic=False,
            image_path=image_path
        )

        db.session.add(reorder)
        db.session.commit()

        # Log action
        log_details = f"Reorder requested for kit {kit.name}: {reorder.part_number}"
        if image_path:
            log_details += " (with image)"
        log = AuditLog(
            action_type="kit_reorder_requested",
            action_details=log_details
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Reorder request created: ID {reorder.id}")
        return jsonify(reorder.to_dict()), 201

    @app.route("/api/reorder-requests", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_reorder_requests():
        """Get all reorder requests with optional filtering"""
        kit_id = request.args.get("kit_id", type=int)
        status = request.args.get("status")
        priority = request.args.get("priority")
        is_automatic = request.args.get("is_automatic")

        query = KitReorderRequest.query

        if kit_id:
            query = query.filter_by(kit_id=kit_id)
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if is_automatic is not None:
            query = query.filter_by(is_automatic=is_automatic.lower() == "true")

        reorders = query.order_by(
            KitReorderRequest.priority.desc(),
            KitReorderRequest.requested_date.desc()
        ).all()

        return jsonify([reorder.to_dict() for reorder in reorders]), 200

    @app.route("/api/reorder-requests/<int:id>", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_reorder_request(id):
        """Get reorder request details"""
        reorder = KitReorderRequest.query.get_or_404(id)
        return jsonify(reorder.to_dict()), 200

    @app.route("/api/reorder-requests/<int:id>/approve", methods=["PUT"])
    @materials_required
    @handle_errors
    def approve_reorder_request(id):
        """Approve a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)

        if reorder.status != "pending":
            raise ValidationError("Can only approve pending requests")

        reorder.status = "approved"
        reorder.approved_by = request.current_user["user_id"]
        reorder.approved_date = datetime.now()

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_reorder_approved",
            action_details=f"Reorder request approved: ID {reorder.id}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reorder.to_dict()), 200

    @app.route("/api/reorder-requests/<int:id>/order", methods=["PUT"])
    @materials_required
    @handle_errors
    def mark_reorder_ordered(id):
        """Mark a reorder request as ordered"""
        reorder = KitReorderRequest.query.get_or_404(id)

        if reorder.status not in ["pending", "approved"]:
            raise ValidationError("Can only mark pending or approved requests as ordered")

        reorder.status = "ordered"

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_reorder_ordered",
            action_details=f"Reorder request marked as ordered: ID {reorder.id}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reorder.to_dict()), 200

    @app.route("/api/reorder-requests/<int:id>/fulfill", methods=["PUT"])
    @materials_required
    @handle_errors
    def fulfill_reorder_request(id):
        """Mark a reorder request as fulfilled"""
        reorder = KitReorderRequest.query.get_or_404(id)

        logger.info(f"Fulfilling reorder request {id}: type={reorder.item_type}, item_id={reorder.item_id}, status={reorder.status}")

        if reorder.status != "ordered":
            raise ValidationError("Can only fulfill ordered requests")

        # Import models needed for fulfillment
        from models import Chemical, Tool, Warehouse, WarehouseTransfer

        # Get box_id from request body (optional - default to first box)
        data = request.get_json(silent=True) or {}
        logger.info(f"Request data: {data}")

        box = None
        box_id = data.get("box_id")
        logger.info(f"Box ID from request: {box_id}, type: {type(box_id)}")

        if box_id:
            box = KitBox.query.filter_by(id=box_id, kit_id=reorder.kit_id).first()
            if not box:
                raise ValidationError("Invalid box_id for this kit")
        else:
            box = KitBox.query.filter_by(kit_id=reorder.kit_id).order_by(KitBox.box_number).first()
            if not box:
                raise ValidationError("box_id is required to fulfill reorder")
            box_id = box.id

        reorder.status = "fulfilled"
        reorder.fulfillment_date = datetime.now()

        # Update or create item based on type
        if reorder.item_type == "expendable":
            # Check if this is updating an existing expendable or creating a new one
            if reorder.item_id:
                # Update existing expendable
                existing_expendable = db.session.get(KitExpendable, reorder.item_id)
                if not existing_expendable:
                    raise ValidationError("Referenced expendable not found")

                existing_expendable.quantity += reorder.quantity_requested
                existing_expendable.last_updated = datetime.now()
                # Update status to available when quantity is restored
                existing_expendable.status = "available"

                logger.info(f"Updated existing expendable {existing_expendable.id} with additional quantity {reorder.quantity_requested}")

                # Log action
                log = AuditLog(
                    action_type="expendable_quantity_updated_via_reorder",
                    action_details=f"Updated expendable {existing_expendable.part_number} quantity by {reorder.quantity_requested} via reorder request {reorder.id}"
                )
                db.session.add(log)
            else:
                # Create new expendable with auto-generated lot number
                from models import Expendable, LotNumberSequence

                # Auto-generate lot number
                lot_number = LotNumberSequence.generate_lot_number()

                logger.info(f"Creating new expendable {reorder.part_number} with lot number {lot_number}")

                # Create new Expendable (warehouse_id will be forced to None)
                expendable = Expendable(
                    part_number=reorder.part_number,
                    serial_number=None,
                    lot_number=lot_number,
                    description=reorder.description or f"Expendable {reorder.part_number}",
                    manufacturer=None,
                    quantity=reorder.quantity_requested,
                    unit="ea",
                    location=f"Box {box.box_number}",
                    category="General",
                    status="available",
                    minimum_stock_level=None,
                    notes=f"Created via reorder request {reorder.id}"
                )
                db.session.add(expendable)
                db.session.flush()  # Get expendable ID

                # Create KitItem to link expendable to kit
                kit_item = KitItem(
                    kit_id=reorder.kit_id,
                    box_id=box_id,
                    item_type="expendable",
                    item_id=expendable.id,
                    part_number=expendable.part_number,
                    serial_number=None,
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
                    action_type="expendable_added_via_reorder",
                    action_details=f"Added expendable {expendable.part_number} (lot={lot_number}) to kit {reorder.kit.name} via reorder request {reorder.id}"
                )
                db.session.add(log)

                logger.info(f"Created expendable {expendable.id} and kit item for reorder {reorder.id}")

        elif reorder.item_type in ["tool", "chemical"]:
            if reorder.item_id:
                # The item_id could be either a KitItem ID (for reordering existing kit items)
                # or a Tool/Chemical ID (for transferring from warehouse)
                # First, check if it's a KitItem
                existing_kit_item = db.session.get(KitItem, reorder.item_id)

                if existing_kit_item and existing_kit_item.item_type == reorder.item_type:
                    # This is an existing KitItem - find another instance in warehouse to transfer
                    logger.info(f"Reordering existing item {existing_kit_item.part_number} - searching for warehouse stock")

                    # Find a tool/chemical with the same part number that IS in a warehouse
                    if reorder.item_type == "tool":
                        warehouse_item = Tool.query.filter(
                            Tool.tool_number == existing_kit_item.part_number,
                            Tool.warehouse_id.isnot(None)
                        ).first()
                    else:
                        warehouse_item = Chemical.query.filter(
                            Chemical.part_number == existing_kit_item.part_number,
                            Chemical.warehouse_id.isnot(None)
                        ).first()

                    if not warehouse_item:
                        raise ValidationError(f"No {reorder.item_type} with part number {existing_kit_item.part_number} found in warehouse. Please add stock to warehouse first.")

                    logger.info(f"Found warehouse {reorder.item_type} ID {warehouse_item.id} with part number {existing_kit_item.part_number}")

                    # Create new kit item based on the warehouse item
                    kit_item = KitItem(
                        kit_id=reorder.kit_id,
                        box_id=box_id,
                        item_type=reorder.item_type,
                        item_id=warehouse_item.id,
                        part_number=existing_kit_item.part_number,
                        serial_number=warehouse_item.serial_number if reorder.item_type == "tool" else None,
                        lot_number=warehouse_item.lot_number,
                        description=existing_kit_item.description,
                        quantity=round(reorder.quantity_requested, 2),
                        location=f"Box {box.box_number}",
                        status="available"
                    )
                    db.session.add(kit_item)
                    db.session.flush()

                    # Create warehouse transfer record
                    transfer = WarehouseTransfer(
                        from_warehouse_id=warehouse_item.warehouse_id,
                        to_kit_id=reorder.kit_id,
                        item_type=reorder.item_type,
                        item_id=warehouse_item.id,
                        quantity=reorder.quantity_requested,
                        transferred_by_id=request.current_user["user_id"],
                        notes=f"Transferred to fulfill reorder request #{reorder.id}",
                        status="completed"
                    )
                    db.session.add(transfer)

                    # Remove from warehouse
                    warehouse_item.warehouse_id = None
                else:
                    # This is a direct Tool/Chemical ID - transfer from warehouse
                    if reorder.item_type == "tool":
                        warehouse_item = db.session.get(Tool, reorder.item_id)
                    else:
                        warehouse_item = db.session.get(Chemical, reorder.item_id)

                    if not warehouse_item:
                        raise ValidationError(f"{reorder.item_type.capitalize()} not found")

                    if not warehouse_item.warehouse_id:
                        raise ValidationError(f"{reorder.item_type.capitalize()} is not in a warehouse. Please add it to a warehouse first.")

                    # Create kit item
                    kit_item = KitItem(
                        kit_id=reorder.kit_id,
                        box_id=box_id,
                        item_type=reorder.item_type,
                        item_id=warehouse_item.id,
                        part_number=warehouse_item.tool_number if reorder.item_type == "tool" else warehouse_item.part_number,
                        serial_number=warehouse_item.serial_number if reorder.item_type == "tool" else None,
                        lot_number=warehouse_item.lot_number,
                        description=warehouse_item.description,
                        quantity=round(reorder.quantity_requested, 2),
                        location=f"Box {box.box_number}",
                        status="available"
                    )
                    db.session.add(kit_item)
                    db.session.flush()

                    # Create warehouse transfer record
                    transfer = WarehouseTransfer(
                        from_warehouse_id=warehouse_item.warehouse_id,
                        to_kit_id=reorder.kit_id,
                        item_type=reorder.item_type,
                        item_id=warehouse_item.id,
                        quantity=reorder.quantity_requested,
                        transferred_by_id=request.current_user["user_id"],
                        notes=f"Transferred to fulfill reorder request #{reorder.id}",
                        status="completed"
                    )
                    db.session.add(transfer)

                    # Remove from warehouse
                    warehouse_item.warehouse_id = None
            else:
                # For NEW items (item_id is None), auto-create in warehouse then transfer
                # This maintains compliance: tools/chemicals must originate in warehouses

                # Find default warehouse (prefer 'main' type, fallback to any active warehouse)
                default_warehouse = Warehouse.query.filter_by(
                    warehouse_type="main",
                    is_active=True
                ).first()

                if not default_warehouse:
                    # Fallback to any active warehouse
                    default_warehouse = Warehouse.query.filter_by(is_active=True).first()

                if not default_warehouse:
                    raise ValidationError(
                        "No active warehouse found. Please create a warehouse before fulfilling new item requests."
                    )

                logger.info(f"Auto-creating new {reorder.item_type} in warehouse {default_warehouse.name}")

                # Create the item in the warehouse
                if reorder.item_type == "tool":
                    # For tools, we need a serial number (required field)
                    # Generate one if not provided in the reorder request
                    serial_number = reorder.notes or f'SN-{reorder.part_number}-{datetime.now().strftime("%Y%m%d%H%M%S")}'

                    warehouse_item = Tool(
                        tool_number=reorder.part_number,
                        serial_number=serial_number,
                        description=reorder.description,
                        condition="new",
                        location=f"Warehouse {default_warehouse.name}",
                        category="General",
                        status="available",
                        warehouse_id=default_warehouse.id,
                        created_at=datetime.now()
                    )
                else:  # chemical
                    # For chemicals, we need a lot number (required field)
                    # Generate one if not provided
                    lot_number = reorder.notes or f'LOT-{reorder.part_number}-{datetime.now().strftime("%Y%m%d%H%M%S")}'

                    warehouse_item = Chemical(
                        part_number=reorder.part_number,
                        lot_number=lot_number,
                        description=reorder.description,
                        manufacturer="Unknown",
                        quantity=int(reorder.quantity_requested),
                        unit="ea",
                        location=f"Warehouse {default_warehouse.name}",
                        category="General",
                        status="available",
                        warehouse_id=default_warehouse.id,
                        date_added=datetime.now()
                    )

                db.session.add(warehouse_item)
                db.session.flush()  # Get the ID

                logger.info(f"Created {reorder.item_type} ID {warehouse_item.id} in warehouse {default_warehouse.name}")

                # Now transfer it to the kit
                kit_item = KitItem(
                    kit_id=reorder.kit_id,
                    box_id=box_id,
                    item_type=reorder.item_type,
                    item_id=warehouse_item.id,
                    part_number=warehouse_item.tool_number if reorder.item_type == "tool" else warehouse_item.part_number,
                    serial_number=warehouse_item.serial_number if reorder.item_type == "tool" else None,
                    lot_number=warehouse_item.lot_number,
                    description=warehouse_item.description,
                    quantity=round(reorder.quantity_requested, 2),
                    location=f"Box {box.box_number}",
                    status="available"
                )
                db.session.add(kit_item)
                db.session.flush()

                # Create warehouse transfer record for audit trail
                transfer = WarehouseTransfer(
                    from_warehouse_id=default_warehouse.id,
                    to_kit_id=reorder.kit_id,
                    item_type=reorder.item_type,
                    item_id=warehouse_item.id,
                    quantity=reorder.quantity_requested,
                    transferred_by_id=request.current_user["user_id"],
                    notes=f"Auto-created and transferred to fulfill reorder request #{reorder.id}",
                    status="completed"
                )
                db.session.add(transfer)

                # Remove from warehouse (it's now in the kit)
                warehouse_item.warehouse_id = None

                logger.info(f"Transferred {reorder.item_type} ID {warehouse_item.id} to kit {reorder.kit_id}")

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_reorder_fulfilled",
            action_details=f"Reorder request fulfilled: ID {reorder.id}, added to box {box.box_number}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reorder.to_dict()), 200

    @app.route("/api/reorder-requests/<int:id>/cancel", methods=["PUT"])
    @jwt_required
    @handle_errors
    def cancel_reorder_request(id):
        """Cancel a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)

        if reorder.status in ["fulfilled", "cancelled"]:
            raise ValidationError("Cannot cancel fulfilled or already cancelled requests")

        # Check if user has permission to cancel
        user_id = request.current_user["user_id"]
        is_admin = request.current_user.get("is_admin", False)
        is_materials = request.current_user.get("department") == "Materials"

        if not (is_admin or is_materials or reorder.requested_by == user_id):
            raise ValidationError("You do not have permission to cancel this request")

        reorder.status = "cancelled"

        db.session.commit()

        # Log action
        log = AuditLog(
            action_type="kit_reorder_cancelled",
            action_details=f"Reorder request cancelled: ID {reorder.id}"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reorder.to_dict()), 200

    @app.route("/api/reorder-requests/<int:id>", methods=["PUT"])
    @jwt_required
    @handle_errors
    def update_reorder_request(id):
        """Update a reorder request"""
        reorder = KitReorderRequest.query.get_or_404(id)
        data = request.get_json() or {}

        # Only allow updates to pending requests
        if reorder.status != "pending":
            raise ValidationError("Can only update pending requests")

        # Check if user has permission to update
        user_id = request.current_user["user_id"]
        is_admin = request.current_user.get("is_admin", False)
        is_materials = request.current_user.get("department") == "Materials"

        if not (is_admin or is_materials or reorder.requested_by == user_id):
            raise ValidationError("You do not have permission to update this request")

        # Update fields
        if "quantity_requested" in data:
            reorder.quantity_requested = float(data["quantity_requested"])
        if "priority" in data:
            reorder.priority = data["priority"]
        if "notes" in data:
            reorder.notes = data["notes"]

        db.session.commit()

        return jsonify(reorder.to_dict()), 200
