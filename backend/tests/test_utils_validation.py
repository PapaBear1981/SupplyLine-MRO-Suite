"""
Tests for Utils Validation Module

This module tests the comprehensive input validation utilities including:
- String sanitization
- Type validation
- Constraint validation
- Date validation
- Schema-based validation
- Format validators (serial numbers, lot numbers, etc.)
"""

import pytest
from datetime import datetime

from utils.validation import (
    sanitize_string,
    validate_types,
    validate_constraints,
    validate_dates,
    validate_schema,
    validate_serial_number_format,
    validate_lot_number_format,
    validate_warehouse_id,
    TOOL_SCHEMA,
    CHEMICAL_SCHEMA,
    USER_SCHEMA,
    CHEMICAL_ISSUANCE_SCHEMA,
    CALIBRATION_SCHEMA,
    CHECKOUT_SCHEMA,
    CYCLE_COUNT_SCHEDULE_SCHEMA,
    CYCLE_COUNT_RESULT_SCHEMA,
)
from utils.error_handler import ValidationError


class TestSanitizeString:
    """Test string sanitization functionality"""

    def test_sanitize_basic_string(self):
        """Test basic string sanitization"""
        result = sanitize_string("Hello World")
        assert result == "Hello World"

    def test_sanitize_removes_dangerous_chars(self):
        """Test removal of dangerous characters"""
        input_str = '<script>alert("XSS")</script>'
        result = sanitize_string(input_str)
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result

    def test_sanitize_respects_max_length(self):
        """Test max length enforcement"""
        input_str = "A" * 500
        result = sanitize_string(input_str, max_length=100)
        assert len(result) == 100

    def test_sanitize_trims_whitespace(self):
        """Test whitespace trimming"""
        input_str = "   Hello World   "
        result = sanitize_string(input_str)
        assert result == "Hello World"

    def test_sanitize_non_string_input(self):
        """Test conversion of non-string input"""
        result = sanitize_string(12345)
        assert result == "12345"
        assert isinstance(result, str)

    def test_sanitize_with_html_allowed(self):
        """Test sanitization with HTML allowed"""
        input_str = "<b>Bold</b>"
        result = sanitize_string(input_str, allow_html=True)
        assert "<b>" in result

    def test_sanitize_escapes_remaining_chars(self):
        """Test that remaining chars are escaped"""
        input_str = "Test&More"
        result = sanitize_string(input_str)
        assert "&amp;" in result

    def test_sanitize_backslash_removal(self):
        """Test backslash removal"""
        input_str = "Path\\to\\file"
        result = sanitize_string(input_str)
        assert "\\" not in result

    def test_sanitize_quote_removal(self):
        """Test quote removal"""
        input_str = "Test'String\"Here"
        result = sanitize_string(input_str)
        assert "'" not in result
        assert '"' not in result


class TestValidateTypes:
    """Test type validation functionality"""

    def test_validate_string_type(self):
        """Test string type validation"""
        data = {"name": "John Doe"}
        schema = {"name": str}
        # Should not raise
        validate_types(data, schema)

    def test_validate_int_type(self):
        """Test integer type validation"""
        data = {"user_id": 123}
        schema = {"user_id": int}
        validate_types(data, schema)

    def test_validate_float_type(self):
        """Test float type validation"""
        data = {"quantity": 10.5}
        schema = {"quantity": (int, float)}
        validate_types(data, schema)

    def test_validate_bool_type(self):
        """Test boolean type validation"""
        data = {"is_active": True}
        schema = {"is_active": bool}
        validate_types(data, schema)

    def test_validate_wrong_type_raises(self):
        """Test that wrong type raises ValidationError"""
        data = {"name": 123}  # Should be string
        schema = {"name": str}
        with pytest.raises(ValidationError):
            validate_types(data, schema)

    def test_validate_missing_field_ignored(self):
        """Test that missing fields are ignored"""
        data = {}
        schema = {"name": str}
        # Should not raise
        validate_types(data, schema)

    def test_validate_none_value_ignored(self):
        """Test that None values are ignored"""
        data = {"name": None}
        schema = {"name": str}
        validate_types(data, schema)


class TestValidateConstraints:
    """Test constraint validation functionality"""

    def test_validate_min_value_pass(self):
        """Test minimum value constraint passes"""
        data = {"quantity": 10}
        schema = {"quantity": {"min": 0}}
        validate_constraints(data, schema)

    def test_validate_min_value_fail(self):
        """Test minimum value constraint fails"""
        data = {"quantity": -5}
        schema = {"quantity": {"min": 0}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_max_value_pass(self):
        """Test maximum value constraint passes"""
        data = {"quantity": 50}
        schema = {"quantity": {"max": 100}}
        validate_constraints(data, schema)

    def test_validate_max_value_fail(self):
        """Test maximum value constraint fails"""
        data = {"quantity": 150}
        schema = {"quantity": {"max": 100}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_min_length_pass(self):
        """Test minimum length constraint passes"""
        data = {"name": "John"}
        schema = {"name": {"min_length": 2}}
        validate_constraints(data, schema)

    def test_validate_min_length_fail(self):
        """Test minimum length constraint fails"""
        data = {"name": "J"}
        schema = {"name": {"min_length": 2}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_max_length_pass(self):
        """Test maximum length constraint passes"""
        data = {"name": "John Doe"}
        schema = {"name": {"max_length": 100}}
        validate_constraints(data, schema)

    def test_validate_max_length_fail(self):
        """Test maximum length constraint fails"""
        data = {"name": "A" * 200}
        schema = {"name": {"max_length": 100}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_choices_pass(self):
        """Test choices constraint passes"""
        data = {"status": "available"}
        schema = {"status": {"choices": ["available", "checked_out", "maintenance"]}}
        validate_constraints(data, schema)

    def test_validate_choices_fail(self):
        """Test choices constraint fails"""
        data = {"status": "invalid"}
        schema = {"status": {"choices": ["available", "checked_out", "maintenance"]}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_pattern_pass(self):
        """Test pattern constraint passes"""
        data = {"tool_number": "T001"}
        schema = {"tool_number": {"pattern": r"^T\d{3}$"}}
        validate_constraints(data, schema)

    def test_validate_pattern_fail(self):
        """Test pattern constraint fails"""
        data = {"tool_number": "invalid"}
        schema = {"tool_number": {"pattern": r"^T\d{3}$"}}
        with pytest.raises(ValidationError):
            validate_constraints(data, schema)

    def test_validate_missing_field_ignored(self):
        """Test that missing fields are ignored"""
        data = {}
        schema = {"name": {"min_length": 2}}
        validate_constraints(data, schema)

    def test_validate_none_value_ignored(self):
        """Test that None values are ignored"""
        data = {"name": None}
        schema = {"name": {"min_length": 2}}
        validate_constraints(data, schema)


class TestValidateDates:
    """Test date validation functionality"""

    def test_validate_iso_date_string(self):
        """Test ISO format date string conversion"""
        data = {"created_at": "2024-12-31T23:59:59"}
        validate_dates(data, ["created_at"])
        assert isinstance(data["created_at"], datetime)

    def test_validate_date_with_z_suffix(self):
        """Test date with Z suffix (UTC)"""
        data = {"expiration_date": "2024-12-31T23:59:59Z"}
        validate_dates(data, ["expiration_date"])
        assert isinstance(data["expiration_date"], datetime)

    def test_validate_date_with_timezone(self):
        """Test date with timezone info"""
        data = {"calibration_date": "2024-12-31T23:59:59+00:00"}
        validate_dates(data, ["calibration_date"])
        assert isinstance(data["calibration_date"], datetime)

    def test_validate_invalid_date_format(self):
        """Test invalid date format raises error"""
        data = {"created_at": "not-a-date"}
        with pytest.raises(ValidationError):
            validate_dates(data, ["created_at"])

    def test_validate_empty_date_field(self):
        """Test empty date field is ignored"""
        data = {"created_at": None}
        validate_dates(data, ["created_at"])
        assert data["created_at"] is None

    def test_validate_missing_date_field(self):
        """Test missing date field is ignored"""
        data = {}
        validate_dates(data, ["created_at"])
        # Should not raise


class TestToolSchemaValidation:
    """Test tool schema validation"""

    def test_validate_tool_complete(self):
        """Test complete tool validation"""
        data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Test Tool",
            "condition": "excellent",
            "location": "Lab A",
            "category": "Testing",
            "status": "available"
        }
        result = validate_schema(data, "tool")
        assert result["tool_number"] == "T001"

    def test_validate_tool_required_only(self):
        """Test tool validation with only required fields"""
        data = {
            "tool_number": "T002",
            "serial_number": "SN002",
            "description": "Minimal Tool"
        }
        result = validate_schema(data, "tool")
        assert "description" in result

    def test_validate_tool_missing_required(self):
        """Test tool validation with missing required field"""
        data = {
            "tool_number": "T003"
            # Missing serial_number and description
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "tool")

    def test_validate_tool_invalid_condition(self):
        """Test tool validation with invalid condition"""
        data = {
            "tool_number": "T004",
            "serial_number": "SN004",
            "description": "Bad Condition Tool",
            "condition": "invalid"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "tool")

    def test_validate_tool_invalid_status(self):
        """Test tool validation with invalid status"""
        data = {
            "tool_number": "T005",
            "serial_number": "SN005",
            "description": "Bad Status Tool",
            "status": "unknown"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "tool")


class TestChemicalSchemaValidation:
    """Test chemical schema validation"""

    def test_validate_chemical_complete(self):
        """Test complete chemical validation"""
        data = {
            "part_number": "PN001",
            "lot_number": "LOT001",
            "quantity": 100,
            "unit": "ml",
            "description": "Test Chemical",
            "manufacturer": "ACME Corp",
            "location": "Storage A",
            "status": "available",
            "minimum_stock_level": 10
        }
        result = validate_schema(data, "chemical")
        assert result["quantity"] == 100

    def test_validate_chemical_required_only(self):
        """Test chemical validation with only required fields"""
        data = {
            "part_number": "PN002",
            "lot_number": "LOT002",
            "quantity": 50,
            "unit": "g"
        }
        result = validate_schema(data, "chemical")
        assert result["unit"] == "g"

    def test_validate_chemical_invalid_unit(self):
        """Test chemical validation with invalid unit"""
        data = {
            "part_number": "PN003",
            "lot_number": "LOT003",
            "quantity": 25,
            "unit": "invalid_unit"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "chemical")

    def test_validate_chemical_negative_quantity(self):
        """Test chemical validation with negative quantity"""
        data = {
            "part_number": "PN004",
            "lot_number": "LOT004",
            "quantity": -10,
            "unit": "ml"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "chemical")

    def test_validate_chemical_with_dates(self):
        """Test chemical validation with date fields"""
        data = {
            "part_number": "PN005",
            "lot_number": "LOT005",
            "quantity": 75,
            "unit": "oz",
            "expiration_date": "2025-12-31T23:59:59Z"
        }
        result = validate_schema(data, "chemical")
        assert isinstance(result["expiration_date"], datetime)


class TestUserSchemaValidation:
    """Test user schema validation"""

    def test_validate_user_complete(self):
        """Test complete user validation"""
        data = {
            "name": "John Doe",
            "employee_number": "EMP001",
            "department": "Engineering",
            "password": "SecurePass123!",
            "is_admin": False,
            "is_active": True
        }
        result = validate_schema(data, "user")
        assert result["name"] == "John Doe"

    def test_validate_user_required_only(self):
        """Test user validation with only required fields"""
        data = {
            "name": "Jane Smith",
            "employee_number": "EMP002",
            "department": "Quality"
        }
        result = validate_schema(data, "user")
        assert result["department"] == "Quality"

    def test_validate_user_invalid_department(self):
        """Test user validation with invalid department"""
        data = {
            "name": "Bob Wilson",
            "employee_number": "EMP003",
            "department": "InvalidDept"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "user")

    def test_validate_user_short_name(self):
        """Test user validation with name too short"""
        data = {
            "name": "J",
            "employee_number": "EMP004",
            "department": "IT"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "user")

    def test_validate_user_invalid_employee_number(self):
        """Test user validation with invalid employee number pattern"""
        data = {
            "name": "Test User",
            "employee_number": "invalid@123",  # Contains invalid characters
            "department": "Admin"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "user")


class TestChemicalIssuanceSchemaValidation:
    """Test chemical issuance schema validation"""

    def test_validate_issuance_complete(self):
        """Test complete issuance validation"""
        data = {
            "quantity": 5,
            "hangar": "Hangar A",
            "user_id": 1,
            "purpose": "Maintenance work"
        }
        result = validate_schema(data, "chemical_issuance")
        assert result["quantity"] == 5

    def test_validate_issuance_required_only(self):
        """Test issuance validation with only required fields"""
        data = {
            "quantity": 3,
            "hangar": "Hangar B",
            "user_id": 2
        }
        result = validate_schema(data, "chemical_issuance")
        assert result["hangar"] == "Hangar B"

    def test_validate_issuance_zero_quantity(self):
        """Test issuance validation with zero quantity"""
        data = {
            "quantity": 0,
            "hangar": "Hangar C",
            "user_id": 3
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "chemical_issuance")

    def test_validate_issuance_invalid_user_id(self):
        """Test issuance validation with invalid user ID"""
        data = {
            "quantity": 2,
            "hangar": "Hangar D",
            "user_id": 0
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "chemical_issuance")


class TestCalibrationSchemaValidation:
    """Test calibration schema validation"""

    def test_validate_calibration_complete(self):
        """Test complete calibration validation"""
        data = {
            "calibration_date": "2024-12-15T10:00:00Z",
            "calibration_status": "pass",
            "next_calibration_date": "2025-12-15T10:00:00Z",
            "calibrated_by": "John Tech",
            "notes": "All tests passed",
            "certificate_number": "CERT-2024-001"
        }
        result = validate_schema(data, "calibration")
        assert result["calibration_status"] == "pass"

    def test_validate_calibration_required_only(self):
        """Test calibration validation with only required fields"""
        data = {
            "calibration_date": "2024-12-16T11:00:00Z",
            "calibration_status": "fail"
        }
        result = validate_schema(data, "calibration")
        assert isinstance(result["calibration_date"], datetime)

    def test_validate_calibration_invalid_status(self):
        """Test calibration validation with invalid status"""
        data = {
            "calibration_date": "2024-12-17T12:00:00Z",
            "calibration_status": "invalid"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "calibration")


class TestSerialNumberValidation:
    """Test serial number format validation"""

    def test_validate_serial_number_valid(self):
        """Test valid serial numbers"""
        valid_serials = ["SN001", "SERIAL-123", "AB_CD.123", "A1B2C3D4E5"]
        for serial in valid_serials:
            assert validate_serial_number_format(serial) is True

    def test_validate_serial_number_empty(self):
        """Test empty serial number"""
        with pytest.raises(ValidationError):
            validate_serial_number_format("")

    def test_validate_serial_number_whitespace(self):
        """Test whitespace-only serial number"""
        with pytest.raises(ValidationError):
            validate_serial_number_format("   ")

    def test_validate_serial_number_too_short(self):
        """Test serial number too short"""
        with pytest.raises(ValidationError):
            validate_serial_number_format("AB")

    def test_validate_serial_number_too_long(self):
        """Test serial number too long"""
        long_serial = "A" * 101
        with pytest.raises(ValidationError):
            validate_serial_number_format(long_serial)

    def test_validate_serial_number_invalid_chars(self):
        """Test serial number with invalid characters"""
        invalid_serials = ["SN@001", "SERIAL#123", "AB CD", "test!"]
        for serial in invalid_serials:
            with pytest.raises(ValidationError):
                validate_serial_number_format(serial)

    def test_validate_serial_number_with_spaces_trimmed(self):
        """Test that spaces are trimmed from serial number"""
        result = validate_serial_number_format("  SN001  ")
        assert result is True


class TestLotNumberValidation:
    """Test lot number format validation"""

    def test_validate_lot_number_valid(self):
        """Test valid lot numbers"""
        valid_lots = ["LOT001", "LOT-241231-0001", "BATCH_123.A"]
        for lot in valid_lots:
            assert validate_lot_number_format(lot) is True

    def test_validate_lot_number_empty(self):
        """Test empty lot number"""
        with pytest.raises(ValidationError):
            validate_lot_number_format("")

    def test_validate_lot_number_whitespace(self):
        """Test whitespace-only lot number"""
        with pytest.raises(ValidationError):
            validate_lot_number_format("   ")

    def test_validate_lot_number_too_short(self):
        """Test lot number too short"""
        with pytest.raises(ValidationError):
            validate_lot_number_format("AB")

    def test_validate_lot_number_too_long(self):
        """Test lot number too long"""
        long_lot = "L" * 101
        with pytest.raises(ValidationError):
            validate_lot_number_format(long_lot)

    def test_validate_lot_number_invalid_chars(self):
        """Test lot number with invalid characters"""
        invalid_lots = ["LOT@001", "BATCH#123", "LOT 001", "lot!"]
        for lot in invalid_lots:
            with pytest.raises(ValidationError):
                validate_lot_number_format(lot)


class TestWarehouseIdValidation:
    """Test warehouse ID validation"""

    def test_validate_warehouse_id_empty(self):
        """Test empty warehouse ID"""
        with pytest.raises(ValidationError):
            validate_warehouse_id(None)

    def test_validate_warehouse_id_zero(self):
        """Test zero warehouse ID"""
        with pytest.raises(ValidationError):
            validate_warehouse_id(0)

    def test_validate_warehouse_id_not_found(self, app, db_session):
        """Test non-existent warehouse ID"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                validate_warehouse_id(99999)
            assert "not found" in str(exc_info.value)

    def test_validate_warehouse_id_inactive(self, app, db_session):
        """Test inactive warehouse validation"""
        from models import Warehouse

        with app.app_context():
            # Create inactive warehouse
            warehouse = Warehouse(
                name="Inactive Warehouse",
                code="IW001",
                is_active=False
            )
            db_session.add(warehouse)
            db_session.commit()

            with pytest.raises(ValidationError) as exc_info:
                validate_warehouse_id(warehouse.id)
            assert "inactive" in str(exc_info.value)

    def test_validate_warehouse_id_active(self, app, db_session):
        """Test active warehouse validation"""
        from models import Warehouse

        with app.app_context():
            # Create active warehouse
            warehouse = Warehouse(
                name="Active Warehouse",
                code="AW001",
                is_active=True
            )
            db_session.add(warehouse)
            db_session.commit()

            result = validate_warehouse_id(warehouse.id)
            assert result.id == warehouse.id
            assert result.name == "Active Warehouse"


class TestCycleCountScheduleSchema:
    """Test cycle count schedule schema validation"""

    def test_validate_schedule_complete(self):
        """Test complete schedule validation"""
        data = {
            "name": "Daily Count",
            "frequency": "daily",
            "method": "ABC",
            "description": "Daily ABC analysis",
            "is_active": True
        }
        result = validate_schema(data, "cycle_count_schedule")
        assert result["name"] == "Daily Count"

    def test_validate_schedule_required_only(self):
        """Test schedule validation with only required fields"""
        data = {
            "name": "Monthly Count",
            "frequency": "monthly",
            "method": "random"
        }
        result = validate_schema(data, "cycle_count_schedule")
        assert result["frequency"] == "monthly"

    def test_validate_schedule_invalid_frequency(self):
        """Test schedule validation with invalid frequency"""
        data = {
            "name": "Invalid Schedule",
            "frequency": "hourly",
            "method": "ABC"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "cycle_count_schedule")

    def test_validate_schedule_invalid_method(self):
        """Test schedule validation with invalid method"""
        data = {
            "name": "Bad Method",
            "frequency": "weekly",
            "method": "invalid"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "cycle_count_schedule")


class TestCycleCountResultSchema:
    """Test cycle count result schema validation"""

    def test_validate_result_complete(self):
        """Test complete result validation"""
        data = {
            "actual_quantity": 50,
            "actual_location": "Bin A-1",
            "condition": "good",
            "notes": "Count verified"
        }
        result = validate_schema(data, "cycle_count_result")
        assert result["actual_quantity"] == 50

    def test_validate_result_required_only(self):
        """Test result validation with only required fields"""
        data = {
            "actual_quantity": 25
        }
        result = validate_schema(data, "cycle_count_result")
        assert result["actual_quantity"] == 25

    def test_validate_result_invalid_condition(self):
        """Test result validation with invalid condition"""
        data = {
            "actual_quantity": 30,
            "condition": "unknown"
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "cycle_count_result")

    def test_validate_result_negative_quantity(self):
        """Test result validation with negative quantity"""
        data = {
            "actual_quantity": -5
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "cycle_count_result")


class TestCheckoutSchemaValidation:
    """Test checkout schema validation"""

    def test_validate_checkout_complete(self):
        """Test complete checkout validation"""
        data = {
            "tool_id": 1,
            "user_id": 1,
            "expected_return_date": "2024-12-31T17:00:00Z",
            "notes": "Need for project A"
        }
        result = validate_schema(data, "checkout")
        assert result["tool_id"] == 1

    def test_validate_checkout_required_only(self):
        """Test checkout validation with only required fields"""
        data = {
            "tool_id": 2,
            "user_id": 3
        }
        result = validate_schema(data, "checkout")
        assert result["user_id"] == 3

    def test_validate_checkout_invalid_tool_id(self):
        """Test checkout validation with invalid tool ID"""
        data = {
            "tool_id": 0,
            "user_id": 1
        }
        with pytest.raises(ValidationError):
            validate_schema(data, "checkout")


class TestUnknownSchemaValidation:
    """Test validation with unknown schema"""

    def test_validate_unknown_schema(self):
        """Test validation with unknown schema name"""
        data = {"field": "value"}
        with pytest.raises(ValidationError):
            validate_schema(data, "unknown_schema")


class TestStringSanitizationInSchema:
    """Test string sanitization within schema validation"""

    def test_schema_sanitizes_strings(self):
        """Test that schema validation sanitizes string fields"""
        data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": '<script>alert("XSS")</script>Tool'
        }
        result = validate_schema(data, "tool")
        # Dangerous characters should be removed
        assert "<script>" not in result["description"]

    def test_schema_respects_max_length(self):
        """Test that schema validation respects max length"""
        data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "A" * 600  # Longer than max_length of 500
        }
        result = validate_schema(data, "tool")
        assert len(result["description"]) <= 500
