"""
Secure Session Manager for SupplyLine MRO Suite

This module provides secure session management functionality including:
- Session creation with security tokens
- Session validation with timeout checks
- CSRF token generation and validation
- Secure session destruction
"""

import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import current_app, request, session


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
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["is_admin"] = user.is_admin
        session["department"] = user.department
        session["login_time"] = datetime.utcnow().isoformat()
        session["last_activity"] = datetime.utcnow().isoformat()
        session["ip_address"] = request.remote_addr
        session["csrf_token"] = secrets.token_hex(16)

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
        if "user_id" not in session:
            return False, "No active session"

        try:
            # Check session age (8 hours max)
            login_time = datetime.fromisoformat(session.get("login_time", ""))
            if datetime.utcnow() - login_time > timedelta(hours=8):
                session.clear()
                return False, "Session expired"
        except (ValueError, TypeError):
            session.clear()
            return False, "Invalid session data"

        try:
            # Check activity timeout (30 minutes)
            last_activity = datetime.fromisoformat(session.get("last_activity", ""))
            if datetime.utcnow() - last_activity > timedelta(minutes=30):
                session.clear()
                return False, "Session timeout due to inactivity"
        except (ValueError, TypeError):
            session.clear()
            return False, "Invalid session data"

        # Optional: Validate IP address (can be problematic with proxies)
        # Disabled by default but can be enabled via config
        if (current_app.config.get("SESSION_VALIDATE_IP", False)
                and session.get("ip_address") != request.remote_addr):
            session.clear()
            return False, "IP address mismatch"

        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()

        return True, "Valid session"

    @staticmethod
    def destroy_session():
        """Securely destroy session"""
        session.clear()
        logger.info("Session destroyed")

    @staticmethod
    def generate_csrf_token():
        """Generate CSRF token for session"""
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return session["csrf_token"]

    @staticmethod
    def validate_csrf_token():
        """Validate CSRF token from request"""
        token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        return token and token == session.get("csrf_token")


def secure_login_required(f):
    """Decorator for secure login requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        valid, message = SessionManager.validate_session()
        if not valid:
            from flask import jsonify
            return jsonify({"error": "Authentication required", "reason": message}), 401
        return f(*args, **kwargs)
    return decorated_function


def secure_admin_required(f):
    """Decorator for secure admin requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        valid, message = SessionManager.validate_session()
        if not valid:
            from flask import jsonify
            return jsonify({"error": "Authentication required", "reason": message}), 401

        if not session.get("is_admin", False):
            from flask import jsonify
            return jsonify({"error": "Admin privileges required"}), 403

        return f(*args, **kwargs)
    return decorated_function


def csrf_required(f):
    """Decorator for CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (request.method in ["POST", "PUT", "DELETE"]
                and not SessionManager.validate_csrf_token()):
            from flask import jsonify
            return jsonify({"error": "CSRF token validation failed"}), 403
        return f(*args, **kwargs)
    return decorated_function
