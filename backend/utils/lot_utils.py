"""
Utility functions for lot number management and splitting.
"""

import string

from models import Chemical


def generate_child_lot_number(parent_lot_number, sequence):
    """
    Generate a child lot number based on the parent lot number and sequence.

    Format: PARENT-A, PARENT-B, ..., PARENT-Z, PARENT-AA, PARENT-AB, etc.

    Args:
        parent_lot_number (str): The parent lot number
        sequence (int): The sequence number (0-based)

    Returns:
        str: The generated child lot number

    Examples:
        >>> generate_child_lot_number("LOT001", 0)
        'LOT001-A'
        >>> generate_child_lot_number("LOT001", 1)
        'LOT001-B'
        >>> generate_child_lot_number("LOT001", 25)
        'LOT001-Z'
        >>> generate_child_lot_number("LOT001", 26)
        'LOT001-AA'
    """
    # Convert sequence to letter suffix (A, B, C, ..., Z, AA, AB, ...)
    suffix = ""
    num = sequence

    while True:
        suffix = string.ascii_uppercase[num % 26] + suffix
        num = num // 26
        if num == 0:
            break
        num -= 1  # Adjust for 0-based indexing

    return f"{parent_lot_number}-{suffix}"


def get_next_child_lot_number(parent_chemical):
    """
    Get the next available child lot number for a parent chemical.
    Increments the lot_sequence counter and generates the child lot number.

    Args:
        parent_chemical (Chemical): The parent chemical object

    Returns:
        tuple: (child_lot_number, sequence) - The generated child lot number and its sequence
    """
    # Get current sequence (defaults to 0 if None)
    current_sequence = parent_chemical.lot_sequence or 0

    # Generate child lot number
    child_lot_number = generate_child_lot_number(parent_chemical.lot_number, current_sequence)

    # Check if this lot number already exists (shouldn't happen, but safety check)
    existing = Chemical.query.filter_by(lot_number=child_lot_number).first()
    if existing:
        # If it exists, increment sequence and try again
        current_sequence += 1
        child_lot_number = generate_child_lot_number(parent_chemical.lot_number, current_sequence)

    # Increment the parent's lot_sequence counter
    parent_chemical.lot_sequence = current_sequence + 1

    return child_lot_number, current_sequence


def create_child_chemical(parent_chemical, quantity, destination_warehouse_id=None, destination_kit_id=None):
    """
    Create a child chemical from a parent chemical for partial transfer.

    Args:
        parent_chemical (Chemical): The parent chemical to split from
        quantity (int): The quantity to transfer to the child
        destination_warehouse_id (int, optional): Destination warehouse ID
        destination_kit_id (int, optional): Destination kit ID (for kit transfers)

    Returns:
        Chemical: The newly created child chemical

    Raises:
        ValueError: If quantity is invalid or exceeds available quantity
    """
    # Validate quantity
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")

    if quantity > parent_chemical.quantity:
        raise ValueError(f"Cannot transfer {quantity} {parent_chemical.unit}. Only {parent_chemical.quantity} {parent_chemical.unit} available.")

    # Generate child lot number
    child_lot_number, _sequence = get_next_child_lot_number(parent_chemical)

    # Create the child chemical
    child_chemical = Chemical(
        part_number=parent_chemical.part_number,
        lot_number=child_lot_number,
        description=parent_chemical.description,
        manufacturer=parent_chemical.manufacturer,
        quantity=quantity,
        unit=parent_chemical.unit,
        location=parent_chemical.location,
        category=parent_chemical.category,
        status="available",
        warehouse_id=destination_warehouse_id,
        expiration_date=parent_chemical.expiration_date,
        minimum_stock_level=parent_chemical.minimum_stock_level,
        notes=f"Split from {parent_chemical.lot_number}",
        parent_lot_number=parent_chemical.lot_number,
        lot_sequence=0  # New child starts with sequence 0
    )

    # Reduce parent quantity
    parent_chemical.quantity -= quantity

    # Update parent status if depleted
    if parent_chemical.quantity == 0:
        parent_chemical.status = "depleted"

    return child_chemical


def get_lot_lineage(chemical):
    """
    Get the complete lineage of a chemical lot (parent and all children).

    Args:
        chemical (Chemical): The chemical to get lineage for

    Returns:
        dict: Dictionary containing parent and children information
    """
    result = {
        "current": chemical.to_dict(),
        "parent": None,
        "children": [],
        "siblings": []
    }

    # Get parent if exists
    if chemical.parent_lot_number:
        parent = Chemical.query.filter_by(lot_number=chemical.parent_lot_number).first()
        if parent:
            result["parent"] = parent.to_dict()

            # Get siblings (other children of the same parent)
            siblings = Chemical.query.filter(
                Chemical.parent_lot_number == chemical.parent_lot_number,
                Chemical.id != chemical.id
            ).all()
            result["siblings"] = [s.to_dict() for s in siblings]

    # Get children (lots split from this one)
    children = Chemical.query.filter_by(parent_lot_number=chemical.lot_number).all()
    result["children"] = [c.to_dict() for c in children]

    return result

