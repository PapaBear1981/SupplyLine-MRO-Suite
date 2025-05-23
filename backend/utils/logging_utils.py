"""
Logging Utilities

This module provides structured logging utilities with data sanitization
and correlation ID support for better debugging and monitoring.
"""

import logging
import uuid
import time
from functools import wraps
from flask import g, request, session, has_request_context
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Sensitive fields that should be redacted in logs
SENSITIVE_FIELDS = [
    'password', 'token', 'secret', 'key', 'auth', 'credential',
    'pass', 'pwd', 'authorization', 'x-api-key', 'session_id'
]


def sanitize_data(data: Any) -> Any:
    """
    Sanitize data by removing or redacting sensitive information.

    Args:
        data: Data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized data with sensitive fields redacted
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in SENSITIVE_FIELDS):
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = sanitize_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str) and len(data) > 100:
        # Truncate very long strings to prevent log bloat
        return data[:100] + '...[truncated]'
    else:
        return data


def get_request_context() -> Dict[str, Any]:
    """
    Get current request context for logging.

    Returns:
        Dictionary with request context information
    """
    context = {
        'correlation_id': getattr(g, 'correlation_id', None),
        'timestamp': time.time()
    }

    # Add request information if we are in an active request context
    if has_request_context():
        context.update({
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100]  # Truncate
        })

    # Add user information if available
    if has_request_context() and 'user_id' in session:
        context.update({
            'user_id': session.get('user_id'),
            'user_name': session.get('name'),
            'user_department': session.get('department')
        })

    return context


def log_business_event(event_type: str, details: Dict[str, Any],
                      user_id: Optional[int] = None, level: str = 'info') -> None:
    """
    Log a business event with structured data.

    Args:
        event_type: Type of business event
        details: Event details (will be sanitized)
        user_id: Optional user ID (defaults to session user)
        level: Log level (info, warning, error)
    """
    context = get_request_context()

    log_data = {
        'event_type': event_type,
        'details': sanitize_data(details),
        'user_id': user_id or (session.get('user_id') if has_request_context() and session else None),
        **context
    }

    log_message = f"Business event: {event_type}"

    business_logger = logging.getLogger('business_events')
    valid_levels = {"debug", "info", "warning", "error", "critical"}
    chosen_level = level.lower()
    if chosen_level not in valid_levels:
        business_logger.warning(
            "Invalid log level '%s' supplied, defaulting to INFO", level,
            extra={**log_data, "invalid_level": level}
        )
        chosen_level = "info"
    getattr(business_logger, chosen_level)(log_message, extra=log_data)


def log_security_event(event_type: str, details: Dict[str, Any],
                      severity: str = 'warning') -> None:
    """
    Log a security event with enhanced context.

    Args:
        event_type: Type of security event
        details: Event details (will be sanitized)
        severity: Severity level (info, warning, error, critical)
    """
    context = get_request_context()

    log_data = {
        'event_type': event_type,
        'details': sanitize_data(details),
        'security_event': True,
        **context
    }

    log_message = f"Security event: {event_type}"

    # Get security logger and log at appropriate level
    security_logger = logging.getLogger('security_events')
    getattr(security_logger, severity.lower())(log_message, extra=log_data)


def log_performance_metric(operation: str, duration_ms: float,
                          details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a performance metric.

    Args:
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        details: Optional additional details
    """
    context = get_request_context()

    log_data = {
        'metric_type': 'performance',
        'operation': operation,
        'duration_ms': round(duration_ms, 2),
        'details': sanitize_data(details) if details else {},
        **context
    }

    # Determine log level based on duration
    if duration_ms > 5000:  # > 5 seconds
        level = 'warning'
    elif duration_ms > 1000:  # > 1 second
        level = 'info'
    else:
        level = 'debug'

    perf_logger = logging.getLogger('performance')
    getattr(perf_logger, level)(f"Performance: {operation} took {duration_ms:.2f}ms", extra=log_data)


def log_database_operation(operation: str, table: str, duration_ms: float,
                          affected_rows: Optional[int] = None) -> None:
    """
    Log a database operation.

    Args:
        operation: Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Duration in milliseconds
        affected_rows: Number of affected rows
    """
    context = get_request_context()

    log_data = {
        'metric_type': 'database',
        'operation': operation,
        'table': table,
        'duration_ms': round(duration_ms, 2),
        'affected_rows': affected_rows,
        **context
    }

    db_logger = logging.getLogger('database')
    db_logger.debug(f"Database: {operation} on {table} took {duration_ms:.2f}ms", extra=log_data)


def performance_monitor(operation_name: str):
    """
    Decorator to monitor performance of functions.

    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                log_performance_metric(operation_name, duration, {'success': True})
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                log_performance_metric(operation_name, duration, {
                    'success': False,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                raise
        return wrapper
    return decorator


def add_correlation_id():
    """Add correlation ID to Flask g object for request tracking."""
    if not hasattr(g, 'correlation_id'):
        g.correlation_id = str(uuid.uuid4())
    return g.correlation_id


def log_request_start():
    """Log the start of a request."""
    correlation_id = add_correlation_id()
    g.start_time = time.time()

    request_logger = logging.getLogger('requests')
    request_logger.info("Request started", extra={
        'correlation_id': correlation_id,
        'method': request.method,
        'path': request.path,
        'ip_address': request.remote_addr,
        'user_id': session.get('user_id') if session else None
    })


def log_request_end(response):
    """Log the end of a request."""
    if hasattr(g, 'start_time'):
        duration = (time.time() - g.start_time) * 1000

        request_logger = logging.getLogger('requests')
        request_logger.info("Request completed", extra={
            'correlation_id': getattr(g, 'correlation_id', None),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration, 2),
            'user_id': session.get('user_id') if session else None
        })

    return response


def setup_request_logging(app):
    """
    Set up request logging middleware for Flask app.

    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        log_request_start()

    @app.after_request
    def after_request(response):
        return log_request_end(response)

    logger.info("Request logging middleware configured")


def get_logger_with_context(name: str) -> logging.Logger:
    """
    Get a logger with automatic context injection.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
