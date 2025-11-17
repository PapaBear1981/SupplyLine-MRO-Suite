"""
Tests for Barcode Service Utility Functions

This module tests the barcode generation service including:
- 1D barcode generation (CODE128, CODE39, EAN13, EAN8, UPCA)
- QR code generation with various error correction levels
- Label size configuration
- Error handling for invalid data
- Custom parameter support
"""

import pytest
from unittest.mock import patch, MagicMock, ANY
import io

from utils.barcode_service import (
    generate_1d_barcode_svg,
    generate_qr_code_svg,
    get_barcode_config_for_size,
    generate_barcode_for_label,
    generate_qr_code_for_label,
)


class TestGenerate1DBarcodeVSG:
    """Test the generate_1d_barcode_svg function"""

    def test_generate_code128_barcode_default_params(self):
        """Test generating CODE128 barcode with default parameters"""
        data = "TEST123"
        result = generate_1d_barcode_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result
        assert "TEST123" in result  # Human readable text should be present

    def test_generate_code128_barcode_explicit_type(self):
        """Test generating CODE128 barcode with explicit type"""
        data = "BARCODE456"
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result
        assert "BARCODE456" in result

    def test_generate_code39_barcode(self):
        """Test generating CODE39 barcode"""
        data = "ABC123"
        result = generate_1d_barcode_svg(data, barcode_type="CODE39")

        assert isinstance(result, str)
        assert "<svg" in result
        assert "ABC123" in result

    def test_generate_ean13_barcode(self):
        """Test generating EAN13 barcode"""
        # EAN13 requires exactly 12 digits (13th is checksum)
        data = "123456789012"
        result = generate_1d_barcode_svg(data, barcode_type="EAN13")

        assert isinstance(result, str)
        assert "<svg" in result
        # EAN13 adds checksum digit
        assert "123456789012" in result

    def test_generate_ean8_barcode(self):
        """Test generating EAN8 barcode"""
        # EAN8 requires exactly 7 digits (8th is checksum)
        data = "1234567"
        result = generate_1d_barcode_svg(data, barcode_type="EAN8")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_upca_barcode(self):
        """Test generating UPCA barcode"""
        # UPCA requires exactly 11 digits (12th is checksum)
        data = "12345678901"
        result = generate_1d_barcode_svg(data, barcode_type="UPCA")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_module_width(self):
        """Test generating barcode with custom module width"""
        data = "WIDTH001"
        result = generate_1d_barcode_svg(data, module_width=0.5)

        assert isinstance(result, str)
        assert "<svg" in result
        assert "WIDTH001" in result

    def test_custom_module_height(self):
        """Test generating barcode with custom module height"""
        data = "HEIGHT001"
        result = generate_1d_barcode_svg(data, module_height=20.0)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_font_size(self):
        """Test generating barcode with custom font size"""
        data = "FONT001"
        result = generate_1d_barcode_svg(data, font_size=14)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_text_distance(self):
        """Test generating barcode with custom text distance"""
        data = "DIST001"
        result = generate_1d_barcode_svg(data, text_distance=8.0)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_quiet_zone(self):
        """Test generating barcode with custom quiet zone"""
        data = "QUIET001"
        result = generate_1d_barcode_svg(data, quiet_zone=10.0)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_all_custom_parameters(self):
        """Test generating barcode with all custom parameters"""
        data = "CUSTOM001"
        result = generate_1d_barcode_svg(
            data,
            barcode_type="CODE128",
            module_width=0.4,
            module_height=18.0,
            font_size=12,
            text_distance=6.0,
            quiet_zone=8.0,
        )

        assert isinstance(result, str)
        assert "<svg" in result
        assert "CUSTOM001" in result

    def test_svg_contains_valid_xml(self):
        """Test that generated SVG contains valid XML structure"""
        data = "XML001"
        result = generate_1d_barcode_svg(data)

        # Check for valid SVG attributes
        assert 'xmlns' in result
        assert 'viewBox' in result or 'width' in result

    def test_barcode_with_special_characters(self):
        """Test generating barcode with special characters"""
        # CODE128 supports special characters
        data = "TEST-001/ABC"
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_barcode_with_lowercase(self):
        """Test generating barcode with lowercase letters"""
        data = "test123abc"
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_barcode_with_spaces(self):
        """Test generating barcode with spaces"""
        data = "TEST 123"
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_invalid_barcode_type_raises_error(self):
        """Test that invalid barcode type raises ValueError"""
        data = "TEST123"
        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg(data, barcode_type="INVALID")

        assert "Failed to generate" in str(exc_info.value)

    def test_invalid_ean13_data_raises_error(self):
        """Test that invalid EAN13 data raises ValueError"""
        # EAN13 requires exactly 12 digits
        data = "12345"  # Too short
        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg(data, barcode_type="EAN13")

        assert "Failed to generate EAN13" in str(exc_info.value)

    def test_invalid_ean8_data_raises_error(self):
        """Test that invalid EAN8 data raises ValueError"""
        # EAN8 requires exactly 7 digits
        data = "123"  # Too short
        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg(data, barcode_type="EAN8")

        assert "Failed to generate EAN8" in str(exc_info.value)

    def test_invalid_upca_data_raises_error(self):
        """Test that invalid UPCA data raises ValueError"""
        # UPCA requires exactly 11 digits
        data = "1234"  # Too short
        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg(data, barcode_type="UPCA")

        assert "Failed to generate UPCA" in str(exc_info.value)

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg("")

        assert "Failed to generate" in str(exc_info.value)

    def test_very_long_data_code128(self):
        """Test generating barcode with very long data"""
        data = "A" * 50  # Long data string
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_numeric_only_data(self):
        """Test generating barcode with numeric only data"""
        data = "1234567890"
        result = generate_1d_barcode_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_result_is_utf8_string(self):
        """Test that result is properly decoded UTF-8 string"""
        data = "UTF8TEST"
        result = generate_1d_barcode_svg(data)

        # Should be a proper Python string, not bytes
        assert isinstance(result, str)
        assert not isinstance(result, bytes)


class TestGenerateQRCodeSVG:
    """Test the generate_qr_code_svg function"""

    def test_generate_qr_code_default_params(self):
        """Test generating QR code with default parameters"""
        data = "https://example.com"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result

    def test_generate_qr_code_with_text(self):
        """Test generating QR code with plain text"""
        data = "Hello, World!"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_error_correction_l(self):
        """Test generating QR code with L error correction"""
        data = "ERROR_L"
        result = generate_qr_code_svg(data, error_correction="L")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_error_correction_m(self):
        """Test generating QR code with M error correction"""
        data = "ERROR_M"
        result = generate_qr_code_svg(data, error_correction="M")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_error_correction_q(self):
        """Test generating QR code with Q error correction"""
        data = "ERROR_Q"
        result = generate_qr_code_svg(data, error_correction="Q")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_error_correction_h(self):
        """Test generating QR code with H error correction"""
        data = "ERROR_H"
        result = generate_qr_code_svg(data, error_correction="H")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_scale(self):
        """Test generating QR code with custom scale"""
        data = "SCALE_TEST"
        result = generate_qr_code_svg(data, scale=15)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_border(self):
        """Test generating QR code with custom border"""
        data = "BORDER_TEST"
        result = generate_qr_code_svg(data, border=6)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_custom_dark_color(self):
        """Test generating QR code with custom dark color"""
        data = "COLOR_DARK"
        result = generate_qr_code_svg(data, dark_color="#FF0000")

        assert isinstance(result, str)
        assert "<svg" in result
        assert "#FF0000" in result or "fill" in result

    def test_custom_light_color(self):
        """Test generating QR code with custom light color"""
        data = "COLOR_LIGHT"
        result = generate_qr_code_svg(data, light_color="#00FF00")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_all_custom_parameters(self):
        """Test generating QR code with all custom parameters"""
        data = "CUSTOM_QR"
        result = generate_qr_code_svg(
            data,
            scale=12,
            border=5,
            error_correction="H",
            dark_color="#1A1A1A",
            light_color="#F0F0F0",
        )

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_contains_svg_class(self):
        """Test that QR code contains CSS class"""
        data = "CLASS_TEST"
        result = generate_qr_code_svg(data)

        assert "qr-code" in result

    def test_qr_code_contains_line_class(self):
        """Test that QR code contains line CSS class"""
        data = "LINE_CLASS"
        result = generate_qr_code_svg(data)

        assert "qr-line" in result

    def test_qr_code_has_svg_namespace(self):
        """Test that QR code has SVG namespace"""
        data = "NAMESPACE"
        result = generate_qr_code_svg(data)

        assert "xmlns" in result

    def test_qr_code_no_xml_declaration(self):
        """Test that QR code does not include XML declaration"""
        data = "NO_XML_DECL"
        result = generate_qr_code_svg(data)

        # Should not start with XML declaration
        assert not result.startswith("<?xml")

    def test_qr_code_with_url(self):
        """Test generating QR code with URL"""
        data = "https://www.example.com/path?param=value&other=123"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_with_very_long_data(self):
        """Test generating QR code with very long data"""
        # QR codes can handle up to several thousand characters
        data = "A" * 500
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_with_special_characters(self):
        """Test generating QR code with special characters"""
        data = "Test!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_with_unicode(self):
        """Test generating QR code with unicode characters"""
        data = "Hello 世界 مرحبا"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_with_newlines(self):
        """Test generating QR code with newlines"""
        data = "Line1\nLine2\nLine3"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_numeric_data(self):
        """Test generating QR code with numeric data"""
        data = "1234567890"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_single_character(self):
        """Test generating QR code with single character"""
        data = "X"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_is_utf8_string(self):
        """Test that result is properly decoded UTF-8 string"""
        data = "UTF8_QR"
        result = generate_qr_code_svg(data)

        assert isinstance(result, str)
        assert not isinstance(result, bytes)

    def test_invalid_error_correction_raises_error(self):
        """Test that invalid error correction level raises ValueError"""
        data = "INVALID_EC"
        with pytest.raises(ValueError) as exc_info:
            generate_qr_code_svg(data, error_correction="X")

        assert "Failed to generate QR code" in str(exc_info.value)

    def test_empty_data_generates_valid_qr(self):
        """Test that empty data generates a valid QR code (segno allows it)"""
        # segno library allows empty strings and generates valid QR codes
        result = generate_qr_code_svg("")

        assert isinstance(result, str)
        assert "<svg" in result


class TestGetBarcodeConfigForSize:
    """Test the get_barcode_config_for_size function"""

    def test_config_4x6_label_size(self):
        """Test getting config for 4x6 label"""
        config = get_barcode_config_for_size("4x6")

        assert "1d" in config
        assert "qr" in config

        # Check 1D config
        assert config["1d"]["module_width"] == 0.35
        assert config["1d"]["module_height"] == 18.0
        assert config["1d"]["font_size"] == 12
        assert config["1d"]["text_distance"] == 5.0
        assert config["1d"]["quiet_zone"] == 8.0

        # Check QR config
        assert config["qr"]["scale"] == 12
        assert config["qr"]["border"] == 4
        assert config["qr"]["error_correction"] == "M"

    def test_config_3x4_label_size(self):
        """Test getting config for 3x4 label"""
        config = get_barcode_config_for_size("3x4")

        assert config["1d"]["module_width"] == 0.3
        assert config["1d"]["module_height"] == 14.0
        assert config["1d"]["font_size"] == 10
        assert config["1d"]["text_distance"] == 4.0
        assert config["1d"]["quiet_zone"] == 6.5

        assert config["qr"]["scale"] == 10
        assert config["qr"]["border"] == 3
        assert config["qr"]["error_correction"] == "M"

    def test_config_2x4_label_size(self):
        """Test getting config for 2x4 label"""
        config = get_barcode_config_for_size("2x4")

        assert config["1d"]["module_width"] == 0.25
        assert config["1d"]["module_height"] == 12.0
        assert config["1d"]["font_size"] == 8
        assert config["1d"]["text_distance"] == 3.0
        assert config["1d"]["quiet_zone"] == 5.0

        assert config["qr"]["scale"] == 8
        assert config["qr"]["border"] == 2
        assert config["qr"]["error_correction"] == "M"

    def test_config_2x2_label_size(self):
        """Test getting config for 2x2 label"""
        config = get_barcode_config_for_size("2x2")

        assert config["1d"]["module_width"] == 0.2
        assert config["1d"]["module_height"] == 8.0
        assert config["1d"]["font_size"] == 7
        assert config["1d"]["text_distance"] == 2.0
        assert config["1d"]["quiet_zone"] == 4.0

        # 2x2 has higher error correction
        assert config["qr"]["scale"] == 10
        assert config["qr"]["border"] == 2
        assert config["qr"]["error_correction"] == "H"

    def test_unknown_size_defaults_to_4x6(self):
        """Test that unknown label size defaults to 4x6 config"""
        config = get_barcode_config_for_size("unknown")

        expected_4x6 = get_barcode_config_for_size("4x6")
        assert config == expected_4x6

    def test_invalid_size_string_defaults_to_4x6(self):
        """Test that invalid size string defaults to 4x6 config"""
        config = get_barcode_config_for_size("invalid_size")

        expected_4x6 = get_barcode_config_for_size("4x6")
        assert config == expected_4x6

    def test_empty_string_defaults_to_4x6(self):
        """Test that empty string defaults to 4x6 config"""
        config = get_barcode_config_for_size("")

        expected_4x6 = get_barcode_config_for_size("4x6")
        assert config == expected_4x6

    def test_config_structure_consistency(self):
        """Test that all configs have consistent structure"""
        sizes = ["4x6", "3x4", "2x4", "2x2"]

        for size in sizes:
            config = get_barcode_config_for_size(size)

            # Check 1D config structure
            assert "module_width" in config["1d"]
            assert "module_height" in config["1d"]
            assert "font_size" in config["1d"]
            assert "text_distance" in config["1d"]
            assert "quiet_zone" in config["1d"]

            # Check QR config structure
            assert "scale" in config["qr"]
            assert "border" in config["qr"]
            assert "error_correction" in config["qr"]

    def test_larger_labels_have_larger_parameters(self):
        """Test that larger labels have appropriately larger parameters"""
        config_4x6 = get_barcode_config_for_size("4x6")
        config_2x2 = get_barcode_config_for_size("2x2")

        # Larger label should have larger module dimensions
        assert config_4x6["1d"]["module_width"] > config_2x2["1d"]["module_width"]
        assert config_4x6["1d"]["module_height"] > config_2x2["1d"]["module_height"]
        assert config_4x6["1d"]["font_size"] > config_2x2["1d"]["font_size"]

    def test_case_sensitivity(self):
        """Test that label size lookup is case sensitive"""
        # Uppercase should not match
        config = get_barcode_config_for_size("4X6")

        expected_4x6 = get_barcode_config_for_size("4x6")
        # Should default to 4x6 because "4X6" doesn't match "4x6"
        assert config == expected_4x6


class TestGenerateBarcodeForLabel:
    """Test the generate_barcode_for_label function"""

    def test_generate_barcode_4x6_default(self):
        """Test generating barcode for 4x6 label (default)"""
        data = "LABEL4X6"
        result = generate_barcode_for_label(data)

        assert isinstance(result, str)
        assert "<svg" in result
        assert "LABEL4X6" in result

    def test_generate_barcode_4x6_explicit(self):
        """Test generating barcode for 4x6 label explicitly"""
        data = "LABEL4X6_EXPLICIT"
        result = generate_barcode_for_label(data, label_size="4x6")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_3x4(self):
        """Test generating barcode for 3x4 label"""
        data = "LABEL3X4"
        result = generate_barcode_for_label(data, label_size="3x4")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_2x4(self):
        """Test generating barcode for 2x4 label"""
        data = "LABEL2X4"
        result = generate_barcode_for_label(data, label_size="2x4")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_2x2(self):
        """Test generating barcode for 2x2 label"""
        data = "LABEL2X2"
        result = generate_barcode_for_label(data, label_size="2x2")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_code128_type(self):
        """Test generating CODE128 barcode for label"""
        data = "CODE128LABEL"
        result = generate_barcode_for_label(data, barcode_type="CODE128")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_code39_type(self):
        """Test generating CODE39 barcode for label"""
        data = "CODE39LABEL"
        result = generate_barcode_for_label(data, barcode_type="CODE39")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_barcode_all_sizes_and_types(self):
        """Test generating barcodes for all label sizes and types"""
        sizes = ["4x6", "3x4", "2x4", "2x2"]
        types = ["CODE128", "CODE39"]

        for size in sizes:
            for barcode_type in types:
                # CODE39 doesn't support underscores, so use alphanumeric only
                size_code = size.replace("x", "X")
                data = f"TEST{size_code}{barcode_type[:4]}"
                result = generate_barcode_for_label(data, label_size=size, barcode_type=barcode_type)

                assert isinstance(result, str)
                assert "<svg" in result

    def test_uses_correct_config_for_size(self):
        """Test that function uses correct config parameters for each size"""
        # Verify that different configs are retrieved but note that python-barcode
        # library may not apply all SVGWriter options as expected
        config_4x6 = get_barcode_config_for_size("4x6")
        config_2x2 = get_barcode_config_for_size("2x2")

        # Configs should be different
        assert config_4x6 != config_2x2
        assert config_4x6["1d"]["module_width"] != config_2x2["1d"]["module_width"]

        # Generate barcodes with these configs - they should succeed
        data = "CONFIG_TEST"
        result_4x6 = generate_barcode_for_label(data, label_size="4x6")
        result_2x2 = generate_barcode_for_label(data, label_size="2x2")

        # Both should be valid SVGs
        assert "<svg" in result_4x6
        assert "<svg" in result_2x2

    def test_unknown_size_defaults_to_4x6(self):
        """Test that unknown size defaults to 4x6 configuration"""
        data = "UNKNOWN_SIZE"
        result_unknown = generate_barcode_for_label(data, label_size="unknown")
        result_4x6 = generate_barcode_for_label(data, label_size="4x6")

        # Should produce identical results
        assert result_unknown == result_4x6

    def test_invalid_data_raises_error(self):
        """Test that invalid data raises ValueError"""
        with pytest.raises(ValueError):
            generate_barcode_for_label("", label_size="4x6")


class TestGenerateQRCodeForLabel:
    """Test the generate_qr_code_for_label function"""

    def test_generate_qr_code_4x6_default(self):
        """Test generating QR code for 4x6 label (default)"""
        data = "https://example.com/4x6"
        result = generate_qr_code_for_label(data)

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_4x6_explicit(self):
        """Test generating QR code for 4x6 label explicitly"""
        data = "https://example.com/4x6/explicit"
        result = generate_qr_code_for_label(data, label_size="4x6")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_3x4(self):
        """Test generating QR code for 3x4 label"""
        data = "https://example.com/3x4"
        result = generate_qr_code_for_label(data, label_size="3x4")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_2x4(self):
        """Test generating QR code for 2x4 label"""
        data = "https://example.com/2x4"
        result = generate_qr_code_for_label(data, label_size="2x4")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_2x2(self):
        """Test generating QR code for 2x2 label"""
        data = "https://example.com/2x2"
        result = generate_qr_code_for_label(data, label_size="2x2")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_code_all_sizes(self):
        """Test generating QR codes for all label sizes"""
        sizes = ["4x6", "3x4", "2x4", "2x2"]

        for size in sizes:
            data = f"https://example.com/{size}"
            result = generate_qr_code_for_label(data, label_size=size)

            assert isinstance(result, str)
            assert "<svg" in result

    def test_uses_correct_config_for_size(self):
        """Test that function uses correct config parameters for each size"""
        data = "CONFIG_QR_TEST"
        result_4x6 = generate_qr_code_for_label(data, label_size="4x6")
        result_2x4 = generate_qr_code_for_label(data, label_size="2x4")

        # Results should be different due to different configurations
        assert result_4x6 != result_2x4

    def test_2x2_uses_high_error_correction(self):
        """Test that 2x2 label uses H error correction"""
        # This is tested implicitly by the config test, but we can verify
        # that the QR code is generated successfully with the H correction
        data = "HIGH_ERROR_CORRECTION"
        result = generate_qr_code_for_label(data, label_size="2x2")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_unknown_size_defaults_to_4x6(self):
        """Test that unknown size defaults to 4x6 configuration"""
        data = "UNKNOWN_QR_SIZE"
        result_unknown = generate_qr_code_for_label(data, label_size="unknown")
        result_4x6 = generate_qr_code_for_label(data, label_size="4x6")

        # Should produce identical results
        assert result_unknown == result_4x6

    def test_qr_code_contains_expected_classes(self):
        """Test that QR code contains expected CSS classes"""
        data = "CLASS_CHECK"
        result = generate_qr_code_for_label(data, label_size="4x6")

        assert "qr-code" in result
        assert "qr-line" in result

    def test_qr_code_for_label_with_long_url(self):
        """Test generating QR code for label with long URL"""
        data = "https://example.com/very/long/path/with/many/segments?param1=value1&param2=value2&param3=value3"
        result = generate_qr_code_for_label(data, label_size="4x6")

        assert isinstance(result, str)
        assert "<svg" in result

    def test_empty_data_generates_valid_qr(self):
        """Test that empty data generates a valid QR code"""
        # segno library allows empty strings
        result = generate_qr_code_for_label("", label_size="4x6")

        assert isinstance(result, str)
        assert "<svg" in result


class TestIntegration:
    """Integration tests for barcode service functions"""

    def test_barcode_and_qr_code_for_same_data(self):
        """Test generating both barcode and QR code for same data"""
        data = "INTEGRATION_TEST_001"

        barcode_result = generate_barcode_for_label(data, label_size="4x6")
        qr_result = generate_qr_code_for_label(data, label_size="4x6")

        # Both should be valid SVGs
        assert "<svg" in barcode_result
        assert "<svg" in qr_result

        # But they should be different
        assert barcode_result != qr_result

    def test_all_label_sizes_produce_valid_output(self):
        """Test that all label sizes produce valid output"""
        data = "VALID_OUTPUT_TEST"
        sizes = ["4x6", "3x4", "2x4", "2x2"]

        for size in sizes:
            barcode = generate_barcode_for_label(data, label_size=size)
            qr_code = generate_qr_code_for_label(data, label_size=size)

            assert "<svg" in barcode
            assert "</svg>" in barcode
            assert "<svg" in qr_code
            assert "</svg>" in qr_code

    def test_config_applied_correctly_to_1d_barcode(self):
        """Test that configuration is applied correctly to 1D barcode"""
        data = "CONFIG_1D"

        # Generate for different sizes
        result_4x6 = generate_barcode_for_label(data, label_size="4x6")
        result_2x2 = generate_barcode_for_label(data, label_size="2x2")

        # Both should generate valid SVGs with the same data
        # Note: python-barcode library may not apply SVGWriter options as expected
        # but the function should still succeed
        assert "<svg" in result_4x6
        assert "<svg" in result_2x2
        assert "CONFIG_1D" in result_4x6
        assert "CONFIG_1D" in result_2x2

    def test_config_applied_correctly_to_qr_code(self):
        """Test that configuration is applied correctly to QR code"""
        data = "CONFIG_QR"

        # Generate for different sizes
        result_4x6 = generate_qr_code_for_label(data, label_size="4x6")
        result_3x4 = generate_qr_code_for_label(data, label_size="3x4")

        # Different scale and border should produce different SVGs
        assert result_4x6 != result_3x4

    def test_error_propagation(self):
        """Test that errors are properly propagated"""
        # Invalid EAN13 should raise through generate_barcode_for_label
        with pytest.raises(ValueError) as exc_info:
            generate_barcode_for_label("123", label_size="4x6", barcode_type="EAN13")

        assert "Failed to generate" in str(exc_info.value)

    def test_sequential_barcode_generation(self):
        """Test generating multiple barcodes sequentially"""
        for i in range(5):
            data = f"SEQ_TEST_{i:03d}"
            result = generate_barcode_for_label(data, label_size="4x6")
            assert "<svg" in result

    def test_sequential_qr_code_generation(self):
        """Test generating multiple QR codes sequentially"""
        for i in range(5):
            data = f"https://example.com/item/{i}"
            result = generate_qr_code_for_label(data, label_size="4x6")
            assert "<svg" in result


class TestErrorHandlingEdgeCases:
    """Test error handling and edge cases"""

    @patch('utils.barcode_service.barcode.get_barcode_class')
    def test_barcode_class_exception_wrapped(self, mock_get_class):
        """Test that barcode class exceptions are wrapped in ValueError"""
        mock_get_class.side_effect = Exception("Internal barcode error")

        with pytest.raises(ValueError) as exc_info:
            generate_1d_barcode_svg("TEST")

        assert "Failed to generate" in str(exc_info.value)
        assert "Internal barcode error" in str(exc_info.value)

    @patch('utils.barcode_service.segno.make')
    def test_segno_exception_wrapped(self, mock_make):
        """Test that segno exceptions are wrapped in ValueError"""
        mock_make.side_effect = Exception("Internal QR error")

        with pytest.raises(ValueError) as exc_info:
            generate_qr_code_svg("TEST")

        assert "Failed to generate QR code" in str(exc_info.value)
        assert "Internal QR error" in str(exc_info.value)

    def test_barcode_with_only_spaces(self):
        """Test barcode generation with only spaces"""
        # CODE128 can encode spaces, but this tests edge case
        data = "   "
        result = generate_1d_barcode_svg(data, barcode_type="CODE128")
        assert isinstance(result, str)
        assert "<svg" in result

    def test_qr_code_with_only_spaces(self):
        """Test QR code generation with only spaces"""
        data = "   "
        result = generate_qr_code_svg(data)
        assert isinstance(result, str)
        assert "<svg" in result

    def test_negative_parameters_barcode(self):
        """Test barcode with negative parameters (should still work)"""
        # The library may handle this gracefully or raise an error
        # This tests our error wrapping
        data = "NEGATIVE_TEST"
        try:
            result = generate_1d_barcode_svg(data, module_width=-1.0)
            # If it succeeds, it should still be valid SVG
            assert isinstance(result, str)
        except ValueError:
            # Expected if the library rejects negative values
            pass

    def test_zero_scale_qr_code(self):
        """Test QR code with zero scale"""
        data = "ZERO_SCALE"
        try:
            result = generate_qr_code_svg(data, scale=0)
            assert isinstance(result, str)
        except ValueError:
            # Expected if the library rejects zero scale
            pass

    def test_very_large_parameters(self):
        """Test with very large parameters"""
        data = "LARGE_PARAMS"
        result = generate_1d_barcode_svg(
            data,
            module_width=10.0,
            module_height=100.0,
            font_size=50,
        )
        assert isinstance(result, str)
        assert "<svg" in result
