"""
Comprehensive tests for bulk import utilities
"""
import csv
import io
from datetime import date
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from utils.bulk_import import (
    BulkImportError,
    BulkImportResult,
    bulk_import_chemicals,
    bulk_import_tools,
    check_duplicate_chemical,
    check_duplicate_tool,
    generate_chemical_template,
    generate_tool_template,
    parse_csv_content,
    validate_chemical_data,
    validate_tool_data,
)
from utils.validation import ValidationError


class TestBulkImportResult:
    """Tests for BulkImportResult class"""

    def test_init(self):
        """Test BulkImportResult initialization"""
        result = BulkImportResult()
        assert result.success_count == 0
        assert result.error_count == 0
        assert result.errors == []
        assert result.warnings == []
        assert result.created_items == []
        assert result.skipped_items == []

    def test_add_success_with_to_dict(self):
        """Test adding success with item that has to_dict method"""
        result = BulkImportResult()
        mock_item = MagicMock()
        mock_item.to_dict.return_value = {"id": 1, "name": "test"}

        item_data = {"tool_number": "T001", "serial_number": "SN001"}
        result.add_success(item_data, mock_item)

        assert result.success_count == 1
        assert len(result.created_items) == 1
        assert result.created_items[0]["data"] == item_data
        assert result.created_items[0]["created"] == {"id": 1, "name": "test"}

    def test_add_success_without_to_dict(self):
        """Test adding success with item that lacks to_dict method"""
        result = BulkImportResult()
        simple_item = "simple_string_item"

        item_data = {"tool_number": "T002", "serial_number": "SN002"}
        result.add_success(item_data, simple_item)

        assert result.success_count == 1
        assert len(result.created_items) == 1
        assert result.created_items[0]["data"] == item_data
        assert result.created_items[0]["created"] == "simple_string_item"

    def test_add_error(self):
        """Test adding import error"""
        result = BulkImportResult()
        item_data = {"tool_number": "T001"}

        result.add_error(2, item_data, "Validation failed")

        assert result.error_count == 1
        assert len(result.errors) == 1
        assert result.errors[0]["row"] == 2
        assert result.errors[0]["data"] == item_data
        assert result.errors[0]["error"] == "Validation failed"

    def test_add_warning(self):
        """Test adding import warning"""
        result = BulkImportResult()
        item_data = {"tool_number": "T001"}

        result.add_warning(3, item_data, "Field truncated")

        assert len(result.warnings) == 1
        assert result.warnings[0]["row"] == 3
        assert result.warnings[0]["data"] == item_data
        assert result.warnings[0]["warning"] == "Field truncated"

    def test_add_skipped(self):
        """Test adding skipped item"""
        result = BulkImportResult()
        item_data = {"tool_number": "T001"}

        result.add_skipped(4, item_data, "Duplicate entry")

        assert len(result.skipped_items) == 1
        assert result.skipped_items[0]["row"] == 4
        assert result.skipped_items[0]["data"] == item_data
        assert result.skipped_items[0]["reason"] == "Duplicate entry"

    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = BulkImportResult()
        result.success_count = 5
        result.error_count = 2
        result.warnings = [{"row": 1, "data": {}, "warning": "warn"}]
        result.skipped_items = [{"row": 2, "data": {}, "reason": "skip"}]
        result.errors = [{"row": 3, "data": {}, "error": "err"}]
        result.created_items = [{"data": {}, "created": {}}]

        result_dict = result.to_dict()

        assert result_dict["success_count"] == 5
        assert result_dict["error_count"] == 2
        assert result_dict["warning_count"] == 1
        assert result_dict["skipped_count"] == 1
        assert len(result_dict["errors"]) == 1
        assert len(result_dict["warnings"]) == 1
        assert len(result_dict["created_items"]) == 1
        assert len(result_dict["skipped_items"]) == 1


class TestBulkImportError:
    """Tests for BulkImportError exception"""

    def test_exception_creation(self):
        """Test that BulkImportError can be raised"""
        with pytest.raises(BulkImportError):
            raise BulkImportError("Test error message")

    def test_exception_message(self):
        """Test exception message is preserved"""
        try:
            raise BulkImportError("Custom error message")
        except BulkImportError as e:
            assert str(e) == "Custom error message"


class TestParseCSVContent:
    """Tests for parse_csv_content function"""

    def test_valid_csv_parsing(self):
        """Test parsing valid CSV content"""
        csv_content = "tool_number,serial_number,description\nT001,SN001,Test Tool\nT002,SN002,Another Tool"
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert errors == []
        assert len(rows) == 2
        assert rows[0]["tool_number"] == "T001"
        assert rows[0]["serial_number"] == "SN001"
        assert rows[0]["description"] == "Test Tool"
        assert rows[0]["_row_number"] == 2
        assert rows[1]["_row_number"] == 3

    def test_empty_csv(self):
        """Test parsing empty CSV"""
        csv_content = ""
        expected_headers = ["tool_number", "serial_number"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert rows == []
        assert len(errors) == 1
        assert "empty or invalid" in errors[0]

    def test_missing_required_headers(self):
        """Test parsing CSV with missing headers"""
        csv_content = "tool_number,description\nT001,Test"
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert rows == []
        assert len(errors) == 1
        assert "Missing required headers" in errors[0]
        assert "serial_number" in errors[0]

    def test_csv_with_extra_headers(self):
        """Test parsing CSV with extra headers is allowed"""
        csv_content = "tool_number,serial_number,description,extra_field\nT001,SN001,Test,Extra"
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert errors == []
        assert len(rows) == 1
        assert rows[0]["extra_field"] == "Extra"

    def test_csv_with_empty_values(self):
        """Test parsing CSV with empty values"""
        csv_content = "tool_number,serial_number,description\nT001,,Test Tool"
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert errors == []
        assert len(rows) == 1
        assert rows[0]["serial_number"] == ""

    def test_csv_with_whitespace(self):
        """Test that CSV values are sanitized"""
        csv_content = "tool_number,serial_number,description\n  T001  ,  SN001  ,  Test Tool  "
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        assert errors == []
        assert len(rows) == 1
        # Values should be sanitized by sanitize_csv_cell
        assert "T001" in rows[0]["tool_number"]

    def test_csv_with_none_values(self):
        """Test parsing CSV handles None values"""
        csv_content = "tool_number,serial_number,description\nT001,SN001,Test"
        expected_headers = ["tool_number", "serial_number", "description"]

        rows, errors = parse_csv_content(csv_content, expected_headers)

        # Just verify it parses correctly
        assert errors == []
        assert len(rows) == 1

    def test_csv_parsing_exception(self):
        """Test handling of CSV parsing exceptions"""
        # Create a mock that raises an exception
        with patch('utils.bulk_import.io.StringIO') as mock_stringio:
            mock_stringio.side_effect = Exception("CSV parsing error")

            rows, errors = parse_csv_content("invalid", ["header"])

            assert rows == []
            assert len(errors) == 1
            assert "Error parsing CSV file" in errors[0]


class TestValidateToolData:
    """Tests for validate_tool_data function"""

    def test_valid_tool_data(self):
        """Test validation of valid tool data"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Test Tool",
            "condition": "good",
            "location": "Lab A",
            "category": "General",
            "status": "available",
            "requires_calibration": "false",
            "calibration_frequency_days": "",
            "warehouse_id": ""
        }

        result = validate_tool_data(row_data)

        assert result["tool_number"] == "T001"
        assert result["serial_number"] == "SN001"
        assert result["description"] == "Test Tool"
        assert result["requires_calibration"] is False
        assert result["calibration_frequency_days"] is None
        assert result["warehouse_id"] is None

    def test_tool_data_with_calibration_enabled(self):
        """Test tool with calibration enabled"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Calibrated Tool",
            "requires_calibration": "true",
            "calibration_frequency_days": "90"
        }

        result = validate_tool_data(row_data)

        assert result["requires_calibration"] is True
        assert result["calibration_frequency_days"] == 90

    def test_tool_data_with_calibration_yes(self):
        """Test tool with calibration set to 'yes'"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool",
            "requires_calibration": "yes",
            "calibration_frequency_days": "30"
        }

        result = validate_tool_data(row_data)

        assert result["requires_calibration"] is True

    def test_tool_data_with_calibration_one(self):
        """Test tool with calibration set to '1'"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool",
            "requires_calibration": "1",
            "calibration_frequency_days": "60"
        }

        result = validate_tool_data(row_data)

        assert result["requires_calibration"] is True

    def test_tool_data_with_valid_warehouse_id(self):
        """Test tool with valid warehouse_id"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool",
            "warehouse_id": "5"
        }

        result = validate_tool_data(row_data)

        assert result["warehouse_id"] == 5

    def test_tool_data_with_invalid_warehouse_id(self):
        """Test tool with invalid warehouse_id"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool",
            "warehouse_id": "invalid"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_tool_data(row_data)

        assert "Invalid warehouse_id" in str(exc_info.value)

    def test_tool_data_with_invalid_calibration_frequency(self):
        """Test tool with invalid calibration frequency"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool",
            "requires_calibration": "true",
            "calibration_frequency_days": "not_a_number"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_tool_data(row_data)

        assert "Invalid calibration frequency" in str(exc_info.value)

    def test_tool_data_with_defaults(self):
        """Test tool data uses default values"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Tool"
        }

        result = validate_tool_data(row_data)

        assert result["condition"] == "good"
        assert result["category"] == "General"
        assert result["status"] == "available"

    def test_tool_data_formula_neutralization(self):
        """Test that CSV formula injection is neutralized"""
        row_data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "=CMD('malicious')"
        }

        result = validate_tool_data(row_data)

        # Formula should be neutralized in description field
        assert not result["description"].startswith("=")


class TestValidateChemicalData:
    """Tests for validate_chemical_data function"""

    def test_valid_chemical_data(self):
        """Test validation of valid chemical data"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "description": "Test Chemical",
            "manufacturer": "TestCo",
            "quantity": "10",
            "unit": "ml",
            "location": "Storage A",
            "category": "General",
            "expiration_date": "2025-12-31",
            "msds_url": "https://example.com/msds",
            "warehouse_id": ""
        }

        result = validate_chemical_data(row_data)

        assert result["part_number"] == "CHEM001"
        assert result["lot_number"] == "LOT001"
        assert result["quantity"] == 10
        assert result["expiration_date"] == date(2025, 12, 31)
        assert result["msds_url"] == "https://example.com/msds"

    def test_chemical_data_empty_msds_url(self):
        """Test that empty MSDS URL becomes None"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "msds_url": ""
        }

        result = validate_chemical_data(row_data)

        assert result["msds_url"] is None

    def test_chemical_data_valid_warehouse_id(self):
        """Test chemical with valid warehouse_id"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "warehouse_id": "3"
        }

        result = validate_chemical_data(row_data)

        assert result["warehouse_id"] == 3

    def test_chemical_data_invalid_warehouse_id(self):
        """Test chemical with invalid warehouse_id"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "warehouse_id": "abc"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_chemical_data(row_data)

        assert "Invalid warehouse_id" in str(exc_info.value)

    def test_chemical_data_valid_quantity_integer(self):
        """Test chemical with valid integer quantity"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "100",
            "unit": "each"
        }

        result = validate_chemical_data(row_data)

        assert result["quantity"] == 100

    def test_chemical_data_valid_quantity_float_whole_number(self):
        """Test chemical with float quantity that is whole number"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "50.0",
            "unit": "each"
        }

        result = validate_chemical_data(row_data)

        assert result["quantity"] == 50

    def test_chemical_data_invalid_quantity_decimal(self):
        """Test chemical with decimal quantity"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "10.5",
            "unit": "each"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_chemical_data(row_data)

        assert "must be a whole number" in str(exc_info.value)

    def test_chemical_data_invalid_quantity_non_numeric(self):
        """Test chemical with non-numeric quantity"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "not_a_number",
            "unit": "each"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_chemical_data(row_data)

        assert "Invalid quantity" in str(exc_info.value)

    def test_chemical_data_empty_quantity(self):
        """Test chemical with empty quantity fails validation"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "",
            "unit": "each"
        }

        # Empty quantity defaults to 0, which is considered falsy and fails required field validation
        with pytest.raises(ValidationError) as exc_info:
            validate_chemical_data(row_data)

        assert "quantity" in str(exc_info.value)

    def test_chemical_data_expiration_date_format_iso(self):
        """Test chemical with ISO date format"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "expiration_date": "2025-06-15"
        }

        result = validate_chemical_data(row_data)

        assert result["expiration_date"] == date(2025, 6, 15)

    def test_chemical_data_expiration_date_format_us(self):
        """Test chemical with US date format (MM/DD/YYYY)"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "expiration_date": "06/15/2025"
        }

        result = validate_chemical_data(row_data)

        assert result["expiration_date"] == date(2025, 6, 15)

    def test_chemical_data_expiration_date_format_european(self):
        """Test chemical with European date format (DD/MM/YYYY)"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "expiration_date": "15/06/2025"
        }

        result = validate_chemical_data(row_data)

        assert result["expiration_date"] == date(2025, 6, 15)

    def test_chemical_data_invalid_expiration_date(self):
        """Test chemical with invalid expiration date format"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "expiration_date": "invalid-date"
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_chemical_data(row_data)

        assert "Invalid expiration date" in str(exc_info.value)

    def test_chemical_data_no_expiration_date(self):
        """Test chemical without expiration date"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each",
            "expiration_date": ""
        }

        result = validate_chemical_data(row_data)

        assert result["expiration_date"] is None

    def test_chemical_data_formula_neutralization(self):
        """Test that CSV formula injection is neutralized"""
        row_data = {
            "part_number": "=SUM(A1:A10)",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each"
        }

        result = validate_chemical_data(row_data)

        # Formula should be neutralized
        assert not result["part_number"].startswith("=")

    def test_chemical_data_with_defaults(self):
        """Test chemical data uses default values"""
        row_data = {
            "part_number": "CHEM001",
            "lot_number": "LOT001",
            "quantity": "5",
            "unit": "each"
        }

        result = validate_chemical_data(row_data)

        assert result["category"] == "General"
        assert result["description"] == ""
        assert result["manufacturer"] == ""


class TestCheckDuplicates:
    """Tests for duplicate checking functions"""

    def test_check_duplicate_tool_no_duplicate(self, db_session):
        """Test check_duplicate_tool when no duplicate exists"""
        tool_data = {
            "tool_number": "UNIQUE001",
            "serial_number": "UNIQUE_SN"
        }

        result = check_duplicate_tool(tool_data)

        assert result is None

    def test_check_duplicate_tool_with_duplicate(self, db_session, test_tool):
        """Test check_duplicate_tool when duplicate exists"""
        tool_data = {
            "tool_number": test_tool.tool_number,
            "serial_number": test_tool.serial_number
        }

        result = check_duplicate_tool(tool_data)

        assert result is not None
        assert result.id == test_tool.id

    def test_check_duplicate_chemical_no_duplicate(self, db_session):
        """Test check_duplicate_chemical when no duplicate exists"""
        chemical_data = {
            "part_number": "UNIQUE_PART",
            "lot_number": "UNIQUE_LOT"
        }

        result = check_duplicate_chemical(chemical_data)

        assert result is None

    def test_check_duplicate_chemical_with_duplicate(self, db_session, test_chemical):
        """Test check_duplicate_chemical when duplicate exists"""
        chemical_data = {
            "part_number": test_chemical.part_number,
            "lot_number": test_chemical.lot_number
        }

        result = check_duplicate_chemical(chemical_data)

        assert result is not None
        assert result.id == test_chemical.id


class TestBulkImportTools:
    """Tests for bulk_import_tools function"""

    def test_bulk_import_tools_success(self, db_session):
        """Test successful bulk import of tools"""
        csv_content = """tool_number,serial_number,description,condition,location,category,status
T001,SN001,Tool One,good,Lab A,General,available
T002,SN002,Tool Two,excellent,Lab B,Testing,available"""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 2
        assert result.error_count == 0
        assert len(result.created_items) == 2

    def test_bulk_import_tools_with_parse_errors(self, db_session):
        """Test bulk import with CSV parse errors"""
        csv_content = "invalid_header\ndata"

        result = bulk_import_tools(csv_content)

        assert result.success_count == 0
        assert result.error_count > 0
        assert "Missing required headers" in result.errors[0]["error"]

    def test_bulk_import_tools_skip_duplicates(self, db_session, test_tool):
        """Test bulk import skips duplicates when skip_duplicates=True"""
        csv_content = f"""tool_number,serial_number,description
{test_tool.tool_number},{test_tool.serial_number},Duplicate Tool
NEW001,NEW_SN,New Tool"""

        result = bulk_import_tools(csv_content, skip_duplicates=True)

        assert result.success_count == 1
        assert len(result.skipped_items) == 1
        assert "already exists" in result.skipped_items[0]["reason"]

    def test_bulk_import_tools_error_on_duplicates(self, db_session, test_tool):
        """Test bulk import errors on duplicates when skip_duplicates=False"""
        csv_content = f"""tool_number,serial_number,description
{test_tool.tool_number},{test_tool.serial_number},Duplicate Tool"""

        result = bulk_import_tools(csv_content, skip_duplicates=False)

        assert result.success_count == 0
        assert result.error_count == 1
        assert "Duplicate tool" in result.errors[0]["error"]

    def test_bulk_import_tools_validation_error(self, db_session):
        """Test bulk import handles validation errors"""
        csv_content = """tool_number,serial_number,description,warehouse_id
T001,SN001,Tool,invalid_warehouse"""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 0
        assert result.error_count == 1
        assert "Invalid warehouse_id" in result.errors[0]["error"]

    def test_bulk_import_tools_with_calibration(self, db_session):
        """Test bulk import tools with calibration requirements"""
        csv_content = """tool_number,serial_number,description,requires_calibration,calibration_frequency_days
T001,SN001,Calibrated Tool,true,90
T002,SN002,Non-Calibrated Tool,false,"""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 2

        # Verify calibration status was set correctly
        from models import Tool
        calibrated_tool = Tool.query.filter_by(tool_number="T001").first()
        non_calibrated_tool = Tool.query.filter_by(tool_number="T002").first()

        assert calibrated_tool.calibration_status == "due_soon"
        assert non_calibrated_tool.calibration_status == "not_applicable"

    def test_bulk_import_tools_empty_csv(self, db_session):
        """Test bulk import with empty CSV"""
        csv_content = ""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 0
        assert result.error_count > 0

    def test_bulk_import_tools_no_successful_imports(self, db_session):
        """Test bulk import with all failures rolls back"""
        csv_content = """tool_number,serial_number,description,warehouse_id
T001,SN001,Tool,invalid"""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 0
        assert result.error_count == 1

    def test_bulk_import_tools_commit_failure(self, db_session):
        """Test bulk import handles database commit failure"""
        csv_content = """tool_number,serial_number,description
T001,SN001,Tool One"""

        with patch('utils.bulk_import.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database commit failed")

            result = bulk_import_tools(csv_content)

            # Should have converted success to error
            assert result.success_count == 0
            assert len(result.created_items) == 0
            # Error added for commit failure
            assert any("Database commit failed" in err["error"] for err in result.errors)

    def test_bulk_import_tools_unexpected_error(self, db_session):
        """Test bulk import handles unexpected errors in row processing"""
        csv_content = """tool_number,serial_number,description
T001,SN001,Tool"""

        with patch('utils.bulk_import.validate_tool_data') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected processing error")

            result = bulk_import_tools(csv_content)

            assert result.error_count == 1
            assert "Unexpected error" in result.errors[0]["error"]


class TestBulkImportChemicals:
    """Tests for bulk_import_chemicals function"""

    def test_bulk_import_chemicals_success(self, db_session):
        """Test successful bulk import of chemicals"""
        csv_content = """part_number,lot_number,quantity,unit,description,manufacturer
CHEM001,LOT001,10,each,Chemical One,ManufacturerA
CHEM002,LOT002,20,ml,Chemical Two,ManufacturerB"""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 2
        assert result.error_count == 0
        assert len(result.created_items) == 2

    def test_bulk_import_chemicals_with_parse_errors(self, db_session):
        """Test bulk import with CSV parse errors"""
        csv_content = "wrong_header\ndata"

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 0
        assert result.error_count > 0

    def test_bulk_import_chemicals_skip_duplicates(self, db_session, test_chemical):
        """Test bulk import skips duplicates when skip_duplicates=True"""
        csv_content = f"""part_number,lot_number,quantity,unit
{test_chemical.part_number},{test_chemical.lot_number},50,each
NEW_CHEM,NEW_LOT,30,each"""

        result = bulk_import_chemicals(csv_content, skip_duplicates=True)

        assert result.success_count == 1
        assert len(result.skipped_items) == 1
        assert "already exists" in result.skipped_items[0]["reason"]

    def test_bulk_import_chemicals_error_on_duplicates(self, db_session, test_chemical):
        """Test bulk import errors on duplicates when skip_duplicates=False"""
        csv_content = f"""part_number,lot_number,quantity,unit
{test_chemical.part_number},{test_chemical.lot_number},50,each"""

        result = bulk_import_chemicals(csv_content, skip_duplicates=False)

        assert result.success_count == 0
        assert result.error_count == 1
        assert "Duplicate chemical" in result.errors[0]["error"]

    def test_bulk_import_chemicals_validation_error(self, db_session):
        """Test bulk import handles validation errors"""
        csv_content = """part_number,lot_number,quantity,unit,warehouse_id
CHEM001,LOT001,10,each,invalid"""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 0
        assert result.error_count == 1
        assert "Invalid warehouse_id" in result.errors[0]["error"]

    def test_bulk_import_chemicals_empty_csv(self, db_session):
        """Test bulk import with empty CSV"""
        csv_content = ""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 0
        assert result.error_count > 0

    def test_bulk_import_chemicals_no_successful_imports(self, db_session):
        """Test bulk import with all failures"""
        csv_content = """part_number,lot_number,quantity,unit
CHEM001,LOT001,invalid_qty,each"""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 0
        assert result.error_count == 1

    def test_bulk_import_chemicals_commit_failure(self, db_session):
        """Test bulk import handles database commit failure"""
        csv_content = """part_number,lot_number,quantity,unit
CHEM001,LOT001,10,each"""

        with patch('utils.bulk_import.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            result = bulk_import_chemicals(csv_content)

            assert result.success_count == 0
            assert len(result.created_items) == 0
            assert any("Database commit failed" in err["error"] for err in result.errors)

    def test_bulk_import_chemicals_unexpected_error(self, db_session):
        """Test bulk import handles unexpected errors"""
        csv_content = """part_number,lot_number,quantity,unit
CHEM001,LOT001,10,each"""

        with patch('utils.bulk_import.validate_chemical_data') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")

            result = bulk_import_chemicals(csv_content)

            assert result.error_count == 1
            assert "Unexpected error" in result.errors[0]["error"]

    def test_bulk_import_chemicals_with_expiration(self, db_session):
        """Test bulk import chemicals with expiration dates"""
        csv_content = """part_number,lot_number,quantity,unit,expiration_date
CHEM001,LOT001,10,each,2025-12-31"""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 1

        from models import Chemical
        chemical = Chemical.query.filter_by(part_number="CHEM001").first()
        # Model stores as datetime, but we compare date portion
        assert chemical.expiration_date.year == 2025
        assert chemical.expiration_date.month == 12
        assert chemical.expiration_date.day == 31


class TestGenerateTemplates:
    """Tests for template generation functions"""

    def test_generate_tool_template(self):
        """Test generating tool CSV template"""
        template = generate_tool_template()

        # Parse the template to verify structure
        csv_file = io.StringIO(template)
        reader = csv.reader(csv_file)
        headers = next(reader)
        sample_data = next(reader)

        # Check headers
        assert "tool_number" in headers
        assert "serial_number" in headers
        assert "description" in headers
        assert "condition" in headers
        assert "location" in headers
        assert "category" in headers
        assert "status" in headers
        assert "requires_calibration" in headers
        assert "calibration_frequency_days" in headers
        assert "warehouse_id" in headers

        # Check sample data exists
        assert len(sample_data) == len(headers)
        assert sample_data[0] == "T001"
        assert sample_data[1] == "SN001"

    def test_generate_chemical_template(self):
        """Test generating chemical CSV template"""
        template = generate_chemical_template()

        # Parse the template to verify structure
        csv_file = io.StringIO(template)
        reader = csv.reader(csv_file)
        headers = next(reader)
        sample_data = next(reader)

        # Check headers
        assert "part_number" in headers
        assert "lot_number" in headers
        assert "description" in headers
        assert "manufacturer" in headers
        assert "quantity" in headers
        assert "unit" in headers
        assert "location" in headers
        assert "category" in headers
        assert "expiration_date" in headers
        assert "msds_url" in headers
        assert "warehouse_id" in headers

        # Check sample data exists
        assert len(sample_data) == len(headers)
        assert sample_data[0] == "CHEM001"
        assert sample_data[1] == "LOT001"

    def test_template_is_valid_csv(self):
        """Test that generated templates are valid CSV"""
        tool_template = generate_tool_template()
        chemical_template = generate_chemical_template()

        # Should be able to parse both without errors
        tool_rows, tool_errors = parse_csv_content(
            tool_template,
            ["tool_number", "serial_number", "description"]
        )
        chemical_rows, chemical_errors = parse_csv_content(
            chemical_template,
            ["part_number", "lot_number", "quantity", "unit"]
        )

        assert tool_errors == []
        assert chemical_errors == []
        assert len(tool_rows) == 1
        assert len(chemical_rows) == 1


class TestIntegration:
    """Integration tests for bulk import functionality"""

    def test_full_tool_import_workflow(self, db_session):
        """Test complete tool import workflow"""
        # Generate template
        template = generate_tool_template()

        # Modify template with actual data
        csv_content = """tool_number,serial_number,description,condition,location,category,status,requires_calibration,calibration_frequency_days,warehouse_id
INT001,SN_INT001,Integration Test Tool,good,Test Lab,Integration,available,true,60,"""

        # Import tools
        result = bulk_import_tools(csv_content)

        # Verify results
        assert result.success_count == 1
        assert result.error_count == 0

        # Verify tool was actually created in database
        from models import Tool
        tool = Tool.query.filter_by(tool_number="INT001").first()
        assert tool is not None
        assert tool.description == "Integration Test Tool"
        assert tool.requires_calibration is True
        assert tool.calibration_frequency_days == 60

    def test_full_chemical_import_workflow(self, db_session):
        """Test complete chemical import workflow"""
        csv_content = """part_number,lot_number,description,manufacturer,quantity,unit,location,category,expiration_date,msds_url,warehouse_id
INT_CHEM001,INT_LOT001,Integration Chemical,TestCo,25,each,Storage B,Integration,2026-01-01,,"""

        result = bulk_import_chemicals(csv_content)

        assert result.success_count == 1
        assert result.error_count == 0

        # Verify chemical was created
        from models import Chemical
        chemical = Chemical.query.filter_by(part_number="INT_CHEM001").first()
        assert chemical is not None
        assert chemical.quantity == 25
        # Model stores as datetime, compare date portion
        assert chemical.expiration_date.year == 2026
        assert chemical.expiration_date.month == 1
        assert chemical.expiration_date.day == 1

    def test_mixed_success_and_errors(self, db_session):
        """Test import with mix of successful and failed rows"""
        csv_content = """tool_number,serial_number,description,warehouse_id
VALID001,SN001,Valid Tool,
INVALID002,SN002,Invalid Tool,not_a_number
VALID003,SN003,Another Valid Tool,"""

        result = bulk_import_tools(csv_content)

        assert result.success_count == 2
        assert result.error_count == 1
        assert "Invalid warehouse_id" in result.errors[0]["error"]

    def test_result_to_dict_complete(self, db_session):
        """Test that result.to_dict() contains all information"""
        csv_content = """tool_number,serial_number,description,warehouse_id
T001,SN001,Tool One,
T002,SN002,Tool Two,invalid"""

        result = bulk_import_tools(csv_content)
        result_dict = result.to_dict()

        # Verify all keys are present
        assert "success_count" in result_dict
        assert "error_count" in result_dict
        assert "warning_count" in result_dict
        assert "skipped_count" in result_dict
        assert "errors" in result_dict
        assert "warnings" in result_dict
        assert "created_items" in result_dict
        assert "skipped_items" in result_dict

        # Verify counts match
        assert result_dict["success_count"] == 1
        assert result_dict["error_count"] == 1
