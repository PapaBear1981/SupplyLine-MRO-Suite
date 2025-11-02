"""
Barcode Generation Service

This module provides functions to generate high-quality SVG barcodes for labels.
Supports both 1D barcodes (CODE128, EAN, etc.) and 2D codes (QR codes).

All barcodes are generated as SVG for crisp, scalable vector graphics suitable
for professional printing on standard printers and future Zebra printer compatibility.
"""

import io
from typing import Literal, Optional

import barcode
from barcode.writer import SVGWriter
import segno


# Barcode type definitions
BarcodeType = Literal["CODE128", "CODE39", "EAN13", "EAN8", "UPCA"]


def generate_1d_barcode_svg(
    data: str,
    barcode_type: BarcodeType = "CODE128",
    module_width: float = 0.3,
    module_height: float = 15.0,
    font_size: int = 10,
    text_distance: float = 5.0,
    quiet_zone: float = 6.5,
) -> str:
    """
    Generate a 1D barcode as SVG string.

    Args:
        data: The data to encode in the barcode
        barcode_type: Type of barcode (CODE128, CODE39, EAN13, etc.)
        module_width: Width of the narrowest bar in mm
        module_height: Height of the barcode in mm
        font_size: Font size for the human-readable text
        text_distance: Distance between barcode and text in mm
        quiet_zone: Size of the quiet zone (margin) in mm

    Returns:
        SVG string representation of the barcode

    Raises:
        ValueError: If the data is invalid for the specified barcode type
    """
    try:
        # Create barcode instance
        barcode_class = barcode.get_barcode_class(barcode_type.lower())

        # Configure SVG writer with professional settings
        writer = SVGWriter()
        writer.set_options({
            "module_width": module_width,
            "module_height": module_height,
            "font_size": font_size,
            "text_distance": text_distance,
            "quiet_zone": quiet_zone,
            "write_text": True,  # Include human-readable text
        })

        # Generate barcode
        barcode_instance = barcode_class(data, writer=writer)

        # Render to SVG
        output = io.BytesIO()
        barcode_instance.write(output)

        # Return SVG as string
        svg_content = output.getvalue().decode("utf-8")
        return svg_content

    except Exception as e:
        raise ValueError(f"Failed to generate {barcode_type} barcode: {str(e)}") from e


def generate_qr_code_svg(
    data: str,
    scale: int = 10,
    border: int = 4,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    dark_color: str = "#000000",
    light_color: str = "#FFFFFF",
) -> str:
    """
    Generate a QR code as SVG string.

    Args:
        data: The data to encode in the QR code (URL, text, etc.)
        scale: Size of each QR code module (pixel equivalent)
        border: Size of the quiet zone border (in modules)
        error_correction: Error correction level:
            - L: ~7% correction
            - M: ~15% correction (default)
            - Q: ~25% correction
            - H: ~30% correction
        dark_color: Color for dark modules (hex color)
        light_color: Color for light modules (hex color)

    Returns:
        SVG string representation of the QR code

    Raises:
        ValueError: If the data is too large or invalid
    """
    try:
        # Create QR code with specified error correction
        qr = segno.make(data, error=error_correction.lower(), boost_error=False)

        # Render to SVG
        output = io.BytesIO()
        qr.save(
            output,
            kind="svg",
            scale=scale,
            border=border,
            dark=dark_color,
            light=light_color,
            xmldecl=False,  # Don't include XML declaration
            svgns=True,  # Include SVG namespace
            svgclass="qr-code",  # Add CSS class for styling
            lineclass="qr-line",  # Add CSS class for lines
        )

        # Return SVG as string
        svg_content = output.getvalue().decode("utf-8")
        return svg_content

    except Exception as e:
        raise ValueError(f"Failed to generate QR code: {str(e)}") from e


def get_barcode_config_for_size(label_size: str) -> dict:
    """
    Get barcode configuration parameters optimized for a specific label size.

    Args:
        label_size: Label size identifier (4x6, 3x4, 2x4, 2x2)

    Returns:
        Dictionary with barcode configuration parameters
    """
    configs = {
        "4x6": {
            "1d": {
                "module_width": 0.35,
                "module_height": 18.0,
                "font_size": 12,
                "text_distance": 5.0,
                "quiet_zone": 8.0,
            },
            "qr": {
                "scale": 12,
                "border": 4,
                "error_correction": "M",
            },
        },
        "3x4": {
            "1d": {
                "module_width": 0.3,
                "module_height": 14.0,
                "font_size": 10,
                "text_distance": 4.0,
                "quiet_zone": 6.5,
            },
            "qr": {
                "scale": 10,
                "border": 3,
                "error_correction": "M",
            },
        },
        "2x4": {
            "1d": {
                "module_width": 0.25,
                "module_height": 12.0,
                "font_size": 8,
                "text_distance": 3.0,
                "quiet_zone": 5.0,
            },
            "qr": {
                "scale": 8,
                "border": 2,
                "error_correction": "M",
            },
        },
        "2x2": {
            "1d": {
                "module_width": 0.2,
                "module_height": 8.0,
                "font_size": 7,
                "text_distance": 2.0,
                "quiet_zone": 4.0,
            },
            "qr": {
                "scale": 10,
                "border": 2,
                "error_correction": "H",  # Higher error correction for small labels
            },
        },
    }

    return configs.get(label_size, configs["4x6"])


def generate_barcode_for_label(
    data: str,
    label_size: str = "4x6",
    barcode_type: BarcodeType = "CODE128",
) -> str:
    """
    Generate a 1D barcode optimized for a specific label size.

    Args:
        data: The data to encode
        label_size: Label size (4x6, 3x4, 2x4, 2x2)
        barcode_type: Type of barcode to generate

    Returns:
        SVG string of the barcode
    """
    config = get_barcode_config_for_size(label_size)
    return generate_1d_barcode_svg(data, barcode_type, **config["1d"])


def generate_qr_code_for_label(
    data: str,
    label_size: str = "4x6",
) -> str:
    """
    Generate a QR code optimized for a specific label size.

    Args:
        data: The data to encode (typically a URL)
        label_size: Label size (4x6, 3x4, 2x4, 2x2)

    Returns:
        SVG string of the QR code
    """
    config = get_barcode_config_for_size(label_size)
    return generate_qr_code_svg(data, **config["qr"])

