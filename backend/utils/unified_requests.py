"""Unified request system utilities for creating requests from different sources."""


from sqlalchemy import text

from models import RequestItem, UserRequest, db, get_current_time


def generate_request_number():
    """Generate a unique request number in format REQ-00001."""
    result = db.session.execute(
        text("SELECT MAX(CAST(SUBSTR(request_number, 5) AS INTEGER)) FROM user_requests WHERE request_number IS NOT NULL")
    ).scalar()
    next_number = (result or 0) + 1
    return f"REQ-{next_number:05d}"


def create_chemical_reorder_request(chemical, requested_quantity, requester_id, notes=None):
    """
    Create a UserRequest for a chemical reorder.

    Args:
        chemical: Chemical model instance
        requested_quantity: Quantity to reorder
        requester_id: ID of the user creating the request
        notes: Optional notes for the request

    Returns:
        UserRequest: The created request with its items
    """
    # Create the request
    title = f"Chemical Reorder: {chemical.part_number}"
    if chemical.description:
        title = f"{title} - {chemical.description[:100]}"

    description_parts = [
        "Automatic reorder request for chemical.",
        f"Lot Number: {chemical.lot_number}",
        f"Manufacturer: {chemical.manufacturer or 'N/A'}",
        f"Current Stock: {chemical.quantity} {chemical.unit}",
    ]
    if chemical.minimum_stock_level is not None:
        description_parts.append(f"Minimum Stock Level: {chemical.minimum_stock_level} {chemical.unit}")
    if chemical.is_expired():
        description_parts.append("Status: EXPIRED - Replacement needed")
    elif chemical.is_low_stock():
        description_parts.append("Status: LOW STOCK")

    request_description = "\n".join(description_parts)
    if notes:
        request_description += f"\n\nNotes: {notes}"

    # Determine priority based on stock status
    priority = "normal"
    if chemical.quantity <= 0:
        priority = "high"
    if chemical.is_expired():
        priority = "critical"

    user_request = UserRequest(
        title=title,
        description=request_description,
        priority=priority,
        status="new",
        requester_id=requester_id,
        notes=notes or "",
        needs_more_info=False,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    db.session.add(user_request)
    db.session.flush()  # Get the ID

    # Generate and assign request number
    user_request.request_number = generate_request_number()

    # Create the request item
    item_description = f"{chemical.description or chemical.part_number}"
    if chemical.lot_number:
        item_description += f" (Lot: {chemical.lot_number})"
    if chemical.manufacturer:
        item_description += f" - {chemical.manufacturer}"

    request_item = RequestItem(
        request_id=user_request.id,
        item_type="chemical",
        part_number=chemical.part_number,
        description=item_description,
        quantity=requested_quantity,
        unit=chemical.unit,
        status="pending",
        source_type="chemical_reorder",
        chemical_id=chemical.id,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    db.session.add(request_item)

    return user_request


def create_kit_reorder_request(kit, reorder_request, requester_id):
    """
    Create a UserRequest for a kit reorder.

    Args:
        kit: Kit model instance (or dict with kit info)
        reorder_request: KitReorderRequest model instance
        requester_id: ID of the user creating the request

    Returns:
        UserRequest: The created request with its items
    """
    # Handle both model instances and dicts
    if hasattr(kit, "name"):
        kit_name = kit.name
        kit_id = kit.id
    else:
        kit_name = kit.get("name", "Unknown Kit")
        kit_id = kit.get("id")

    # Create the request
    title = f"Kit Reorder: {reorder_request.part_number}"
    if reorder_request.description:
        title = f"{title} - {reorder_request.description[:80]}"

    description_parts = [
        f"Kit reorder request from {kit_name}.",
        f"Part Number: {reorder_request.part_number}",
        f"Description: {reorder_request.description}",
        f"Quantity Requested: {reorder_request.quantity_requested}",
    ]
    if reorder_request.notes:
        description_parts.append(f"Notes: {reorder_request.notes}")
    if hasattr(reorder_request, "is_automatic") and reorder_request.is_automatic:
        description_parts.append("Type: Automatic reorder (low stock detected)")

    request_description = "\n".join(description_parts)

    # Map kit priority to request priority
    priority_map = {
        "urgent": "critical",
        "high": "high",
        "medium": "normal",
        "low": "low",
    }
    priority = priority_map.get(reorder_request.priority, "normal")

    user_request = UserRequest(
        title=title,
        description=request_description,
        priority=priority,
        status="new",
        requester_id=requester_id,
        notes=reorder_request.notes or "",
        needs_more_info=False,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    db.session.add(user_request)
    db.session.flush()  # Get the ID

    # Generate and assign request number
    user_request.request_number = generate_request_number()

    # Create the request item
    request_item = RequestItem(
        request_id=user_request.id,
        item_type="expendable",  # Kit reorders are typically for expendables
        part_number=reorder_request.part_number,
        description=reorder_request.description,
        quantity=reorder_request.quantity_requested,
        unit="each",
        status="pending",
        source_type="kit_reorder",
        kit_id=kit_id,
        kit_reorder_request_id=reorder_request.id,
        created_at=get_current_time(),
        updated_at=get_current_time(),
    )
    db.session.add(request_item)

    return user_request


def update_request_item_status(source_type, source_id, new_status, **kwargs):
    """
    Update the status of a request item based on its source.

    Args:
        source_type: "chemical_reorder" or "kit_reorder"
        source_id: ID of the chemical or kit_reorder_request
        new_status: New status for the request item
        **kwargs: Additional fields to update (vendor, tracking_number, etc.)
    """
    if source_type == "chemical_reorder":
        item = RequestItem.query.filter_by(
            source_type="chemical_reorder",
            chemical_id=source_id
        ).first()
    elif source_type == "kit_reorder":
        item = RequestItem.query.filter_by(
            source_type="kit_reorder",
            kit_reorder_request_id=source_id
        ).first()
    else:
        return None

    if not item:
        return None

    item.status = new_status
    item.updated_at = get_current_time()

    # Update additional fields if provided
    if "vendor" in kwargs:
        item.vendor = kwargs["vendor"]
    if "tracking_number" in kwargs:
        item.tracking_number = kwargs["tracking_number"]
    if "ordered_date" in kwargs:
        item.ordered_date = kwargs["ordered_date"]
    if "expected_delivery_date" in kwargs:
        item.expected_delivery_date = kwargs["expected_delivery_date"]
    if "received_date" in kwargs:
        item.received_date = kwargs["received_date"]
    if "received_quantity" in kwargs:
        item.received_quantity = kwargs["received_quantity"]
    if "order_notes" in kwargs:
        item.order_notes = kwargs["order_notes"]

    # Update the parent request status
    if item.request:
        item.request.update_status_from_items()

    return item
