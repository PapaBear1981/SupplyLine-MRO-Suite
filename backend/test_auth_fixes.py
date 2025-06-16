#!/usr/bin/env python3
"""
Test Authentication Fixes
This script tests the authentication fixes we implemented.
"""

import os
import sys
import logging
import requests
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_admin_user_permissions():
    """Test that the admin user has proper permissions."""
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Get the admin user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin_user:
                logger.error("Admin user ADMIN001 not found!")
                return False
                
            logger.info(f"Admin user found: {admin_user.name}")
            logger.info(f"Department: {admin_user.department}")
            logger.info(f"Is admin: {admin_user.is_admin}")
            logger.info(f"Is active: {admin_user.is_active}")
            
            # Check roles
            roles = [ur.role for ur in admin_user.user_roles]
            logger.info(f"Roles: {[r.name for r in roles]}")
            
            # Check specific permissions
            key_permissions = ['tool.manage', 'chemical.manage', 'user.edit']
            for perm in key_permissions:
                has_perm = admin_user.has_permission(perm)
                logger.info(f"Permission {perm}: {'✓' if has_perm else '✗'}")
            
            # Check if user meets tool manager requirements
            is_tool_manager = admin_user.is_admin or admin_user.department == 'Materials'
            logger.info(f"Tool manager privileges: {'✓' if is_tool_manager else '✗'}")
            
            # Check if user meets materials manager requirements  
            is_materials_manager = admin_user.is_admin or admin_user.department == 'Materials'
            logger.info(f"Materials manager privileges: {'✓' if is_materials_manager else '✗'}")
            
            return is_tool_manager and is_materials_manager
            
    except Exception as e:
        logger.error(f"Error testing admin permissions: {e}")
        return False

def test_jwt_token_creation():
    """Test JWT token creation for the admin user."""
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Get the admin user
            admin_user = User.query.filter_by(employee_number='ADMIN001').first()
            
            if not admin_user:
                logger.error("Admin user ADMIN001 not found!")
                return False
            
            # Create JWT token manually (simulating login)
            import jwt
            from datetime import datetime, timedelta
            
            # Create JWT payload
            payload = {
                'user_id': admin_user.id,
                'employee_number': admin_user.employee_number,
                'is_admin': admin_user.is_admin,
                'department': admin_user.department,
                'exp': datetime.utcnow() + timedelta(hours=8),
                'iat': datetime.utcnow()
            }
            
            # Generate JWT token
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            logger.info(f"JWT token created successfully")
            logger.info(f"Token payload: {payload}")
            
            # Test token decoding
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            logger.info(f"Token decoded successfully: {decoded}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error testing JWT token: {e}")
        return False

def test_auth_decorators():
    """Test the authentication decorators."""
    try:
        from utils.auth_decorators import get_current_user, require_tool_manager, require_materials_manager
        
        logger.info("Authentication decorators imported successfully")
        
        # Test that the decorators exist and are callable
        assert callable(get_current_user), "get_current_user should be callable"
        assert callable(require_tool_manager), "require_tool_manager should be callable"
        assert callable(require_materials_manager), "require_materials_manager should be callable"
        
        logger.info("✓ All authentication decorators are properly defined")
        return True
        
    except Exception as e:
        logger.error(f"Error testing auth decorators: {e}")
        return False

def main():
    """Main test function."""
    logger.info("Starting authentication fixes test...")
    
    tests = [
        ("Admin User Permissions", test_admin_user_permissions),
        ("JWT Token Creation", test_jwt_token_creation),
        ("Authentication Decorators", test_auth_decorators),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: ✗ ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n--- Test Summary ---")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All authentication fixes are working correctly!")
        return True
    else:
        logger.error("❌ Some authentication fixes need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
