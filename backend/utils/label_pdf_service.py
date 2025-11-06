"""
Label PDF Generation Service

This module provides functions to generate professional PDF labels using
Jinja2 templates and WeasyPrint. Supports multiple label sizes and item types.
"""

import os
from typing import Any, Literal

from flask import current_app
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .barcode_service import generate_barcode_for_label, generate_qr_code_for_label
from .label_config import get_label_template_context


def _get_weasyprint():
    """Lazy import WeasyPrint to avoid GTK dependency issues."""
    try:
        from weasyprint import CSS, HTML
        return HTML, CSS
    except (ImportError, OSError) as e:
        raise RuntimeError(
            "WeasyPrint is not available. This is likely due to missing GTK libraries on Windows. "
            "PDF label generation requires WeasyPrint with GTK support. "
            f"Error: {e}"
        ) from e


# Type definitions
ItemType = Literal["tool", "chemical", "expendable", "kit_item"]
CodeType = Literal["barcode", "qrcode"]


def get_template_environment() -> Environment:
    """
    Get configured Jinja2 environment for label templates.

    Returns:
        Configured Jinja2 Environment instance
    """
    # Get template directory path
    template_dir = os.path.join(
        current_app.root_path, "templates", "labels"
    )

    # Create and return Jinja2 environment
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_label_pdf(
    item_title: str,
    barcode_data: str,
    fields: list[dict[str, str]],
    label_size: str = "4x6",
    code_type: CodeType = "barcode",
    is_transfer: bool = False,
    warning_text: str | None = None,
    barcode_type: str = "CODE128",
) -> bytes:
    """
    Generate a professional PDF label.

    Args:
        item_title: Title to display on the label (e.g., "CHEM-001 - LOT-12345")
        barcode_data: Data to encode in the barcode/QR code
        fields: List of field dictionaries with 'label' and 'value' keys
        label_size: Label size (4x6, 3x4, 2x4, 2x2)
        code_type: Type of code to generate (barcode or qrcode)
        is_transfer: Whether this is a transfer label
        warning_text: Optional warning text to display
        barcode_type: Type of 1D barcode (CODE128, CODE39, etc.)

    Returns:
        PDF file as bytes

    Raises:
        ValueError: If invalid parameters are provided
        RuntimeError: If PDF generation fails
    """
    try:
        # Generate barcode/QR code SVG
        if code_type == "qrcode":
            barcode_svg = generate_qr_code_for_label(barcode_data, label_size)
        else:
            barcode_svg = generate_barcode_for_label(
                barcode_data, label_size, barcode_type
            )

        # Get template context
        context = get_label_template_context(
            label_size=label_size,
            item_title=item_title,
            barcode_svg=barcode_svg,
            fields=fields,
            is_transfer=is_transfer,
            warning_text=warning_text,
        )

        # Load and render template
        env = get_template_environment()
        template = env.get_template("base_label.html")
        html_content = template.render(**context)

        # Generate PDF using WeasyPrint (lazy loaded)
        html_class, _ = _get_weasyprint()
        html = html_class(string=html_content)
        pdf_bytes = html.write_pdf()

        if pdf_bytes is None:
            raise RuntimeError("PDF generation returned None")

        return pdf_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to generate label PDF: {e!s}") from e


def generate_tool_label_pdf(
    tool: Any,
    label_size: str = "4x6",
    code_type: CodeType = "barcode",
) -> bytes:
    """
    Generate a PDF label for a tool.

    Args:
        tool: Tool model instance
        label_size: Label size (4x6, 3x4, 2x4, 2x2)
        code_type: Type of code to generate

    Returns:
        PDF file as bytes
    """
    # Generate barcode data
    tool_number = tool.tool_number or ""
    if tool.lot_number:
        barcode_data = f"{tool_number}-LOT-{tool.lot_number}"
    else:
        barcode_data = f"{tool_number}-{tool.serial_number or ''}"

    # Build title
    title = f"{tool.tool_number}"
    if tool.lot_number:
        title += f" - LOT {tool.lot_number}"
    elif tool.serial_number:
        title += f" - SN {tool.serial_number}"

    # Build fields
    fields = [
        {"label": "Tool Number", "value": tool.tool_number or "N/A"},
        {"label": "Description", "value": tool.description or "N/A"},
        {"label": "Location", "value": tool.location or "N/A"},
        {"label": "Status", "value": tool.status or "N/A"},
    ]

    if tool.lot_number:
        fields.append({"label": "Lot Number", "value": tool.lot_number})
    if tool.serial_number:
        fields.append({"label": "Serial Number", "value": tool.serial_number})
    if tool.category:
        fields.append({"label": "Category", "value": tool.category})
    if tool.condition:
        fields.append({"label": "Condition", "value": tool.condition})
    if hasattr(tool, "created_at") and tool.created_at:
        fields.append({"label": "Date Added", "value": tool.created_at.strftime("%Y-%m-%d")})

    return generate_label_pdf(
        item_title=title,
        barcode_data=barcode_data,
        fields=fields,
        label_size=label_size,
        code_type=code_type,
    )


def generate_chemical_label_pdf(
    chemical: Any,
    label_size: str = "4x6",
    code_type: CodeType = "barcode",
    is_transfer: bool = False,
    transfer_data: dict[str, Any] | None = None,
) -> bytes:
    """
    Generate a PDF label for a chemical.

    Args:
        chemical: Chemical model instance
        label_size: Label size (4x6, 3x4, 2x4, 2x2)
        code_type: Type of code to generate
        is_transfer: Whether this is a transfer label
        transfer_data: Optional transfer metadata

    Returns:
        PDF file as bytes
    """
    # Generate barcode data
    part_number = chemical.part_number or ""
    lot_number = chemical.lot_number or ""
    exp_date = chemical.expiration_date.strftime("%Y%m%d") if chemical.expiration_date else "NOEXP"
    barcode_data = f"{part_number}-{lot_number}-{exp_date}"

    # Build title
    title = f"{chemical.part_number} - {chemical.lot_number}"

    # Build fields
    fields = [
        {"label": "Part Number", "value": chemical.part_number or "N/A"},
        {"label": "Lot Number", "value": chemical.lot_number or "N/A"},
        {"label": "Description", "value": chemical.description or "N/A"},
        {"label": "Manufacturer", "value": chemical.manufacturer or "N/A"},
        {"label": "Quantity", "value": f"{chemical.quantity} {chemical.unit or 'each'}" if chemical.quantity is not None else "N/A"},
        {"label": "Location", "value": chemical.location or "N/A"},
        {"label": "Status", "value": chemical.status or "N/A"},
    ]

    if chemical.expiration_date:
        fields.append({"label": "Expiration Date", "value": chemical.expiration_date.strftime("%Y-%m-%d")})
    if chemical.date_added:
        fields.append({"label": "Date Added", "value": chemical.date_added.strftime("%Y-%m-%d")})

    # Add transfer-specific fields
    warning_text = None
    if is_transfer and transfer_data:
        if transfer_data.get("parent_lot_number"):
            fields.append({"label": "Parent Lot", "value": transfer_data["parent_lot_number"]})
        if transfer_data.get("destination"):
            fields.append({"label": "Destination", "value": transfer_data["destination"]})
        if transfer_data.get("transfer_date"):
            transfer_date = transfer_data["transfer_date"]
            if hasattr(transfer_date, "strftime"):
                date_str = transfer_date.strftime("%Y-%m-%d")
            else:
                date_str = str(transfer_date)
            fields.append({"label": "Transfer Date", "value": date_str})

        warning_text = "PARTIAL TRANSFER - NEW LOT NUMBER"

    return generate_label_pdf(
        item_title=title,
        barcode_data=barcode_data,
        fields=fields,
        label_size=label_size,
        code_type=code_type,
        is_transfer=is_transfer,
        warning_text=warning_text,
    )


def generate_expendable_label_pdf(
    expendable: Any,
    label_size: str = "4x6",
    code_type: CodeType = "barcode",
) -> bytes:
    """
    Generate a PDF label for an expendable.

    Args:
        expendable: Expendable model instance
        label_size: Label size (4x6, 3x4, 2x4, 2x2)
        code_type: Type of code to generate

    Returns:
        PDF file as bytes
    """
    # Generate barcode data
    part_number = expendable.part_number or ""
    if expendable.lot_number:
        barcode_data = f"{part_number}-LOT-{expendable.lot_number}"
    else:
        barcode_data = f"{part_number}-SN-{expendable.serial_number or ''}"

    # Build title
    title = f"{expendable.part_number}"
    if expendable.lot_number:
        title += f" - LOT {expendable.lot_number}"
    elif expendable.serial_number:
        title += f" - SN {expendable.serial_number}"

    # Build fields
    fields = [
        {"label": "Part Number", "value": expendable.part_number or "N/A"},
        {"label": "Description", "value": expendable.description or "N/A"},
        {"label": "Quantity", "value": f"{expendable.quantity} {expendable.unit}" if expendable.quantity else "N/A"},
        {"label": "Location", "value": expendable.location or "N/A"},
        {"label": "Category", "value": expendable.category or "N/A"},
    ]

    if expendable.lot_number:
        fields.append({"label": "Lot Number", "value": expendable.lot_number})
    if expendable.serial_number:
        fields.append({"label": "Serial Number", "value": expendable.serial_number})
    if expendable.date_added:
        fields.append({"label": "Date Added", "value": expendable.date_added.strftime("%Y-%m-%d")})

    return generate_label_pdf(
        item_title=title,
        barcode_data=barcode_data,
        fields=fields,
        label_size=label_size,
        code_type=code_type,
    )

