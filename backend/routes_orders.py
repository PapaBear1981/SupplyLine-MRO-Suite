"""API routes for procurement order management."""

import logging
import os
import secrets
from collections import Counter
from datetime import datetime, timezone

from flask import current_app, jsonify, request
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from auth import jwt_required, permission_required, permission_required_any
from models import (
    AuditLog,
    ProcurementOrder,
    ProcurementOrderMessage,
    User,
    UserActivity,
    db,
    get_current_time,
)
from models_kits import Kit
from utils.error_handler import ValidationError, handle_errors
from utils.file_validation import (
    ALLOWED_ATTACHMENT_EXTENSIONS,
    FileValidationError,
    scan_file_for_malware,
    validate_file_upload,
)


logger = logging.getLogger(__name__)

orders_permission = permission_required("page.orders")
orders_or_requests_permission = permission_required_any("page.orders", "page.requests")

VALID_ORDER_TYPES = {"tool", "chemical", "expendable", "kit"}
VALID_PRIORITIES = {"low", "normal", "high", "critical"}
VALID_STATUSES = {
    "new",
    "awaiting_info",
    "in_progress",
    "ordered",
    "shipped",
    "received",
    "cancelled",
}
CLOSED_STATUSES = {"received", "cancelled"}
OPEN_STATUSES = VALID_STATUSES - CLOSED_STATUSES


def _parse_datetime(value, field_name="timestamp"):
    if not value:
        return None

    if isinstance(value, datetime):
        dt_value = value
    else:
        try:
            normalized = value.replace("Z", "+00:00") if isinstance(value, str) else value
            dt_value = datetime.fromisoformat(normalized)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise ValidationError(f"Invalid {field_name} format. Use ISO 8601 format.") from exc

    if dt_value.tzinfo:
        dt_value = dt_value.astimezone(timezone.utc).replace(tzinfo=None)

    return dt_value


def _user_can_access_order(payload, order):
    if not payload or not order:
        return False

    if payload.get("is_admin"):
        return True

    permissions = set(payload.get("permissions", []))
    if "page.orders" in permissions:
        return True

    user_id = payload.get("user_id")
    return user_id in {order.requester_id, order.buyer_id}


def _load_user(user_id, field_name):
    if user_id is None:
        return None

    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError(f"{field_name} not found")
    return user


def register_order_routes(app):
    """Register procurement order endpoints."""

    @app.route("/api/orders", methods=["GET"])
    @orders_or_requests_permission
    @handle_errors
    def list_orders():
        """Return procurement orders with filtering support."""

        query = ProcurementOrder.query

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        status_filter = request.args.get("status")
        if status_filter:
            statuses = {status.strip() for status in status_filter.split(",") if status.strip()}
            invalid_statuses = statuses - VALID_STATUSES
            if invalid_statuses:
                raise ValidationError(f"Invalid status filter: {', '.join(sorted(invalid_statuses))}")
            query = query.filter(ProcurementOrder.status.in_(statuses))

        type_filter = request.args.get("order_type")
        if type_filter:
            types = {value.strip() for value in type_filter.split(",") if value.strip()}
            invalid_types = types - VALID_ORDER_TYPES
            if invalid_types:
                raise ValidationError(f"Invalid order type filter: {', '.join(sorted(invalid_types))}")
            query = query.filter(ProcurementOrder.order_type.in_(types))

        priority_filter = request.args.get("priority")
        if priority_filter:
            priorities = {value.strip() for value in priority_filter.split(",") if value.strip()}
            invalid_priorities = priorities - VALID_PRIORITIES
            if invalid_priorities:
                raise ValidationError(f"Invalid priority filter: {', '.join(sorted(invalid_priorities))}")
            query = query.filter(ProcurementOrder.priority.in_(priorities))

        buyer_id = request.args.get("buyer_id", type=int)
        if buyer_id:
            query = query.filter(ProcurementOrder.buyer_id == buyer_id)

        requester_filter = request.args.get("requester_id", type=int)

        search_term = request.args.get("search")
        if search_term:
            wildcard = f"%{search_term.strip()}%"
            query = query.filter(
                or_(
                    ProcurementOrder.title.ilike(wildcard),
                    ProcurementOrder.description.ilike(wildcard),
                    ProcurementOrder.reference_number.ilike(wildcard),
                    ProcurementOrder.tracking_number.ilike(wildcard),
                )
            )

        due_after = _parse_datetime(request.args.get("due_after"), "due_after")
        if due_after:
            query = query.filter(ProcurementOrder.expected_due_date >= due_after)

        due_before = _parse_datetime(request.args.get("due_before"), "due_before")
        if due_before:
            query = query.filter(ProcurementOrder.expected_due_date <= due_before)

        if request.args.get("is_late", type=lambda v: v.lower() == "true"):
            now = get_current_time()
            query = query.filter(
                ProcurementOrder.expected_due_date.isnot(None),
                ProcurementOrder.expected_due_date < now,
                ProcurementOrder.status.notin_(list(CLOSED_STATUSES)),
            )

        sort = request.args.get("sort", "due_date")
        if sort == "created":
            query = query.order_by(ProcurementOrder.created_at.desc())
        else:
            query = query.order_by(ProcurementOrder.expected_due_date.is_(None), ProcurementOrder.expected_due_date.asc())

        limit = request.args.get("limit", type=int)
        if limit:
            query = query.limit(limit)

        if has_orders_permission:
            if requester_filter:
                query = query.filter(ProcurementOrder.requester_id == requester_filter)
        else:
            requester_id = current_user.get("user_id")
            if requester_id:
                query = query.filter(ProcurementOrder.requester_id == requester_id)
            else:
                return jsonify({"error": "Unable to determine requesting user"}), 403

        orders = query.all()
        return jsonify([order.to_dict() for order in orders])

    @app.route("/api/orders", methods=["POST"])
    @orders_or_requests_permission
    @handle_errors
    def create_order():
        """Create a new procurement order."""

        if request.content_type and "multipart/form-data" in request.content_type:
            data = request.form.to_dict()
            documentation_file = request.files.get("documentation")
        else:
            data = request.get_json() or {}
            documentation_file = None

        current_user = getattr(request, "current_user", {}) or {}
        permission_set = set(current_user.get("permissions", []))
        has_orders_permission = bool(current_user.get("is_admin")) or "page.orders" in permission_set

        title = data.get("title")
        if not title:
            raise ValidationError("Title is required")

        order_type = data.get("order_type", "tool").lower()
        if order_type not in VALID_ORDER_TYPES:
            raise ValidationError("Invalid order type")

        priority = data.get("priority", "normal").lower()
        if priority not in VALID_PRIORITIES:
            raise ValidationError("Invalid priority")

        status = data.get("status", "new").lower()
        if not has_orders_permission:
            status = "new"
        if status not in VALID_STATUSES:
            raise ValidationError("Invalid status")

        expected_due_date = _parse_datetime(data.get("expected_due_date"), "expected_due_date")

        quantity_value = data.get("quantity")
        if quantity_value is not None and quantity_value != "":
            try:
                quantity_int = int(quantity_value)
            except (TypeError, ValueError) as exc:
                raise ValidationError("Quantity must be a positive integer") from exc
            if quantity_int <= 0:
                raise ValidationError("Quantity must be a positive integer")
        else:
            quantity_int = None

        requester_id = data.get("requester_id") if has_orders_permission else current_user.get("user_id")
        requester_id = requester_id or current_user.get("user_id")
        requester = _load_user(requester_id, "Requester")
        buyer_id = data.get("buyer_id") if has_orders_permission else None
        buyer = _load_user(buyer_id, "Buyer") if buyer_id else None

        kit_id = data.get("kit_id")
        if kit_id:
            kit = db.session.get(Kit, kit_id)
            if not kit:
                raise ValidationError("Kit not found")

        documentation_path = None
        if documentation_file and documentation_file.filename:
            original_filename = secure_filename(documentation_file.filename)
            ext = os.path.splitext(original_filename)[1].lower()

            if ext and ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
                allowed_list = ", ".join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))
                raise ValidationError(
                    f"File type not allowed. Allowed extensions: {allowed_list}"
                )

            static_folder = current_app.static_folder or "static"
            order_docs_folder = os.path.join(static_folder, "order_documents")
            os.makedirs(order_docs_folder, exist_ok=True)

            unique_id = secrets.token_urlsafe(16)
            timestamp = get_current_time().strftime("%Y%m%d_%H%M%S")
            safe_basename = f"{timestamp}_{unique_id}{ext or ''}"
            disk_path = os.path.join(order_docs_folder, safe_basename)

            documentation_file.save(disk_path)

            try:
                # Validate file content and perform a basic malware scan
                validate_file_upload(disk_path)
                scan_file_for_malware(disk_path)
            except FileValidationError as exc:
                # Remove invalid file and bubble up the validation error
                if os.path.exists(disk_path):
                    os.remove(disk_path)
                raise exc

            documentation_path = f"/api/static/order_documents/{safe_basename}"

        order = ProcurementOrder(
            title=title,
            order_type=order_type,
            part_number=data.get("part_number"),
            description=data.get("description"),
            priority=priority,
            status=status,
            reference_type=data.get("reference_type"),
            reference_number=data.get("reference_number"),
            tracking_number=data.get("tracking_number"),
            documentation_path=documentation_path,
            expected_due_date=expected_due_date,
            notes=data.get("notes"),
            quantity=quantity_int,
            unit=data.get("unit") or None,
            kit_id=kit_id,
            requester_id=requester.id,
            buyer_id=buyer.id if buyer else None,
        )

        db.session.add(order)
        db.session.commit()

        log = AuditLog(
            action_type="procurement_order_created",
            action_details=f"Order {order.id} created with status {order.status}",
        )
        db.session.add(log)
        db.session.commit()

        logger.info("Procurement order created", extra={"order_id": order.id})
        return jsonify(order.to_dict()), 201

    @app.route("/api/orders/<int:order_id>", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_order(order_id):
        order = ProcurementOrder.query.get_or_404(order_id)
        if not _user_can_access_order(request.current_user, order):
            return jsonify({"error": "You do not have access to this order"}), 403
        include_messages = request.args.get("include_messages", "false").lower() == "true"
        return jsonify(order.to_dict(include_messages=include_messages))

    @app.route("/api/orders/<int:order_id>", methods=["PUT"])
    @orders_permission
    @handle_errors
    def update_order(order_id):
        order = ProcurementOrder.query.get_or_404(order_id)
        data = request.get_json() or {}

        if data.get("title"):
            order.title = data["title"]

        if "part_number" in data:
            order.part_number = data.get("part_number")

        if "description" in data:
            order.description = data["description"]

        if "order_type" in data:
            new_type = data["order_type"].lower()
            if new_type not in VALID_ORDER_TYPES:
                raise ValidationError("Invalid order type")
            order.order_type = new_type

        if "priority" in data:
            new_priority = data["priority"].lower()
            if new_priority not in VALID_PRIORITIES:
                raise ValidationError("Invalid priority")
            order.priority = new_priority

        if "status" in data:
            new_status = data["status"].lower()
            if new_status not in VALID_STATUSES:
                raise ValidationError("Invalid status")
            order.status = new_status
            if new_status in CLOSED_STATUSES and not order.completed_date:
                order.completed_date = get_current_time()
            if new_status not in CLOSED_STATUSES:
                order.completed_date = None

        if "expected_due_date" in data:
            order.expected_due_date = _parse_datetime(data.get("expected_due_date"), "expected_due_date")

        if "reference_type" in data:
            order.reference_type = data.get("reference_type")

        if "reference_number" in data:
            order.reference_number = data.get("reference_number")

        if "tracking_number" in data:
            order.tracking_number = data.get("tracking_number")

        if "notes" in data:
            order.notes = data.get("notes")

        if "quantity" in data:
            quantity_value = data.get("quantity")
            if quantity_value in (None, ""):
                order.quantity = None
            else:
                try:
                    quantity_int = int(quantity_value)
                except (TypeError, ValueError) as exc:
                    raise ValidationError("Quantity must be a positive integer") from exc
                if quantity_int <= 0:
                    raise ValidationError("Quantity must be a positive integer")
                order.quantity = quantity_int

        if "unit" in data:
            unit_value = data.get("unit")
            order.unit = unit_value or None

        if "kit_id" in data:
            kit_id = data.get("kit_id")
            if kit_id:
                kit = db.session.get(Kit, kit_id)
                if not kit:
                    raise ValidationError("Kit not found")
            order.kit_id = kit_id

        if "requester_id" in data:
            requester = _load_user(data.get("requester_id"), "Requester")
            order.requester_id = requester.id

        if "buyer_id" in data:
            buyer_value = data.get("buyer_id")
            buyer = _load_user(buyer_value, "Buyer") if buyer_value else None
            order.buyer_id = buyer.id if buyer else None

        db.session.commit()

        log = AuditLog(
            action_type="procurement_order_updated",
            action_details=f"Order {order.id} updated",
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(order.to_dict())

    @app.route("/api/orders/analytics", methods=["GET"])
    @orders_permission
    @handle_errors
    def order_analytics():
        """Return aggregated analytics for procurement orders."""

        orders = ProcurementOrder.query.all()
        now = get_current_time()

        status_counter = Counter(order.status or "unknown" for order in orders)
        type_counter = Counter(order.order_type or "unspecified" for order in orders)
        priority_counter = Counter(order.priority or "normal" for order in orders)

        late_orders = [
            order for order in orders
            if order.expected_due_date and order.expected_due_date < now and order.status not in CLOSED_STATUSES
        ]

        due_soon_orders = [
            order for order in orders
            if order.expected_due_date and 0 <= (order.expected_due_date - now).days <= 3 and order.status not in CLOSED_STATUSES
        ]

        month_counter = Counter()
        total_open_days = 0
        open_count = 0

        for order in orders:
            if order.expected_due_date:
                month_counter[order.expected_due_date.strftime("%Y-%m")] += 1
            if order.status not in CLOSED_STATUSES and order.created_at:
                open_count += 1
                total_open_days += (now - order.created_at).days

        analytics_payload = {
            "status_breakdown": [
                {"status": status, "count": count}
                for status, count in sorted(status_counter.items())
            ],
            "type_breakdown": [
                {"type": order_type, "count": count}
                for order_type, count in sorted(type_counter.items())
            ],
            "priority_breakdown": [
                {"priority": priority, "count": count}
                for priority, count in sorted(priority_counter.items())
            ],
            "late_count": len(late_orders),
            "due_soon_count": len(due_soon_orders),
            "total_open": sum(
                1 for order in orders if order.status not in CLOSED_STATUSES
            ),
            "orders_per_month": [
                {"month": month, "count": count}
                for month, count in sorted(month_counter.items())
            ],
            "average_open_days": (total_open_days / open_count) if open_count else 0,
        }

        return jsonify(analytics_payload)

    @app.route("/api/orders/late-alerts", methods=["GET"])
    @orders_permission
    @handle_errors
    def late_order_alerts():
        limit = request.args.get("limit", 5, type=int) or 5
        now = get_current_time()

        query = ProcurementOrder.query.filter(
            ProcurementOrder.expected_due_date.isnot(None),
            ProcurementOrder.expected_due_date < now,
            ProcurementOrder.status.notin_(list(CLOSED_STATUSES)),
        ).order_by(ProcurementOrder.expected_due_date.asc())

        orders = query.limit(limit).all()
        return jsonify([order.to_dict() for order in orders])

    @app.route("/api/orders/<int:order_id>/messages", methods=["GET"])
    @jwt_required
    @handle_errors
    def list_order_messages(order_id):
        order = ProcurementOrder.query.get_or_404(order_id)
        if not _user_can_access_order(request.current_user, order):
            return jsonify({"error": "You do not have access to this order"}), 403

        messages = order.messages.order_by(ProcurementOrderMessage.sent_date.desc()).all()
        return jsonify([message.to_dict() for message in messages])

    @app.route("/api/orders/<int:order_id>/messages", methods=["POST"])
    @jwt_required
    @handle_errors
    def send_order_message(order_id):
        order = ProcurementOrder.query.get_or_404(order_id)
        if not _user_can_access_order(request.current_user, order):
            return jsonify({"error": "You do not have access to this order"}), 403

        data = request.get_json() or {}
        subject = data.get("subject") or f"Order {order.id} update"
        body = data.get("message")
        if not body:
            raise ValidationError("Message content is required")

        sender_id = request.current_user.get("user_id")
        recipient_id = data.get("recipient_id")

        if recipient_id not in (None, ""):
            try:
                recipient_id = int(recipient_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError("Recipient must be a valid user") from exc
        else:
            recipient_id = None

        if not recipient_id:
            if sender_id == order.requester_id and order.buyer_id:
                recipient_id = order.buyer_id
            elif (order.buyer_id and sender_id == order.buyer_id) or sender_id != order.requester_id:
                recipient_id = order.requester_id

        if recipient_id == sender_id:
            if data.get("recipient_id") not in (None, ""):
                raise ValidationError("Recipient must be different from sender")
            recipient_id = None

        recipient = _load_user(recipient_id, "Recipient") if recipient_id else None

        message = ProcurementOrderMessage(
            order_id=order.id,
            sender_id=sender_id,
            recipient_id=recipient.id if recipient else None,
            subject=subject,
            message=body,
            attachments=data.get("attachments"),
        )

        db.session.add(message)
        db.session.commit()

        log = AuditLog(
            action_type="procurement_order_message_sent",
            action_details=f"Message sent for order {order.id}",
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(message.to_dict()), 201

    @app.route("/api/orders/messages/<int:message_id>/reply", methods=["POST"])
    @jwt_required
    @handle_errors
    def reply_to_order_message(message_id):
        parent_message = ProcurementOrderMessage.query.get_or_404(message_id)
        order = parent_message.order

        if not _user_can_access_order(request.current_user, order):
            return jsonify({"error": "You do not have access to this order"}), 403

        data = request.get_json() or {}
        body = data.get("message")
        if not body:
            raise ValidationError("Message content is required")

        recipient_id = data.get("recipient_id") or parent_message.sender_id
        if recipient_id == request.current_user.get("user_id"):
            recipient_id = parent_message.recipient_id

        if recipient_id == request.current_user.get("user_id"):
            raise ValidationError("Recipient must be different from sender")

        recipient = _load_user(recipient_id, "Recipient") if recipient_id else None

        reply = ProcurementOrderMessage(
            order_id=order.id,
            sender_id=request.current_user.get("user_id"),
            recipient_id=recipient.id if recipient else None,
            subject=data.get("subject") or f"Re: {parent_message.subject}",
            message=body,
            parent_message_id=parent_message.id,
            attachments=data.get("attachments"),
        )

        db.session.add(reply)
        db.session.commit()

        log = AuditLog(
            action_type="procurement_order_message_reply",
            action_details=f"Reply sent for order {order.id}",
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reply.to_dict()), 201

    @app.route("/api/orders/<int:order_id>/mark-delivered", methods=["POST"])
    @orders_permission
    @handle_errors
    def mark_order_delivered(order_id):
        """Mark any procurement order as delivered/received"""
        order = ProcurementOrder.query.get_or_404(order_id)

        # Only allow marking as delivered if order is in an open status
        if order.status not in ["new", "ordered", "shipped", "in_progress"]:
            return jsonify({"error": f"Cannot mark order as delivered when status is '{order.status}'"}), 400

        # Get optional received quantity from request
        data = request.get_json() or {}
        received_quantity = data.get("received_quantity")

        # Update order status to received
        order.status = "received"
        order.completed_date = get_current_time()

        # Add note about received quantity if provided
        if received_quantity is not None:
            quantity_note = f"\n\nReceived Quantity: {received_quantity} {order.unit or 'units'}"
            order.notes = (order.notes or "") + quantity_note

        # Log the action
        user_name = request.current_user.get("user_name", "Unknown user")
        log = AuditLog(
            action_type="order_delivered",
            action_details=f"Order '{order.title}' (ID: {order.id}) marked as delivered by {user_name}"
        )
        db.session.add(log)

        # Log user activity
        if hasattr(request, "current_user"):
            activity = UserActivity(
                user_id=request.current_user["user_id"],
                activity_type="order_delivered",
                description=f"Marked order '{order.title}' as delivered"
            )
            db.session.add(activity)

        db.session.commit()

        logger.info("Order marked as delivered", extra={"order_id": order.id, "user": user_name})
        return jsonify({
            "order": order.to_dict(),
            "message": "Order marked as delivered successfully"
        })

    @app.route("/api/orders/messages/<int:message_id>/read", methods=["PUT"])
    @jwt_required
    @handle_errors
    def mark_order_message_read(message_id):
        message = ProcurementOrderMessage.query.get_or_404(message_id)

        if message.recipient_id and message.recipient_id != request.current_user.get("user_id"):
            return jsonify({"error": "You can only mark your messages as read"}), 403

        if not message.is_read:
            message.is_read = True
            message.read_date = get_current_time()
            db.session.commit()

        return jsonify(message.to_dict())
