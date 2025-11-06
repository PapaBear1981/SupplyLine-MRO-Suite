"""
Label Configuration Module

Defines size-specific configurations for professional label printing.
Each configuration includes dimensions, styling, and field display rules.
"""

from datetime import datetime
from typing import Any


# Label size configurations
LABEL_SIZES = {
    "4x6": {
        "name": '4" × 6" (Standard Shipping Label)',
        "dimensions": {
            "width": "4in",
            "height": "6in",
        },
        "styling": {
            "padding": "0.15in",
            "header_padding": "0.25in 0.3in",
            "content_padding": "0.25in",
            "content_gap": "0.2in",
            "barcode_padding": "0.15in",
            "fields_gap": "0.12in",
            "field_padding": "0.12in",
            "footer_padding": "0.12in 0.25in",
            "warning_padding": "0.15in",
            "warning_margin": "0.12in",
            "logo_gap": "0.25in",
            "logo_size": "1.2rem",
            "company_name_size": "0.75rem",
            "title_size": "0.9rem",
            "field_label_size": "0.55rem",
            "field_value_size": "0.7rem",
            "warning_size": "0.75rem",
            "footer_size": "0.55rem",
            "fields_columns": "2",
        },
        "max_fields": 12,
        "priority_fields": "all",
        "hide_logo": False,
        "hide_title": False,
        "show_footer": True,
    },
    "3x4": {
        "name": '3" × 4" (Medium Label)',
        "dimensions": {
            "width": "3in",
            "height": "4in",
        },
        "styling": {
            "padding": "0.08in",
            "header_padding": "0.15in 0.2in",
            "content_padding": "0.15in",
            "content_gap": "0.12in",
            "barcode_padding": "0.12in",
            "fields_gap": "0.08in",
            "field_padding": "0.08in",
            "footer_padding": "0.08in 0.15in",
            "warning_padding": "0.12in",
            "warning_margin": "0.08in",
            "logo_gap": "0.15in",
            "logo_size": "1rem",
            "company_name_size": "0.6rem",
            "title_size": "0.75rem",
            "field_label_size": "0.5rem",
            "field_value_size": "0.6rem",
            "warning_size": "0.65rem",
            "footer_size": "0.48rem",
            "fields_columns": "2",
        },
        "max_fields": 8,
        "priority_fields": [
            "Part Number",
            "Tool Number",
            "Lot Number",
            "Serial Number",
            "Description",
            "Location",
            "Expiration Date",
            "Created Date",
        ],
        "hide_logo": False,
        "hide_title": False,
        "show_footer": True,
    },
    "2x4": {
        "name": '2" × 4" (Small Label)',
        "dimensions": {
            "width": "2in",
            "height": "4in",
        },
        "styling": {
            "padding": "0.06in",
            "header_padding": "0.12in 0.15in",
            "content_padding": "0.12in",
            "content_gap": "0.08in",
            "barcode_padding": "0.08in",
            "fields_gap": "0.06in",
            "field_padding": "0.06in",
            "footer_padding": "0.06in 0.12in",
            "warning_padding": "0.08in",
            "warning_margin": "0.06in",
            "logo_gap": "0.12in",
            "logo_size": "0.85rem",
            "company_name_size": "0.55rem",
            "title_size": "0.65rem",
            "field_label_size": "0.45rem",
            "field_value_size": "0.52rem",
            "warning_size": "0.55rem",
            "footer_size": "0.4rem",
            "fields_columns": "1",
        },
        "max_fields": 5,
        "priority_fields": [
            "Part Number",
            "Tool Number",
            "Lot Number",
            "Serial Number",
            "Description",
        ],
        "hide_logo": False,
        "hide_title": False,
        "show_footer": False,
    },
    "2x2": {
        "name": '2" × 2" (Compact Label)',
        "dimensions": {
            "width": "2in",
            "height": "2in",
        },
        "styling": {
            "padding": "0.04in",
            "header_padding": "0.08in 0.12in",
            "content_padding": "0.08in",
            "content_gap": "0.06in",
            "barcode_padding": "0.06in",
            "fields_gap": "0.04in",
            "field_padding": "0.04in",
            "footer_padding": "0.04in 0.08in",
            "warning_padding": "0.06in",
            "warning_margin": "0.04in",
            "logo_gap": "0.08in",
            "logo_size": "0.7rem",
            "company_name_size": "0.42rem",
            "title_size": "0.52rem",
            "field_label_size": "0.38rem",
            "field_value_size": "0.45rem",
            "warning_size": "0.48rem",
            "footer_size": "0.35rem",
            "fields_columns": "1",
        },
        "max_fields": 2,
        "priority_fields": [
            "Part Number",
            "Tool Number",
            "Lot Number",
            "Serial Number",
        ],
        "hide_logo": True,
        "hide_title": False,
        "show_footer": False,
    },
}


def filter_fields_for_label_size(
    fields: list[dict[str, str]], label_size: str
) -> list[dict[str, str]]:
    """
    Filter and prioritize fields based on label size constraints.

    Args:
        fields: List of field dictionaries with 'label' and 'value' keys
        label_size: Label size identifier (4x6, 3x4, 2x4, 2x2)

    Returns:
        Filtered list of fields appropriate for the label size
    """
    config = LABEL_SIZES.get(label_size, LABEL_SIZES["4x6"])
    max_fields = config["max_fields"]
    priority_fields = config["priority_fields"]

    # If showing all fields or we have fewer fields than max, return all
    if priority_fields == "all" or len(fields) <= max_fields:
        return fields

    # Filter based on priority
    prioritized = []
    remaining = []

    for field in fields:
        if field["label"] in priority_fields:
            prioritized.append(field)
        else:
            remaining.append(field)

    # Sort prioritized fields by their priority order
    prioritized.sort(key=lambda f: priority_fields.index(f["label"]))

    # Combine prioritized and remaining, then truncate to max_fields
    result = prioritized + remaining
    return result[:max_fields]


def get_label_template_context(
    label_size: str,
    item_title: str,
    barcode_svg: str,
    fields: list[dict[str, str]],
    is_transfer: bool = False,
    warning_text: str | None = None,
    footer_note: str = "SupplyLine MRO Suite",
) -> dict[str, Any]:
    """
    Generate template context for rendering a label.

    Args:
        label_size: Label size identifier (4x6, 3x4, 2x4, 2x2)
        item_title: Title to display on the label
        barcode_svg: SVG string of the barcode
        fields: List of field dictionaries
        is_transfer: Whether this is a transfer label
        warning_text: Optional warning text to display
        footer_note: Footer note text

    Returns:
        Dictionary of template context variables
    """
    config = LABEL_SIZES.get(label_size, LABEL_SIZES["4x6"])

    # Filter fields based on label size
    filtered_fields = filter_fields_for_label_size(fields, label_size)

    # Build context
    context = {
        "title": f"SupplyLine MRO - {item_title}",
        "page_width": config["dimensions"]["width"],
        "page_height": config["dimensions"]["height"],
        "item_title": item_title,
        "barcode_svg": barcode_svg,
        "fields": filtered_fields,
        "is_transfer": is_transfer,
        "warning_text": warning_text,
        "hide_logo": config["hide_logo"],
        "hide_title": config["hide_title"],
        "show_footer": config["show_footer"],
        "footer_note": footer_note,
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # Add all styling parameters
    context.update(config["styling"])

    return context

