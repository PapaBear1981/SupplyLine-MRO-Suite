import logging
from datetime import datetime

from flask import current_app, jsonify, request
from sqlalchemy.orm import joinedload

from auth import department_required, jwt_required
from models import (
    AuditLog,
    Chemical,
    ChemicalIssuance,
    ChemicalReturn,
    ProcurementOrder,
    RequestItem,
    User,
    UserActivity,
    UserRequest,
    Warehouse,
    db,
)
from sqlalchemy import text
from utils.error_handler import ValidationError, handle_errors
from utils.validation import validate_lot_number_format, validate_schema, validate_warehouse_id


logger = logging.getLogger(__name__)

# Decorator to check if user is admin or in Materials department
materials_manager_required = department_required("Materials")


def _generate_request_number():
    """Generate a unique request number in format REQ-00001."""
    result = db.session.execute(
        text("SELECT MAX(CAST(SUBSTR(request_number, 5) AS INTEGER)) FROM user_requests WHERE request_number IS NOT NULL")
    ).scalar()
    next_number = (result or 0) + 1
    return f"REQ-{next_number:05d}"


def _generate_order_number():
    """Generate a unique order number in format ORD-00001."""
    result = db.session.execute(
        text("SELECT MAX(CAST(SUBSTR(order_number, 5) AS INTEGER)) FROM procurement_orders WHERE order_number IS NOT NULL")
    ).scalar()
    next_number = (result or 0) + 1
    return f"ORD-{next_number:05d}"


def _create_auto_reorder_request(chemical, user_id):
    """Create an automatic reorder request for a chemical that is low stock or out of stock."""
    # Check if there's already an open request for this chemical
    existing_request = (
        db.session.query(UserRequest)
        .join(RequestItem, UserRequest.id == RequestItem.request_id)
        .filter(
            RequestItem.item_type == "chemical",
            RequestItem.part_number == chemical.part_number,
            UserRequest.status.in_(UserRequest.OPEN_STATUSES)
        )
        .first()
    )

    if existing_request:
        logger.info(f"Auto-reorder request already exists for chemical {chemical.part_number}: Request #{existing_request.request_number}")
        return None

    # Determine priority based on status
    if chemical.status == "out_of_stock":
        priority = "critical"
        title = f"URGENT: Restock {chemical.part_number} - Out of Stock"
    else:  # low_stock
        priority = "high"
        title = f"Restock {chemical.part_number} - Low Stock"

    # Calculate quantity to order (bring back to minimum stock level + buffer)
    if chemical.minimum_stock_level:
        quantity_to_order = max(chemical.minimum_stock_level * 2, 1)
    else:
        quantity_to_order = 1

    # Create the request
    user_request = UserRequest(
        request_number=_generate_request_number(),
        title=title,
        description=f"Auto-generated reorder request for {chemical.part_number} ({chemical.lot_number}). "
                    f"Current quantity: {chemical.quantity} {chemical.unit}. "
                    f"Minimum stock level: {chemical.minimum_stock_level or 'Not set'}.",
        priority=priority,
        status="new",
        requester_id=user_id,
        notes=f"Automatically created after issuance depleted stock.",
        is_auto_generated=True
    )
    db.session.add(user_request)
    db.session.flush()  # Get the request ID

    # Create the request item
    request_item = RequestItem(
        request_id=user_request.id,
        item_type="chemical",
        part_number=chemical.part_number,
        description=chemical.description or f"{chemical.part_number} - {chemical.manufacturer or 'Unknown manufacturer'}",
        quantity=quantity_to_order,
        unit=chemical.unit,
        status="pending"
    )
    db.session.add(request_item)

    # Log the auto-creation
    log = AuditLog(
        action_type="auto_reorder_request_created",
        action_details=f"Auto-created reorder request {user_request.request_number} for chemical {chemical.part_number} (status: {chemical.status})"
    )
    db.session.add(log)

    logger.info(f"Auto-created reorder request {user_request.request_number} for chemical {chemical.part_number}")
    return user_request


def register_chemical_routes(app):
    # Get all chemicals with pagination
    @app.route("/api/chemicals", methods=["GET"])
    @handle_errors
    def chemicals_route():
        # PERFORMANCE: Add pagination to prevent unbounded dataset returns
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        # Get query parameters for filtering
        category = request.args.get("category")
        status = request.args.get("status")
        search = request.args.get("q")
        show_archived = request.args.get("archived", "false").lower() == "true"

        # Validate pagination parameters
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 500:
            return jsonify({"error": "Per page must be between 1 and 500"}), 400

        # Start with base query
        query = Chemical.query

        # Filter by archived status if the column exists
        try:
            if not show_archived:
                query = query.filter(Chemical.is_archived.is_(False))
        except AttributeError:
            # If the column doesn't exist, we can't filter by it
            logger.warning("is_archived column not found, skipping archived filter")

        # Apply filters if provided
        if category:
            query = query.filter(Chemical.category == category)
        if status:
            query = query.filter(Chemical.status == status)
        if search:
            query = query.filter(
                db.or_(
                    Chemical.part_number.ilike(f"%{search}%"),
                    Chemical.lot_number.ilike(f"%{search}%"),
                    Chemical.description.ilike(f"%{search}%"),
                    Chemical.manufacturer.ilike(f"%{search}%")
                )
            )

        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        chemicals = pagination.items

        # Batch update status based on expiration and stock level to avoid N+1 queries
        chemicals_to_update = []
        archive_logs = []

        for chemical in chemicals:
            try:
                is_archived = chemical.is_archived
            except AttributeError:
                # If the column doesn't exist, assume not archived
                logger.debug(f"is_archived attribute not found for chemical {chemical.id}")
                is_archived = False

            if not is_archived:  # Only update status for non-archived chemicals
                status_changed = False

                if chemical.is_expired():
                    chemical.status = "expired"
                    status_changed = True

                    # Auto-archive expired chemicals if the columns exist
                    try:
                        chemical.is_archived = True
                        chemical.archived_reason = "expired"
                        chemical.archived_date = datetime.utcnow()

                        # Prepare log for archiving (batch insert later)
                        archive_logs.append({
                            "action_type": "chemical_archived",
                            "action_details": f"Chemical {chemical.part_number} - {chemical.lot_number} automatically archived: expired",
                            "timestamp": datetime.utcnow()
                        })

                        # Update reorder status for expired chemicals
                        chemical.update_reorder_status()
                    except AttributeError as e:
                        # If the columns don't exist, just update the status
                        logger.debug(f"Archive columns not found for chemical {chemical.id}: {e!s}")
                elif chemical.quantity <= 0:
                    chemical.status = "out_of_stock"
                    status_changed = True
                    # Update reorder status for out-of-stock chemicals
                    chemical.update_reorder_status()
                elif chemical.is_low_stock():
                    chemical.status = "low_stock"
                    status_changed = True
                    # Update reorder status for low-stock chemicals
                    chemical.update_reorder_status()

                # Check if chemical is expiring soon (within 30 days)
                if chemical.is_expiring_soon(30):
                    # Add a flag to the chemical data
                    chemical.expiring_soon = True

                if status_changed:
                    chemicals_to_update.append(chemical)

        # Batch insert archive logs if any
        if archive_logs:
            db.session.bulk_insert_mappings(AuditLog, archive_logs)

        # Single commit for all changes
        if chemicals_to_update or archive_logs:
            db.session.commit()

        # Get kit and box information for chemicals
        from models_kits import KitItem
        chemical_kit_info = {}
        kit_items = KitItem.query.filter(
            KitItem.item_type == "chemical",
            KitItem.item_id.in_([c.id for c in chemicals])
        ).all()

        for kit_item in kit_items:
            chemical_kit_info[kit_item.item_id] = {
                "kit_id": kit_item.kit_id,
                "kit_name": kit_item.kit.name if kit_item.kit else None,
                "box_id": kit_item.box_id,
                "box_number": kit_item.box.box_number if kit_item.box else None
            }

        # Serialize after all mutations to ensure client gets updated data
        chemicals_data = [
            {
                **c.to_dict(),
                **({"expiring_soon": True} if getattr(c, "expiring_soon", False) else {}),
                "kit_id": chemical_kit_info.get(c.id, {}).get("kit_id"),
                "kit_name": chemical_kit_info.get(c.id, {}).get("kit_name"),
                "box_id": chemical_kit_info.get(c.id, {}).get("box_id"),
                "box_number": chemical_kit_info.get(c.id, {}).get("box_number")
            }
            for c in chemicals
        ]

        # Return paginated response
        response = {
            "chemicals": chemicals_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }

        return jsonify(response)

    # Create a new chemical
    @app.route("/api/chemicals", methods=["POST"])
    @materials_manager_required
    @handle_errors
    def create_chemical_route():
        data = request.get_json() or {}

        # Validate warehouse_id is required
        if not data.get("warehouse_id"):
            raise ValidationError("warehouse_id is required for all chemicals")

        # Validate warehouse exists and is active using validation function
        warehouse = validate_warehouse_id(data["warehouse_id"])

        # Validate and sanitize input using schema
        validated_data = validate_schema(data, "chemical")

        # Validate lot number format
        validate_lot_number_format(validated_data["lot_number"])

        logger.info(f"Creating chemical with part number: {validated_data.get('part_number')} in warehouse {warehouse.name}")

        # Check if chemical with same part number and lot number already exists
        existing_chemical = Chemical.query.filter_by(
            part_number=validated_data["part_number"],
            lot_number=validated_data["lot_number"]
        ).first()

        if existing_chemical:
            raise ValidationError("Chemical with this part number and lot number already exists")

        # Create new chemical - warehouse_id is required
        chemical = Chemical(
            part_number=validated_data["part_number"],
            lot_number=validated_data["lot_number"],
            description=validated_data.get("description", ""),
            manufacturer=validated_data.get("manufacturer", ""),
            quantity=validated_data["quantity"],
            unit=validated_data["unit"],
            location=validated_data.get("location", ""),
            category=validated_data.get("category", "General"),
            status=validated_data.get("status", "available"),
            warehouse_id=data["warehouse_id"],  # Required field
            expiration_date=validated_data.get("expiration_date"),
            minimum_stock_level=validated_data.get("minimum_stock_level"),
            notes=validated_data.get("notes", "")
        )

        db.session.add(chemical)
        db.session.flush()  # Flush to get the chemical ID

        # Record transaction
        from utils.transaction_helper import record_item_receipt
        try:
            record_item_receipt(
                item_type="chemical",
                item_id=chemical.id,
                user_id=request.current_user["user_id"],
                quantity=validated_data["quantity"],
                location=validated_data.get("location", "Unknown"),
                notes="Initial chemical creation"
            )
        except Exception as e:
            logger.error(f"Error recording chemical creation transaction: {e!s}")

        # Log the action
        log = AuditLog(
            action_type="chemical_added",
            action_details=f"Chemical {validated_data['part_number']} - {validated_data['lot_number']} added"
        )
        db.session.add(log)

        # Log user activity
        if hasattr(request, "current_user"):
            activity = UserActivity(
                user_id=request.current_user["user_id"],
                activity_type="chemical_added",
                description=f"Added chemical {validated_data['part_number']} - {validated_data['lot_number']}"
            )
            db.session.add(activity)

        db.session.commit()

        logger.info(f"Chemical created successfully: {chemical.part_number} - {chemical.lot_number}")
        return jsonify(chemical.to_dict()), 201

    # Get barcode data for a chemical
    @app.route("/api/chemicals/<int:id>/barcode", methods=["GET"])
    def chemical_barcode_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Format expiration date for barcode (YYYYMMDD)
            expiration_date = "NOEXP"
            if chemical.expiration_date:
                expiration_date = chemical.expiration_date.strftime("%Y%m%d")

            # Create barcode data
            barcode_data = f"{chemical.part_number}-{chemical.lot_number}-{expiration_date}"

            # Get the base URL for QR code
            # Use PUBLIC_URL from config if set (for external access), otherwise use request host
            base_url = current_app.config.get("PUBLIC_URL")
            base_url = request.host_url.rstrip("/") if not base_url else base_url.rstrip("/")

            # Create QR code URL that points to the chemical view page
            qr_url = f"{base_url}/chemical-view/{chemical.id}"

            return jsonify({
                "chemical_id": chemical.id,
                "part_number": chemical.part_number,
                "lot_number": chemical.lot_number,
                "description": chemical.description,
                "manufacturer": chemical.manufacturer,
                "location": chemical.location,
                "status": chemical.status,
                "expiration_date": chemical.expiration_date.isoformat() if chemical.expiration_date else None,
                "created_at": chemical.created_at.isoformat() if chemical.created_at else None,
                "barcode_data": barcode_data,
                "qr_url": qr_url
            })
        except Exception as e:
            print(f"Error in chemical barcode route: {e!s}")
            return jsonify({"error": "An error occurred while generating barcode data"}), 500

    # Issue a chemical
    @app.route("/api/chemicals/<int:id>/issue", methods=["POST"])
    @jwt_required
    @handle_errors
    def chemical_issue_route(id):
        from utils.lot_utils import create_child_chemical

        # Get the chemical
        chemical = Chemical.query.get_or_404(id)

        # Check if chemical can be issued
        if chemical.status == "expired":
            raise ValidationError("Cannot issue an expired chemical")

        if chemical.quantity <= 0:
            raise ValidationError("Cannot issue a chemical that is out of stock")

        # Get and validate request data
        data = request.get_json() or {}

        # Use centralized schema validation
        validated_data = validate_schema(data, "chemical_issuance")

        # Ensure the user exists
        if not db.session.get(User, validated_data["user_id"]):
            raise ValidationError("Supplied user_id does not exist")

        quantity = float(validated_data["quantity"])
        if quantity > chemical.quantity:
            raise ValidationError(f"Cannot issue more than available quantity ({chemical.quantity} {chemical.unit})")

        # Check if this is a partial issue (doesn't consume entire lot)
        is_partial_issue = quantity < chemical.quantity
        child_chemical = None

        if is_partial_issue:
            # Create a child lot for the issued quantity
            child_chemical = create_child_chemical(
                parent_chemical=chemical,
                quantity=quantity,
                destination_warehouse_id=chemical.warehouse_id
            )
            db.session.add(child_chemical)
            db.session.flush()  # Flush to get the child chemical ID

            # Create issuance record for the child lot
            issuance = ChemicalIssuance(
                chemical_id=child_chemical.id,
                user_id=validated_data["user_id"],
                quantity=quantity,
                hangar=validated_data["hangar"],
                purpose=validated_data.get("purpose", "")
            )

            # Update child chemical after issuance - it's been fully consumed
            child_chemical.quantity = 0
            child_chemical.status = "issued"

            # Update parent status and reorder flags
            if chemical.quantity == 0:
                chemical.status = "depleted"
            elif chemical.is_low_stock():
                chemical.status = "low_stock"

            # Track if reorder was triggered
            reorder_was_needed = chemical.needs_reorder
            # Update reorder status for parent
            chemical.update_reorder_status()

            # Create unified request if reorder was just triggered
            auto_request = None
            if chemical.needs_reorder and not reorder_was_needed:
                from utils.unified_requests import create_chemical_reorder_request
                auto_request = create_chemical_reorder_request(
                    chemical=chemical,
                    requested_quantity=chemical.minimum_stock_level or 1,
                    requester_id=request.current_user["user_id"],
                    notes="Automatic reorder triggered by low stock after issuance"
                )
                # Set requested_quantity on the chemical
                chemical.requested_quantity = chemical.minimum_stock_level or 1

            # Log the action for child lot creation
            log_child = AuditLog(
                action_type="child_lot_created",
                action_details=f"Child lot {child_chemical.lot_number} created from {chemical.lot_number}: {quantity} {chemical.unit}"
            )
            db.session.add(log_child)
        else:
            # Full consumption - issue from original chemical
            issuance = ChemicalIssuance(
                chemical_id=chemical.id,
                user_id=validated_data["user_id"],
                quantity=quantity,
                hangar=validated_data["hangar"],
                purpose=validated_data.get("purpose", "")
            )

            # Update chemical quantity
            chemical.quantity -= quantity

            # Track if reorder was triggered
            reorder_was_needed = chemical.needs_reorder
            auto_request = None

            # Update chemical status based on new quantity
            if chemical.quantity <= 0:
                chemical.status = "out_of_stock"
                # Update reorder status
                chemical.update_reorder_status()
            elif chemical.is_low_stock():
                chemical.status = "low_stock"
                # Update reorder status
                chemical.update_reorder_status()

            # Create unified request if reorder was just triggered
            if chemical.needs_reorder and not reorder_was_needed:
                from utils.unified_requests import create_chemical_reorder_request
                auto_request = create_chemical_reorder_request(
                    chemical=chemical,
                    requested_quantity=chemical.minimum_stock_level or 1,
                    requester_id=request.current_user["user_id"],
                    notes="Automatic reorder triggered by low stock after issuance"
                )
                # Set requested_quantity on the chemical
                chemical.requested_quantity = chemical.minimum_stock_level or 1

        db.session.add(issuance)

        # Record transaction (use authenticated user as actor, not recipient)
        from utils.transaction_helper import record_chemical_issuance
        try:
            record_chemical_issuance(
                chemical_id=child_chemical.id if child_chemical else chemical.id,
                user_id=request.current_user.get("user_id"),  # Authenticated user performing the issuance
                quantity=quantity,
                hangar=validated_data["hangar"],
                purpose=validated_data.get("purpose"),
                work_order=validated_data.get("work_order"),
                recipient_id=validated_data["user_id"]  # Actual recipient of the chemical
            )
        except Exception as e:
            logger.exception(f"Error recording chemical issuance transaction: {e}")

        # Log the action
        log = AuditLog(
            action_type="chemical_issued",
            action_details=f"Chemical {chemical.part_number} - {child_chemical.lot_number if child_chemical else chemical.lot_number} issued: {quantity} {chemical.unit}"
        )
        db.session.add(log)

        # Log user activity
        if hasattr(request, "current_user"):
            activity = UserActivity(
                user_id=request.current_user["user_id"],
                activity_type="chemical_issued",
                description=f"Issued {quantity} {chemical.unit} of chemical {chemical.part_number} - {child_chemical.lot_number if child_chemical else chemical.lot_number}"
            )
            db.session.add(activity)

        # Auto-create reorder request if chemical is now low stock or out of stock
        auto_request = None
        if chemical.status in ("low_stock", "out_of_stock"):
            try:
                auto_request = _create_auto_reorder_request(chemical, request.current_user["user_id"])
            except Exception as e:
                logger.exception(f"Error creating auto-reorder request: {e}")
                # Don't fail the issuance if request creation fails

        db.session.commit()

        logger.info(f"Chemical issued successfully: {chemical.part_number} - {child_chemical.lot_number if child_chemical else chemical.lot_number}, quantity: {quantity}")

        # Return updated chemical and issuance record, including child lot if created
        response_data = {
            "chemical": chemical.to_dict(),
            "issuance": issuance.to_dict()
        }

        if child_chemical:
            response_data["child_chemical"] = child_chemical.to_dict()

        # Include auto-created request info if reorder was triggered
        if auto_request:
            response_data["auto_reorder_request"] = auto_request.to_dict()
            response_data["message"] = f"Low stock detected. Automatic reorder request #{auto_request.request_number} has been created."
            logger.info(f"Auto-created reorder request {auto_request.request_number} for chemical {chemical.part_number}")

        return jsonify(response_data)

    def _parse_chemical_barcode(code):
        """Parse a chemical barcode into part and lot numbers.

        Expected format: {part_number}-{lot_number}
        Example: AMS-1424-LOT-251102-0001-A
        - part_number: AMS-1424
        - lot_number: LOT-251102-0001-A
        """
        if not code or not isinstance(code, str):
            raise ValidationError("Barcode value is required")

        # Find the first occurrence of "LOT" to split part number and lot number
        # This handles cases where part numbers may contain hyphens (e.g., AMS-1424)
        lot_index = code.find("-LOT")

        if lot_index == -1:
            # Fallback: try simple split if no "-LOT" pattern found
            parts = code.split("-", 1)
            if len(parts) < 2:
                raise ValidationError("Unable to parse barcode. Please scan a chemical label")
            part_number = parts[0]
            lot_number = parts[1]
        else:
            # Split at the "-LOT" boundary
            part_number = code[:lot_index]
            lot_number = code[lot_index + 1:]  # Skip the leading hyphen

        if not part_number or not lot_number:
            raise ValidationError("Invalid barcode data")

        return part_number, lot_number

    # Lookup issued chemical information for returns
    @app.route("/api/chemicals/returns/lookup", methods=["POST"])
    @jwt_required
    @handle_errors
    def chemical_return_lookup():
        data = request.get_json() or {}

        chemical_id = data.get("chemical_id")
        code = data.get("code")

        if not chemical_id and not code:
            raise ValidationError("Chemical ID or barcode is required")

        if chemical_id:
            chemical = Chemical.query.get_or_404(chemical_id)
        else:
            part_number, lot_number = _parse_chemical_barcode(code)
            chemical = Chemical.query.filter_by(
                part_number=part_number,
                lot_number=lot_number,
            ).first()
            if not chemical:
                raise ValidationError("No chemical found for the provided barcode")

        issuance = (
            ChemicalIssuance.query.filter_by(chemical_id=chemical.id)
            .order_by(ChemicalIssuance.issue_date.desc())
            .first()
        )

        if not issuance:
            raise ValidationError("This lot does not have any issuance history")

        returns = (
            ChemicalReturn.query.filter_by(issuance_id=issuance.id)
            .order_by(ChemicalReturn.return_date.desc())
            .all()
        )

        total_returned = sum(ret.quantity for ret in returns)
        remaining_quantity = max(issuance.quantity - total_returned, 0)

        response = {
            "chemical": chemical.to_dict(),
            "issuance": issuance.to_dict(),
            "returns": [ret.to_dict() for ret in returns],
            "remaining_quantity": remaining_quantity,
            "default_warehouse_id": chemical.warehouse_id,
            "default_location": chemical.location,
        }

        return jsonify(response)

    # Process a chemical return
    @app.route("/api/chemicals/<int:id>/return", methods=["POST"])
    @jwt_required
    @handle_errors
    def chemical_return_route(id):
        chemical = Chemical.query.get_or_404(id)
        data = request.get_json() or {}

        issuance_id = data.get("issuance_id")
        if not issuance_id:
            raise ValidationError("Issuance ID is required")

        issuance = db.session.get(ChemicalIssuance, issuance_id)
        if not issuance or issuance.chemical_id != chemical.id:
            raise ValidationError("Issuance does not match the selected chemical")

        quantity = data.get("quantity")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValidationError("Quantity must be a whole number")

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")

        total_returned = sum(ret.quantity for ret in issuance.returns)
        remaining_quantity = issuance.quantity - total_returned

        if quantity > remaining_quantity:
            raise ValidationError(
                f"Cannot return more than the outstanding issued quantity ({remaining_quantity})"
            )

        warehouse_id = data.get("warehouse_id", chemical.warehouse_id)
        warehouse = None
        if warehouse_id:
            warehouse = db.session.get(Warehouse, warehouse_id)
            if not warehouse:
                raise ValidationError("Selected warehouse does not exist")
            if not warehouse.is_active:
                raise ValidationError("Selected warehouse is inactive")

        location = data.get("location") or chemical.location
        notes = data.get("notes")

        chemical.quantity = (chemical.quantity or 0) + quantity
        chemical.location = location
        chemical.warehouse_id = warehouse_id

        if chemical.quantity > 0:
            chemical.status = "available"
        if chemical.minimum_stock_level and chemical.quantity <= chemical.minimum_stock_level:
            chemical.status = "low_stock"

        try:
            if hasattr(chemical, "needs_reorder") and chemical.quantity is not None:
                if chemical.quantity > 0 and (
                    not chemical.minimum_stock_level or chemical.quantity > chemical.minimum_stock_level
                ):
                    chemical.needs_reorder = False
                    if hasattr(chemical, "reorder_status"):
                        chemical.reorder_status = "not_needed"
        except Exception:
            logger.exception("Failed to reset reorder state after return")

        try:
            chemical.update_reorder_status()
        except Exception:
            logger.exception("Failed to update reorder status after return")

        chemical_return = ChemicalReturn(
            chemical_id=chemical.id,
            issuance_id=issuance.id,
            returned_by_id=request.current_user.get("user_id"),
            quantity=quantity,
            warehouse_id=warehouse_id,
            location=location,
            notes=notes,
        )

        db.session.add(chemical_return)

        from utils.transaction_helper import record_chemical_return

        try:
            record_chemical_return(
                chemical_id=chemical.id,
                user_id=request.current_user.get("user_id"),
                quantity=quantity,
                location_from=issuance.hangar,
                location_to=location or (warehouse.name if warehouse else None),
                notes=notes,
            )
        except Exception as exc:
            logger.exception("Error recording chemical return transaction: %s", exc)

        log = AuditLog(
            action_type="chemical_returned",
            action_details=(
                f"Chemical {chemical.part_number} - {chemical.lot_number} returned: {quantity} {chemical.unit}"
            ),
        )
        db.session.add(log)

        if hasattr(request, "current_user"):
            activity = UserActivity(
                user_id=request.current_user.get("user_id"),
                activity_type="chemical_returned",
                description=(
                    f"Returned {quantity} {chemical.unit} of chemical {chemical.part_number} - {chemical.lot_number}"
                ),
            )
            db.session.add(activity)

        db.session.commit()

        returns = (
            ChemicalReturn.query.filter_by(issuance_id=issuance.id)
            .order_by(ChemicalReturn.return_date.desc())
            .all()
        )

        total_returned = sum(ret.quantity for ret in returns)
        remaining_quantity = max(issuance.quantity - total_returned, 0)

        response = {
            "chemical": chemical.to_dict(),
            "return": chemical_return.to_dict(),
            "issuance": issuance.to_dict(),
            "returns": [ret.to_dict() for ret in returns],
            "remaining_quantity": remaining_quantity,
        }

        return jsonify(response), 201

    # Get return history for a chemical
    @app.route("/api/chemicals/<int:id>/returns", methods=["GET"])
    @jwt_required
    @handle_errors
    def chemical_returns_route(id):
        Chemical.query.get_or_404(id)

        returns = (
            ChemicalReturn.query.filter_by(chemical_id=id)
            .order_by(ChemicalReturn.return_date.desc())
            .all()
        )

        return jsonify([ret.to_dict() for ret in returns])

    # Get issuance history for a chemical
    @app.route("/api/chemicals/<int:id>/issuances", methods=["GET"])
    @handle_errors
    def chemical_issuances_route(id):
        # Get the chemical and eagerly load any issuances created from child lots
        chemical = Chemical.query.get_or_404(id)

        related_ids = {chemical.id}
        lots_to_process = []

        if chemical.lot_number:
            lots_to_process.append((chemical.lot_number, chemical.part_number))

        while lots_to_process:
            current_lot, part_number = lots_to_process.pop()
            # Filter by both parent_lot_number AND part_number to avoid lot number collisions
            # between different chemicals that happen to use the same lot number
            children = Chemical.query.filter_by(
                parent_lot_number=current_lot,
                part_number=part_number
            ).all()

            for child in children:
                if child.id not in related_ids:
                    related_ids.add(child.id)
                    if child.lot_number:
                        lots_to_process.append((child.lot_number, child.part_number))

        # Get issuance records with eager loading to avoid N+1 queries
        # Include the issuance relationship for issued child lots to populate issued_quantity
        issuances = ChemicalIssuance.query.options(
            joinedload(ChemicalIssuance.user),
            joinedload(ChemicalIssuance.chemical).joinedload(Chemical.issuance)
        ).filter(ChemicalIssuance.chemical_id.in_(list(related_ids))).order_by(ChemicalIssuance.issue_date.desc()).all()

        # Convert to list of dictionaries
        result = [i.to_dict() for i in issuances]

        # Return the result
        return jsonify(result)

    # Request reorder for a chemical
    @app.route("/api/chemicals/<int:id>/request-reorder", methods=["POST"])
    @materials_manager_required
    def request_chemical_reorder_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Get request data
            data = request.get_json() or {}

            # Validate requested quantity
            requested_quantity = data.get("requested_quantity")
            if requested_quantity is None:
                return jsonify({"error": "Requested quantity is required"}), 400

            try:
                requested_quantity = int(requested_quantity)
                if requested_quantity <= 0:
                    return jsonify({"error": "Requested quantity must be greater than 0"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Requested quantity must be a valid number"}), 400

            # Set the chemical as needing reorder
            chemical.needs_reorder = True
            chemical.reorder_status = "needed"
            chemical.reorder_date = datetime.utcnow()
            chemical.requested_quantity = requested_quantity

            # Add notes if provided
            notes = data.get("notes", "")
            if notes:
                # Append reorder request notes to existing notes
                reorder_note = f"\n[Reorder Request {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} - Qty: {requested_quantity}]: {notes}"
                chemical.notes = (chemical.notes or "") + reorder_note

            # Create unified request for the chemical reorder
            from utils.unified_requests import create_chemical_reorder_request
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=requested_quantity,
                requester_id=request.current_user["user_id"],
                notes=notes
            )

            # Log the action
            user_name = request.current_user.get("user_name", "Unknown user")
            log = AuditLog(
                action_type="chemical_reorder_requested",
                action_details=f"Reorder requested for chemical {chemical.part_number} - {chemical.lot_number} by {user_name} (Qty: {requested_quantity}). Request #{user_request.request_number} created."
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_reorder_requested",
                    description=f"Requested reorder for chemical {chemical.part_number} - {chemical.lot_number} (Qty: {requested_quantity}). Request #{user_request.request_number}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical and request info
            return jsonify({
                "chemical": chemical.to_dict(),
                "request": user_request.to_dict(),
                "message": f"Reorder request created successfully. Request #{user_request.request_number} has been added to the Requests system."
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in request chemical reorder route: {e!s}")
            return jsonify({"error": "An error occurred while requesting reorder"}), 500

    # Mark a chemical as ordered
    @app.route("/api/chemicals/<int:id>/mark-ordered", methods=["POST"])
    @materials_manager_required
    def mark_chemical_as_ordered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Only allow ordering when a reorder is needed
            if chemical.reorder_status != "needed":
                return jsonify({
                    "error": f'Cannot mark chemical as ordered when reorder_status is "{chemical.reorder_status}"'
                }), 400

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            if not data.get("expected_delivery_date"):
                return jsonify({"error": "Missing required field: expected_delivery_date"}), 400

            # Validate order quantity
            order_quantity = data.get("order_quantity")
            if order_quantity is None:
                return jsonify({"error": "Missing required field: order_quantity"}), 400

            try:
                order_quantity = int(order_quantity)
                if order_quantity <= 0:
                    return jsonify({"error": "Order quantity must be greater than 0"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Order quantity must be a valid number"}), 400

            # Parse the expected delivery date
            try:
                expected_delivery_date = datetime.fromisoformat(data.get("expected_delivery_date"))
                # Note: We're allowing past dates for testing purposes
                # This would normally validate that the date is in the future
            except ValueError:
                return jsonify({"error": "Invalid date format for expected_delivery_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

            # Create a procurement order for this chemical
            # Generate order title
            order_title = f"Chemical Reorder: {chemical.part_number} - {chemical.description or chemical.lot_number}"

            # Build description with quantity information
            description_parts = [
                chemical.description or "",
                f"Lot Number: {chemical.lot_number}",
                f"Manufacturer: {chemical.manufacturer or 'N/A'}",
                f"Order Quantity: {order_quantity} {chemical.unit}"
            ]
            if chemical.requested_quantity and chemical.requested_quantity != order_quantity:
                description_parts.append(f"Originally Requested: {chemical.requested_quantity} {chemical.unit}")

            # Create the procurement order
            procurement_order = ProcurementOrder(
                title=order_title,
                order_type="chemical",
                part_number=chemical.part_number,
                description="\n".join(description_parts),
                priority="normal",
                status="ordered",
                requester_id=request.current_user.get("user_id"),
                buyer_id=request.current_user.get("user_id"),
                ordered_date=datetime.utcnow(),
                expected_due_date=expected_delivery_date,
                notes=data.get("notes", ""),
                quantity=order_quantity,
                unit=chemical.unit
            )
            db.session.add(procurement_order)
            db.session.flush()  # Get the procurement_order.id

            # Generate and assign order number
            procurement_order.order_number = _generate_order_number()

            # Update chemical reorder status and link to procurement order
            try:
                chemical.reorder_status = "ordered"
                chemical.reorder_date = datetime.utcnow()
                chemical.expected_delivery_date = expected_delivery_date
                chemical.procurement_order_id = procurement_order.id
            except Exception as e:
                print(f"Error updating reorder status: {e!s}")
                return jsonify({"error": "Failed to update reorder status"}), 500

            # Update the unified request system if a request item exists for this chemical
            from utils.unified_requests import update_request_item_status
            update_request_item_status(
                source_type="chemical_reorder",
                source_id=chemical.id,
                new_status="ordered",
                ordered_date=datetime.utcnow(),
                expected_delivery_date=expected_delivery_date,
                order_notes=f"Procurement Order #{procurement_order.id}"
            )

            # Log the action
            user_name = request.current_user.get("user_name", "Unknown user")
            log = AuditLog(
                action_type="chemical_ordered",
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as ordered by {user_name}. Procurement order #{procurement_order.id} created for {order_quantity} {chemical.unit}."
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_ordered",
                    description=f"Marked chemical {chemical.part_number} - {chemical.lot_number} as ordered (Order #{procurement_order.id}, Qty: {order_quantity} {chemical.unit})"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical and procurement order
            return jsonify({
                "chemical": chemical.to_dict(),
                "procurement_order": procurement_order.to_dict(),
                "message": "Chemical marked as ordered successfully and procurement order created"
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in mark chemical as ordered route: {e!s}")
            return jsonify({"error": "An error occurred while marking the chemical as ordered"}), 500

    # Get, update, or delete a specific chemical
    @app.route("/api/chemicals/<int:id>", methods=["GET", "PUT", "DELETE"])
    @handle_errors
    def chemical_detail_route(id):
        # Get the chemical
        chemical = Chemical.query.get_or_404(id)

        if request.method == "GET":
            # Update status based on expiration and stock level
            try:
                is_archived = chemical.is_archived
            except Exception:
                is_archived = False

            if not is_archived:  # Only update non-archived chemicals
                if chemical.is_expired():
                    chemical.status = "expired"

                    # Auto-archive expired chemicals if the columns exist
                    try:
                        chemical.is_archived = True
                        chemical.archived_reason = "expired"
                        chemical.archived_date = datetime.utcnow()

                        # Add log for archiving
                        archive_log = AuditLog(
                            action_type="chemical_archived",
                            action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} automatically archived: expired"
                        )
                        db.session.add(archive_log)

                        # Update reorder status for expired chemicals
                        chemical.update_reorder_status()
                    except Exception:
                        # If the columns don't exist, just update the status
                        pass
                elif chemical.quantity <= 0:
                    chemical.status = "out_of_stock"
                    # Update reorder status for out-of-stock chemicals
                    chemical.update_reorder_status()
                elif chemical.is_low_stock():
                    chemical.status = "low_stock"
                    # Update reorder status for low-stock chemicals
                    chemical.update_reorder_status()

                # Check if chemical is expiring soon (within 30 days)
                if chemical.is_expiring_soon(30):
                    # Add a flag to the chemical data
                    chemical.expiring_soon = True

                db.session.commit()

            return jsonify(chemical.to_dict())

        if request.method == "PUT":
            # Update chemical
            data = request.get_json() or {}

            # Validate and sanitize input using schema
            validated_data = validate_schema(data, "chemical")

            logger.info(f"Updating chemical {id} with data: {validated_data}")

            # Update fields
            if "part_number" in validated_data:
                chemical.part_number = validated_data["part_number"]
            if "lot_number" in validated_data:
                chemical.lot_number = validated_data["lot_number"]
            if "description" in validated_data:
                chemical.description = validated_data["description"]
            if "manufacturer" in validated_data:
                chemical.manufacturer = validated_data["manufacturer"]
            if "quantity" in validated_data:
                chemical.quantity = validated_data["quantity"]
            if "unit" in validated_data:
                chemical.unit = validated_data["unit"]
            if "location" in validated_data:
                chemical.location = validated_data["location"]
            if "category" in validated_data:
                chemical.category = validated_data["category"]
            if "status" in validated_data:
                chemical.status = validated_data["status"]
            if "expiration_date" in validated_data:
                chemical.expiration_date = validated_data["expiration_date"]
            if "minimum_stock_level" in validated_data:
                chemical.minimum_stock_level = validated_data["minimum_stock_level"]
            if "notes" in validated_data:
                chemical.notes = validated_data["notes"]

            # Update reorder status based on new values
            chemical.update_reorder_status()

            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type="chemical_updated",
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} updated"
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_updated",
                    description=f"Updated chemical {chemical.part_number} - {chemical.lot_number}"
                )
                db.session.add(activity)

            db.session.commit()

            logger.info(f"Chemical {id} updated successfully")
            return jsonify(chemical.to_dict())

        if request.method == "DELETE":
            # Delete chemical
            part_number = chemical.part_number
            lot_number = chemical.lot_number

            db.session.delete(chemical)

            # Log the action
            log = AuditLog(
                action_type="chemical_deleted",
                action_details=f"Chemical {part_number} - {lot_number} deleted"
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_deleted",
                    description=f"Deleted chemical {part_number} - {lot_number}"
                )
                db.session.add(activity)

            db.session.commit()

            logger.info(f"Chemical {id} deleted successfully")
            return jsonify({"message": "Chemical deleted successfully"}), 200
        return None

    # Archive a chemical
    @app.route("/api/chemicals/<int:id>/archive", methods=["POST"])
    @materials_manager_required
    def archive_chemical_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is already archived
            try:
                if chemical.is_archived:
                    return jsonify({"error": "Chemical is already archived"}), 400
            except Exception:
                return jsonify({"error": "Archive functionality not available"}), 500

            # Get request data
            data = request.get_json() or {}

            # Validate required fields
            if not data.get("reason"):
                return jsonify({"error": "Missing required field: reason"}), 400

            # Update chemical archive status
            try:
                chemical.is_archived = True
                chemical.archived_reason = data.get("reason")
                chemical.archived_date = datetime.utcnow()
            except Exception as e:
                print(f"Error updating archive status: {e!s}")
                return jsonify({"error": "Failed to update archive status"}), 500

            # Log the action
            user_name = request.current_user.get("user_name", "Unknown user")
            log = AuditLog(
                action_type="chemical_archived",
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} archived by {user_name}: {data.get('reason')}"
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_archived",
                    description=f"Archived chemical {chemical.part_number} - {chemical.lot_number}: {data.get('reason')}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                "chemical": chemical.to_dict(),
                "message": "Chemical archived successfully"
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in archive chemical route: {e!s}")
            return jsonify({"error": "An error occurred while archiving the chemical"}), 500

    # Unarchive a chemical
    @app.route("/api/chemicals/<int:id>/unarchive", methods=["POST"])
    @materials_manager_required
    def unarchive_chemical_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is archived
            try:
                if not chemical.is_archived:
                    return jsonify({"error": "Chemical is not archived"}), 400
            except Exception:
                return jsonify({"error": "Archive functionality not available"}), 500

            # Update chemical archive status
            try:
                chemical.is_archived = False
                chemical.archived_reason = None
                chemical.archived_date = None
            except Exception as e:
                print(f"Error updating archive status: {e!s}")
                return jsonify({"error": "Failed to update archive status"}), 500

            # Log the action
            user_name = request.current_user.get("user_name", "Unknown user")
            log = AuditLog(
                action_type="chemical_unarchived",
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} unarchived by {user_name}"
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_unarchived",
                    description=f"Unarchived chemical {chemical.part_number} - {chemical.lot_number}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                "chemical": chemical.to_dict(),
                "message": "Chemical unarchived successfully"
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in unarchive chemical route: {e!s}")
            return jsonify({"error": "An error occurred while unarchiving the chemical"}), 500

    # Mark a chemical as delivered
    @app.route("/api/chemicals/<int:id>/mark-delivered", methods=["POST"])
    @materials_manager_required
    def mark_chemical_as_delivered_route(id):
        try:
            # Get the chemical
            chemical = Chemical.query.get_or_404(id)

            # Check if the chemical is currently marked as ordered
            if chemical.reorder_status != "ordered":
                return jsonify({"error": "Chemical is not currently on order"}), 400

            # Get request data
            data = request.get_json() or {}

            # Check if received quantity is provided
            quantity_log = ""
            if "received_quantity" in data and data["received_quantity"] is not None:
                try:
                    received_quantity = float(data["received_quantity"])
                    if received_quantity <= 0:
                        return jsonify({"error": "Received quantity must be greater than zero"}), 400

                    # Update chemical quantity
                    previous_quantity = chemical.quantity
                    chemical.quantity += received_quantity

                    # Include quantity update in log details
                    quantity_log = f" with {received_quantity} {chemical.unit} received (previous: {previous_quantity} {chemical.unit}, new: {chemical.quantity} {chemical.unit})"
                except ValueError:
                    return jsonify({"error": "Invalid received quantity format"}), 400

            # Update chemical reorder status and ensure it's properly added to active inventory
            try:
                # Update reorder status
                chemical.reorder_status = "not_needed"
                chemical.needs_reorder = False
                chemical.reorder_date = None
                chemical.expected_delivery_date = None

                # Update chemical status to available if it's not already
                if chemical.status != "available" and chemical.quantity > 0:
                    chemical.status = "available"
                elif chemical.quantity <= 0:
                    chemical.status = "out_of_stock"
                elif chemical.is_low_stock():
                    chemical.status = "low_stock"

                # Make sure the chemical is not archived
                chemical.is_archived = False
                chemical.archived_reason = None
                chemical.archived_date = None

                # Update the linked procurement order status if it exists
                if chemical.procurement_order_id:
                    from models import ProcurementOrder
                    procurement_order = ProcurementOrder.query.get(chemical.procurement_order_id)
                    if procurement_order and procurement_order.status not in ["received", "cancelled"]:
                        procurement_order.status = "received"
                        procurement_order.completed_date = datetime.utcnow()

                    # Clear the procurement order link
                    chemical.procurement_order_id = None

                # Update the unified request system if a request item exists for this chemical
                from utils.unified_requests import update_request_item_status
                received_qty = data.get("received_quantity") if "received_quantity" in data else None
                update_request_item_status(
                    source_type="chemical_reorder",
                    source_id=chemical.id,
                    new_status="received",
                    received_date=datetime.utcnow(),
                    received_quantity=received_qty
                )
            except Exception as e:
                print(f"Error updating chemical status: {e!s}")
                return jsonify({"error": "Failed to update chemical status"}), 500

            # Log the action
            user_name = request.current_user.get("user_name", "Unknown user")
            log = AuditLog(
                action_type="chemical_delivered",
                action_details=f"Chemical {chemical.part_number} - {chemical.lot_number} marked as delivered by {user_name}{quantity_log}"
            )
            db.session.add(log)

            # Log user activity
            if hasattr(request, "current_user"):
                activity = UserActivity(
                    user_id=request.current_user["user_id"],
                    activity_type="chemical_delivered",
                    description=f"Marked chemical {chemical.part_number} - {chemical.lot_number} as delivered{quantity_log}"
                )
                db.session.add(activity)

            db.session.commit()

            # Return updated chemical
            return jsonify({
                "chemical": chemical.to_dict(),
                "message": "Chemical marked as delivered successfully"
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error in mark chemical as delivered route: {e!s}")
            return jsonify({"error": "An error occurred while marking the chemical as delivered"}), 500
