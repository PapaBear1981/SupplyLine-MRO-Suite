"""
Input Validation and Sanitization for SupplyLine MRO Suite

This module provides comprehensive input validation and sanitization
to prevent security vulnerabilities like SQL injection, XSS, and data corruption.
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from flask import request, jsonify
from functools import wraps

logger = logging.getLogger(__name__)

# Validation patterns
PATTERNS = {
    'employee_number': re.compile(r'^[A-Z0-9]{3,20}$'),
    'tool_number': re.compile(r'^[A-Z0-9\-]{1,50}$'),
    'serial_number': re.compile(r'^[A-Z0-9\-\.]{1,100}$'),
    'part_number': re.compile(r'^[A-Z0-9\-\.]{1,100}$'),
    'lot_number': re.compile(r'^[A-Z0-9\-\.]{1,100}$'),
    'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    'phone': re.compile(r'^\+?1?[0-9]{10,15}$'),
    'alphanumeric': re.compile(r'^[a-zA-Z0-9\s\-\.]{1,255}$'),
    'name': re.compile(r'^[a-zA-Z\s\-\.\']{1,200}$'),
    'department': re.compile(r'^[a-zA-Z\s\-]{1,100}$'),
    'location': re.compile(r'^[a-zA-Z0-9\s\-\.\,]{1,200}$'),
    'category': re.compile(r'^[a-zA-Z\s\-]{1,100}$'),
    'condition': re.compile(r'^[a-zA-Z\s\-]{1,50}$'),
    'status': re.compile(r'^[a-zA-Z_]{1,50}$'),
    'unit': re.compile(r'^[a-zA-Z\s]{1,20}$'),
    'manufacturer': re.compile(r'^[a-zA-Z0-9\s\-\.\,&]{1,200}$'),
    'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
    'date': re.compile(r'^\d{4}-\d{2}-\d{2}$'),
    'datetime': re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'),
}

# Allowed values for specific fields
ALLOWED_VALUES = {
    'condition': ['Excellent', 'Good', 'Fair', 'Poor', 'Needs Repair'],
    'status': ['available', 'checked_out', 'maintenance', 'retired'],
    'chemical_status': ['available', 'low_stock', 'expired', 'disposed'],
    'department': ['Engineering', 'Materials', 'Quality', 'Production', 'Maintenance', 'IT'],
    'unit': ['ml', 'L', 'g', 'kg', 'oz', 'lb', 'gal', 'qt', 'pt', 'each', 'box', 'case'],
    'activity_type': ['login', 'logout', 'checkout', 'return', 'create', 'update', 'delete'],
    'audit_action': ['create', 'update', 'delete', 'login', 'logout', 'checkout', 'return'],
}

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for field '{field}': {message}")

class InputValidator:
    """Input validation and sanitization class"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input by removing dangerous characters and limiting length
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # HTML escape to prevent XSS
        value = html.escape(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_field(field_name: str, value: Any, required: bool = True) -> Any:
        """
        Validate a single field based on its name and type
        
        Args:
            field_name: Name of the field to validate
            value: Value to validate
            required: Whether the field is required
            
        Returns:
            Validated and sanitized value
            
        Raises:
            ValidationError: If validation fails
        """
        # Handle None/empty values
        if value is None or value == '':
            if required:
                raise ValidationError(field_name, "This field is required")
            return None
        
        # Convert to string for pattern matching
        str_value = str(value).strip()
        
        # Check against patterns
        if field_name in PATTERNS:
            if not PATTERNS[field_name].match(str_value):
                raise ValidationError(field_name, f"Invalid format for {field_name}")
        
        # Check against allowed values
        if field_name in ALLOWED_VALUES:
            if str_value not in ALLOWED_VALUES[field_name]:
                raise ValidationError(field_name, f"Value must be one of: {', '.join(ALLOWED_VALUES[field_name])}")
        
        # Type-specific validation
        if field_name.endswith('_id') or field_name == 'id':
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(field_name, "Must be a valid integer")
        
        if field_name in ['quantity', 'minimum_stock_level', 'reorder_point']:
            try:
                float_value = float(value)
                if float_value < 0:
                    raise ValidationError(field_name, "Must be a positive number")
                return float_value
            except (ValueError, TypeError):
                raise ValidationError(field_name, "Must be a valid number")
        
        if field_name in ['calibration_frequency_days', 'failed_login_attempts']:
            try:
                int_value = int(value)
                if int_value < 0:
                    raise ValidationError(field_name, "Must be a positive integer")
                return int_value
            except (ValueError, TypeError):
                raise ValidationError(field_name, "Must be a valid integer")
        
        if field_name in ['is_admin', 'is_active', 'requires_calibration']:
            if isinstance(value, bool):
                return value
            if str_value.lower() in ['true', '1', 'yes']:
                return True
            if str_value.lower() in ['false', '0', 'no']:
                return False
            raise ValidationError(field_name, "Must be a boolean value")
        
        # Default string sanitization
        return InputValidator.sanitize_string(str_value)
    
    @staticmethod
    def validate_json_data(data: Dict[str, Any], schema: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Validate JSON data against a schema
        
        Args:
            data: Input data dictionary
            schema: Validation schema with field definitions
            
        Returns:
            Validated and sanitized data dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        validated_data = {}
        
        for field_name, field_config in schema.items():
            required = field_config.get('required', False)
            value = data.get(field_name)
            
            try:
                validated_value = InputValidator.validate_field(field_name, value, required)
                if validated_value is not None:
                    validated_data[field_name] = validated_value
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                raise
        
        return validated_data

# Validation schemas for different endpoints
VALIDATION_SCHEMAS = {
    'user_create': {
        'name': {'required': True},
        'employee_number': {'required': True},
        'department': {'required': True},
        'password': {'required': True},
        'is_admin': {'required': False},
        'is_active': {'required': False},
    },
    'user_update': {
        'name': {'required': False},
        'department': {'required': False},
        'is_admin': {'required': False},
        'is_active': {'required': False},
    },
    'tool_create': {
        'tool_number': {'required': True},
        'serial_number': {'required': True},
        'description': {'required': True},
        'condition': {'required': True},
        'location': {'required': True},
        'category': {'required': True},
        'status': {'required': False},
        'requires_calibration': {'required': False},
        'calibration_frequency_days': {'required': False},
    },
    'tool_update': {
        'description': {'required': False},
        'condition': {'required': False},
        'location': {'required': False},
        'category': {'required': False},
        'status': {'required': False},
        'requires_calibration': {'required': False},
        'calibration_frequency_days': {'required': False},
    },
    'chemical_create': {
        'part_number': {'required': True},
        'lot_number': {'required': True},
        'description': {'required': True},
        'manufacturer': {'required': True},
        'quantity': {'required': True},
        'unit': {'required': True},
        'location': {'required': True},
        'category': {'required': False},
        'minimum_stock_level': {'required': False},
        'reorder_point': {'required': False},
    },
    'login': {
        'employee_number': {'required': True},
        'password': {'required': True},
        'remember_me': {'required': False},
    },
    'password_change': {
        'current_password': {'required': True},
        'new_password': {'required': True},
    },
}

def validate_request_data(schema_name: str):
    """
    Decorator to validate request JSON data against a schema
    
    Args:
        schema_name: Name of the validation schema to use
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get JSON data from request
                data = request.get_json() or {}
                
                # Get validation schema
                if schema_name not in VALIDATION_SCHEMAS:
                    logger.error(f"Unknown validation schema: {schema_name}")
                    return jsonify({'error': 'Internal validation error'}), 500
                
                schema = VALIDATION_SCHEMAS[schema_name]
                
                # Validate data
                validated_data = InputValidator.validate_json_data(data, schema)
                
                # Add validated data to request context
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Request validation failed: {e}")
                return jsonify({
                    'error': 'Validation failed',
                    'field': e.field,
                    'message': e.message
                }), 400
            except Exception as e:
                logger.error(f"Unexpected validation error: {str(e)}")
                return jsonify({'error': 'Internal validation error'}), 500
        
        return decorated_function
    return decorator
