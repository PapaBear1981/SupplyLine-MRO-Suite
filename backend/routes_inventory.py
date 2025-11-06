"""
Routes for Inventory Management - Lot/Serial Number Tracking

This module provides API endpoints for:
- Lot number auto-generation
- Transaction history retrieval
- Comprehensive item detail with transaction history
"""

import logging

from flask import jsonify, request

from auth import jwt_required
from models import LotNumberSequence, db
from utils.error_handler import ValidationError, handle_errors
from utils.transaction_helper import get_item_detail_with_transactions, get_item_transactions


logger = logging.getLogger(__name__)


def register_inventory_routes(app):
    """Register all inventory-related routes"""

    # ==================== Lot Number Generation ====================

    @app.route("/api/lot-numbers/generate", methods=["POST"])
    @jwt_required
    @handle_errors
    def generate_lot_number():
        """
        Generate a unique lot number in format LOT-YYMMDD-XXXX.

        Request body (optional):
            {
                "override": "CUSTOM-LOT-NUMBER"  # Optional: Use custom lot number instead
            }

        Returns:
            {
                "lot_number": "LOT-251014-0001",
                "generated": true,
                "message": "Lot number generated successfully"
            }
        """
        data = request.get_json(silent=True) or {}

        # Check if user wants to override with custom lot number
        if data.get("override"):
            custom_lot = data["override"].strip()
            if not custom_lot:
                raise ValidationError("Override lot number cannot be empty")

            return jsonify({
                "lot_number": custom_lot,
                "generated": False,
                "message": "Using custom lot number"
            }), 200

        # Generate new lot number
        try:
            lot_number = LotNumberSequence.generate_lot_number()
            db.session.commit()

            logger.info(f"Generated lot number: {lot_number}")

            return jsonify({
                "lot_number": lot_number,
                "generated": True,
                "message": "Lot number generated successfully"
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating lot number: {e!s}")
            raise ValidationError(f"Failed to generate lot number: {e!s}")


    # ==================== Transaction History ====================

    @app.route("/api/inventory/<item_type>/<int:item_id>/transactions", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_inventory_transactions(item_type, item_id):
        """
        Get transaction history for an inventory item.

        Path parameters:
            item_type: Type of item (tool, chemical, expendable, kit_item)
            item_id: ID of the item

        Query parameters:
            limit: Maximum number of transactions to return (default: 100)
            offset: Offset for pagination (default: 0)

        Returns:
            {
                "item_type": "tool",
                "item_id": 123,
                "transactions": [...],
                "total_count": 45,
                "limit": 100,
                "offset": 0
            }
        """
        # Validate item type
        valid_types = ["tool", "chemical", "expendable", "kit_item"]
        if item_type not in valid_types:
            raise ValidationError(f'Invalid item_type. Must be one of: {", ".join(valid_types)}')

        # Get pagination parameters
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        # Validate pagination
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValidationError("Offset must be non-negative")

        # Get transactions
        transactions = get_item_transactions(item_type, item_id, limit=limit, offset=offset)

        # Get total count
        from models import InventoryTransaction
        total_count = InventoryTransaction.query.filter_by(
            item_type=item_type,
            item_id=item_id
        ).count()

        return jsonify({
            "item_type": item_type,
            "item_id": item_id,
            "transactions": transactions,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }), 200


    # ==================== Item Detail with Transactions ====================

    @app.route("/api/inventory/<item_type>/<int:item_id>/detail", methods=["GET"])
    @jwt_required
    @handle_errors
    def get_inventory_item_detail(item_type, item_id):
        """
        Get comprehensive item detail including transaction history.
        This endpoint is used for the item detail modal.

        Path parameters:
            item_type: Type of item (tool, chemical, expendable, kit_item)
            item_id: ID of the item

        Returns:
            {
                "item_type": "tool",
                "item_id": 123,
                "part_number": "T-12345",
                "description": "Torque Wrench",
                "serial_number": "SN-001",
                "lot_number": "LOT-251014-0001",
                "location": "Tool Crib A",
                "quantity": 1,
                "status": "available",
                "created_at": "2025-01-01T00:00:00",
                "transactions": [...],
                "transaction_count": 15
            }
        """
        # Validate item type
        valid_types = ["tool", "chemical", "expendable", "kit_item"]
        if item_type not in valid_types:
            raise ValidationError(f'Invalid item_type. Must be one of: {", ".join(valid_types)}')

        # Get item detail with transactions
        item_detail = get_item_detail_with_transactions(item_type, item_id)

        if not item_detail:
            return jsonify({
                "error": f"{item_type.capitalize()} with ID {item_id} not found"
            }), 404

        # Add item_type to response
        item_detail["item_type"] = item_type

        return jsonify(item_detail), 200


    # ==================== Batch Transaction Recording ====================

    @app.route("/api/inventory/transactions/batch", methods=["POST"])
    @jwt_required
    @handle_errors
    def create_batch_transactions():
        """
        Create multiple transaction records in a single request.
        Useful for bulk operations.

        Request body:
            {
                "transactions": [
                    {
                        "item_type": "tool",
                        "item_id": 123,
                        "transaction_type": "adjustment",
                        "quantity_change": 1.0,
                        "notes": "Found missing tool"
                    },
                    ...
                ]
            }

        Returns:
            {
                "created_count": 5,
                "message": "Successfully created 5 transactions"
            }
        """
        from utils.transaction_helper import record_transaction

        data = request.get_json()
        if not data or "transactions" not in data:
            raise ValidationError('Request must include "transactions" array')

        transactions_data = data["transactions"]
        if not isinstance(transactions_data, list):
            raise ValidationError('"transactions" must be an array')

        if len(transactions_data) == 0:
            raise ValidationError("At least one transaction is required")

        if len(transactions_data) > 100:
            raise ValidationError("Maximum 100 transactions per batch")

        # Get current user
        user_id = request.current_user["user_id"]

        created_count = 0
        try:
            for trans_data in transactions_data:
                # Validate required fields
                required_fields = ["item_type", "item_id", "transaction_type"]
                for field in required_fields:
                    if field not in trans_data:
                        raise ValidationError(f"Transaction missing required field: {field}")

                # Create transaction
                record_transaction(
                    item_type=trans_data["item_type"],
                    item_id=trans_data["item_id"],
                    transaction_type=trans_data["transaction_type"],
                    user_id=user_id,
                    quantity_change=trans_data.get("quantity_change"),
                    location_from=trans_data.get("location_from"),
                    location_to=trans_data.get("location_to"),
                    reference_number=trans_data.get("reference_number"),
                    notes=trans_data.get("notes"),
                    lot_number=trans_data.get("lot_number"),
                    serial_number=trans_data.get("serial_number")
                )
                created_count += 1

            db.session.commit()

            logger.info(f"Created {created_count} transactions in batch")

            return jsonify({
                "created_count": created_count,
                "message": f"Successfully created {created_count} transactions"
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating batch transactions: {e!s}")
            raise


    logger.info("Inventory routes registered successfully")
