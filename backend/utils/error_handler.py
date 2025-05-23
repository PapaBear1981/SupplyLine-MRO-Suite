"""
Secure Error Handling Utility

This module provides structured error handling without information disclosure.
"""

import logging
from functools import wraps
from flask import jsonify, current_app, request
from sqlalchemy.exc import SQLAlchemyError

# Configure logging only if no handlers exist
if not logging.root.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Custom Exception Classes
class SupplyLineError(Exception):
    """Base exception for SupplyLine application"""
    pass

class ValidationError(SupplyLineError):
    """Raised when input validation fails"""
    pass

class AuthenticationError(SupplyLineError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(SupplyLineError):
    """Raised when user lacks required permissions"""
    pass

class DatabaseError(SupplyLineError):
    """Raised when database operations fail"""
    pass

class RateLimitError(SupplyLineError):
    """Raised when rate limit is exceeded"""
    pass


def handle_errors(f):
    """Decorator for comprehensive error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Invalid input', 'message': str(e)}), 400
        except AuthenticationError as e:
            logger.warning(f"Authentication error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Authentication required'}), 401
        except AuthorizationError as e:
            logger.warning(f"Permission error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Insufficient permissions', 'message': str(e)}), 403
        except RateLimitError as e:
            logger.warning(f"Rate limit error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Too many requests', 'message': str(e)}), 429
        except DatabaseError as e:
            logger.error(f"Database error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Database error occurred'}), 500
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Database error occurred'}), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
            return create_error_response(e, 500)
    return decorated_function


def create_error_response(error, status_code):
    """Create error response with environment-specific details"""
    from flask import has_app_context

    response = {'error': 'Internal server error'}

    # Only include debug info in development
    if has_app_context() and (
        current_app.config.get('DEBUG') or current_app.config.get('FLASK_ENV') == 'development'
    ):
        response['debug_info'] = str(error)
        response['type'] = type(error).__name__

    return jsonify(response), status_code


def setup_global_error_handlers(app):
    """Setup global error handlers for the Flask app"""

    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {request.url}")
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        logger.warning(f"405 error: {request.method} {request.url}")
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}", exc_info=True)
        from models import db
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return create_error_response(e, 500)


def log_security_event(event_type, details, user_id=None, ip_address=None):
    """Log security-related events"""
    from flask import session, request

    user_id = user_id or session.get('user_id', 'anonymous')
    ip_address = ip_address or request.remote_addr

    logger.warning(f"SECURITY EVENT - Type: {event_type}, User: {user_id}, IP: {ip_address}, Details: {details}")


def validate_input(data, required_fields, optional_fields=None):
    """Validate input data"""
    if not isinstance(data, dict):
        raise ValidationError("Invalid input format")

    # Check required fields
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    # Check for unexpected fields (optional security measure)
    if optional_fields is not None:
        allowed_fields = set(required_fields + optional_fields)
        unexpected_fields = set(data.keys()) - allowed_fields
        if unexpected_fields:
            logger.warning(f"Unexpected fields in input: {unexpected_fields}")

    return True
