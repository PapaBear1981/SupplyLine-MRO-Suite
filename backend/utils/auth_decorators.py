"""
Standardized Authentication Decorators
This module provides consistent authentication decorators that work with both JWT and session-based auth.
"""

from functools import wraps
from flask import request, jsonify, session, g, current_app
import jwt
import logging

logger = logging.getLogger(__name__)

def get_current_user():
    """
    Get the current user from either JWT token or session.
    Returns the user object or None if not authenticated.
    """
    try:
        # First try JWT token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Decode JWT token
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                
                # Get user from database
                from models import User
                user = User.query.get(payload['user_id'])
                if user and user.is_active:
                    return user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass
        
        # Fall back to session-based auth
        if 'user_id' in session:
            from models import User
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                return user
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None

def require_auth(f):
    """
    Decorator that requires authentication via JWT or session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Store user in g for use in the route
        g.current_user = user
        g.current_user_id = user.id
        g.is_admin = user.is_admin
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """
    Decorator that requires admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        # Store user in g for use in the route
        g.current_user = user
        g.current_user_id = user.id
        g.is_admin = user.is_admin
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_tool_manager(f):
    """
    Decorator that requires tool management privileges.
    Admin users or Materials department users can manage tools.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has tool management privileges
        # Allow admins or Materials department users
        if not (user.is_admin or user.department == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403
        
        # Store user in g for use in the route
        g.current_user = user
        g.current_user_id = user.id
        g.is_admin = user.is_admin
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_materials_manager(f):
    """
    Decorator that requires materials management privileges.
    Admin users or Materials department users can manage chemicals.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has materials management privileges
        # Allow admins or Materials department users
        if not (user.is_admin or user.department == 'Materials'):
            return jsonify({'error': 'Materials management privileges required'}), 403
        
        # Store user in g for use in the route
        g.current_user = user
        g.current_user_id = user.id
        g.is_admin = user.is_admin
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission_name):
    """
    Decorator that requires a specific permission via RBAC system.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user has the required permission
            if not user.has_permission(permission_name):
                return jsonify({'error': f'Permission {permission_name} required'}), 403
            
            # Store user in g for use in the route
            g.current_user = user
            g.current_user_id = user.id
            g.is_admin = user.is_admin
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_any_permission(*permission_names):
    """
    Decorator that requires any one of the specified permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user has any of the required permissions
            has_permission = any(user.has_permission(perm) for perm in permission_names)
            
            if not has_permission:
                return jsonify({'error': f'One of these permissions required: {", ".join(permission_names)}'}), 403
            
            # Store user in g for use in the route
            g.current_user = user
            g.current_user_id = user.id
            g.is_admin = user.is_admin
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_department(*departments):
    """
    Decorator that requires user to be in one of the specified departments.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user is in one of the required departments or is admin
            if not (user.is_admin or user.department in departments):
                return jsonify({'error': f'Department access required: {", ".join(departments)}'}), 403
            
            # Store user in g for use in the route
            g.current_user = user
            g.current_user_id = user.id
            g.is_admin = user.is_admin
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Backward compatibility aliases
admin_required = require_admin
tool_manager_required = require_tool_manager
materials_manager_required = require_materials_manager
permission_required = require_permission
