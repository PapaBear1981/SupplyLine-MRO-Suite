"""
Transaction Helper Utilities

This module provides helper functions for recording inventory transactions
across all inventory types (tools, chemicals, expendables).
"""

from models import db, InventoryTransaction, Tool, Chemical
from models_kits import KitExpendable, KitItem
import logging

logger = logging.getLogger(__name__)


def record_transaction(item_type, item_id, transaction_type, user_id, **kwargs):
    """
    Record an inventory transaction.
    
    Args:
        item_type (str): Type of item ('tool', 'chemical', 'expendable', 'kit_item')
        item_id (int): ID of the item
        transaction_type (str): Type of transaction (receipt, issuance, transfer, etc.)
        user_id (int): ID of user performing the transaction
        **kwargs: Additional transaction details
            - quantity_change (float): Change in quantity
            - location_from (str): Source location
            - location_to (str): Destination location
            - reference_number (str): Work order, PO number, etc.
            - notes (str): Additional notes
            - lot_number (str): Lot number (if not auto-detected)
            - serial_number (str): Serial number (if not auto-detected)
    
    Returns:
        InventoryTransaction: Created transaction record
    """
    try:
        # Auto-detect lot/serial numbers if not provided
        lot_number = kwargs.get('lot_number')
        serial_number = kwargs.get('serial_number')
        
        if not lot_number and not serial_number:
            # Try to get from the item itself
            if item_type == 'tool':
                tool = Tool.query.get(item_id)
                if tool:
                    lot_number = tool.lot_number
                    serial_number = tool.serial_number
            elif item_type == 'chemical':
                chemical = Chemical.query.get(item_id)
                if chemical:
                    lot_number = chemical.lot_number
            elif item_type == 'expendable':
                expendable = KitExpendable.query.get(item_id)
                if expendable:
                    lot_number = expendable.lot_number
                    serial_number = expendable.serial_number
            elif item_type == 'kit_item':
                kit_item = KitItem.query.get(item_id)
                if kit_item:
                    lot_number = kit_item.lot_number
                    serial_number = kit_item.serial_number
        
        # Create transaction record
        transaction = InventoryTransaction.create_transaction(
            item_type=item_type,
            item_id=item_id,
            transaction_type=transaction_type,
            user_id=user_id,
            quantity_change=kwargs.get('quantity_change'),
            location_from=kwargs.get('location_from'),
            location_to=kwargs.get('location_to'),
            reference_number=kwargs.get('reference_number'),
            notes=kwargs.get('notes'),
            lot_number=lot_number,
            serial_number=serial_number
        )
        
        db.session.add(transaction)
        logger.info(f"Recorded {transaction_type} transaction for {item_type} {item_id}")
        
        return transaction
        
    except Exception as e:
        logger.error(f"Error recording transaction: {str(e)}")
        raise


def record_tool_checkout(tool_id, user_id, expected_return_date=None, notes=None):
    """Record a tool checkout transaction"""
    tool = Tool.query.get(tool_id)
    if not tool:
        raise ValueError(f"Tool {tool_id} not found")
    
    return record_transaction(
        item_type='tool',
        item_id=tool_id,
        transaction_type='checkout',
        user_id=user_id,
        quantity_change=-1.0,
        location_from=tool.location,
        location_to=f"Checked out to user {user_id}",
        reference_number=f"Expected return: {expected_return_date}" if expected_return_date else None,
        notes=notes
    )


def record_tool_return(tool_id, user_id, condition=None, notes=None):
    """Record a tool return transaction"""
    tool = Tool.query.get(tool_id)
    if not tool:
        raise ValueError(f"Tool {tool_id} not found")
    
    return record_transaction(
        item_type='tool',
        item_id=tool_id,
        transaction_type='return',
        user_id=user_id,
        quantity_change=1.0,
        location_from=f"Returned by user {user_id}",
        location_to=tool.location,
        notes=f"Condition: {condition}. {notes}" if condition else notes
    )


def record_chemical_issuance(chemical_id, user_id, quantity, hangar=None, purpose=None, work_order=None, recipient_id=None):
    """
    Record a chemical issuance transaction.

    Args:
        chemical_id: ID of the chemical
        user_id: ID of the user performing the issuance (authenticated user)
        quantity: Quantity issued
        hangar: Destination hangar
        purpose: Purpose of issuance
        work_order: Work order number
        recipient_id: ID of the user receiving the chemical (optional, for audit trail)
    """
    chemical = Chemical.query.get(chemical_id)
    if not chemical:
        raise ValueError(f"Chemical {chemical_id} not found")

    # Build notes with purpose and recipient info
    notes_parts = []
    if purpose:
        notes_parts.append(f"Purpose: {purpose}")
    if recipient_id and recipient_id != user_id:
        notes_parts.append(f"Recipient User ID: {recipient_id}")
    notes = ". ".join(notes_parts) if notes_parts else None

    return record_transaction(
        item_type='chemical',
        item_id=chemical_id,
        transaction_type='issuance',
        user_id=user_id,
        quantity_change=-quantity,
        location_from=chemical.location,
        location_to=hangar,
        reference_number=work_order,
        notes=notes
    )


def record_kit_item_transfer(item_type, item_id, user_id, from_location, to_location, quantity=None, reference=None, notes=None):
    """Record a kit item transfer transaction"""
    return record_transaction(
        item_type=item_type,
        item_id=item_id,
        transaction_type='transfer',
        user_id=user_id,
        quantity_change=quantity,
        location_from=from_location,
        location_to=to_location,
        reference_number=reference,
        notes=notes
    )


def record_kit_issuance(item_type, item_id, user_id, quantity, work_order=None, purpose=None, notes=None):
    """Record a kit item issuance transaction"""
    return record_transaction(
        item_type=item_type,
        item_id=item_id,
        transaction_type='kit_issuance',
        user_id=user_id,
        quantity_change=-quantity,
        reference_number=work_order,
        notes=f"Purpose: {purpose}. {notes}" if purpose else notes
    )


def record_inventory_adjustment(item_type, item_id, user_id, quantity_change, reason, notes=None):
    """Record an inventory adjustment transaction"""
    return record_transaction(
        item_type=item_type,
        item_id=item_id,
        transaction_type='adjustment',
        user_id=user_id,
        quantity_change=quantity_change,
        notes=f"Reason: {reason}. {notes}" if notes else f"Reason: {reason}"
    )


def record_item_receipt(item_type, item_id, user_id, quantity, location, po_number=None, notes=None):
    """Record an item receipt transaction"""
    return record_transaction(
        item_type=item_type,
        item_id=item_id,
        transaction_type='receipt',
        user_id=user_id,
        quantity_change=quantity,
        location_to=location,
        reference_number=po_number,
        notes=notes
    )


def validate_serial_number_uniqueness(part_number, serial_number, item_type, exclude_id=None):
    """
    Validate that a serial number is unique for a given part number.
    
    Args:
        part_number (str): Part number to check
        serial_number (str): Serial number to validate
        item_type (str): Type of item ('tool', 'expendable')
        exclude_id (int): ID to exclude from check (for updates)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not serial_number:
        return True, None
    
    if item_type == 'tool':
        query = Tool.query.filter_by(
            tool_number=part_number,
            serial_number=serial_number
        )
        if exclude_id:
            query = query.filter(Tool.id != exclude_id)
        
        if query.first():
            return False, f"Serial number {serial_number} already exists for tool number {part_number}"
    
    elif item_type == 'expendable':
        query = KitExpendable.query.filter_by(
            part_number=part_number,
            serial_number=serial_number
        )
        if exclude_id:
            query = query.filter(KitExpendable.id != exclude_id)
        
        if query.first():
            return False, f"Serial number {serial_number} already exists for part number {part_number}"
    
    return True, None


def get_item_transactions(item_type, item_id, limit=100, offset=0):
    """
    Get transaction history for an item.
    
    Args:
        item_type (str): Type of item
        item_id (int): ID of item
        limit (int): Maximum number of transactions to return
        offset (int): Offset for pagination
    
    Returns:
        list: List of transaction dictionaries
    """
    transactions = InventoryTransaction.query.filter_by(
        item_type=item_type,
        item_id=item_id
    ).order_by(
        InventoryTransaction.timestamp.desc()
    ).limit(limit).offset(offset).all()
    
    return [t.to_dict() for t in transactions]


def get_item_detail_with_transactions(item_type, item_id):
    """
    Get comprehensive item detail including transaction history.
    
    Args:
        item_type (str): Type of item
        item_id (int): ID of item
    
    Returns:
        dict: Item details with transaction history
    """
    item_data = None
    
    if item_type == 'tool':
        item = Tool.query.get(item_id)
        if item:
            item_data = item.to_dict()
    elif item_type == 'chemical':
        item = Chemical.query.get(item_id)
        if item:
            item_data = item.to_dict()
    elif item_type == 'expendable':
        item = KitExpendable.query.get(item_id)
        if item:
            item_data = item.to_dict()
    elif item_type == 'kit_item':
        item = KitItem.query.get(item_id)
        if item:
            item_data = item.to_dict()
    
    if not item_data:
        return None
    
    # Add transaction history
    item_data['transactions'] = get_item_transactions(item_type, item_id)
    item_data['transaction_count'] = len(item_data['transactions'])
    
    return item_data

