"""
Authentication module for SupplyLine MRO Suite

This module provides JWT-based authentication functionality.
"""

from .jwt_manager import (
    JWTManager,
    jwt_required,
    admin_required,
    permission_required,
    department_required,
    csrf_required,
    login_required,
    tool_manager_required,
    materials_manager_required
)

__all__ = [
    'JWTManager',
    'jwt_required',
    'admin_required',
    'permission_required',
    'department_required',
    'csrf_required',
    'login_required',
    'tool_manager_required',
    'materials_manager_required'
]
