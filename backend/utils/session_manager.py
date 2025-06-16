"""
Secure Session Manager for SupplyLine MRO Suite

This module provides secure session management functionality including:
- Session creation with security tokens
- Session validation with timeout checks
- CSRF token generation and validation
- Secure session destruction
"""

import secrets
import logging
from datetime import datetime, timedelta, timezone
from flask import session, request, current_app
from functools import wraps

logger = logging.getLogger(__name__)

class SessionManager:
    """Secure session management class"""

    @staticmethod
    def create_session(user):
        """
        Create a new secure session for user

        Args:
            user: User object to create session for
        """
        # Clear any existing session data
        session.clear()

        # Set session data
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['is_admin'] = user.is_admin
        session['department'] = user.department
        session['login_time'] = datetime.now(timezone.utc).isoformat()
        session['last_activity'] = datetime.now(timezone.utc).isoformat()
        session['ip_address'] = request.remote_addr
        session['csrf_token'] = secrets.token_hex(16)

        # Make session permanent with timeout
        session.permanent = True

        logger.info(f"Secure session created for user {user.id} ({user.name})")

    @staticmethod
    def validate_session():
        """
        Validate current session security

        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if 'user_id' not in session:
            return False, 'No active session'

        try:
            # Check session age (8 hours max)
            login_time = datetime.fromisoformat(session.get('login_time', ''))
            if datetime.utcnow() - login_time > timedelta(hours=8):
                session.clear()
                return False, 'Session expired'
        except (ValueError, TypeError):
            session.clear()
            return False, 'Invalid session data'

        try:
            # Check activity timeout - get from system settings or use default (30 minutes)
            from models import SystemSettings
            timeout_minutes = SystemSettings.get_setting('auto_logout_timeout', 30)

            last_activity = datetime.fromisoformat(session.get('last_activity', ''))
            if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
                session.clear()
                return False, 'Session timeout due to inactivity'
        except (ValueError, TypeError):
            session.clear()
            return False, 'Invalid session data'

        # Optional: Validate IP address (can be problematic with proxies)
        # Disabled by default but can be enabled via config
        if (current_app.config.get('SESSION_VALIDATE_IP', False)
                and session.get('ip_address') != request.remote_addr):
            session.clear()
            return False, 'IP address mismatch'

        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()

        return True, 'Valid session'

    @staticmethod
    def destroy_session():
        """Securely destroy session"""
        session.clear()
        logger.info("Session destroyed")

    @staticmethod
    def generate_csrf_token():
        """Generate CSRF token for session"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']

    @staticmethod
    def validate_csrf_token():
        """Validate CSRF token from request"""
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        return token and token == session.get('csrf_token')

    @staticmethod
    def get_auto_logout_timeout():
        """
        Get the current auto logout timeout in minutes

        Returns:
            int: Timeout in minutes
        """
        try:
            from models import SystemSettings
            return SystemSettings.get_setting('auto_logout_timeout', 30)
        except Exception:
            return 30  # Default fallback

    @staticmethod
    def get_session_info():
        """
        Get current session information including timeout settings

        Returns:
            dict: Session information
        """
        if 'user_id' not in session:
            return None

        try:
            login_time = datetime.fromisoformat(session.get('login_time', ''))
            last_activity = datetime.fromisoformat(session.get('last_activity', ''))
            timeout_minutes = SessionManager.get_auto_logout_timeout()

            # Calculate remaining time
            time_since_activity = datetime.now() - last_activity
            remaining_seconds = max(0, (timeout_minutes * 60) - time_since_activity.total_seconds())

            return {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name'),
                'login_time': login_time.isoformat(),
                'last_activity': last_activity.isoformat(),
                'timeout_minutes': timeout_minutes,
                'remaining_seconds': int(remaining_seconds),
                'is_active': remaining_seconds > 0
            }
        except (ValueError, TypeError):
            return None


def secure_login_required(f):
    """Decorator for secure login requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        valid, message = SessionManager.validate_session()
        if not valid:
            from flask import jsonify
            return jsonify({'error': 'Authentication required', 'reason': message}), 401
        return f(*args, **kwargs)
    return decorated_function


def secure_admin_required(f):
    """Decorator for secure admin requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        valid, message = SessionManager.validate_session()
        if not valid:
            from flask import jsonify
            return jsonify({'error': 'Authentication required', 'reason': message}), 401

        if not session.get('is_admin', False):
            from flask import jsonify
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function


def csrf_required(f):
    """Decorator for CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (request.method in ['POST', 'PUT', 'DELETE']
                and not SessionManager.validate_csrf_token()):
            from flask import jsonify
            return jsonify({'error': 'CSRF token validation failed'}), 403
        return f(*args, **kwargs)
    return decorated_function
