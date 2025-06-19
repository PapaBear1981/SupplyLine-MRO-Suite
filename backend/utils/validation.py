"""
Comprehensive Input Validation Utilities

This module provides validation schemas and functions for all data types
used in the SupplyLine MRO Suite application.

Enhanced for pre-deployment security improvements to handle malformed requests.
"""

import re
import html
import json
from datetime import datetime
from flask import request, jsonify
from utils.error_handler import ValidationError, validate_input


def validate_request_size(max_size_mb=10):
    """
    Validate request size to prevent large payload attacks

    Args:
        max_size_mb: Maximum allowed request size in MB

    Raises:
        ValidationError: If request is too large
    """
    if request.content_length and request.content_length > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Request too large. Maximum size is {max_size_mb}MB")

def validate_json_request():
    """
    Validate JSON request format and structure

    Returns:
        Parsed JSON data

    Raises:
        ValidationError: If JSON is malformed or missing
    """
    # Check content type
    if not request.is_json:
        if request.content_type and 'application/json' not in request.content_type:
            raise ValidationError("Content-Type must be application/json")

    # Validate request size first
    validate_request_size()

    try:
        data = request.get_json(force=True)
        if data is None:
            raise ValidationError("Request body must contain valid JSON")

        # Check for common malformed JSON patterns
        if not isinstance(data, dict):
            raise ValidationError("JSON request must be an object")

        # Check for excessively nested objects (potential DoS)
        _check_json_depth(data, max_depth=10)

        return data

    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")
    except UnicodeDecodeError as e:
        raise ValidationError(f"Invalid character encoding: {str(e)}")

def _check_json_depth(obj, current_depth=0, max_depth=10):
    """
    Check JSON object depth to prevent deeply nested DoS attacks

    Args:
        obj: Object to check
        current_depth: Current nesting depth
        max_depth: Maximum allowed depth

    Raises:
        ValidationError: If depth exceeds maximum
    """
    if current_depth > max_depth:
        raise ValidationError(f"JSON nesting too deep. Maximum depth is {max_depth}")

    if isinstance(obj, dict):
        for value in obj.values():
            _check_json_depth(value, current_depth + 1, max_depth)
    elif isinstance(obj, list):
        for item in obj:
            _check_json_depth(item, current_depth + 1, max_depth)

def validate_query_parameters(allowed_params=None, max_param_length=1000):
    """
    Validate URL query parameters

    Args:
        allowed_params: List of allowed parameter names (None = allow all)
        max_param_length: Maximum length for parameter values

    Raises:
        ValidationError: If parameters are invalid
    """
    for key, value in request.args.items():
        # Check parameter name length
        if len(key) > 100:
            raise ValidationError(f"Parameter name too long: {key}")

        # Check parameter value length
        if len(value) > max_param_length:
            raise ValidationError(f"Parameter value too long for {key}")

        # Check allowed parameters
        if allowed_params and key not in allowed_params:
            raise ValidationError(f"Unknown parameter: {key}")

        # Basic XSS prevention in query params
        if re.search(r'[<>"\']', value):
            raise ValidationError(f"Invalid characters in parameter {key}")

def sanitize_string(value, max_length=None, allow_html=False):
    """
    Sanitize string input to prevent XSS and injection attacks

    Args:
        value: String value to sanitize
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags (default: False)

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    if not allow_html:
        # 1. strip raw dangerous characters
        value = re.sub(r'[<>\"\'\\]', '', value)
        # 2. escape whatever is left
        value = html.escape(value)

    # Limit length
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value.strip()


def validate_types(data, type_schema):
    """
    Validate data types according to schema

    Args:
        data: Dictionary to validate
        type_schema: Dictionary mapping field names to expected types
    """
    for field, expected_type in type_schema.items():
        if field in data and data[field] is not None and not isinstance(data[field], expected_type):
            raise ValidationError(f"{field} must be of type {expected_type.__name__}")


def validate_constraints(data, constraint_schema):
    """
    Validate data constraints (ranges, choices, patterns)

    Args:
        data: Dictionary to validate
        constraint_schema: Dictionary mapping field names to constraint rules
    """
    for field, constraints in constraint_schema.items():
        if field not in data or data[field] is None:
            continue

        value = data[field]

        # Check minimum value
        if 'min' in constraints and isinstance(value, (int, float)) and value < constraints['min']:
            raise ValidationError(f"{field} must be at least {constraints['min']}")

        # Check maximum value
        if 'max' in constraints and isinstance(value, (int, float)) and value > constraints['max']:
            raise ValidationError(f"{field} must be at most {constraints['max']}")

        # Check minimum length
        if 'min_length' in constraints and isinstance(value, str) and len(value) < constraints['min_length']:
            raise ValidationError(f"{field} must be at least {constraints['min_length']} characters")

        # Check maximum length
        if 'max_length' in constraints and isinstance(value, str) and len(value) > constraints['max_length']:
            raise ValidationError(f"{field} must be at most {constraints['max_length']} characters")

        # Check choices
        if 'choices' in constraints and value not in constraints['choices']:
            raise ValidationError(f"{field} must be one of: {', '.join(map(str, constraints['choices']))}")

        # Check pattern
        if 'pattern' in constraints and isinstance(value, str) and not re.match(constraints['pattern'], value):
            raise ValidationError(f"{field} format is invalid")


def validate_dates(data, date_fields):
    """
    Validate date fields and convert to datetime objects

    Args:
        data: Dictionary to validate
        date_fields: List of field names that should contain dates
    """
    for field in date_fields:
        if field in data and data[field]:
            try:
                if isinstance(data[field], str):
                    # Handle various timezone formats or convert to UTC
                    date_str = data[field]
                    if date_str.endswith('Z'):
                        date_str = date_str.replace('Z', '+00:00')
                    data[field] = datetime.fromisoformat(date_str)
            except ValueError as err:
                raise ValidationError(
                    f"{field} must be a valid ISO format date"
                ) from err


# Validation Schemas
TOOL_SCHEMA = {
    'required': ['tool_number', 'serial_number', 'description'],
    'optional': ['condition', 'location', 'category', 'status', 'status_reason'],
    'types': {
        'tool_number': str,
        'serial_number': str,
        'description': str,
        'condition': str,
        'location': str,
        'category': str,
        'status': str,
        'status_reason': str
    },
    'constraints': {
        'tool_number': {'max_length': 50, 'pattern': r'^[A-Z0-9-]+$'},
        'serial_number': {'max_length': 100},
        'description': {'max_length': 500},
        'condition': {'choices': ['excellent', 'good', 'fair', 'poor']},
        'status': {'choices': ['available', 'checked_out', 'maintenance', 'retired']},
        'category': {'max_length': 100}
    }
}

CHEMICAL_SCHEMA = {
    'required': ['part_number', 'lot_number', 'quantity', 'unit'],
    'optional': ['description', 'manufacturer', 'location', 'expiration_date', 'msds_url'],
    'types': {
        'part_number': str,
        'lot_number': str,
        'quantity': (int, float),
        'unit': str,
        'description': str,
        'manufacturer': str,
        'location': str,
        'msds_url': str
    },
    'constraints': {
        'part_number': {'max_length': 100},
        'lot_number': {'max_length': 100},
        'quantity': {'min': 0},
        'unit': {'choices': ['each', 'oz', 'ml', 'gal', 'lb', 'kg', 'liter']},
        'description': {'max_length': 500},
        'manufacturer': {'max_length': 200},
        'location': {'max_length': 100}
    },
    'date_fields': ['expiration_date']
}

USER_SCHEMA = {
    'required': ['name', 'employee_number', 'department'],
    'optional': ['password', 'is_admin', 'is_active'],
    'types': {
        'name': str,
        'employee_number': str,
        'department': str,
        'password': str,
        'is_admin': bool,
        'is_active': bool
    },
    'constraints': {
        'name': {'max_length': 100, 'min_length': 2},
        'employee_number': {'max_length': 20, 'pattern': r'^[A-Z0-9]+$'},
        'department': {'choices': ['Materials', 'Quality', 'Engineering', 'Production', 'IT', 'Admin']},
        'password': {
            'min_length': 8,
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
        }
    }
}

CHEMICAL_ISSUANCE_SCHEMA = {
    'required': ['quantity', 'hangar', 'user_id'],
    'optional': ['purpose'],
    'types': {
        'quantity': (int, float),
        'hangar': str,
        'user_id': int,
        'purpose': str
    },
    'constraints': {
        'quantity': {'min': 0.01},
        'hangar': {'max_length': 100},
        'user_id': {'min': 1},
        'purpose': {'max_length': 500}
    }
}

CALIBRATION_SCHEMA = {
    'required': ['calibration_date', 'calibration_status'],
    'optional': ['next_calibration_date', 'calibrated_by', 'notes', 'certificate_number'],
    'types': {
        'calibration_date': str,
        'next_calibration_date': str,
        'calibrated_by': str,
        'notes': str,
        'certificate_number': str,
        'calibration_status': str
    },
    'constraints': {
        'calibration_status': {'choices': ['pass', 'fail', 'limited']},
        'calibrated_by': {'max_length': 100},
        'notes': {'max_length': 1000},
        'certificate_number': {'max_length': 100}
    },
    'date_fields': ['calibration_date', 'next_calibration_date']
}

CHECKOUT_SCHEMA = {
    'required': ['tool_id', 'user_id'],
    'optional': ['expected_return_date', 'notes'],
    'types': {
        'tool_id': int,
        'user_id': int,
        'expected_return_date': str,
        'notes': str
    },
    'constraints': {
        'tool_id': {'min': 1},
        'user_id': {'min': 1},
        'notes': {'max_length': 500}
    },
    'date_fields': ['expected_return_date']
}

CYCLE_COUNT_SCHEDULE_SCHEMA = {
    'required': ['name', 'frequency', 'method'],
    'optional': ['description', 'is_active'],
    'types': {
        'name': str,
        'description': str,
        'frequency': str,
        'method': str,
        'is_active': bool
    },
    'constraints': {
        'name': {'max_length': 100, 'min_length': 1},
        'description': {'max_length': 500},
        'frequency': {'choices': ['daily', 'weekly', 'monthly', 'quarterly', 'annual']},
        'method': {'choices': ['ABC', 'random', 'location', 'category']}
    }
}

CYCLE_COUNT_BATCH_SCHEMA = {
    'required': ['name'],
    'optional': ['schedule_id', 'start_date', 'end_date', 'notes', 'generate_items', 'item_selection', 'item_count', 'category', 'location'],
    'types': {
        'name': str,
        'schedule_id': int,
        'start_date': str,
        'end_date': str,
        'notes': str,
        'generate_items': bool,
        'item_selection': str,
        'item_count': int,
        'category': str,
        'location': str
    },
    'constraints': {
        'name': {'max_length': 100, 'min_length': 1},
        'notes': {'max_length': 1000},
        'item_selection': {'choices': ['all', 'random', 'category', 'location']},
        'item_count': {'min': 1, 'max': 10000},
        'category': {'max_length': 50},
        'location': {'max_length': 100}
    },
    'date_fields': ['start_date', 'end_date']
}

CYCLE_COUNT_RESULT_SCHEMA = {
    'required': ['actual_quantity'],
    'optional': ['actual_location', 'condition', 'notes'],
    'types': {
        'actual_quantity': int,
        'actual_location': str,
        'condition': str,
        'notes': str
    },
    'constraints': {
        'actual_quantity': {'min': 0, 'max': 999999},
        'actual_location': {'max_length': 100},
        'condition': {'choices': ['good', 'fair', 'poor', 'damaged']},
        'notes': {'max_length': 500}
    }
}


def validate_schema(data, schema_name):
    """
    Validate data against a predefined schema

    Args:
        data: Dictionary to validate
        schema_name: Name of the schema to use

    Returns:
        Sanitized and validated data
    """
    schemas = {
        'tool': TOOL_SCHEMA,
        'chemical': CHEMICAL_SCHEMA,
        'user': USER_SCHEMA,
        'chemical_issuance': CHEMICAL_ISSUANCE_SCHEMA,
        'calibration': CALIBRATION_SCHEMA,
        'checkout': CHECKOUT_SCHEMA,
        'cycle_count_schedule': CYCLE_COUNT_SCHEDULE_SCHEMA,
        'cycle_count_batch': CYCLE_COUNT_BATCH_SCHEMA,
        'cycle_count_result': CYCLE_COUNT_RESULT_SCHEMA
    }

    if schema_name not in schemas:
        raise ValidationError(f"Unknown schema: {schema_name}")

    schema = schemas[schema_name]

    # Validate required/optional fields
    validate_input(data, schema['required'], schema.get('optional', []))

    # Validate types
    validate_types(data, schema['types'])

    # Validate constraints
    if 'constraints' in schema:
        validate_constraints(data, schema['constraints'])

    # Validate and convert dates
    if 'date_fields' in schema:
        validate_dates(data, schema['date_fields'])

    # Perform cross-field validation for specific schemas
    if schema_name == 'cycle_count_batch':
        validate_cycle_count_batch_cross_fields(data)

    # Sanitize string fields
    sanitized_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            max_length = None
            if 'constraints' in schema and key in schema['constraints']:
                max_length = schema['constraints'][key].get('max_length')
            sanitized_data[key] = sanitize_string(value, max_length)
        else:
            sanitized_data[key] = value

    return sanitized_data


def validate_cycle_count_batch_cross_fields(data):
    """
    Validate cross-field relationships for cycle count batch data

    Args:
        data: Dictionary containing cycle count batch data

    Raises:
        ValidationError: If cross-field validation fails
    """
    from datetime import datetime

    # Validate start_date and end_date relationship
    if 'start_date' in data and 'end_date' in data and data['start_date'] and data['end_date']:
        try:
            start_date = datetime.fromisoformat(data['start_date'])
            end_date = datetime.fromisoformat(data['end_date'])

            if end_date < start_date:
                raise ValidationError("End date cannot be before start date")

            # Check if dates are too far in the future (more than 1 year)
            now = datetime.now()
            if start_date > now.replace(year=now.year + 1):
                raise ValidationError("Start date cannot be more than 1 year in the future")

        except ValueError as e:
            raise ValidationError(f"Invalid date format: {str(e)}") from e

    # Validate item generation parameters
    if data.get('generate_items', False):
        if 'item_selection' not in data:
            raise ValidationError("item_selection is required when generate_items is True")

        # Validate item_count for random selection
        if data.get('item_selection') == 'random':
            if 'item_count' not in data or not data['item_count']:
                raise ValidationError("item_count is required when item_selection is 'random'")
            if data['item_count'] < 1:
                raise ValidationError("item_count must be at least 1 for random selection")

        # Validate category for category selection
        if data.get('item_selection') == 'category' and ('category' not in data or not data['category']):
            raise ValidationError("category is required when item_selection is 'category'")

        # Validate location for location selection
        if data.get('item_selection') == 'location' and ('location' not in data or not data['location']):
            raise ValidationError("location is required when item_selection is 'location'")


def enhanced_validation(schema_name=None, allowed_params=None):
    """
    Decorator for enhanced request validation

    Args:
        schema_name: Name of validation schema to apply to JSON body
        allowed_params: List of allowed query parameters

    Returns:
        Decorator function
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validate query parameters
                if request.args:
                    validate_query_parameters(allowed_params)

                # Validate JSON body if present
                if request.method in ['POST', 'PUT', 'PATCH'] and request.content_length:
                    data = validate_json_request()

                    # Apply schema validation if specified
                    if schema_name:
                        data = validate_schema(data, schema_name)
                        # Replace request data with validated data
                        request.validated_data = data

                return func(*args, **kwargs)

            except ValidationError as e:
                return jsonify({
                    'error': 'Validation Error',
                    'message': str(e),
                    'type': 'validation_error'
                }), 400
            except Exception as e:
                return jsonify({
                    'error': 'Request Processing Error',
                    'message': 'Invalid request format',
                    'type': 'request_error'
                }), 400

        return wrapper
    return decorator
