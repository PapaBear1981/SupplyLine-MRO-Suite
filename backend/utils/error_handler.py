"""
Enhanced Error Handling Utility

This module provides comprehensive error handling with structured logging,
transaction management, and security event tracking.
"""

import logging
import time
from functools import wraps
from flask import jsonify, current_app, request, session
from sqlalchemy.exc import SQLAlchemyError
from .logging_utils import get_request_context, log_security_event

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
    """Enhanced decorator for comprehensive error handling with context and transaction management"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        context = get_request_context()

        try:
            result = f(*args, **kwargs)

            # Log successful operation
            duration = (time.time() - start_time) * 1000
            logger.debug(f"Operation {f.__name__} completed successfully", extra={
                **context,
                'operation': f.__name__,
                'duration_ms': round(duration, 2),
                'success': True
            })

            return result

        except ValidationError as e:
            duration = (time.time() - start_time) * 1000
            logger.warning(f"Validation error in {f.__name__}", extra={
                **context,
                'operation': f.__name__,
                'error_type': 'ValidationError',
                'error_message': str(e),
                'duration_ms': round(duration, 2)
            })
            return jsonify({'error': str(e)}), 400

        except AuthenticationError as e:
            duration = (time.time() - start_time) * 1000
            log_security_event('authentication_failure', {
                'operation': f.__name__,
                'error_message': str(e),
                'ip_address': request.remote_addr if request else None
            })
            return jsonify({'error': 'Authentication required'}), 401

        except AuthorizationError as e:
            duration = (time.time() - start_time) * 1000
            log_security_event('authorization_failure', {
                'operation': f.__name__,
                'error_message': str(e),
                'user_id': session.get('user_id') if session else None
            })
            return jsonify({'error': 'Insufficient permissions', 'message': str(e)}), 403

        except RateLimitError as e:
            duration = (time.time() - start_time) * 1000
            log_security_event('rate_limit_exceeded', {
                'operation': f.__name__,
                'ip_address': request.remote_addr if request else None
            })
            return jsonify({'error': 'Too many requests', 'message': str(e)}), 429

        except DatabaseError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Database error in {f.__name__}", extra={
                **context,
                'operation': f.__name__,
                'error_type': 'DatabaseError',
                'error_message': str(e),
                'duration_ms': round(duration, 2)
            })
            # Database errors are automatically rolled back by SQLAlchemy
            return jsonify({'error': 'Database operation failed'}), 500

        except SQLAlchemyError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"SQLAlchemy error in {f.__name__}", extra={
                **context,
                'operation': f.__name__,
                'error_type': 'SQLAlchemyError',
                'error_message': str(e),
                'duration_ms': round(duration, 2)
            })
            return jsonify({'error': 'Database error occurred'}), 500

        except Exception as e:
            # Handle werkzeug NotFound (from get_or_404)
            if type(e).__name__ == 'NotFound':
                duration = (time.time() - start_time) * 1000
                logger.warning(f"Resource not found in {f.__name__}", extra={
                    **context,
                    'operation': f.__name__,
                    'error_type': 'NotFound',
                    'duration_ms': round(duration, 2)
                })
                return jsonify({'error': 'Resource not found'}), 404

            duration = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error in {f.__name__}", exc_info=True, extra={
                **context,
                'operation': f.__name__,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_ms': round(duration, 2)
            })
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
