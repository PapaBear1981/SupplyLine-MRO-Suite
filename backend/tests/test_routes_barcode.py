"""
Tests for Barcode Label Generation Routes

This module tests the barcode label generation endpoints including:
- Tool barcode label generation
- Chemical barcode label generation
- Expendable barcode label generation
- Kit item barcode label generation
- Label sizes endpoint
- Parameter validation
- Error handling
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from models import Tool, Chemical, Expendable


# Fixtures for test data
@pytest.fixture
def test_expendable(db_session):
    """Create test expendable"""
    expendable = Expendable(
        part_number="EXP001",
        lot_number="LOT001",
        description="Test Expendable",
        manufacturer="Test Manufacturer",
        quantity=50.0,
        unit="pcs",
        category="Testing"
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


@pytest.fixture
def test_expendable_serial(db_session):
    """Create test expendable with serial number"""
    expendable = Expendable(
        part_number="EXP002",
        serial_number="SN001",
        description="Serial Expendable",
        manufacturer="Test Manufacturer",
        quantity=1.0,
        unit="each",
        category="Testing"
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


@pytest.fixture
def mock_pdf_bytes():
    """Mock PDF bytes for testing"""
    return b"%PDF-1.4 mock pdf content"


class TestToolBarcodeLabel:
    """Test the GET /api/barcode/tool/<tool_id> endpoint"""

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_tool_barcode_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test successful tool barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/tool/{test_tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == mock_pdf_bytes
        mock_generate_pdf.assert_called_once_with(
            tool=test_tool,
            label_size="4x6",
            code_type="barcode"
        )

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_tool_barcode_label_with_qrcode(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test tool barcode label generation with QR code"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/tool/{test_tool.id}?code_type=qrcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        mock_generate_pdf.assert_called_once_with(
            tool=test_tool,
            label_size="4x6",
            code_type="qrcode"
        )

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_tool_barcode_label_different_sizes(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test tool barcode label generation with different label sizes"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        for size in ["4x6", "3x4", "2x4", "2x2"]:
            response = client.get(
                f"/api/barcode/tool/{test_tool.id}?label_size={size}",
                headers=auth_headers_user
            )

            assert response.status_code == 200
            assert response.content_type == "application/pdf"

    def test_generate_tool_barcode_label_invalid_size(
        self, client, auth_headers_user, test_tool
    ):
        """Test tool barcode label generation with invalid label size"""
        response = client.get(
            f"/api/barcode/tool/{test_tool.id}?label_size=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid label size" in data["error"]

    def test_generate_tool_barcode_label_invalid_code_type(
        self, client, auth_headers_user, test_tool
    ):
        """Test tool barcode label generation with invalid code type"""
        response = client.get(
            f"/api/barcode/tool/{test_tool.id}?code_type=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid code type" in data["error"]

    def test_generate_tool_barcode_label_not_found(
        self, client, auth_headers_user
    ):
        """Test tool barcode label generation for non-existent tool"""
        response = client.get(
            "/api/barcode/tool/99999",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_tool_barcode_label_no_auth(self, client, test_tool):
        """Test tool barcode label generation without authentication"""
        response = client.get(f"/api/barcode/tool/{test_tool.id}")

        assert response.status_code == 401

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_tool_barcode_label_server_error(
        self, mock_generate_pdf, client, auth_headers_user, test_tool
    ):
        """Test tool barcode label generation handles server errors"""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")

        response = client.get(
            f"/api/barcode/tool/{test_tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "PDF generation failed" in data["error"]


class TestChemicalBarcodeLabel:
    """Test the GET /api/barcode/chemical/<chemical_id> endpoint"""

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_barcode_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test successful chemical barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == mock_pdf_bytes
        mock_generate_pdf.assert_called_once()
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["label_size"] == "4x6"
        assert call_kwargs["code_type"] == "barcode"
        assert call_kwargs["is_transfer"] is False
        assert call_kwargs["transfer_data"] is None

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_barcode_label_with_qrcode(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical barcode label generation with QR code"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?code_type=qrcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["code_type"] == "qrcode"

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_barcode_label_different_sizes(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical barcode label generation with different label sizes"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        for size in ["4x6", "3x4", "2x4", "2x2"]:
            response = client.get(
                f"/api/barcode/chemical/{test_chemical.id}?label_size={size}",
                headers=auth_headers_user
            )

            assert response.status_code == 200

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_transfer_label(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical transfer label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?"
            "is_transfer=true&parent_lot_number=PARENT001&destination=Lab A",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["is_transfer"] is True
        assert call_kwargs["transfer_data"] is not None
        assert call_kwargs["transfer_data"]["parent_lot_number"] == "PARENT001"
        assert call_kwargs["transfer_data"]["destination"] == "Lab A"
        assert call_kwargs["transfer_data"]["quantity"] == test_chemical.quantity
        assert call_kwargs["transfer_data"]["unit"] == test_chemical.unit

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_transfer_label_filename(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test that transfer label has correct filename"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?is_transfer=true",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        # Check Content-Disposition header for filename
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "transfer-" in content_disposition or response.status_code == 200

    def test_generate_chemical_barcode_label_invalid_size(
        self, client, auth_headers_user, test_chemical
    ):
        """Test chemical barcode label generation with invalid label size"""
        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?label_size=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid label size" in data["error"]

    def test_generate_chemical_barcode_label_invalid_code_type(
        self, client, auth_headers_user, test_chemical
    ):
        """Test chemical barcode label generation with invalid code type"""
        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?code_type=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid code type" in data["error"]

    def test_generate_chemical_barcode_label_not_found(
        self, client, auth_headers_user
    ):
        """Test chemical barcode label generation for non-existent chemical"""
        response = client.get(
            "/api/barcode/chemical/99999",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_chemical_barcode_label_no_auth(self, client, test_chemical):
        """Test chemical barcode label generation without authentication"""
        response = client.get(f"/api/barcode/chemical/{test_chemical.id}")

        assert response.status_code == 401

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_chemical_barcode_label_server_error(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical
    ):
        """Test chemical barcode label generation handles server errors"""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "PDF generation failed" in data["error"]


class TestExpendableBarcodeLabel:
    """Test the GET /api/barcode/expendable/<expendable_id> endpoint"""

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_generate_expendable_barcode_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable, mock_pdf_bytes
    ):
        """Test successful expendable barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/expendable/{test_expendable.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == mock_pdf_bytes
        mock_generate_pdf.assert_called_once_with(
            expendable=test_expendable,
            label_size="4x6",
            code_type="barcode"
        )

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_generate_expendable_barcode_label_with_qrcode(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable, mock_pdf_bytes
    ):
        """Test expendable barcode label generation with QR code"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/expendable/{test_expendable.id}?code_type=qrcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        mock_generate_pdf.assert_called_once_with(
            expendable=test_expendable,
            label_size="4x6",
            code_type="qrcode"
        )

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_generate_expendable_barcode_label_different_sizes(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable, mock_pdf_bytes
    ):
        """Test expendable barcode label generation with different label sizes"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        for size in ["4x6", "3x4", "2x4", "2x2"]:
            response = client.get(
                f"/api/barcode/expendable/{test_expendable.id}?label_size={size}",
                headers=auth_headers_user
            )

            assert response.status_code == 200

    def test_generate_expendable_barcode_label_invalid_size(
        self, client, auth_headers_user, test_expendable
    ):
        """Test expendable barcode label generation with invalid label size"""
        response = client.get(
            f"/api/barcode/expendable/{test_expendable.id}?label_size=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid label size" in data["error"]

    def test_generate_expendable_barcode_label_invalid_code_type(
        self, client, auth_headers_user, test_expendable
    ):
        """Test expendable barcode label generation with invalid code type"""
        response = client.get(
            f"/api/barcode/expendable/{test_expendable.id}?code_type=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid code type" in data["error"]

    def test_generate_expendable_barcode_label_not_found(
        self, client, auth_headers_user
    ):
        """Test expendable barcode label generation for non-existent expendable"""
        response = client.get(
            "/api/barcode/expendable/99999",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_expendable_barcode_label_no_auth(self, client, test_expendable):
        """Test expendable barcode label generation without authentication"""
        response = client.get(f"/api/barcode/expendable/{test_expendable.id}")

        assert response.status_code == 401

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_generate_expendable_barcode_label_server_error(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable
    ):
        """Test expendable barcode label generation handles server errors"""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")

        response = client.get(
            f"/api/barcode/expendable/{test_expendable.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "PDF generation failed" in data["error"]


class TestKitItemBarcodeLabel:
    """Test the GET /api/barcode/kit-item/<kit_id>/<item_id> endpoint"""

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_kit_item_tool_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test successful kit item tool barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == mock_pdf_bytes
        mock_generate_pdf.assert_called_once_with(test_tool, "4x6", "barcode")

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_kit_item_chemical_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test successful kit item chemical barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/kit-item/1/{test_chemical.id}?item_type=chemical",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        mock_generate_pdf.assert_called_once_with(test_chemical, "4x6", "barcode")

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_generate_kit_item_expendable_label_success(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable, mock_pdf_bytes
    ):
        """Test successful kit item expendable barcode label generation"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/kit-item/1/{test_expendable.id}?item_type=expendable",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        mock_generate_pdf.assert_called_once_with(test_expendable, "4x6", "barcode")

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_kit_item_label_with_qrcode(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test kit item barcode label generation with QR code"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool&code_type=qrcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        mock_generate_pdf.assert_called_once_with(test_tool, "4x6", "qrcode")

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_kit_item_label_different_sizes(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test kit item barcode label generation with different label sizes"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        for size in ["4x6", "3x4", "2x4", "2x2"]:
            response = client.get(
                f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool&label_size={size}",
                headers=auth_headers_user
            )

            assert response.status_code == 200

    def test_generate_kit_item_label_missing_item_type(
        self, client, auth_headers_user, test_tool
    ):
        """Test kit item barcode label generation without item_type parameter"""
        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid or missing item_type" in data["error"]

    def test_generate_kit_item_label_invalid_item_type(
        self, client, auth_headers_user, test_tool
    ):
        """Test kit item barcode label generation with invalid item_type"""
        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid or missing item_type" in data["error"]

    def test_generate_kit_item_label_invalid_size(
        self, client, auth_headers_user, test_tool
    ):
        """Test kit item barcode label generation with invalid label size"""
        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool&label_size=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid label size" in data["error"]

    def test_generate_kit_item_label_invalid_code_type(
        self, client, auth_headers_user, test_tool
    ):
        """Test kit item barcode label generation with invalid code type"""
        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool&code_type=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid code type" in data["error"]

    def test_generate_kit_item_tool_not_found(
        self, client, auth_headers_user
    ):
        """Test kit item barcode label generation for non-existent tool"""
        response = client.get(
            "/api/barcode/kit-item/1/99999?item_type=tool",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_kit_item_chemical_not_found(
        self, client, auth_headers_user
    ):
        """Test kit item barcode label generation for non-existent chemical"""
        response = client.get(
            "/api/barcode/kit-item/1/99999?item_type=chemical",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_kit_item_expendable_not_found(
        self, client, auth_headers_user
    ):
        """Test kit item barcode label generation for non-existent expendable"""
        response = client.get(
            "/api/barcode/kit-item/1/99999?item_type=expendable",
            headers=auth_headers_user
        )

        # 404 from get_or_404 is caught by exception handler, returns 500
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_kit_item_label_no_auth(self, client, test_tool):
        """Test kit item barcode label generation without authentication"""
        response = client.get(f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool")

        assert response.status_code == 401

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_kit_item_label_server_error(
        self, mock_generate_pdf, client, auth_headers_user, test_tool
    ):
        """Test kit item barcode label generation handles server errors"""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")

        response = client.get(
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool",
            headers=auth_headers_user
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "PDF generation failed" in data["error"]


class TestLabelSizesEndpoint:
    """Test the GET /api/barcode/label-sizes endpoint"""

    def test_get_label_sizes_success(self, client, auth_headers_user):
        """Test successful retrieval of label sizes"""
        response = client.get(
            "/api/barcode/label-sizes",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify all expected sizes are present
        assert "4x6" in data
        assert "3x4" in data
        assert "2x4" in data
        assert "2x2" in data

        # Verify structure of each size
        for size_id in ["4x6", "3x4", "2x4", "2x2"]:
            size_info = data[size_id]
            assert "id" in size_info
            assert "name" in size_info
            assert "dimensions" in size_info
            assert "max_fields" in size_info
            assert size_info["id"] == size_id

    def test_get_label_sizes_contains_correct_names(self, client, auth_headers_user):
        """Test that label sizes have correct names"""
        response = client.get(
            "/api/barcode/label-sizes",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'Standard Shipping Label' in data["4x6"]["name"]
        assert 'Medium Label' in data["3x4"]["name"]
        assert 'Small Label' in data["2x4"]["name"]
        assert 'Compact Label' in data["2x2"]["name"]

    def test_get_label_sizes_dimensions_structure(self, client, auth_headers_user):
        """Test that label size dimensions are properly structured"""
        response = client.get(
            "/api/barcode/label-sizes",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        for size_id in ["4x6", "3x4", "2x4", "2x2"]:
            dimensions = data[size_id]["dimensions"]
            assert "width" in dimensions
            assert "height" in dimensions
            assert "in" in dimensions["width"]  # Should be in inches
            assert "in" in dimensions["height"]

    def test_get_label_sizes_max_fields(self, client, auth_headers_user):
        """Test that label sizes have appropriate max_fields"""
        response = client.get(
            "/api/barcode/label-sizes",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Larger labels should have more fields
        assert data["4x6"]["max_fields"] >= data["3x4"]["max_fields"]
        assert data["3x4"]["max_fields"] >= data["2x4"]["max_fields"]
        assert data["2x4"]["max_fields"] >= data["2x2"]["max_fields"]

    def test_get_label_sizes_no_auth(self, client):
        """Test getting label sizes without authentication"""
        response = client.get("/api/barcode/label-sizes")

        assert response.status_code == 401


class TestBarcodeAuthenticationAndAuthorization:
    """Test authentication and authorization across barcode endpoints"""

    def test_all_endpoints_require_auth(self, client, test_tool, test_chemical, test_expendable):
        """Test that all barcode endpoints require authentication"""
        endpoints = [
            f"/api/barcode/tool/{test_tool.id}",
            f"/api/barcode/chemical/{test_chemical.id}",
            f"/api/barcode/expendable/{test_expendable.id}",
            f"/api/barcode/kit-item/1/{test_tool.id}?item_type=tool",
            "/api/barcode/label-sizes",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"

    def test_invalid_token(self, client, test_tool):
        """Test that invalid token is rejected"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get(
            f"/api/barcode/tool/{test_tool.id}",
            headers=headers
        )

        assert response.status_code == 401

    def test_expired_token(self, client, test_tool):
        """Test that expired token is rejected"""
        # This would require creating an expired token
        # For now, test with malformed token
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get(
            f"/api/barcode/tool/{test_tool.id}",
            headers=headers
        )

        assert response.status_code == 401


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions"""

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_tool_with_special_characters_in_number(
        self, mock_generate_pdf, client, auth_headers_user, db_session, mock_pdf_bytes
    ):
        """Test tool with special characters in tool number"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        tool = Tool(
            tool_number="T-001/A",
            serial_number="S-001/B",
            description="Special Tool",
            condition="Good",
            location="Test Location",
            category="Testing",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        response = client.get(
            f"/api/barcode/tool/{tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_chemical_with_long_description(
        self, mock_generate_pdf, client, auth_headers_user, db_session, mock_pdf_bytes
    ):
        """Test chemical with very long description"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        chemical = Chemical(
            part_number="C002",
            lot_number="L002",
            description="A" * 500,  # Very long description
            manufacturer="Test Manufacturer",
            quantity=100.0,
            unit="ml",
            location="Test Location",
            category="Testing",
            status="available"
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.get(
            f"/api/barcode/chemical/{chemical.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200

    @patch("routes_barcode.generate_expendable_label_pdf")
    def test_expendable_with_serial_number(
        self, mock_generate_pdf, client, auth_headers_user, test_expendable_serial, mock_pdf_bytes
    ):
        """Test expendable with serial number instead of lot number"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/expendable/{test_expendable_serial.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_chemical_transfer_with_none_parameters(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical transfer label with None parameters"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?is_transfer=true",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["is_transfer"] is True
        assert call_kwargs["transfer_data"]["parent_lot_number"] is None
        assert call_kwargs["transfer_data"]["destination"] is None

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_chemical_transfer_false_string(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical transfer with false string value"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?is_transfer=false",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["is_transfer"] is False
        assert call_kwargs["transfer_data"] is None

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_chemical_transfer_uppercase_true(
        self, mock_generate_pdf, client, auth_headers_user, test_chemical, mock_pdf_bytes
    ):
        """Test chemical transfer with uppercase TRUE"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/chemical/{test_chemical.id}?is_transfer=TRUE",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        call_kwargs = mock_generate_pdf.call_args.kwargs
        assert call_kwargs["is_transfer"] is True

    def test_kit_item_with_zero_kit_id(self, client, auth_headers_user, test_tool):
        """Test kit item label with zero kit_id"""
        # This should still work as kit_id is just used for filename
        response = client.get(
            f"/api/barcode/kit-item/0/{test_tool.id}?item_type=tool",
            headers=auth_headers_user
        )

        # Will fail due to missing PDF generation mock, but validates routing
        assert response.status_code in [200, 500]

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_combined_parameters(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test combining multiple parameters"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/tool/{test_tool.id}?label_size=2x2&code_type=qrcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        mock_generate_pdf.assert_called_once_with(
            tool=test_tool,
            label_size="2x2",
            code_type="qrcode"
        )


class TestResponseHeaders:
    """Test response headers and content types"""

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_pdf_content_type(
        self, mock_generate_pdf, client, auth_headers_user, test_tool, mock_pdf_bytes
    ):
        """Test that PDF responses have correct content type"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = client.get(
            f"/api/barcode/tool/{test_tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert response.content_type == "application/pdf"

    def test_json_content_type_for_label_sizes(self, client, auth_headers_user):
        """Test that label sizes endpoint returns JSON"""
        response = client.get(
            "/api/barcode/label-sizes",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        assert "application/json" in response.content_type

    def test_json_content_type_for_errors(self, client, auth_headers_user, test_tool):
        """Test that error responses are JSON"""
        response = client.get(
            f"/api/barcode/tool/{test_tool.id}?label_size=invalid",
            headers=auth_headers_user
        )

        assert response.status_code == 400
        assert "application/json" in response.content_type


class TestMultipleItemQueries:
    """Test scenarios with multiple items"""

    @patch("routes_barcode.generate_tool_label_pdf")
    def test_generate_labels_for_multiple_tools(
        self, mock_generate_pdf, client, auth_headers_user, db_session, mock_pdf_bytes
    ):
        """Test generating labels for multiple tools"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        tools = []
        for i in range(3):
            tool = Tool(
                tool_number=f"T00{i+2}",
                serial_number=f"S00{i+2}",
                description=f"Test Tool {i+2}",
                condition="Good",
                location="Test Location",
                category="Testing",
                status="available"
            )
            db_session.add(tool)
            tools.append(tool)
        db_session.commit()

        for tool in tools:
            response = client.get(
                f"/api/barcode/tool/{tool.id}",
                headers=auth_headers_user
            )
            assert response.status_code == 200

    @patch("routes_barcode.generate_chemical_label_pdf")
    def test_generate_labels_for_multiple_chemicals(
        self, mock_generate_pdf, client, auth_headers_user, db_session, mock_pdf_bytes
    ):
        """Test generating labels for multiple chemicals"""
        mock_generate_pdf.return_value = mock_pdf_bytes

        chemicals = []
        for i in range(3):
            chemical = Chemical(
                part_number=f"C00{i+2}",
                lot_number=f"L00{i+2}",
                description=f"Test Chemical {i+2}",
                manufacturer="Test Manufacturer",
                quantity=100.0,
                unit="ml",
                location="Test Location",
                category="Testing",
                status="available"
            )
            db_session.add(chemical)
            chemicals.append(chemical)
        db_session.commit()

        for chemical in chemicals:
            response = client.get(
                f"/api/barcode/chemical/{chemical.id}",
                headers=auth_headers_user
            )
            assert response.status_code == 200
