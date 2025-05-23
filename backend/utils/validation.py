"""
Comprehensive Input Validation Utilities

This module provides validation schemas and functions for all data types
used in the SupplyLine MRO Suite application.
"""

import re
import html
from datetime import datetime
from utils.error_handler import ValidationError, validate_input


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
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
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
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
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
        'password': {'min_length': 8}
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
        'calibration': CALIBRATION_SCHEMA,
        'checkout': CHECKOUT_SCHEMA
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
