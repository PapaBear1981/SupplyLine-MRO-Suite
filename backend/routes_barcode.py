"""
Barcode Label Generation Routes

Unified API endpoints for generating professional PDF labels for all item types.
Supports tools, chemicals, expendables, and kit items with multiple label sizes.
"""

import io

from flask import Blueprint, jsonify, request, send_file
from sqlalchemy.orm import joinedload

from auth.jwt_manager import jwt_required
from models import Chemical, Expendable, Tool
from utils.label_pdf_service import (
    generate_chemical_label_pdf,
    generate_expendable_label_pdf,
    generate_tool_label_pdf,
)


barcode_bp = Blueprint("barcode", __name__)


@barcode_bp.route("/api/barcode/tool/<int:tool_id>", methods=["GET"])
@jwt_required
def generate_tool_barcode_label(tool_id):
    """
    Generate a PDF barcode label for a tool.

    Query Parameters:
        - label_size: Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
        - code_type: Code type (barcode, qrcode) - default: barcode

    Returns:
        PDF file for printing
    """
    try:
        # Get tool
        tool = Tool.query.get_or_404(tool_id)

        # Get query parameters
        label_size = request.args.get("label_size", "4x6")
        code_type = request.args.get("code_type", "barcode")

        # Validate parameters
        if label_size not in ["4x6", "3x4", "2x4", "2x2"]:
            return jsonify({"error": "Invalid label size"}), 400
        if code_type not in ["barcode", "qrcode"]:
            return jsonify({"error": "Invalid code type"}), 400

        # Generate PDF
        pdf_bytes = generate_tool_label_pdf(
            tool=tool,
            label_size=label_size,
            code_type=code_type,
        )

        # Return PDF
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"tool-{tool.tool_number}-label.pdf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@barcode_bp.route("/api/barcode/chemical/<int:chemical_id>", methods=["GET"])
@jwt_required
def generate_chemical_barcode_label(chemical_id):
    """
    Generate a PDF barcode label for a chemical.

    Query Parameters:
        - label_size: Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
        - code_type: Code type (barcode, qrcode) - default: barcode
        - is_transfer: Whether this is a transfer label - default: false
        - parent_lot_number: Parent lot number (for transfers)
        - destination: Destination name (for transfers)

    Returns:
        PDF file for printing
    """
    try:
        # Get chemical with eager loading of issuance relationship for issued child lots
        chemical = Chemical.query.options(
            joinedload(Chemical.issuance)
        ).get_or_404(chemical_id)

        # Get query parameters
        label_size = request.args.get("label_size", "4x6")
        code_type = request.args.get("code_type", "barcode")
        is_transfer = request.args.get("is_transfer", "false").lower() == "true"
        parent_lot_number = request.args.get("parent_lot_number")
        destination = request.args.get("destination")

        # Validate parameters
        if label_size not in ["4x6", "3x4", "2x4", "2x2"]:
            return jsonify({"error": "Invalid label size"}), 400
        if code_type not in ["barcode", "qrcode"]:
            return jsonify({"error": "Invalid code type"}), 400

        # Build transfer data if applicable
        transfer_data = None
        if is_transfer:
            transfer_data = {
                "parent_lot_number": parent_lot_number,
                "destination": destination,
                "quantity": chemical.quantity,
                "unit": chemical.unit,
            }

        # Generate PDF
        pdf_bytes = generate_chemical_label_pdf(
            chemical=chemical,
            label_size=label_size,
            code_type=code_type,
            is_transfer=is_transfer,
            transfer_data=transfer_data,
        )

        # Return PDF
        filename = f"chemical-{chemical.part_number}-{chemical.lot_number}-label.pdf"
        if is_transfer:
            filename = f"transfer-{chemical.lot_number}-label.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=filename,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@barcode_bp.route("/api/barcode/expendable/<int:expendable_id>", methods=["GET"])
@jwt_required
def generate_expendable_barcode_label(expendable_id):
    """
    Generate a PDF barcode label for an expendable.

    Query Parameters:
        - label_size: Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
        - code_type: Code type (barcode, qrcode) - default: barcode

    Returns:
        PDF file for printing
    """
    try:
        # Get expendable
        expendable = Expendable.query.get_or_404(expendable_id)

        # Get query parameters
        label_size = request.args.get("label_size", "4x6")
        code_type = request.args.get("code_type", "barcode")

        # Validate parameters
        if label_size not in ["4x6", "3x4", "2x4", "2x2"]:
            return jsonify({"error": "Invalid label size"}), 400
        if code_type not in ["barcode", "qrcode"]:
            return jsonify({"error": "Invalid code type"}), 400

        # Generate PDF
        pdf_bytes = generate_expendable_label_pdf(
            expendable=expendable,
            label_size=label_size,
            code_type=code_type,
        )

        # Return PDF
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"expendable-{expendable.part_number}-label.pdf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@barcode_bp.route("/api/barcode/kit-item/<int:kit_id>/<int:item_id>", methods=["GET"])
@jwt_required
def generate_kit_item_barcode_label(kit_id, item_id):
    """
    Generate a PDF barcode label for a kit item.

    Query Parameters:
        - label_size: Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
        - code_type: Code type (barcode, qrcode) - default: barcode
        - item_type: Type of item (tool, chemical, expendable) - required

    Returns:
        PDF file for printing
    """
    try:
        # Get query parameters
        label_size = request.args.get("label_size", "4x6")
        code_type = request.args.get("code_type", "barcode")
        item_type = request.args.get("item_type")

        # Validate parameters
        if label_size not in ["4x6", "3x4", "2x4", "2x2"]:
            return jsonify({"error": "Invalid label size"}), 400
        if code_type not in ["barcode", "qrcode"]:
            return jsonify({"error": "Invalid code type"}), 400
        if item_type not in ["tool", "chemical", "expendable"]:
            return jsonify({"error": "Invalid or missing item_type parameter"}), 400

        # Get the actual item based on type
        if item_type == "tool":
            item = Tool.query.get_or_404(item_id)
            pdf_bytes = generate_tool_label_pdf(item, label_size, code_type)
            filename = f"kit-{kit_id}-tool-{item.tool_number}-label.pdf"
        elif item_type == "chemical":
            # Eager load issuance relationship for issued child lots
            item = Chemical.query.options(
                joinedload(Chemical.issuance)
            ).get_or_404(item_id)
            pdf_bytes = generate_chemical_label_pdf(item, label_size, code_type)
            filename = f"kit-{kit_id}-chemical-{item.part_number}-label.pdf"
        else:  # expendable
            item = Expendable.query.get_or_404(item_id)
            pdf_bytes = generate_expendable_label_pdf(item, label_size, code_type)
            filename = f"kit-{kit_id}-expendable-{item.part_number}-label.pdf"

        # Return PDF
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=filename,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@barcode_bp.route("/api/barcode/label-sizes", methods=["GET"])
@jwt_required
def get_label_sizes():
    """
    Get available label sizes and their configurations.

    Returns:
        JSON object with label size information
    """
    from utils.label_config import LABEL_SIZES

    sizes = {}
    for size_id, config in LABEL_SIZES.items():
        sizes[size_id] = {
            "id": size_id,
            "name": config["name"],
            "dimensions": config["dimensions"],
            "max_fields": config["max_fields"],
        }

    return jsonify(sizes)

