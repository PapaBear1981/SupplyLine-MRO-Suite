"""
Tests for Label PDF Service Utility Functions

This module tests the label PDF generation service including:
- WeasyPrint lazy import handling
- Template environment configuration
- PDF label generation for tools, chemicals, and expendables
- Different label sizes and code types (barcode/QR code)
- Transfer label generation with metadata
- Edge cases and error handling
"""

import pytest
from unittest.mock import patch, MagicMock, Mock, ANY
from datetime import datetime, date


class TestGetWeasyprint:
    """Test the _get_weasyprint lazy import function"""

    def test_get_weasyprint_success(self):
        """Test successful lazy import of WeasyPrint"""
        from utils.label_pdf_service import _get_weasyprint

        # Mock successful import
        mock_html = MagicMock()
        mock_css = MagicMock()
        mock_module = MagicMock(HTML=mock_html, CSS=mock_css)

        with patch.dict('sys.modules', {'weasyprint': mock_module}):
            HTML, CSS = _get_weasyprint()
            assert HTML is mock_html
            assert CSS is mock_css

    def test_get_weasyprint_import_error(self):
        """Test that ImportError is properly wrapped"""
        from utils.label_pdf_service import _get_weasyprint

        with patch.dict('sys.modules', {'weasyprint': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'weasyprint'")):
                with pytest.raises(RuntimeError) as exc_info:
                    _get_weasyprint()

                assert "WeasyPrint is not available" in str(exc_info.value)
                assert "GTK" in str(exc_info.value)

    def test_get_weasyprint_os_error(self):
        """Test that OSError (GTK issues) is properly wrapped"""
        from utils.label_pdf_service import _get_weasyprint

        with patch.dict('sys.modules', {'weasyprint': None}):
            with patch('builtins.__import__', side_effect=OSError("cannot load library 'libgobject'")):
                with pytest.raises(RuntimeError) as exc_info:
                    _get_weasyprint()

                assert "WeasyPrint is not available" in str(exc_info.value)
                assert "libgobject" in str(exc_info.value)


class TestGetTemplateEnvironment:
    """Test the get_template_environment function"""

    def test_get_template_environment_returns_jinja_env(self, app):
        """Test that get_template_environment returns a Jinja2 Environment"""
        from utils.label_pdf_service import get_template_environment
        from jinja2 import Environment

        with app.app_context():
            env = get_template_environment()
            assert isinstance(env, Environment)

    def test_template_environment_has_correct_settings(self, app):
        """Test that template environment has correct configuration"""
        from utils.label_pdf_service import get_template_environment

        with app.app_context():
            env = get_template_environment()

            # Check autoescape is enabled (it's a callable when using select_autoescape)
            assert callable(env.autoescape) or env.autoescape is True

            # Check trim_blocks and lstrip_blocks
            assert env.trim_blocks is True
            assert env.lstrip_blocks is True

    def test_template_environment_uses_correct_loader(self, app):
        """Test that template environment uses FileSystemLoader"""
        from utils.label_pdf_service import get_template_environment
        from jinja2 import FileSystemLoader

        with app.app_context():
            env = get_template_environment()
            assert isinstance(env.loader, FileSystemLoader)

    def test_template_directory_path(self, app):
        """Test that template directory is correctly set"""
        from utils.label_pdf_service import get_template_environment
        import os

        with app.app_context():
            env = get_template_environment()
            expected_path = os.path.join(app.root_path, "templates", "labels")

            # Check the searchpath of the loader
            assert expected_path in env.loader.searchpath


class TestGenerateLabelPDF:
    """Test the generate_label_pdf function"""

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_with_barcode(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test generating PDF label with 1D barcode"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test", "barcode_svg": "<svg>barcode</svg>"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"PDF_CONTENT"
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        with app.app_context():
            result = generate_label_pdf(
                item_title="TEST-001",
                barcode_data="TEST123",
                fields=[{"label": "Field1", "value": "Value1"}],
                label_size="4x6",
                code_type="barcode",
            )

            assert result == b"PDF_CONTENT"
            mock_barcode.assert_called_once_with("TEST123", "4x6", "CODE128")

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_qr_code_for_label')
    def test_generate_label_pdf_with_qrcode(
        self, mock_qrcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test generating PDF label with QR code"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_qrcode.return_value = "<svg>qrcode</svg>"
        mock_context.return_value = {"title": "Test", "barcode_svg": "<svg>qrcode</svg>"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"PDF_QR_CONTENT"
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        with app.app_context():
            result = generate_label_pdf(
                item_title="TEST-002",
                barcode_data="TEST456",
                fields=[{"label": "Field1", "value": "Value1"}],
                label_size="3x4",
                code_type="qrcode",
            )

            assert result == b"PDF_QR_CONTENT"
            mock_qrcode.assert_called_once_with("TEST456", "3x4")

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_with_transfer_and_warning(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test generating PDF label with transfer flag and warning text"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test", "barcode_svg": "<svg>barcode</svg>"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"PDF_TRANSFER"
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        with app.app_context():
            result = generate_label_pdf(
                item_title="TRANSFER-001",
                barcode_data="TRANSFER123",
                fields=[],
                label_size="2x4",
                code_type="barcode",
                is_transfer=True,
                warning_text="PARTIAL TRANSFER - NEW LOT NUMBER",
            )

            assert result == b"PDF_TRANSFER"
            mock_context.assert_called_once_with(
                label_size="2x4",
                item_title="TRANSFER-001",
                barcode_svg="<svg>barcode</svg>",
                fields=[],
                is_transfer=True,
                warning_text="PARTIAL TRANSFER - NEW LOT NUMBER",
            )

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_with_different_barcode_types(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test generating PDF label with different barcode types"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test", "barcode_svg": "<svg>barcode</svg>"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"PDF_CODE39"
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        with app.app_context():
            result = generate_label_pdf(
                item_title="TEST-003",
                barcode_data="TEST789",
                fields=[],
                label_size="2x2",
                code_type="barcode",
                barcode_type="CODE39",
            )

            assert result == b"PDF_CODE39"
            mock_barcode.assert_called_once_with("TEST789", "2x2", "CODE39")

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_none_result_raises_error(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test that None PDF result raises RuntimeError"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test", "barcode_svg": "<svg>barcode</svg>"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None  # Return None
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        with app.app_context():
            with pytest.raises(RuntimeError) as exc_info:
                generate_label_pdf(
                    item_title="TEST",
                    barcode_data="TEST",
                    fields=[],
                )

            assert "PDF generation returned None" in str(exc_info.value)

    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_barcode_error_raises_runtime_error(
        self, mock_barcode, app
    ):
        """Test that barcode generation error is wrapped in RuntimeError"""
        from utils.label_pdf_service import generate_label_pdf

        mock_barcode.side_effect = ValueError("Invalid barcode data")

        with app.app_context():
            with pytest.raises(RuntimeError) as exc_info:
                generate_label_pdf(
                    item_title="TEST",
                    barcode_data="",
                    fields=[],
                )

            assert "Failed to generate label PDF" in str(exc_info.value)
            assert "Invalid barcode data" in str(exc_info.value)

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_template_error_raises_runtime_error(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test that template rendering error is wrapped in RuntimeError"""
        from utils.label_pdf_service import generate_label_pdf

        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test"}

        mock_env_instance = MagicMock()
        mock_env_instance.get_template.side_effect = Exception("Template not found")
        mock_env.return_value = mock_env_instance

        with app.app_context():
            with pytest.raises(RuntimeError) as exc_info:
                generate_label_pdf(
                    item_title="TEST",
                    barcode_data="TEST",
                    fields=[],
                )

            assert "Failed to generate label PDF" in str(exc_info.value)
            assert "Template not found" in str(exc_info.value)

    @patch('utils.label_pdf_service._get_weasyprint')
    @patch('utils.label_pdf_service.get_template_environment')
    @patch('utils.label_pdf_service.get_label_template_context')
    @patch('utils.label_pdf_service.generate_barcode_for_label')
    def test_generate_label_pdf_all_label_sizes(
        self, mock_barcode, mock_context, mock_env, mock_weasyprint, app
    ):
        """Test generating PDF labels for all supported sizes"""
        from utils.label_pdf_service import generate_label_pdf

        # Setup mocks
        mock_barcode.return_value = "<svg>barcode</svg>"
        mock_context.return_value = {"title": "Test"}

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>test</html>"
        mock_env_instance = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance

        mock_html_class = MagicMock()
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"PDF"
        mock_html_class.return_value = mock_html_instance
        mock_weasyprint.return_value = (mock_html_class, MagicMock())

        sizes = ["4x6", "3x4", "2x4", "2x2"]

        with app.app_context():
            for size in sizes:
                result = generate_label_pdf(
                    item_title=f"TEST-{size}",
                    barcode_data=f"DATA-{size}",
                    fields=[],
                    label_size=size,
                )
                assert result == b"PDF"


class TestGenerateToolLabelPDF:
    """Test the generate_tool_label_pdf function"""

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_tool_label_with_lot_number(self, mock_generate, app):
        """Test generating tool label with lot number"""
        from utils.label_pdf_service import generate_tool_label_pdf

        # Create mock tool with lot number
        mock_tool = MagicMock()
        mock_tool.tool_number = "TOOL-001"
        mock_tool.lot_number = "LOT-123"
        mock_tool.serial_number = None
        mock_tool.description = "Test Tool Description"
        mock_tool.location = "Bay A1"
        mock_tool.status = "available"
        mock_tool.category = "Hand Tools"
        mock_tool.condition = "Good"
        mock_tool.created_at = datetime(2024, 1, 15, 10, 30, 0)

        mock_generate.return_value = b"TOOL_PDF"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool, label_size="4x6", code_type="barcode")

            assert result == b"TOOL_PDF"

            # Verify the call
            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "TOOL-001 - LOT LOT-123"
            assert call_args[1]["barcode_data"] == "TOOL-001-LOT-LOT-123"
            assert call_args[1]["label_size"] == "4x6"
            assert call_args[1]["code_type"] == "barcode"

            # Check fields
            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Tool Number" in field_labels
            assert "Description" in field_labels
            assert "Location" in field_labels
            assert "Status" in field_labels
            assert "Lot Number" in field_labels
            assert "Category" in field_labels
            assert "Condition" in field_labels
            assert "Date Added" in field_labels

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_tool_label_with_serial_number(self, mock_generate, app):
        """Test generating tool label with serial number"""
        from utils.label_pdf_service import generate_tool_label_pdf

        # Create mock tool with serial number
        mock_tool = MagicMock()
        mock_tool.tool_number = "TOOL-002"
        mock_tool.lot_number = None
        mock_tool.serial_number = "SN-456"
        mock_tool.description = "Test Tool"
        mock_tool.location = "Bay B2"
        mock_tool.status = "in_use"
        mock_tool.category = None
        mock_tool.condition = None
        mock_tool.created_at = None

        mock_generate.return_value = b"TOOL_PDF_SN"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool)

            assert result == b"TOOL_PDF_SN"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "TOOL-002 - SN SN-456"
            assert call_args[1]["barcode_data"] == "TOOL-002-SN-456"

            # Check fields don't include category, condition, or date added
            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Category" not in field_labels
            assert "Condition" not in field_labels
            assert "Date Added" not in field_labels
            assert "Serial Number" in field_labels

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_tool_label_no_lot_or_serial(self, mock_generate, app):
        """Test generating tool label without lot or serial number"""
        from utils.label_pdf_service import generate_tool_label_pdf

        # Create mock tool without lot or serial
        mock_tool = MagicMock()
        mock_tool.tool_number = "TOOL-003"
        mock_tool.lot_number = None
        mock_tool.serial_number = None
        mock_tool.description = "Basic Tool"
        mock_tool.location = "Storage"
        mock_tool.status = "available"
        mock_tool.category = "General"
        mock_tool.condition = "Fair"
        # Tool without created_at attribute
        del mock_tool.created_at

        mock_generate.return_value = b"TOOL_PDF_BASIC"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool, label_size="2x2", code_type="qrcode")

            assert result == b"TOOL_PDF_BASIC"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "TOOL-003"
            assert call_args[1]["barcode_data"] == "TOOL-003-"
            assert call_args[1]["label_size"] == "2x2"
            assert call_args[1]["code_type"] == "qrcode"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_tool_label_empty_tool_number(self, mock_generate, app):
        """Test generating tool label with empty tool number"""
        from utils.label_pdf_service import generate_tool_label_pdf

        mock_tool = MagicMock()
        mock_tool.tool_number = None
        mock_tool.lot_number = "LOT-999"
        mock_tool.serial_number = None
        mock_tool.description = None
        mock_tool.location = None
        mock_tool.status = None
        mock_tool.category = None
        mock_tool.condition = None
        del mock_tool.created_at

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool)

            call_args = mock_generate.call_args
            assert call_args[1]["barcode_data"] == "-LOT-LOT-999"
            fields = call_args[1]["fields"]
            # Check N/A values for None fields
            tool_num_field = next(f for f in fields if f["label"] == "Tool Number")
            assert tool_num_field["value"] == "N/A"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_tool_label_all_fields_populated(self, mock_generate, app):
        """Test generating tool label with all fields populated"""
        from utils.label_pdf_service import generate_tool_label_pdf

        mock_tool = MagicMock()
        mock_tool.tool_number = "TOOL-FULL"
        mock_tool.lot_number = "LOT-FULL"
        mock_tool.serial_number = "SN-FULL"
        mock_tool.description = "Full Tool"
        mock_tool.location = "Location"
        mock_tool.status = "available"
        mock_tool.category = "Category"
        mock_tool.condition = "Excellent"
        mock_tool.created_at = datetime(2024, 12, 25)

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool)

            call_args = mock_generate.call_args
            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]

            # Should have all standard fields plus optional fields
            assert len(fields) >= 8
            assert "Lot Number" in field_labels
            assert "Serial Number" in field_labels
            assert "Category" in field_labels
            assert "Condition" in field_labels
            assert "Date Added" in field_labels


class TestGenerateChemicalLabelPDF:
    """Test the generate_chemical_label_pdf function"""

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_basic(self, mock_generate, app):
        """Test generating basic chemical label"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-001"
        mock_chemical.lot_number = "LOT-001"
        mock_chemical.description = "Test Chemical"
        mock_chemical.manufacturer = "ABC Corp"
        mock_chemical.quantity = 100.0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Lab A"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"CHEM_PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical)

            assert result == b"CHEM_PDF"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "CHEM-001 - LOT-001"
            assert call_args[1]["barcode_data"] == "CHEM-001-LOT-001-NOEXP"
            assert call_args[1]["is_transfer"] is False
            assert call_args[1]["warning_text"] is None

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_with_expiration_date(self, mock_generate, app):
        """Test generating chemical label with expiration date"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-002"
        mock_chemical.lot_number = "LOT-002"
        mock_chemical.description = "Expiring Chemical"
        mock_chemical.manufacturer = "XYZ Corp"
        mock_chemical.quantity = 50.5
        mock_chemical.unit = "L"
        mock_chemical.location = "Storage"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = date(2025, 6, 30)
        mock_chemical.date_added = date(2024, 1, 1)
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"CHEM_PDF_EXP"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical, label_size="3x4")

            assert result == b"CHEM_PDF_EXP"

            call_args = mock_generate.call_args
            assert call_args[1]["barcode_data"] == "CHEM-002-LOT-002-20250630"
            assert call_args[1]["label_size"] == "3x4"

            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Expiration Date" in field_labels
            assert "Date Added" in field_labels

            exp_field = next(f for f in fields if f["label"] == "Expiration Date")
            assert exp_field["value"] == "2025-06-30"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_issued_with_issuance(self, mock_generate, app):
        """Test generating chemical label for issued item with issuance record"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_issuance = MagicMock()
        mock_issuance.quantity = 25.0

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-003"
        mock_chemical.lot_number = "LOT-003"
        mock_chemical.description = "Issued Chemical"
        mock_chemical.manufacturer = "Manufacturer"
        mock_chemical.quantity = 0  # Current quantity is 0 after issuance
        mock_chemical.unit = "g"
        mock_chemical.location = "Field"
        mock_chemical.status = "issued"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = "PARENT-LOT"
        mock_chemical.issuance = mock_issuance

        mock_generate.return_value = b"CHEM_PDF_ISSUED"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical)

            assert result == b"CHEM_PDF_ISSUED"

            call_args = mock_generate.call_args
            fields = call_args[1]["fields"]

            # Check that display quantity is from issuance, not current quantity
            qty_field = next(f for f in fields if f["label"] == "Quantity")
            assert "25.0 g" in qty_field["value"]

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_transfer_with_data(self, mock_generate, app):
        """Test generating chemical transfer label with transfer data"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-004"
        mock_chemical.lot_number = "NEW-LOT"
        mock_chemical.description = "Transferred Chemical"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 30.0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Dest"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        transfer_data = {
            "parent_lot_number": "PARENT-LOT-001",
            "destination": "Lab B",
            "transfer_date": datetime(2024, 3, 15),
        }

        mock_generate.return_value = b"CHEM_PDF_TRANSFER"

        with app.app_context():
            result = generate_chemical_label_pdf(
                mock_chemical,
                is_transfer=True,
                transfer_data=transfer_data,
            )

            assert result == b"CHEM_PDF_TRANSFER"

            call_args = mock_generate.call_args
            assert call_args[1]["is_transfer"] is True
            assert call_args[1]["warning_text"] == "PARTIAL TRANSFER - NEW LOT NUMBER"

            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Parent Lot" in field_labels
            assert "Destination" in field_labels
            assert "Transfer Date" in field_labels

            parent_field = next(f for f in fields if f["label"] == "Parent Lot")
            assert parent_field["value"] == "PARENT-LOT-001"

            dest_field = next(f for f in fields if f["label"] == "Destination")
            assert dest_field["value"] == "Lab B"

            date_field = next(f for f in fields if f["label"] == "Transfer Date")
            assert date_field["value"] == "2024-03-15"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_transfer_date_as_string(self, mock_generate, app):
        """Test generating chemical transfer label with string transfer date"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-005"
        mock_chemical.lot_number = "LOT-005"
        mock_chemical.description = "Chemical"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 10.0
        mock_chemical.unit = "kg"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        transfer_data = {
            "transfer_date": "2024-05-20",  # String date
        }

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(
                mock_chemical,
                is_transfer=True,
                transfer_data=transfer_data,
            )

            call_args = mock_generate.call_args
            fields = call_args[1]["fields"]
            date_field = next(f for f in fields if f["label"] == "Transfer Date")
            assert date_field["value"] == "2024-05-20"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_is_transfer_but_no_data(self, mock_generate, app):
        """Test generating transfer label without transfer data"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-006"
        mock_chemical.lot_number = "LOT-006"
        mock_chemical.description = "Chemical"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 5.0
        mock_chemical.unit = "oz"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(
                mock_chemical,
                is_transfer=True,
                transfer_data=None,
            )

            call_args = mock_generate.call_args
            # Warning text should still be None since transfer_data is None
            assert call_args[1]["warning_text"] is None

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_empty_transfer_data(self, mock_generate, app):
        """Test generating transfer label with empty transfer data dict"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-007"
        mock_chemical.lot_number = "LOT-007"
        mock_chemical.description = "Chemical"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 1.0
        mock_chemical.unit = "each"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(
                mock_chemical,
                is_transfer=True,
                transfer_data={},  # Empty dict
            )

            call_args = mock_generate.call_args
            # Warning text is still set as long as is_transfer=True and transfer_data exists (even if empty)
            # The code checks `if is_transfer and transfer_data:` so empty dict evaluates to False
            assert call_args[1]["warning_text"] is None
            # No transfer fields should be added for empty dict
            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Parent Lot" not in field_labels
            assert "Destination" not in field_labels
            assert "Transfer Date" not in field_labels

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_none_values(self, mock_generate, app):
        """Test generating chemical label with None values"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = None
        mock_chemical.lot_number = None
        mock_chemical.description = None
        mock_chemical.manufacturer = None
        mock_chemical.quantity = None
        mock_chemical.unit = None
        mock_chemical.location = None
        mock_chemical.status = None
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical)

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "None - None"
            assert call_args[1]["barcode_data"] == "--NOEXP"

            fields = call_args[1]["fields"]
            qty_field = next(f for f in fields if f["label"] == "Quantity")
            assert qty_field["value"] == "N/A"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_chemical_label_with_qrcode(self, mock_generate, app):
        """Test generating chemical label with QR code"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM-QR"
        mock_chemical.lot_number = "LOT-QR"
        mock_chemical.description = "QR Chemical"
        mock_chemical.manufacturer = "QR Mfg"
        mock_chemical.quantity = 100.0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Lab"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(
                mock_chemical,
                label_size="2x4",
                code_type="qrcode",
            )

            call_args = mock_generate.call_args
            assert call_args[1]["label_size"] == "2x4"
            assert call_args[1]["code_type"] == "qrcode"


class TestGenerateExpendableLabelPDF:
    """Test the generate_expendable_label_pdf function"""

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_with_lot_number(self, mock_generate, app):
        """Test generating expendable label with lot number"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-001"
        mock_expendable.lot_number = "LOT-EXP-001"
        mock_expendable.serial_number = None
        mock_expendable.description = "Test Expendable"
        mock_expendable.quantity = 50
        mock_expendable.unit = "each"
        mock_expendable.location = "Storage A"
        mock_expendable.category = "Consumables"
        mock_expendable.date_added = datetime(2024, 2, 10)

        mock_generate.return_value = b"EXP_PDF"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable)

            assert result == b"EXP_PDF"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "EXP-001 - LOT LOT-EXP-001"
            assert call_args[1]["barcode_data"] == "EXP-001-LOT-LOT-EXP-001"

            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Part Number" in field_labels
            assert "Description" in field_labels
            assert "Quantity" in field_labels
            assert "Location" in field_labels
            assert "Category" in field_labels
            assert "Lot Number" in field_labels
            assert "Date Added" in field_labels

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_with_serial_number(self, mock_generate, app):
        """Test generating expendable label with serial number"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-002"
        mock_expendable.lot_number = None
        mock_expendable.serial_number = "SN-EXP-002"
        mock_expendable.description = "Serial Expendable"
        mock_expendable.quantity = 1
        mock_expendable.unit = "piece"
        mock_expendable.location = "Storage B"
        mock_expendable.category = "Tools"
        mock_expendable.date_added = None

        mock_generate.return_value = b"EXP_PDF_SN"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable, label_size="3x4")

            assert result == b"EXP_PDF_SN"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "EXP-002 - SN SN-EXP-002"
            assert call_args[1]["barcode_data"] == "EXP-002-SN-SN-EXP-002"
            assert call_args[1]["label_size"] == "3x4"

            fields = call_args[1]["fields"]
            field_labels = [f["label"] for f in fields]
            assert "Serial Number" in field_labels
            assert "Lot Number" not in field_labels
            assert "Date Added" not in field_labels

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_no_lot_or_serial(self, mock_generate, app):
        """Test generating expendable label without lot or serial number"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-003"
        mock_expendable.lot_number = None
        mock_expendable.serial_number = None
        mock_expendable.description = "Basic Expendable"
        mock_expendable.quantity = 100
        mock_expendable.unit = "kg"
        mock_expendable.location = "Warehouse"
        mock_expendable.category = "Bulk"
        mock_expendable.date_added = None

        mock_generate.return_value = b"EXP_PDF_BASIC"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable, code_type="qrcode")

            assert result == b"EXP_PDF_BASIC"

            call_args = mock_generate.call_args
            assert call_args[1]["item_title"] == "EXP-003"
            assert call_args[1]["barcode_data"] == "EXP-003-SN-"
            assert call_args[1]["code_type"] == "qrcode"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_empty_quantity(self, mock_generate, app):
        """Test generating expendable label with no quantity"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-004"
        mock_expendable.lot_number = "LOT-004"
        mock_expendable.serial_number = None
        mock_expendable.description = "Empty Expendable"
        mock_expendable.quantity = None  # No quantity
        mock_expendable.unit = "ml"
        mock_expendable.location = "Storage"
        mock_expendable.category = "Other"
        mock_expendable.date_added = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable)

            call_args = mock_generate.call_args
            fields = call_args[1]["fields"]
            qty_field = next(f for f in fields if f["label"] == "Quantity")
            assert qty_field["value"] == "N/A"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_none_part_number(self, mock_generate, app):
        """Test generating expendable label with None part number"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = None
        mock_expendable.lot_number = "LOT-NOPART"
        mock_expendable.serial_number = None
        mock_expendable.description = None
        mock_expendable.quantity = 10
        mock_expendable.unit = "each"
        mock_expendable.location = None
        mock_expendable.category = None
        mock_expendable.date_added = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable)

            call_args = mock_generate.call_args
            assert call_args[1]["barcode_data"] == "-LOT-LOT-NOPART"

            fields = call_args[1]["fields"]
            part_field = next(f for f in fields if f["label"] == "Part Number")
            assert part_field["value"] == "N/A"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_generate_expendable_label_all_sizes(self, mock_generate, app):
        """Test generating expendable labels for all supported sizes"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-SIZE"
        mock_expendable.lot_number = "LOT-SIZE"
        mock_expendable.serial_number = None
        mock_expendable.description = "Size Test"
        mock_expendable.quantity = 1
        mock_expendable.unit = "each"
        mock_expendable.location = "Test"
        mock_expendable.category = "Test"
        mock_expendable.date_added = None

        mock_generate.return_value = b"PDF"

        sizes = ["4x6", "3x4", "2x4", "2x2"]

        with app.app_context():
            for size in sizes:
                result = generate_expendable_label_pdf(mock_expendable, label_size=size)
                assert result == b"PDF"

                call_args = mock_generate.call_args
                assert call_args[1]["label_size"] == size


class TestIntegration:
    """Integration tests for label PDF service"""

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_tool_label_respects_code_type_parameter(self, mock_generate, app):
        """Test that tool label correctly passes code_type parameter"""
        from utils.label_pdf_service import generate_tool_label_pdf

        mock_tool = MagicMock()
        mock_tool.tool_number = "T-INT"
        mock_tool.lot_number = None
        mock_tool.serial_number = "SN-INT"
        mock_tool.description = "Test"
        mock_tool.location = "Loc"
        mock_tool.status = "available"
        mock_tool.category = None
        mock_tool.condition = None
        del mock_tool.created_at

        mock_generate.return_value = b"PDF"

        with app.app_context():
            generate_tool_label_pdf(mock_tool, code_type="qrcode")
            call_args = mock_generate.call_args
            assert call_args[1]["code_type"] == "qrcode"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_chemical_label_respects_all_parameters(self, mock_generate, app):
        """Test that chemical label correctly passes all parameters"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "C-INT"
        mock_chemical.lot_number = "L-INT"
        mock_chemical.description = "Test"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 10.0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            generate_chemical_label_pdf(
                mock_chemical,
                label_size="2x2",
                code_type="qrcode",
                is_transfer=False,
            )

            call_args = mock_generate.call_args
            assert call_args[1]["label_size"] == "2x2"
            assert call_args[1]["code_type"] == "qrcode"
            assert call_args[1]["is_transfer"] is False

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_expendable_label_respects_all_parameters(self, mock_generate, app):
        """Test that expendable label correctly passes all parameters"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "E-INT"
        mock_expendable.lot_number = "L-INT"
        mock_expendable.serial_number = None
        mock_expendable.description = "Test"
        mock_expendable.quantity = 5
        mock_expendable.unit = "each"
        mock_expendable.location = "Loc"
        mock_expendable.category = "Cat"
        mock_expendable.date_added = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            generate_expendable_label_pdf(
                mock_expendable,
                label_size="3x4",
                code_type="barcode",
            )

            call_args = mock_generate.call_args
            assert call_args[1]["label_size"] == "3x4"
            assert call_args[1]["code_type"] == "barcode"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_chemical_with_zero_quantity(self, mock_generate, app):
        """Test chemical label with zero quantity"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM"
        mock_chemical.lot_number = "LOT"
        mock_chemical.description = "Test"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical)

            call_args = mock_generate.call_args
            fields = call_args[1]["fields"]
            qty_field = next(f for f in fields if f["label"] == "Quantity")
            # Zero is a valid quantity
            assert "0 ml" in qty_field["value"]

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_tool_with_very_long_description(self, mock_generate, app):
        """Test tool label with very long description"""
        from utils.label_pdf_service import generate_tool_label_pdf

        mock_tool = MagicMock()
        mock_tool.tool_number = "T-LONG"
        mock_tool.lot_number = None
        mock_tool.serial_number = "SN"
        mock_tool.description = "A" * 500  # Very long description
        mock_tool.location = "Loc"
        mock_tool.status = "available"
        mock_tool.category = None
        mock_tool.condition = None
        del mock_tool.created_at

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_tool_label_pdf(mock_tool)
            assert result == b"PDF"

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_expendable_with_special_characters_in_part_number(self, mock_generate, app):
        """Test expendable label with special characters in part number"""
        from utils.label_pdf_service import generate_expendable_label_pdf

        mock_expendable = MagicMock()
        mock_expendable.part_number = "EXP-001/A_B.C"
        mock_expendable.lot_number = "LOT-001"
        mock_expendable.serial_number = None
        mock_expendable.description = "Special"
        mock_expendable.quantity = 1
        mock_expendable.unit = "each"
        mock_expendable.location = "Loc"
        mock_expendable.category = "Cat"
        mock_expendable.date_added = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_expendable_label_pdf(mock_expendable)

            call_args = mock_generate.call_args
            assert "EXP-001/A_B.C" in call_args[1]["barcode_data"]

    @patch('utils.label_pdf_service.generate_label_pdf')
    def test_chemical_with_both_lot_and_serial(self, mock_generate, app):
        """Test chemical with both lot and serial (unusual but possible)"""
        from utils.label_pdf_service import generate_chemical_label_pdf

        mock_chemical = MagicMock()
        mock_chemical.part_number = "CHEM"
        mock_chemical.lot_number = "LOT"
        mock_chemical.description = "Test"
        mock_chemical.manufacturer = "Mfg"
        mock_chemical.quantity = 10.0
        mock_chemical.unit = "ml"
        mock_chemical.location = "Loc"
        mock_chemical.status = "available"
        mock_chemical.expiration_date = None
        mock_chemical.date_added = None
        mock_chemical.parent_lot_number = None
        mock_chemical.issuance = None

        mock_generate.return_value = b"PDF"

        with app.app_context():
            result = generate_chemical_label_pdf(mock_chemical)
            assert result == b"PDF"
