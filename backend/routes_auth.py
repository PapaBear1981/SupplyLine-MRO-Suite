"""
JWT Authentication Routes for SupplyLine MRO Suite

This module provides JWT-based authentication endpoints including:
- Login with JWT token generation
- Token refresh
- Logout (token invalidation)
- User registration
- Password reset functionality
"""

import logging

from flask import current_app, jsonify, request
from werkzeug.exceptions import BadRequest

import utils as password_utils
from auth import JWTManager, jwt_required
from models import AuditLog, User, UserActivity, db


logger = logging.getLogger(__name__)


def register_auth_routes(app):
    """Register JWT authentication routes"""

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """JWT-based login endpoint"""
        try:
            # Get JSON data
            try:
                data = request.get_json() or {}
            except BadRequest:
                return jsonify({
                    "error": "Invalid JSON payload",
                    "code": "INVALID_JSON"
                }), 400

            # Basic validation
            employee_number = data.get("employee_number")
            password = data.get("password")

            if not employee_number or not password:
                return jsonify({"error": "Missing employee_number or password"}), 400

            # Find user
            user = User.query.filter_by(employee_number=employee_number).first()

            # SECURITY: Use timing-safe authentication to prevent user enumeration
            # Always perform password check even if user doesn't exist to prevent timing attacks
            if not user:
                # Perform a dummy password check to maintain consistent timing
                # Use a valid bcrypt hash format (this is a hash of "dummy_password")
                from werkzeug.security import check_password_hash
                dummy_hash = "pbkdf2:sha256:600000$dummysalt$dummyhashtopreventtimingattacks1234567890abcdef"
                try:
                    check_password_hash(dummy_hash, password)
                except Exception:
                    pass  # Ignore any errors from dummy check

                # SECURITY: PII REDACTION - Don't log employee numbers (PII)
                logger.warning(f"Login attempt for non-existent user from IP: {request.remote_addr}")
                # Return generic error - don't reveal if user exists
                return jsonify({
                    "error": "Invalid employee number or password",
                    "code": "INVALID_CREDENTIALS"
                }), 401

            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {user.id}")
                # Return generic error - don't reveal account status
                return jsonify({
                    "error": "Invalid employee number or password",
                    "code": "INVALID_CREDENTIALS"
                }), 401

            # Check account lockout
            if user.is_locked():
                logger.warning(f"Login attempt for locked account: {user.id}")
                # Return specific error for locked accounts (user already knows account exists)
                return jsonify({
                    "error": "Account is temporarily locked due to multiple failed login attempts. Please try again later.",
                    "code": "ACCOUNT_LOCKED"
                }), 423

            # Verify password
            if not user.check_password(password):
                # Increment failed login attempts
                user.increment_failed_login()
                db.session.commit()

                logger.warning(f"Failed login attempt for user {user.id}: {user.failed_login_attempts} attempts")

                # Log failed attempt
                activity = UserActivity(
                    user_id=user.id,
                    activity_type="login_failed",
                    description=f"Failed login attempt ({user.failed_login_attempts})",
                    ip_address=request.remote_addr
                )
                db.session.add(activity)
                db.session.commit()

                # Return generic error - don't differentiate between bad password and bad username
                return jsonify({
                    "error": "Invalid employee number or password",
                    "code": "INVALID_CREDENTIALS"
                }), 401

            # Successful login - reset failed attempts
            user.reset_failed_login_attempts()

            # Enforce password expiry policy (90 days)
            if hasattr(user, "is_password_expired") and user.is_password_expired():
                user.force_password_change = True

                activity = UserActivity(
                    user_id=user.id,
                    activity_type="password_expired",
                    description="User password expired - change required",
                    ip_address=request.remote_addr
                )
                db.session.add(activity)

                audit_log = AuditLog(
                    action_type="password_expired",
                    action_details=f"User {user.id} ({user.name}) password expired"
                )
                db.session.add(audit_log)
                db.session.commit()

                return jsonify({
                    "message": "Password change required",
                    "code": "PASSWORD_CHANGE_REQUIRED",
                    "user_id": user.id,
                    "employee_number": user.employee_number
                }), 200

            # Check if user needs to change password
            if hasattr(user, "force_password_change") and user.force_password_change:
                # Return special response indicating password change required
                return jsonify({
                    "message": "Password change required",
                    "code": "PASSWORD_CHANGE_REQUIRED",
                    "user_id": user.id,
                    "employee_number": user.employee_number
                }), 200

            # Generate JWT tokens
            tokens = JWTManager.generate_tokens(user)

            # Log successful login
            activity = UserActivity(
                user_id=user.id,
                activity_type="login",
                description="User logged in with JWT",
                ip_address=request.remote_addr
            )
            db.session.add(activity)

            audit_log = AuditLog(
                action_type="user_login",
                action_details=f"User {user.id} ({user.name}) logged in with JWT"
            )
            db.session.add(audit_log)
            db.session.commit()

            logger.info(f"Successful JWT login for user {user.id} ({user.name})")

            # SECURITY: Set tokens in HttpOnly cookies to prevent XSS attacks
            # Tokens are no longer accessible via JavaScript
            response = jsonify({
                "message": "Login successful",
                "user": user.to_dict(include_roles=True, include_permissions=True)
            })

            # Set access token cookie (HttpOnly, Secure, SameSite)
            response.set_cookie(
                "access_token",
                value=tokens["access_token"],
                max_age=900,  # 15 minutes
                httponly=True,  # Prevents JavaScript access
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),  # HTTPS only in production
                samesite="Lax",  # CSRF protection
                path="/"
            )

            # Set refresh token cookie (HttpOnly, Secure, SameSite)
            response.set_cookie(
                "refresh_token",
                value=tokens["refresh_token"],
                max_age=604800,  # 7 days
                httponly=True,  # Prevents JavaScript access
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),  # HTTPS only in production
                samesite="Lax",  # CSRF protection
                path="/"
            )

            return response, 200

        except Exception as e:
            logger.error(f"Login error: {e!s}")
            return jsonify({
                "error": "Internal server error",
                "code": "SERVER_ERROR"
            }), 500

    @app.route("/api/auth/refresh", methods=["POST"])
    def refresh_token():
        """Refresh JWT access token using refresh token from HttpOnly cookie"""
        try:
            # SECURITY: Extract refresh token from HttpOnly cookie (preferred)
            # or from request body (legacy support)
            refresh_token_value = request.cookies.get("refresh_token")

            if not refresh_token_value:
                # Fallback to request body for backward compatibility
                data = request.get_json(silent=True) or {}
                refresh_token_value = data.get("refresh_token")

            if not refresh_token_value:
                return jsonify({
                    "error": "Refresh token required",
                    "code": "MISSING_REFRESH_TOKEN"
                }), 400

            # Generate new tokens
            new_tokens = JWTManager.refresh_access_token(refresh_token_value)
            if not new_tokens:
                return jsonify({
                    "error": "Invalid or expired refresh token",
                    "code": "INVALID_REFRESH_TOKEN"
                }), 401

            logger.info("JWT tokens refreshed successfully")

            # SECURITY: Set new tokens in HttpOnly cookies
            response = jsonify({
                "message": "Tokens refreshed successfully"
            })

            # Set new access token cookie
            response.set_cookie(
                "access_token",
                value=new_tokens["access_token"],
                max_age=900,  # 15 minutes
                httponly=True,
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),
                samesite="Lax",
                path="/"
            )

            # Set new refresh token cookie
            response.set_cookie(
                "refresh_token",
                value=new_tokens["refresh_token"],
                max_age=604800,  # 7 days
                httponly=True,
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),
                samesite="Lax",
                path="/"
            )

            return response, 200

        except Exception as e:
            logger.error(f"Token refresh error: {e!s}")
            return jsonify({
                "error": "Internal server error",
                "code": "SERVER_ERROR"
            }), 500

    @app.route("/api/auth/logout", methods=["POST"])
    @jwt_required
    def logout():
        """JWT-based logout endpoint"""
        try:
            user_payload = request.current_user
            user_id = user_payload["user_id"]

            # Log logout activity
            activity = UserActivity(
                user_id=user_id,
                activity_type="logout",
                description="User logged out (JWT)",
                ip_address=request.remote_addr
            )
            db.session.add(activity)

            audit_log = AuditLog(
                action_type="user_logout",
                action_details=f'User {user_id} ({user_payload["user_name"]}) logged out'
            )
            db.session.add(audit_log)
            db.session.commit()

            logger.info(f"User {user_id} logged out successfully")

            # SECURITY: Clear HttpOnly cookies on logout
            # Note: In a production system, you might want to implement token blacklisting
            # For now, we rely on short token expiration times and cookie clearing
            response = jsonify({
                "message": "Logged out successfully"
            })

            # Clear access token cookie
            response.set_cookie(
                "access_token",
                value="",
                max_age=0,
                httponly=True,
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),
                samesite="Lax",
                path="/"
            )

            # Clear refresh token cookie
            response.set_cookie(
                "refresh_token",
                value="",
                max_age=0,
                httponly=True,
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),
                samesite="Lax",
                path="/"
            )

            return response, 200

        except Exception as e:
            logger.error(f"Logout error: {e!s}")
            return jsonify({
                "error": "Internal server error",
                "code": "SERVER_ERROR"
            }), 500

    @app.route("/api/auth/me", methods=["GET"])
    @jwt_required
    def get_current_user():
        """Get current user information from JWT token"""
        try:
            user_payload = request.current_user
            user_id = user_payload["user_id"]

            # Get fresh user data from database
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return jsonify({
                    "error": "User not found or inactive",
                    "code": "USER_NOT_FOUND"
                }), 404

            return jsonify({
                "user": user.to_dict(include_roles=True, include_permissions=True)
            }), 200

        except Exception as e:
            logger.error(f"Get current user error: {e!s}")
            return jsonify({
                "error": "Internal server error",
                "code": "SERVER_ERROR"
            }), 500

    @app.route("/api/auth/status", methods=["GET"])
    def auth_status():
        """Check authentication status"""
        try:
            user_payload = JWTManager.get_current_user()
            if not user_payload:
                return jsonify({
                    "authenticated": False,
                    "message": "Not authenticated"
                }), 200

            return jsonify({
                "authenticated": True,
                "user": {
                    "id": user_payload["user_id"],
                    "name": user_payload["user_name"],
                    "employee_number": user_payload["employee_number"],
                    "is_admin": user_payload["is_admin"],
                    "department": user_payload["department"],
                    "permissions": user_payload.get("permissions", [])
                }
            }), 200

        except Exception as e:
            logger.error(f"Auth status error: {e!s}")
            return jsonify({
                "authenticated": False,
                "error": "Internal server error"
            }), 500

    @app.route("/api/auth/csrf-token", methods=["GET"])
    @jwt_required
    def get_csrf_token():
        """Generate CSRF token for authenticated user"""
        try:
            user_payload = request.current_user
            token_secret = user_payload.get("jti", "")

            csrf_token = JWTManager.generate_csrf_token(
                user_payload["user_id"],
                token_secret
            )

            return jsonify({
                "csrf_token": csrf_token,
                "expires_in": 3600  # 1 hour
            }), 200

        except Exception as e:
            logger.error(f"CSRF token generation error: {e!s}")
            return jsonify({
                "error": "Failed to generate CSRF token"
            }), 500

    @app.route("/api/auth/change-password", methods=["POST"])
    def auth_change_password():
        """Change password for users with force_password_change flag"""
        try:
            data = request.get_json() or {}

            # Get required fields
            employee_number = data.get("employee_number")
            current_password = data.get("current_password")
            new_password = data.get("new_password")

            if not all([employee_number, current_password, new_password]):
                return jsonify({
                    "error": "Missing required fields: employee_number, current_password, new_password"
                }), 400

            # Find user
            user = User.query.filter_by(employee_number=employee_number).first()
            if not user:
                return jsonify({"error": "Invalid credentials"}), 401

            # Verify current password
            if not user.check_password(current_password):
                return jsonify({"error": "Invalid current password"}), 401

            # Check if user is required to change password
            if not (hasattr(user, "force_password_change") and user.force_password_change):
                return jsonify({"error": "Password change not required"}), 400

            # Validate password strength using comprehensive validation
            is_valid, errors = password_utils.validate_password_strength(new_password)
            if not is_valid:
                return jsonify({
                    "error": "Password does not meet security requirements",
                    "details": errors
                }), 400

            # Check password reuse
            if hasattr(user, "is_password_reused") and user.is_password_reused(new_password):
                return jsonify({"error": "New password cannot match any of your last 5 passwords"}), 400

            # Update password and clear force_password_change flag
            user.set_password(new_password)
            user.force_password_change = False
            db.session.commit()

            # Log password change
            activity = UserActivity(
                user_id=user.id,
                activity_type="password_change",
                description="User changed password (forced)",
                ip_address=request.remote_addr
            )
            db.session.add(activity)

            audit_log = AuditLog(
                action_type="password_change",
                action_details=f"User {user.id} ({user.name}) changed password (forced)"
            )
            db.session.add(audit_log)
            db.session.commit()

            logger.info(f"User {user.id} successfully changed password (forced)")

            # Generate JWT tokens for the user
            tokens = JWTManager.generate_tokens(user)

            # SECURITY: Set tokens in HttpOnly cookies to prevent XSS attacks
            # This ensures the user is properly authenticated after password change
            response = jsonify({
                "message": "Password changed successfully",
                "user": user.to_dict(include_roles=True, include_permissions=True)
            })

            # Set access token cookie (HttpOnly, Secure, SameSite)
            response.set_cookie(
                "access_token",
                value=tokens["access_token"],
                max_age=900,  # 15 minutes
                httponly=True,  # Prevents JavaScript access
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),  # HTTPS only in production
                samesite="Lax",  # CSRF protection
                path="/"
            )

            # Set refresh token cookie (HttpOnly, Secure, SameSite)
            response.set_cookie(
                "refresh_token",
                value=tokens["refresh_token"],
                max_age=604800,  # 7 days
                httponly=True,  # Prevents JavaScript access
                secure=current_app.config.get("SESSION_COOKIE_SECURE", True),  # HTTPS only in production
                samesite="Lax",  # CSRF protection
                path="/"
            )

            return response, 200

        except Exception as e:
            logger.error(f"Password change error: {e!s}")
            return jsonify({
                "error": "Internal server error",
                "code": "SERVER_ERROR"
            }), 500
