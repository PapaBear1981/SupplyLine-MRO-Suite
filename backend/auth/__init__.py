"""
Authentication module for SupplyLine MRO Suite

This module provides JWT-based authentication functionality.
"""

from .jwt_manager import (
    JWTManager,
    jwt_required,
    admin_required,
    permission_required,
    department_required
)

__all__ = [
    'JWTManager',
    'jwt_required',
    'admin_required',
    'permission_required',
    'department_required'
]
