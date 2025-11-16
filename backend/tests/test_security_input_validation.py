"""
Tests for Security Input Validation Module

This module tests the input validation and sanitization functionality including:
- String sanitization (XSS prevention)
- Field validation patterns
- Schema-based validation
- Validation decorators
"""

import pytest
from flask import Flask, request, jsonify

from security.input_validation import (
    InputValidator,
    ValidationError,
    PATTERNS,
    ALLOWED_VALUES,
    VALIDATION_SCHEMAS,
    validate_request_data,
)


class TestStringSanitization:
    """Test string sanitization functionality"""

    def test_sanitize_basic_string(self):
        """Test basic string sanitization"""
        result = InputValidator.sanitize_string("Hello World")
        assert result == "Hello World"

    def test_sanitize_removes_control_characters(self):
        """Test removal of control characters"""
        # String with null byte and control characters
        input_str = "Hello\x00World\x08Test\x1F"
        result = InputValidator.sanitize_string(input_str)
        assert "\x00" not in result
        assert "\x08" not in result
        assert "\x1F" not in result
        assert "HelloWorldTest" in result

    def test_sanitize_html_escaping(self):
        """Test HTML escaping for XSS prevention"""
        input_str = '<script>alert("XSS")</script>'
        result = InputValidator.sanitize_string(input_str)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_sanitize_trims_whitespace(self):
        """Test whitespace trimming"""
        input_str = "   Hello World   "
        result = InputValidator.sanitize_string(input_str)
        assert result == "Hello World"

    def test_sanitize_respects_max_length(self):
        """Test max length enforcement"""
        input_str = "A" * 500
        result = InputValidator.sanitize_string(input_str, max_length=100)
        assert len(result) == 100

    def test_sanitize_non_string_input(self):
        """Test conversion of non-string input"""
        result = InputValidator.sanitize_string(12345)
        assert result == "12345"
        assert isinstance(result, str)

    def test_sanitize_sql_injection_attempt(self):
        """Test sanitization of SQL injection attempt"""
        input_str = "'; DROP TABLE users; --"
        result = InputValidator.sanitize_string(input_str)
        # HTML escaping will convert quotes
        assert "DROP TABLE" in result
        # The dangerous quotes are escaped
        assert "&#x27;" in result

    def test_sanitize_unicode_characters(self):
        """Test that valid unicode is preserved"""
        input_str = "Hello \u4e16\u754c"  # "Hello 世界"
        result = InputValidator.sanitize_string(input_str)
        assert "\u4e16" in result
        assert "\u754c" in result


class TestFieldValidation:
    """Test individual field validation"""

    def test_validate_employee_number_valid(self):
        """Test valid employee number formats"""
        valid_numbers = ["ABC123", "TEST", "A1B2C3", "ADMIN001"]
        for number in valid_numbers:
            result = InputValidator.validate_field("employee_number", number)
            assert result is not None

    def test_validate_employee_number_invalid(self):
        """Test invalid employee number formats"""
        invalid_numbers = ["abc123", "AB", "TEST@123", "A B C 1 2 3"]
        for number in invalid_numbers:
            with pytest.raises(ValidationError):
                InputValidator.validate_field("employee_number", number)

    def test_validate_email_valid(self):
        """Test valid email formats"""
        valid_emails = ["test@example.com", "user.name@domain.org", "test123@sub.domain.co"]
        for email in valid_emails:
            result = InputValidator.validate_field("email", email)
            assert "@" in result

    def test_validate_email_invalid(self):
        """Test invalid email formats"""
        invalid_emails = ["notanemail", "@missing.com", "missing@", "no@tld"]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                InputValidator.validate_field("email", email)

    def test_validate_tool_number_valid(self):
        """Test valid tool number formats"""
        valid_numbers = ["T001", "TOOL-123", "A-B-C-1"]
        for number in valid_numbers:
            result = InputValidator.validate_field("tool_number", number)
            assert result is not None

    def test_validate_serial_number_valid(self):
        """Test valid serial number formats"""
        valid_serials = ["SN123", "SERIAL-456.789", "A.B.C-123"]
        for serial in valid_serials:
            result = InputValidator.validate_field("serial_number", serial)
            assert result is not None

    def test_validate_date_format_valid(self):
        """Test valid date format"""
        result = InputValidator.validate_field("date", "2024-12-31")
        assert result == "2024-12-31"

    def test_validate_date_format_invalid(self):
        """Test invalid date format"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("date", "31-12-2024")

    def test_validate_datetime_format_valid(self):
        """Test valid datetime formats"""
        valid_datetimes = [
            "2024-12-31T23:59:59",
            "2024-12-31T23:59:59.123",
            "2024-12-31T23:59:59Z"
        ]
        for dt in valid_datetimes:
            result = InputValidator.validate_field("datetime", dt)
            assert result is not None

    def test_validate_uuid_valid(self):
        """Test valid UUID format"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        result = InputValidator.validate_field("uuid", uuid_str)
        assert result == uuid_str

    def test_validate_uuid_invalid(self):
        """Test invalid UUID format"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("uuid", "not-a-uuid")

    def test_validate_required_field_missing(self):
        """Test that required fields cannot be None"""
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_field("name", None, required=True)
        assert "required" in str(exc_info.value)

    def test_validate_optional_field_missing(self):
        """Test that optional fields can be None"""
        result = InputValidator.validate_field("name", None, required=False)
        assert result is None

    def test_validate_id_field_conversion(self):
        """Test ID field integer conversion"""
        result = InputValidator.validate_field("user_id", "123")
        assert result == 123
        assert isinstance(result, int)

    def test_validate_id_field_invalid(self):
        """Test ID field with non-numeric value"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("tool_id", "not-a-number")

    def test_validate_quantity_positive(self):
        """Test quantity validation for positive numbers"""
        result = InputValidator.validate_field("quantity", "10.5")
        assert result == 10.5

    def test_validate_quantity_negative_fails(self):
        """Test quantity validation rejects negative numbers"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("quantity", "-5")

    def test_validate_boolean_true_values(self):
        """Test boolean field accepts true values"""
        true_values = [True, "true", "1", "yes"]
        for value in true_values:
            result = InputValidator.validate_field("is_admin", value)
            assert result is True

    def test_validate_boolean_false_values(self):
        """Test boolean field accepts false values"""
        false_values = [False, "false", "0", "no"]
        for value in false_values:
            result = InputValidator.validate_field("is_active", value)
            assert result is False

    def test_validate_boolean_invalid(self):
        """Test boolean field rejects invalid values"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("is_admin", "maybe")


class TestAllowedValues:
    """Test validation against allowed values"""

    def test_validate_condition_valid(self):
        """Test valid condition values"""
        for condition in ALLOWED_VALUES["condition"]:
            result = InputValidator.validate_field("condition", condition)
            assert result in ALLOWED_VALUES["condition"]

    def test_validate_condition_invalid(self):
        """Test invalid condition value"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("condition", "Invalid Condition")

    def test_validate_status_valid(self):
        """Test valid status values"""
        for status in ALLOWED_VALUES["status"]:
            result = InputValidator.validate_field("status", status)
            assert result in ALLOWED_VALUES["status"]

    def test_validate_department_valid(self):
        """Test valid department values"""
        for dept in ALLOWED_VALUES["department"]:
            result = InputValidator.validate_field("department", dept)
            assert result in ALLOWED_VALUES["department"]

    def test_validate_unit_valid(self):
        """Test valid unit values"""
        for unit in ALLOWED_VALUES["unit"]:
            result = InputValidator.validate_field("unit", unit)
            assert result in ALLOWED_VALUES["unit"]


class TestSchemaValidation:
    """Test JSON schema validation"""

    def test_validate_user_create_schema_complete(self):
        """Test complete user create validation"""
        data = {
            "name": "John Doe",
            "employee_number": "EMP001",
            "department": "Engineering",
            "password": "SecurePass123!",
            "is_admin": False,
            "is_active": True
        }
        result = InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["user_create"])
        assert result["name"] == "John Doe"
        assert result["is_admin"] is False

    def test_validate_user_create_schema_missing_required(self):
        """Test user create validation with missing required field"""
        data = {
            "name": "John Doe",
            # Missing employee_number and department
            "password": "SecurePass123!"
        }
        with pytest.raises(ValidationError):
            InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["user_create"])

    def test_validate_tool_create_schema(self):
        """Test tool create validation"""
        data = {
            "tool_number": "T001",
            "serial_number": "SN001",
            "description": "Test Tool",
            "condition": "Excellent",
            "location": "Lab A",
            "category": "Testing",
            "status": "available"
        }
        result = InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["tool_create"])
        assert result["tool_number"] == "T001"
        assert result["status"] == "available"

    def test_validate_chemical_create_schema(self):
        """Test chemical create validation"""
        data = {
            "part_number": "PN001",
            "lot_number": "LOT001",
            "description": "Test Chemical",
            "manufacturer": "ACME Corp",
            "quantity": 100,
            "unit": "ml",
            "location": "Storage A"
        }
        result = InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["chemical_create"])
        assert result["part_number"] == "PN001"
        assert result["quantity"] == 100.0

    def test_validate_login_schema(self):
        """Test login validation schema"""
        data = {
            "employee_number": "EMP001",
            "password": "mypassword"
        }
        result = InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["login"])
        assert "employee_number" in result
        assert "password" in result

    def test_validate_password_change_schema(self):
        """Test password change validation schema"""
        data = {
            "current_password": "oldpass",
            "new_password": "newpass"
        }
        result = InputValidator.validate_json_data(data, VALIDATION_SCHEMAS["password_change"])
        assert "current_password" in result
        assert "new_password" in result


class TestValidationDecorator:
    """Test the request validation decorator"""

    @pytest.fixture
    def test_app(self):
        """Create a test Flask application"""
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.route("/test-user", methods=["POST"])
        @validate_request_data("user_create")
        def test_user_endpoint():
            return jsonify({"validated_data": request.validated_data}), 200

        @app.route("/test-login", methods=["POST"])
        @validate_request_data("login")
        def test_login_endpoint():
            return jsonify({"validated_data": request.validated_data}), 200

        @app.route("/test-unknown", methods=["POST"])
        @validate_request_data("unknown_schema")
        def test_unknown_endpoint():
            return jsonify({"message": "success"}), 200

        return app

    def test_decorator_valid_data(self, test_app):
        """Test decorator with valid data"""
        with test_app.test_client() as client:
            response = client.post("/test-login", json={
                "employee_number": "EMP001",
                "password": "testpass"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert "validated_data" in data

    def test_decorator_invalid_data(self, test_app):
        """Test decorator with invalid data"""
        with test_app.test_client() as client:
            response = client.post("/test-user", json={
                "name": "Test User"
                # Missing required fields
            })
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Validation failed"

    def test_decorator_unknown_schema(self, test_app):
        """Test decorator with unknown schema"""
        with test_app.test_client() as client:
            response = client.post("/test-unknown", json={
                "some": "data"
            })
            assert response.status_code == 500

    def test_decorator_empty_json(self, test_app):
        """Test decorator with empty JSON"""
        with test_app.test_client() as client:
            response = client.post("/test-login", json={})
            assert response.status_code == 400


class TestPatternValidation:
    """Test regex pattern validation"""

    def test_pattern_employee_number(self):
        """Test employee number pattern"""
        pattern = PATTERNS["employee_number"]
        assert pattern.match("ABC123")
        assert pattern.match("ADMIN001")
        assert not pattern.match("abc123")  # lowercase not allowed
        assert not pattern.match("AB")  # too short

    def test_pattern_tool_number(self):
        """Test tool number pattern"""
        pattern = PATTERNS["tool_number"]
        assert pattern.match("T001")
        assert pattern.match("TOOL-123")
        assert not pattern.match("")  # empty not allowed
        assert not pattern.match("tool@123")  # special chars not allowed

    def test_pattern_email(self):
        """Test email pattern"""
        pattern = PATTERNS["email"]
        assert pattern.match("test@example.com")
        assert pattern.match("user.name+tag@domain.org")
        assert not pattern.match("invalid-email")
        assert not pattern.match("@missing-user.com")

    def test_pattern_phone(self):
        """Test phone pattern"""
        pattern = PATTERNS["phone"]
        assert pattern.match("1234567890")
        assert pattern.match("+15551234567")
        assert not pattern.match("123")  # too short
        assert not pattern.match("abc1234567")  # letters not allowed

    def test_pattern_name(self):
        """Test name pattern"""
        pattern = PATTERNS["name"]
        assert pattern.match("John Doe")
        assert pattern.match("O'Connor")
        assert pattern.match("Mary-Jane")
        assert not pattern.match("Name123")  # numbers not allowed


class TestXSSPrevention:
    """Test XSS attack prevention"""

    def test_xss_script_tag(self):
        """Test sanitization of script tags"""
        malicious = '<script>alert("XSS")</script>'
        result = InputValidator.sanitize_string(malicious)
        assert "<script>" not in result
        assert "alert" in result  # Content preserved but escaped

    def test_xss_event_handler(self):
        """Test sanitization of event handlers"""
        malicious = '<img src=x onerror="alert(1)">'
        result = InputValidator.sanitize_string(malicious)
        assert "onerror=" not in result or "&quot;" in result

    def test_xss_javascript_url(self):
        """Test sanitization of javascript URLs"""
        malicious = 'javascript:alert("XSS")'
        result = InputValidator.sanitize_string(malicious)
        # Should be HTML escaped
        assert "javascript:" in result  # URL scheme preserved
        assert "&quot;" in result or "&#x27;" in result  # Quotes escaped

    def test_xss_html_entities(self):
        """Test HTML entity encoding"""
        malicious = '"><script>alert(1)</script>'
        result = InputValidator.sanitize_string(malicious)
        assert "&lt;" in result
        assert "&gt;" in result


class TestSQLInjectionPrevention:
    """Test SQL injection prevention through sanitization"""

    def test_sql_injection_basic(self):
        """Test basic SQL injection attempt"""
        malicious = "'; DROP TABLE users; --"
        result = InputValidator.sanitize_string(malicious)
        # Quotes should be escaped
        assert "&#x27;" in result

    def test_sql_injection_union(self):
        """Test UNION-based SQL injection"""
        malicious = "' UNION SELECT * FROM passwords --"
        result = InputValidator.sanitize_string(malicious)
        # Content preserved but quotes escaped
        assert "UNION" in result
        assert "&#x27;" in result

    def test_sql_injection_comment(self):
        """Test comment-based SQL injection"""
        malicious = "admin'--"
        result = InputValidator.sanitize_string(malicious)
        assert "&#x27;" in result


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_string_required(self):
        """Test empty string for required field"""
        with pytest.raises(ValidationError):
            InputValidator.validate_field("name", "", required=True)

    def test_very_long_string(self):
        """Test very long string truncation"""
        long_string = "A" * 10000
        result = InputValidator.sanitize_string(long_string, max_length=255)
        assert len(result) == 255

    def test_nested_html_tags(self):
        """Test nested HTML tags"""
        malicious = '<div><script><b>alert("XSS")</b></script></div>'
        result = InputValidator.sanitize_string(malicious)
        assert "<script>" not in result

    def test_mixed_encoding(self):
        """Test mixed character encodings"""
        mixed = "Hello%20World&lt;script&gt;"
        result = InputValidator.sanitize_string(mixed)
        # Already encoded characters get double-encoded
        assert "&amp;lt;" in result

    def test_numeric_string_id(self):
        """Test numeric string conversion for ID"""
        result = InputValidator.validate_field("id", "999")
        assert result == 999
        assert isinstance(result, int)

    def test_float_quantity(self):
        """Test float conversion for quantity"""
        result = InputValidator.validate_field("quantity", "3.14159")
        assert result == 3.14159
        assert isinstance(result, float)
