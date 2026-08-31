"""
Enhanced Error Handling Utility

This module provides comprehensive error handling with structured logging,
transaction management, and security event tracking.
"""

import logging
import time
import uuid
from functools import wraps
from typing import Any

from flask import current_app, has_app_context, jsonify, request, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from .logging_utils import get_request_context


logger = logging.getLogger(__name__)

# Custom Exception Classes


class SupplyLineError(Exception):
    """Base exception for SupplyLine application"""


class ValidationError(SupplyLineError):
    """Raised when input validation fails"""


class AuthenticationError(SupplyLineError):
    """Raised when authentication fails"""


class AuthorizationError(SupplyLineError):
    """Raised when user lacks required permissions"""


class DatabaseError(SupplyLineError):
    """Raised when database operations fail"""


class RateLimitError(SupplyLineError):
    """Raised when rate limit is exceeded"""


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
                "operation": f.__name__,
                "duration_ms": round(duration, 2),
                "success": True
            })

            return result

        except ValidationError as e:
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            logger.warning(
                f"Validation error in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "ValidationError",
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return _build_error_response(
                message=str(e),
                status_code=400,
                error_code="validation_error",
                hint="Please review the submitted information and try again.",
                reference=error_reference,
                error=e
            )

        except AuthenticationError as e:
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            log_security_event("authentication_failure", {
                "operation": f.__name__,
                "error_message": str(e),
                "ip_address": request.remote_addr if request else None,
                "error_reference": error_reference
            })
            logger.warning(
                f"Authentication error in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "AuthenticationError",
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return _build_error_response(
                message="Authentication is required to complete this request.",
                status_code=401,
                error_code="authentication_required",
                hint="Please sign in and retry the operation.",
                reference=error_reference,
                error=e
            )

        except AuthorizationError as e:
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            log_security_event("authorization_failure", {
                "operation": f.__name__,
                "error_message": str(e),
                "user_id": session.get("user_id") if session else None,
                "error_reference": error_reference
            })
            logger.warning(
                f"Authorization error in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "AuthorizationError",
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return _build_error_response(
                message="You do not have permission to perform this action.",
                status_code=403,
                error_code="insufficient_permissions",
                hint=str(e) or "Contact an administrator if you believe this is an error.",
                reference=error_reference,
                error=e
            )

        except RateLimitError as e:
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            log_security_event("rate_limit_exceeded", {
                "operation": f.__name__,
                "ip_address": request.remote_addr if request else None,
                "error_reference": error_reference
            })
            logger.warning(
                f"Rate limit exceeded in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "RateLimitError",
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return _build_error_response(
                message="Too many requests were made in a short period.",
                status_code=429,
                error_code="rate_limit_exceeded",
                hint=str(e) or "Please wait a moment before trying again.",
                reference=error_reference,
                error=e
            )

        except DatabaseError as e:
            _rollback_session()
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            logger.error(
                f"Database error in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "DatabaseError",
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            # Database errors are automatically rolled back by SQLAlchemy
            return _build_error_response(
                message="We were unable to complete the request due to a database issue.",
                status_code=500,
                error_code="database_error",
                hint="The operation was rolled back. Please retry or contact support with the reference ID.",
                reference=error_reference,
                error=e
            )

        except SQLAlchemyError as e:
            _rollback_session()
            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            logger.error(
                f"SQLAlchemy error in {f.__name__}",
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": "SQLAlchemyError",
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return _build_error_response(
                message="A database error occurred while processing your request.",
                status_code=500,
                error_code="database_error",
                hint="Please retry the request or contact support with the reference ID provided.",
                reference=error_reference,
                error=e
            )

        except Exception as e:
            # Preserve all intentional HTTP failures (including get_or_404)
            # instead of turning them into misleading 500 responses.
            if isinstance(e, HTTPException):
                duration = (time.time() - start_time) * 1000
                error_reference = _generate_error_reference()
                logger.warning(
                    f"HTTP {e.code} in {f.__name__}",
                    extra={
                        **context,
                        "operation": f.__name__,
                        "error_type": type(e).__name__,
                        "duration_ms": round(duration, 2),
                        "error_reference": error_reference
                    }
                )
                return _build_error_response(
                    message=_default_message_for_code(_status_code_to_error_code(e.code)),
                    status_code=e.code,
                    error_code=_status_code_to_error_code(e.code),
                    hint="Review the request and try again.",
                    reference=error_reference,
                    error=e
                )

            duration = (time.time() - start_time) * 1000
            error_reference = _generate_error_reference()
            _rollback_session()
            logger.error(
                f"Unexpected error in {f.__name__}",
                exc_info=True,
                extra={
                    **context,
                    "operation": f.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": round(duration, 2),
                    "error_reference": error_reference
                }
            )
            return create_error_response(
                e,
                500,
                code="internal_server_error",
                message="An unexpected error occurred while processing your request.",
                hint="Our team has been notified. Please retry later or contact support with the reference ID.",
                reference=error_reference
            )

    return decorated_function


def create_error_response(
    error: Exception,
    status_code: int,
    *,
    code: str | None = None,
    message: str | None = None,
    hint: str | None = None,
    reference: str | None = None
):
    """Create error response with environment-specific details"""

    error_code = code or _status_code_to_error_code(status_code)
    error_message = message or _default_message_for_code(error_code)

    return _build_error_response(
        message=error_message,
        status_code=status_code,
        error_code=error_code,
        hint=hint,
        reference=reference,
        error=error
    )


def setup_global_error_handlers(app):
    """Setup global error handlers for the Flask app"""

    @app.errorhandler(404)
    def not_found(error):
        error_reference = _generate_error_reference()
        logger.warning(
            f"404 error: {request.url}",
            extra={"error_reference": error_reference, "path": getattr(request, "path", None)}
        )
        return _build_error_response(
            message="The requested resource could not be found.",
            status_code=404,
            error_code="not_found",
            hint="Verify the address and try again.",
            reference=error_reference,
            error=error
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        error_reference = _generate_error_reference()
        logger.warning(
            f"405 error: {request.method} {request.url}",
            extra={"error_reference": error_reference}
        )
        return _build_error_response(
            message="This endpoint does not support the requested HTTP method.",
            status_code=405,
            error_code="method_not_allowed",
            hint="Confirm you are using the correct HTTP method for this request.",
            reference=error_reference,
            error=error
        )

    @app.errorhandler(500)
    def internal_error(error):
        error_reference = _generate_error_reference()
        logger.error(
            f"500 error: {error!s}",
            exc_info=True,
            extra={"error_reference": error_reference}
        )
        from models import db
        db.session.rollback()
        return create_error_response(
            error,
            500,
            code="internal_server_error",
            message="An unexpected error occurred while processing your request.",
            hint="Please retry later or contact support with the reference ID provided.",
            reference=error_reference
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            error_reference = _generate_error_reference()
            return _build_error_response(
                message=_default_message_for_code(_status_code_to_error_code(e.code)),
                status_code=e.code,
                error_code=_status_code_to_error_code(e.code),
                hint="Review the request and try again.",
                reference=error_reference,
                error=e
            )

        error_reference = _generate_error_reference()
        _rollback_session()
        logger.error(
            f"Unhandled exception: {e!s}",
            exc_info=True,
            extra={"error_reference": error_reference}
        )
        return create_error_response(
            e,
            500,
            code="internal_server_error",
            message="An unexpected error occurred while processing your request.",
            hint="Please retry later or contact support with the reference ID provided.",
            reference=error_reference
        )


def log_security_event(event_type, details, user_id=None, ip_address=None):
    """Log security-related events"""
    from flask import request, session

    user_id = user_id or (session.get("user_id", "anonymous") if has_app_context() else "anonymous")
    ip_address = ip_address or (request.remote_addr if has_app_context() else None)

    logger.warning(f"SECURITY EVENT - Type: {event_type}, User: {user_id}, IP: {ip_address}, Details: {details}")


def _generate_error_reference() -> str:
    """Generate a short unique error reference identifier."""
    return uuid.uuid4().hex[:12].upper()


def _build_error_response(
    *,
    message: str,
    status_code: int,
    error_code: str | None = None,
    hint: str | None = None,
    reference: str | None = None,
    error: Exception | None = None
):
    payload: dict[str, Any] = {"error": message}

    if error_code:
        payload["error_code"] = error_code
    if hint:
        payload["hint"] = hint
    if reference:
        payload["reference"] = reference

    if _in_debug_mode() and error is not None:
        payload["debug"] = {
            "type": type(error).__name__,
            "details": str(error)
        }

    response = jsonify(payload)
    response.status_code = status_code
    if reference:
        response.headers["X-Error-Reference"] = reference
    response.headers["Cache-Control"] = "no-store"
    return response


def _rollback_session() -> None:
    """Best-effort rollback so a failed request cannot poison the next one."""
    if not has_app_context():
        return
    try:
        from models import db
        db.session.rollback()
    except Exception:
        logger.exception("Failed to roll back database session after an error")


def _in_debug_mode() -> bool:
    """Determine if the application is running in debug/development mode."""
    return has_app_context() and bool(
        current_app.config.get("DEBUG")
        or current_app.config.get("TESTING")
        or current_app.config.get("FLASK_ENV") == "development"
    )


def _status_code_to_error_code(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "authentication_required",
        403: "insufficient_permissions",
        404: "not_found",
        405: "method_not_allowed",
        406: "not_acceptable",
        408: "request_timeout",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
        502: "bad_gateway",
        503: "service_unavailable",
        504: "gateway_timeout",
        500: "internal_server_error"
    }
    return mapping.get(status_code, "http_error" if 400 <= status_code < 500 else "internal_server_error")


def _default_message_for_code(error_code: str) -> str:
    defaults = {
        "validation_error": "There was a problem with the data provided.",
        "authentication_required": "Authentication is required to complete this request.",
        "insufficient_permissions": "You do not have permission to perform this action.",
        "not_found": "The requested resource could not be found.",
        "method_not_allowed": "This endpoint does not support the requested HTTP method.",
        "not_acceptable": "The requested response format is not supported.",
        "request_timeout": "The request timed out before it could be completed.",
        "conflict": "The request could not be completed due to a conflict with the current state of the resource.",
        "rate_limit_exceeded": "Too many requests were made in a short period.",
        "bad_gateway": "An upstream service returned an invalid response.",
        "service_unavailable": "The service is temporarily unavailable.",
        "gateway_timeout": "An upstream service took too long to respond.",
        "http_error": "The request could not be completed.",
        "database_error": "We were unable to complete the request due to a database issue.",
        "internal_server_error": "An unexpected error occurred while processing your request."
    }
    return defaults.get(error_code, "An unexpected error occurred while processing your request.")


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
