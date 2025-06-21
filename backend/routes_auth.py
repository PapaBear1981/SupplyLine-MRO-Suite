"""
JWT Authentication Routes for SupplyLine MRO Suite

This module provides JWT-based authentication endpoints including:
- Login with JWT token generation
- Token refresh
- Logout (token invalidation)
- User registration
- Password reset functionality
"""

from flask import request, jsonify, current_app
from models import db, User, UserActivity, AuditLog
from auth import JWTManager, jwt_required, csrf_required
from security import validate_request_data, rate_limit, log_security_event
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_auth_routes(app):
    """Register JWT authentication routes"""

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """JWT-based login endpoint"""
        try:
            # Get JSON data
            data = request.get_json() or {}

            # Basic validation
            employee_number = data.get('employee_number')
            password = data.get('password')

            if not employee_number or not password:
                return jsonify({'error': 'Missing employee_number or password'}), 400
            
            # Find user
            user = User.query.filter_by(employee_number=employee_number).first()
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {user.id}")
                return jsonify({
                    'error': 'Account is inactive',
                    'code': 'ACCOUNT_INACTIVE'
                }), 401
            
            # Check account lockout
            if user.is_account_locked():
                logger.warning(f"Login attempt for locked account: {user.id}")
                return jsonify({
                    'error': 'Account is temporarily locked due to failed login attempts',
                    'code': 'ACCOUNT_LOCKED'
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
                    activity_type='login_failed',
                    description=f'Failed login attempt ({user.failed_login_attempts})',
                    ip_address=request.remote_addr
                )
                db.session.add(activity)
                db.session.commit()
                
                return jsonify({
                    'error': 'Invalid credentials',
                    'code': 'INVALID_CREDENTIALS'
                }), 401
            
            # Successful login - reset failed attempts
            user.reset_failed_login_attempts()
            
            # Generate JWT tokens
            tokens = JWTManager.generate_tokens(user)
            
            # Log successful login
            activity = UserActivity(
                user_id=user.id,
                activity_type='login',
                description='User logged in with JWT',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            
            audit_log = AuditLog(
                action_type='user_login',
                action_details=f'User {user.id} ({user.name}) logged in with JWT'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            logger.info(f"Successful JWT login for user {user.id} ({user.name})")
            
            # Return tokens and user info
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(include_roles=True, include_permissions=True),
                **tokens
            }), 200
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh_token():
        """Refresh JWT access token using refresh token"""
        try:
            data = request.get_json() or {}
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({
                    'error': 'Refresh token required',
                    'code': 'MISSING_REFRESH_TOKEN'
                }), 400
            
            # Generate new tokens
            new_tokens = JWTManager.refresh_access_token(refresh_token)
            if not new_tokens:
                return jsonify({
                    'error': 'Invalid or expired refresh token',
                    'code': 'INVALID_REFRESH_TOKEN'
                }), 401
            
            logger.info("JWT tokens refreshed successfully")
            return jsonify({
                'message': 'Tokens refreshed successfully',
                **new_tokens
            }), 200
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required
    def logout():
        """JWT-based logout endpoint"""
        try:
            user_payload = request.current_user
            user_id = user_payload['user_id']
            
            # Log logout activity
            activity = UserActivity(
                user_id=user_id,
                activity_type='logout',
                description='User logged out (JWT)',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            
            audit_log = AuditLog(
                action_type='user_logout',
                action_details=f'User {user_id} ({user_payload["user_name"]}) logged out'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            logger.info(f"User {user_id} logged out successfully")
            
            # Note: In a production system, you might want to implement token blacklisting
            # For now, we rely on short token expiration times
            
            return jsonify({
                'message': 'Logged out successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required
    def get_current_user():
        """Get current user information from JWT token"""
        try:
            user_payload = request.current_user
            user_id = user_payload['user_id']
            
            # Get fresh user data from database
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'error': 'User not found or inactive',
                    'code': 'USER_NOT_FOUND'
                }), 404
            
            return jsonify({
                'user': user.to_dict(include_roles=True, include_permissions=True)
            }), 200
            
        except Exception as e:
            logger.error(f"Get current user error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
    
    @app.route('/api/auth/status', methods=['GET'])
    def auth_status():
        """Check authentication status"""
        try:
            user_payload = JWTManager.get_current_user()
            if not user_payload:
                return jsonify({
                    'authenticated': False,
                    'message': 'Not authenticated'
                }), 200

            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user_payload['user_id'],
                    'name': user_payload['user_name'],
                    'employee_number': user_payload['employee_number'],
                    'is_admin': user_payload['is_admin'],
                    'department': user_payload['department'],
                    'permissions': user_payload.get('permissions', [])
                }
            }), 200

        except Exception as e:
            logger.error(f"Auth status error: {str(e)}")
            return jsonify({
                'authenticated': False,
                'error': 'Internal server error'
            }), 500

    @app.route('/api/auth/csrf-token', methods=['GET'])
    @jwt_required
    def get_csrf_token():
        """Generate CSRF token for authenticated user"""
        try:
            user_payload = request.current_user
            token_secret = user_payload.get('jti', '')

            csrf_token = JWTManager.generate_csrf_token(
                user_payload['user_id'],
                token_secret
            )

            return jsonify({
                'csrf_token': csrf_token,
                'expires_in': 3600  # 1 hour
            }), 200

        except Exception as e:
            logger.error(f"CSRF token generation error: {str(e)}")
            return jsonify({
                'error': 'Failed to generate CSRF token'
            }), 500
