"""API routes for multi-item user request management."""

import logging
from collections import Counter
from datetime import datetime, timezone

from flask import jsonify, request
from sqlalchemy import or_, text

from auth import jwt_required, permission_required_any
from models import (
    AuditLog,
    Chemical,
    ProcurementOrder,
    RequestItem,
    User,
    UserActivity,
    UserRequest,
    UserRequestMessage,
    db,
    get_current_time,
)
from utils.error_handler import ValidationError, handle_errors


logger = logging.getLogger(__name__)

requests_permission = permission_required_any("page.orders", "page.requests")


def _generate_order_number():
    """Generate a unique order number in format ORD-00001."""
    result = db.session.execute(
        text("SELECT MAX(CAST(SUBSTR(order_number, 5) AS INTEGER)) FROM procurement_orders WHERE order_number IS NOT NULL")
    ).scalar()
    next_number = (result or 0) + 1
    return f"ORD-{next_number:05d}"

VALID_ITEM_TYPES = {"tool", "chemical", "expendable", "other"}
VALID_PRIORITIES = {"low", "normal", "high", "critical"}
VALID_REQUEST_STATUSES = {
    "new",
    "awaiting_info",
    "in_progress",
    "partially_ordered",
    "ordered",
    "partially_received",
    "received",
    "cancelled",
}
VALID_ITEM_STATUSES = {"pending", "ordered", "shipped", "received", "cancelled"}
CLOSED_STATUSES = {"received", "cancelled"}
OPEN_STATUSES = VALID_REQUEST_STATUSES - CLOSED_STATUSES


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


def _parse_datetime(value, field_name="timestamp"):
    if not value:
        return None

    if isinstance(value, datetime):
        dt_value = value
    else:
        try:
            normalized = value.replace("Z", "+00:00") if isinstance(value, str) else value
            dt_value = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValidationError(f"Invalid {field_name} format. Use ISO 8601 format.") from exc

    if dt_value.tzinfo:
        dt_value = dt_value.astimezone(timezone.utc).replace(tzinfo=None)

    return dt_value


def _user_can_access_request(payload, user_request):
    """Check if user can access this request."""
    if not payload or not user_request:
        return False

    if payload.get("is_admin"):
        return True

    permissions = set(payload.get("permissions", []))
    if "page.orders" in permissions:
        return True

    user_id = payload.get("user_id")
    return user_id in {user_request.requester_id, user_request.buyer_id}


def _load_user(user_id, field_name):
    if user_id is None:
        return None

    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError(f"{field_name} not found")
    return user


def register_user_request_routes(app):
    """Register user request endpoints."""

    @app.route("/api/user-requests", methods=["GET"])
    @requests_permission
    @handle_errors
    def list_user_requests():
        """Return user requests with filtering support."""

        query = UserRequest.query

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set
        user_id = current_user.get("user_id")

        # If user doesn't have orders permission, only show their own requests
        if not has_orders_permission and user_id:
            query = query.filter(UserRequest.requester_id == user_id)

        # Status filtering
        status_filter = request.args.get("status")
        if status_filter:
            statuses = {status.strip() for status in status_filter.split(",") if status.strip()}
            invalid_statuses = statuses - VALID_REQUEST_STATUSES
            if invalid_statuses:
                raise ValidationError(f"Invalid status filter: {', '.join(sorted(invalid_statuses))}")
            query = query.filter(UserRequest.status.in_(statuses))

        # Priority filtering
        priority_filter = request.args.get("priority")
        if priority_filter:
            priorities = {value.strip() for value in priority_filter.split(",") if value.strip()}
            invalid_priorities = priorities - VALID_PRIORITIES
            if invalid_priorities:
                raise ValidationError(f"Invalid priority filter: {', '.join(sorted(invalid_priorities))}")
            query = query.filter(UserRequest.priority.in_(priorities))

        # Buyer filtering
        buyer_id = request.args.get("buyer_id", type=int)
        if buyer_id:
            query = query.filter(UserRequest.buyer_id == buyer_id)

        # Requester filtering
        requester_filter = request.args.get("requester_id", type=int)

        # Search filtering
        search_term = request.args.get("search")
        if search_term:
            wildcard = f"%{search_term.strip()}%"
            query = query.filter(
                or_(
                    UserRequest.title.ilike(wildcard),
                    UserRequest.description.ilike(wildcard),
                    UserRequest.notes.ilike(wildcard),
                )
            )

        # Needs more info filtering
        needs_info = request.args.get("needs_more_info")
        if needs_info is not None:
            needs_info_bool = needs_info.lower() == "true"
            query = query.filter(UserRequest.needs_more_info == needs_info_bool)

        # Due date filtering
        due_after = _parse_datetime(request.args.get("due_after"), "due_after")
        if due_after:
            query = query.filter(UserRequest.expected_due_date >= due_after)

        due_before = _parse_datetime(request.args.get("due_before"), "due_before")
        if due_before:
            query = query.filter(UserRequest.expected_due_date <= due_before)

        # Late requests filtering
        if request.args.get("is_late", type=lambda v: v.lower() == "true"):
            now = get_current_time()
            query = query.filter(
                UserRequest.expected_due_date.isnot(None),
                UserRequest.expected_due_date < now,
                UserRequest.status.notin_(list(CLOSED_STATUSES)),
            )

        # Sorting
        sort = request.args.get("sort", "created")
        if sort == "due_date":
            query = query.order_by(UserRequest.expected_due_date.is_(None), UserRequest.expected_due_date.asc())
        else:
            query = query.order_by(UserRequest.created_at.desc())

        # Limit
        limit = request.args.get("limit", type=int)
        if limit:
            query = query.limit(limit)

        # Access control
        if has_orders_permission:
            if requester_filter:
                query = query.filter(UserRequest.requester_id == requester_filter)
        else:
            requester_id = current_user.get("user_id")
            if requester_id:
                query = query.filter(UserRequest.requester_id == requester_id)
            else:
                return jsonify({"error": "Unable to determine requesting user"}), 403

        requests_list = query.all()
        return jsonify([req.to_dict(include_items=True) for req in requests_list])

    @app.route("/api/user-requests", methods=["POST"])
    @requests_permission
    @handle_errors
    def create_user_request():
        """Create a new user request with multiple items."""

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        # Validate required fields
        title = data.get("title", "").strip()
        if not title:
            raise ValidationError("Title is required")

        items = data.get("items", [])
        if not items:
            raise ValidationError("At least one item is required")

        if not isinstance(items, list):
            raise ValidationError("Items must be an array")

        # Validate priority
        priority = data.get("priority", "normal")
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority. Must be one of: {', '.join(sorted(VALID_PRIORITIES))}")

        # Get current user
        current_user = getattr(request, "current_user", {}) or {}
        requester_id = current_user.get("user_id")
        if not requester_id:
            raise ValidationError("Unable to determine requesting user")

        # Create the request
        user_request = UserRequest(
            title=title,
            description=data.get("description", "").strip() or None,
            priority=priority,
            notes=data.get("notes", "").strip() or None,
            expected_due_date=_parse_datetime(data.get("expected_due_date"), "expected_due_date"),
            requester_id=requester_id,
        )
        db.session.add(user_request)
        db.session.flush()  # Get the ID

        # Generate and assign request number
        user_request.request_number = _generate_request_number()

        # Validate and create items
        for idx, item_data in enumerate(items):
            if not isinstance(item_data, dict):
                raise ValidationError(f"Item {idx + 1} must be an object")

            description = item_data.get("description", "").strip()
            if not description:
                raise ValidationError(f"Item {idx + 1} is missing a description")

            item_type = item_data.get("item_type", "tool")
            if item_type not in VALID_ITEM_TYPES:
                raise ValidationError(f"Item {idx + 1} has invalid type. Must be one of: {', '.join(sorted(VALID_ITEM_TYPES))}")

            quantity = item_data.get("quantity", 1)
            if not isinstance(quantity, int) or quantity < 1:
                raise ValidationError(f"Item {idx + 1} quantity must be a positive integer")

            request_item = RequestItem(
                request_id=user_request.id,
                item_type=item_type,
                part_number=item_data.get("part_number", "").strip() or None,
                description=description,
                quantity=quantity,
                unit=item_data.get("unit", "each").strip() or "each",
            )
            db.session.add(request_item)

        # Log the activity
        activity = UserActivity(
            user_id=requester_id,
            activity_type="user_request_created",
            description=f"Created request '{title}' with {len(items)} item(s)",
            ip_address=request.remote_addr,
        )
        db.session.add(activity)

        audit = AuditLog(
            action_type="USER_REQUEST_CREATED",
            action_details=f"Request '{title}' created by user {requester_id} with {len(items)} items",
        )
        db.session.add(audit)

        db.session.commit()

        return jsonify(user_request.to_dict(include_items=True)), 201

    @app.route("/api/user-requests/<int:request_id>", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_user_request(request_id):
        """Get a single user request with items."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        include_messages = request.args.get("include_messages", "false").lower() == "true"
        return jsonify(user_request.to_dict(include_items=True, include_messages=include_messages))

    @app.route("/api/user-requests/<int:request_id>", methods=["PUT"])
    @requests_permission
    @handle_errors
    def update_user_request(request_id):
        """Update a user request (admin/buyer operations)."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        if not has_orders_permission:
            # Regular users can only update notes and description
            data = request.get_json()
            if "notes" in data:
                user_request.notes = data["notes"].strip() if data["notes"] else None
            if "description" in data:
                user_request.description = data["description"].strip() if data["description"] else None
            db.session.commit()
            return jsonify(user_request.to_dict(include_items=True))

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        # Update request fields
        if "title" in data:
            title = data["title"].strip()
            if not title:
                raise ValidationError("Title cannot be empty")
            user_request.title = title

        if "description" in data:
            user_request.description = data["description"].strip() if data["description"] else None

        if "priority" in data:
            if data["priority"] not in VALID_PRIORITIES:
                raise ValidationError(f"Invalid priority. Must be one of: {', '.join(sorted(VALID_PRIORITIES))}")
            user_request.priority = data["priority"]

        if "status" in data:
            if data["status"] not in VALID_REQUEST_STATUSES:
                raise ValidationError(f"Invalid status. Must be one of: {', '.join(sorted(VALID_REQUEST_STATUSES))}")
            user_request.status = data["status"]

        if "buyer_id" in data:
            if data["buyer_id"]:
                _load_user(data["buyer_id"], "Buyer")
            user_request.buyer_id = data["buyer_id"]

        if "notes" in data:
            user_request.notes = data["notes"].strip() if data["notes"] else None

        if "needs_more_info" in data:
            user_request.needs_more_info = bool(data["needs_more_info"])

        if "expected_due_date" in data:
            user_request.expected_due_date = _parse_datetime(data["expected_due_date"], "expected_due_date")

        db.session.commit()

        return jsonify(user_request.to_dict(include_items=True))

    @app.route("/api/user-requests/<int:request_id>", methods=["DELETE"])
    @requests_permission
    @handle_errors
    def cancel_user_request(request_id):
        """Cancel a user request."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        if user_request.status in CLOSED_STATUSES:
            raise ValidationError("Cannot cancel a closed request")

        user_request.status = "cancelled"
        # Cancel all pending items
        for item in user_request.items.all():
            if item.status not in ("received", "cancelled"):
                item.status = "cancelled"

        audit = AuditLog(
            action_type="USER_REQUEST_CANCELLED",
            action_details=f"Request {request_id} cancelled",
        )
        db.session.add(audit)

        db.session.commit()

        return jsonify({"message": "Request cancelled", "request": user_request.to_dict(include_items=True)})

    @app.route("/api/user-requests/<int:request_id>/items/cancel", methods=["POST"])
    @requests_permission
    @handle_errors
    def cancel_request_items(request_id):
        """Cancel specific items in a request with a cancellation reason."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json() or {}
        item_ids = data.get("item_ids", [])
        cancellation_reason = data.get("reason", "").strip()

        if not item_ids:
            raise ValidationError("At least one item must be selected for cancellation")

        if not cancellation_reason:
            raise ValidationError("Cancellation reason is required")

        if len(cancellation_reason) < 10:
            raise ValidationError("Cancellation reason must be at least 10 characters")

        cancelled_items = []
        for item_id in item_ids:
            item = db.session.get(RequestItem, item_id)
            if not item or item.request_id != request_id:
                continue

            if item.status in ("received", "cancelled"):
                continue

            item.status = "cancelled"
            item.order_notes = f"CANCELLED: {cancellation_reason}" + (f"\n\nPrevious notes: {item.order_notes}" if item.order_notes else "")
            cancelled_items.append(item.id)

        if not cancelled_items:
            raise ValidationError("No items were cancelled. Items may already be received or cancelled.")

        # Update request status based on remaining items
        user_request.update_status_from_items()

        # Log the cancellation
        audit = AuditLog(
            action_type="REQUEST_ITEMS_CANCELLED",
            action_details=f"Items {cancelled_items} cancelled in request {request_id}. Reason: {cancellation_reason}",
        )
        db.session.add(audit)

        db.session.commit()

        return jsonify({
            "message": f"{len(cancelled_items)} item(s) cancelled successfully",
            "cancelled_item_ids": cancelled_items,
            "request": user_request.to_dict(include_items=True)
        })

    # Item-specific routes
    @app.route("/api/user-requests/<int:request_id>/items", methods=["POST"])
    @requests_permission
    @handle_errors
    def add_request_item(request_id):
        """Add an item to an existing request."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        if user_request.status in CLOSED_STATUSES:
            raise ValidationError("Cannot add items to a closed request")

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        description = data.get("description", "").strip()
        if not description:
            raise ValidationError("Item description is required")

        item_type = data.get("item_type", "tool")
        if item_type not in VALID_ITEM_TYPES:
            raise ValidationError(f"Invalid item type. Must be one of: {', '.join(sorted(VALID_ITEM_TYPES))}")

        quantity = data.get("quantity", 1)
        if not isinstance(quantity, int) or quantity < 1:
            raise ValidationError("Quantity must be a positive integer")

        request_item = RequestItem(
            request_id=request_id,
            item_type=item_type,
            part_number=data.get("part_number", "").strip() or None,
            description=description,
            quantity=quantity,
            unit=data.get("unit", "each").strip() or "each",
        )
        db.session.add(request_item)
        db.session.commit()

        return jsonify(request_item.to_dict()), 201

    @app.route("/api/user-requests/<int:request_id>/items/<int:item_id>", methods=["PUT"])
    @requests_permission
    @handle_errors
    def update_request_item(request_id, item_id):
        """Update an item in a request (buyer fulfillment)."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        if not has_orders_permission:
            return jsonify({"error": "Access denied"}), 403

        request_item = RequestItem.query.filter_by(id=item_id, request_id=request_id).first()
        if not request_item:
            return jsonify({"error": "Item not found"}), 404

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        # Update item fields
        if "item_type" in data:
            if data["item_type"] not in VALID_ITEM_TYPES:
                raise ValidationError(f"Invalid item type. Must be one of: {', '.join(sorted(VALID_ITEM_TYPES))}")
            request_item.item_type = data["item_type"]

        if "part_number" in data:
            request_item.part_number = data["part_number"].strip() if data["part_number"] else None

        if "description" in data:
            description = data["description"].strip()
            if not description:
                raise ValidationError("Description cannot be empty")
            request_item.description = description

        if "quantity" in data:
            if not isinstance(data["quantity"], int) or data["quantity"] < 1:
                raise ValidationError("Quantity must be a positive integer")
            request_item.quantity = data["quantity"]

        if "unit" in data:
            request_item.unit = data["unit"].strip() or "each"

        if "status" in data:
            if data["status"] not in VALID_ITEM_STATUSES:
                raise ValidationError(f"Invalid status. Must be one of: {', '.join(sorted(VALID_ITEM_STATUSES))}")
            request_item.status = data["status"]

        # Order fulfillment fields
        if "vendor" in data:
            request_item.vendor = data["vendor"].strip() if data["vendor"] else None

        if "tracking_number" in data:
            request_item.tracking_number = data["tracking_number"].strip() if data["tracking_number"] else None

        if "ordered_date" in data:
            request_item.ordered_date = _parse_datetime(data["ordered_date"], "ordered_date")

        if "expected_delivery_date" in data:
            request_item.expected_delivery_date = _parse_datetime(data["expected_delivery_date"], "expected_delivery_date")

        if "received_date" in data:
            request_item.received_date = _parse_datetime(data["received_date"], "received_date")

        if "received_quantity" in data:
            request_item.received_quantity = data["received_quantity"]

        if "unit_cost" in data:
            request_item.unit_cost = data["unit_cost"]

        if "total_cost" in data:
            request_item.total_cost = data["total_cost"]

        if "order_notes" in data:
            request_item.order_notes = data["order_notes"].strip() if data["order_notes"] else None

        # Update parent request status
        user_request.update_status_from_items()

        db.session.commit()

        return jsonify(request_item.to_dict())

    @app.route("/api/user-requests/<int:request_id>/items/<int:item_id>", methods=["DELETE"])
    @requests_permission
    @handle_errors
    def remove_request_item(request_id, item_id):
        """Remove an item from a request."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        if user_request.status in CLOSED_STATUSES:
            raise ValidationError("Cannot remove items from a closed request")

        request_item = RequestItem.query.filter_by(id=item_id, request_id=request_id).first()
        if not request_item:
            return jsonify({"error": "Item not found"}), 404

        if request_item.status in ("ordered", "shipped", "received"):
            raise ValidationError("Cannot remove an item that has been ordered or received")

        db.session.delete(request_item)

        # Check if there are any items left
        remaining_items = RequestItem.query.filter_by(request_id=request_id).count()
        if remaining_items == 0:
            raise ValidationError("Cannot remove the last item. Cancel the request instead.")

        user_request.update_status_from_items()
        db.session.commit()

        return jsonify({"message": "Item removed"})

    # Bulk operations for buyers
    @app.route("/api/user-requests/<int:request_id>/items/mark-ordered", methods=["POST"])
    @requests_permission
    @handle_errors
    def mark_items_ordered(request_id):
        """Mark multiple items as ordered with vendor/tracking info."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        if not has_orders_permission:
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        item_updates = data.get("items", [])
        if not item_updates:
            raise ValidationError("At least one item update is required")

        # Group items by vendor to create procurement orders
        items_by_vendor = {}
        request_items_to_update = []
        created_orders = []

        for item_update in item_updates:
            item_id = item_update.get("item_id")
            if not item_id:
                raise ValidationError("item_id is required for each update")

            request_item = RequestItem.query.filter_by(id=item_id, request_id=request_id).first()
            if not request_item:
                raise ValidationError(f"Item {item_id} not found in this request")

            vendor = item_update.get("vendor", "").strip() or "Unknown Vendor"

            request_item.status = "ordered"
            request_item.vendor = vendor if vendor != "Unknown Vendor" else None
            request_item.tracking_number = item_update.get("tracking_number", "").strip() or None
            request_item.ordered_date = get_current_time()

            if "expected_delivery_date" in item_update:
                request_item.expected_delivery_date = _parse_datetime(
                    item_update["expected_delivery_date"], "expected_delivery_date"
                )

            if "unit_cost" in item_update:
                request_item.unit_cost = item_update["unit_cost"]

            if "total_cost" in item_update:
                request_item.total_cost = item_update["total_cost"]

            if "order_notes" in item_update:
                request_item.order_notes = item_update["order_notes"].strip() if item_update["order_notes"] else None

            # Group by vendor for procurement order creation
            if vendor not in items_by_vendor:
                items_by_vendor[vendor] = []
            items_by_vendor[vendor].append((request_item, item_update))
            request_items_to_update.append(request_item)

        # Assign buyer if not already assigned
        if not user_request.buyer_id:
            user_request.buyer_id = current_user.get("user_id")

        # Create procurement orders for each vendor
        created_orders = []
        for vendor, vendor_items in items_by_vendor.items():
            # Create a title for the procurement order
            item_descriptions = [item.description[:50] for item, _ in vendor_items[:3]]
            if len(vendor_items) > 3:
                order_title = f"{', '.join(item_descriptions)}... ({len(vendor_items)} items)"
            else:
                order_title = ", ".join(item_descriptions)

            # Determine priority (use highest priority from items or request)
            priority = user_request.priority

            # Get part number (use first item's part number if available)
            first_item = vendor_items[0][0]
            part_number = first_item.part_number
            if len(vendor_items) > 1:
                # If multiple items, list all part numbers
                part_numbers = [item.part_number for item, _ in vendor_items if item.part_number]
                if part_numbers:
                    part_number = ", ".join(part_numbers[:5])
                    if len(part_numbers) > 5:
                        part_number += f"... (+{len(part_numbers) - 5} more)"

            # Calculate total quantity
            total_quantity = sum(item.quantity for item, _ in vendor_items)

            # Determine order_type based on items (use most common type, default to first item's type)
            item_types = [item.item_type for item, _ in vendor_items]
            # Use most common item type, or first item's type if all different
            type_counts = Counter(item_types)
            order_type = type_counts.most_common(1)[0][0] if type_counts else "tool"
            # Ensure order_type is valid (tool, chemical, expendable, kit)
            if order_type not in {"tool", "chemical", "expendable", "kit"}:
                order_type = "tool"  # Default fallback

            # Create the procurement order
            procurement_order = ProcurementOrder(
                title=order_title,
                order_type=order_type,
                part_number=part_number,
                description=f"Order from request {user_request.request_number or f'#{user_request.id}'}: {user_request.title}",
                priority=priority,
                status="ordered",
                vendor=vendor if vendor != "Unknown Vendor" else None,
                quantity=total_quantity,
                requester_id=user_request.requester_id,
                buyer_id=current_user.get("user_id"),
                ordered_date=get_current_time(),
                expected_due_date=user_request.expected_due_date,
            )

            # Generate order number
            procurement_order.order_number = _generate_order_number()

            db.session.add(procurement_order)
            db.session.flush()  # Get the ID

            # Link items to this procurement order
            for request_item, _ in vendor_items:
                request_item.procurement_order_id = procurement_order.id

            # If any items are chemicals, update the corresponding Chemical records
            for request_item, _ in vendor_items:
                if request_item.item_type == "chemical" and request_item.part_number:
                    # Find matching chemicals by part_number
                    chemicals = Chemical.query.filter_by(part_number=request_item.part_number).all()
                    for chemical in chemicals:
                        # Update reorder status to "ordered"
                        chemical.reorder_status = "ordered"
                        chemical.reorder_date = get_current_time()
                        logger.info(
                            f"Updated chemical {chemical.id} (part: {chemical.part_number}) reorder_status to 'ordered'"
                        )

            created_orders.append(procurement_order)

            # Log the order creation
            logger.info(
                f"Created procurement order {procurement_order.order_number} for {len(vendor_items)} items from request {request_id}"
            )

        user_request.update_status_from_items()
        db.session.commit()

        response_data = user_request.to_dict(include_items=True)
        response_data["created_orders"] = [
            {
                "id": order.id,
                "order_number": order.order_number,
                "vendor": order.vendor,
                "item_count": len([item for item in request_items_to_update if item.procurement_order_id == order.id]),
            }
            for order in created_orders
        ]

        return jsonify(response_data)

    @app.route("/api/user-requests/<int:request_id>/items/mark-received", methods=["POST"])
    @requests_permission
    @handle_errors
    def mark_items_received(request_id):
        """Mark multiple items as received."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        item_ids = data.get("item_ids", [])
        if not item_ids:
            raise ValidationError("At least one item_id is required")

        for item_id in item_ids:
            request_item = RequestItem.query.filter_by(id=item_id, request_id=request_id).first()
            if not request_item:
                raise ValidationError(f"Item {item_id} not found in this request")

            request_item.status = "received"
            request_item.received_date = get_current_time()
            if not request_item.received_quantity:
                request_item.received_quantity = request_item.quantity

        user_request.update_status_from_items()
        db.session.commit()

        return jsonify(user_request.to_dict(include_items=True))

    # Messaging routes
    @app.route("/api/user-requests/<int:request_id>/messages", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_request_messages(request_id):
        """Get messages for a request."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        messages = user_request.messages.order_by(UserRequestMessage.sent_date.desc()).all()
        return jsonify([msg.to_dict() for msg in messages])

    @app.route("/api/user-requests/<int:request_id>/messages", methods=["POST"])
    @jwt_required
    @handle_errors
    def send_request_message(request_id):
        """Send a message on a request."""

        user_request = db.session.get(UserRequest, request_id)
        if not user_request:
            return jsonify({"error": "Request not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        if not _user_can_access_request(current_user, user_request):
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        subject = data.get("subject", "").strip()
        if not subject:
            raise ValidationError("Subject is required")

        message_text = data.get("message", "").strip()
        if not message_text:
            raise ValidationError("Message is required")

        sender_id = current_user.get("user_id")
        if not sender_id:
            raise ValidationError("Unable to determine sender")

        # Determine recipient
        recipient_id = None
        if sender_id == user_request.requester_id and user_request.buyer_id:
            recipient_id = user_request.buyer_id
        elif sender_id == user_request.buyer_id:
            recipient_id = user_request.requester_id
        else:
            # Admin or other user - direct to requester
            recipient_id = user_request.requester_id

        message = UserRequestMessage(
            request_id=request_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject=subject,
            message=message_text,
            attachments=data.get("attachments", "").strip() or None,
        )
        db.session.add(message)
        db.session.commit()

        return jsonify(message.to_dict()), 201

    @app.route("/api/user-requests/messages/<int:message_id>/read", methods=["PUT"])
    @jwt_required
    @handle_errors
    def mark_user_request_message_read(message_id):
        """Mark a message as read."""

        message = db.session.get(UserRequestMessage, message_id)
        if not message:
            return jsonify({"error": "Message not found"}), 404

        current_user = getattr(request, "current_user", {}) or {}
        user_id = current_user.get("user_id")

        if message.recipient_id != user_id:
            return jsonify({"error": "Cannot mark other users' messages as read"}), 403

        message.is_read = True
        message.read_date = get_current_time()
        db.session.commit()

        return jsonify(message.to_dict())

    # Analytics
    @app.route("/api/user-requests/analytics", methods=["GET"])
    @requests_permission
    @handle_errors
    def request_analytics():
        """Get analytics for user requests."""

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        query = UserRequest.query

        if not has_orders_permission:
            requester_id = current_user.get("user_id")
            if requester_id:
                query = query.filter(UserRequest.requester_id == requester_id)

        requests_list = query.all()

        # Calculate statistics
        status_counts = {}
        priority_counts = {}
        total_items = 0
        items_by_status = {}

        for req in requests_list:
            status_counts[req.status] = status_counts.get(req.status, 0) + 1
            priority_counts[req.priority] = priority_counts.get(req.priority, 0) + 1

            for item in req.items.all():
                total_items += 1
                items_by_status[item.status] = items_by_status.get(item.status, 0) + 1

        return jsonify({
            "total_requests": len(requests_list),
            "total_items": total_items,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "items_by_status": items_by_status,
        })
