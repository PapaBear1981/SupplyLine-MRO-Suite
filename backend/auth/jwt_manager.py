"""
JWT Authentication Manager for SupplyLine MRO Suite

This module provides JWT-based authentication functionality including:
- Access and refresh token generation
- Token validation and verification
- Secure token management
- User authentication decorators
"""

import jwt
import secrets
import logging
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from functools import wraps
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT Authentication Manager"""
    
    @staticmethod
    def generate_tokens(user) -> Dict[str, str]:
        """
        Generate access and refresh tokens for user
        
        Args:
            user: User object to generate tokens for
            
        Returns:
            Dict containing access_token and refresh_token
        """
        now = datetime.now(timezone.utc)
        
        # Access token payload (short-lived: 15 minutes)
        access_payload = {
            'user_id': user.id,
            'user_name': user.name,
            'employee_number': user.employee_number,
            'is_admin': user.is_admin,
            'department': user.department,
            'permissions': user.get_permissions(),
            'iat': now,
            'exp': now + timedelta(minutes=15),
            'type': 'access'
        }
        
        # Refresh token payload (long-lived: 7 days)
        refresh_payload = {
            'user_id': user.id,
            'iat': now,
            'exp': now + timedelta(days=7),
            'type': 'refresh',
            'jti': secrets.token_hex(16)  # JWT ID for token revocation
        }
        
        secret_key = current_app.config['SECRET_KEY']
        
        access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
        
        logger.info(f"JWT tokens generated for user {user.id} ({user.name})")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 900,  # 15 minutes in seconds
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def verify_token(token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            secret_key = current_app.config['SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('type') != token_type:
                logger.warning(f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token pair or None if refresh token is invalid
        """
        payload = JWTManager.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        # Get user from database
        from models import User
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            logger.warning(f"User {payload['user_id']} not found or inactive")
            return None
        
        # Generate new tokens
        return JWTManager.generate_tokens(user)
    
    @staticmethod
    def extract_token_from_header() -> Optional[str]:
        """
        Extract JWT token from Authorization header
        
        Returns:
            Token string or None if not found
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """
        Get current user from JWT token
        
        Returns:
            User payload from token or None if not authenticated
        """
        token = JWTManager.extract_token_from_header()
        if not token:
            return None
        
        return JWTManager.verify_token(token, 'access')


def jwt_required(f):
    """Decorator for JWT authentication requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        
        # Add user info to request context
        request.current_user = user_payload
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for admin privilege requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        
        if not user_payload.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required', 'code': 'ADMIN_REQUIRED'}), 403
        
        # Add user info to request context
        request.current_user = user_payload
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name: str):
    """Decorator for specific permission requirement"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_payload = JWTManager.get_current_user()
            if not user_payload:
                return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
            
            permissions = user_payload.get('permissions', [])
            if permission_name not in permissions:
                return jsonify({
                    'error': f'Permission {permission_name} required',
                    'code': 'PERMISSION_REQUIRED'
                }), 403
            
            # Add user info to request context
            request.current_user = user_payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def department_required(department_name: str):
    """Decorator for department-specific access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_payload = JWTManager.get_current_user()
            if not user_payload:
                return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
            
            # Allow admin access to all departments
            if user_payload.get('is_admin', False):
                request.current_user = user_payload
                return f(*args, **kwargs)
            
            user_department = user_payload.get('department')
            if user_department != department_name:
                return jsonify({
                    'error': f'Access restricted to {department_name} department',
                    'code': 'DEPARTMENT_REQUIRED'
                }), 403
            
            # Add user info to request context
            request.current_user = user_payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator
