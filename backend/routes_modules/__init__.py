"""
Routes package for SupplyLine MRO Suite

This package contains modular route definitions organized by functionality.
"""

from .health import register_health_routes
from .admin import register_admin_routes
from .tools import register_tool_routes
from .users import register_user_routes
from .checkouts import register_checkout_routes

__all__ = [
    'register_health_routes',
    'register_admin_routes',
    'register_tool_routes',
    'register_user_routes',
    'register_checkout_routes'
]
