"""
Authentication module for SupplyLine MRO Suite

This module provides JWT-based authentication functionality.
"""

from .jwt_manager import JWTManager, admin_required, csrf_required, department_required, jwt_required, permission_required


__all__ = [
    "JWTManager",
    "admin_required",
    "csrf_required",
    "department_required",
    "jwt_required",
    "permission_required"
]
