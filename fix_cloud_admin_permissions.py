#!/usr/bin/env python3
"""
Fix Cloud Admin Permissions Script
This script fixes the admin user permissions in the cloud database.
"""

import os
import sys
import logging
import psycopg2
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_cloud_db():
    """Connect to the Cloud SQL database via proxy."""
    try:
        # Database connection parameters for Cloud SQL
        conn_params = {
            'host': '127.0.0.1',  # Cloud SQL Proxy
            'port': 5432,
            'database': 'supplyline',
            'user': 'supplyline_user',
            'password': 'SupplyLine2025SecurePass!'
        }
        
        conn = psycopg2.connect(**conn_params)
        logger.info("✓ Connected to Cloud SQL database")
        return conn
        
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def fix_admin_permissions(conn):
    """Fix admin user permissions in the cloud database."""
    try:
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id, name, department, is_admin FROM users WHERE employee_number = %s", ('ADMIN001',))
        admin_user = cursor.fetchone()
        
        if not admin_user:
            logger.error("Admin user ADMIN001 not found!")
            return False
        
        user_id, name, department, is_admin = admin_user
        logger.info(f"Found admin user: {name}")
        logger.info(f"Current department: {department}")
        logger.info(f"Is admin: {is_admin}")
        
        # Update admin user department to Materials
        cursor.execute("""
            UPDATE users 
            SET department = %s, is_admin = %s, is_active = %s 
            WHERE employee_number = %s
        """, ('Materials', True, True, 'ADMIN001'))
        
        logger.info("✓ Updated admin user department to 'Materials'")
        
        # Create default permissions if they don't exist
        default_permissions = [
            ('user.view', 'View users', 'User Management'),
            ('user.create', 'Create users', 'User Management'),
            ('user.edit', 'Edit users', 'User Management'),
            ('user.delete', 'Delete users', 'User Management'),
            ('tool.view', 'View tools', 'Tool Management'),
            ('tool.create', 'Create tools', 'Tool Management'),
            ('tool.edit', 'Edit tools', 'Tool Management'),
            ('tool.delete', 'Delete tools', 'Tool Management'),
            ('tool.checkout', 'Checkout tools', 'Tool Management'),
            ('tool.return', 'Return tools', 'Tool Management'),
            ('tool.manage', 'Manage tools', 'Tool Management'),
            ('chemical.view', 'View chemicals', 'Chemical Management'),
            ('chemical.create', 'Create chemicals', 'Chemical Management'),
            ('chemical.edit', 'Edit chemicals', 'Chemical Management'),
            ('chemical.delete', 'Delete chemicals', 'Chemical Management'),
            ('chemical.issue', 'Issue chemicals', 'Chemical Management'),
            ('chemical.manage', 'Manage chemicals', 'Chemical Management'),
            ('calibration.view', 'View calibrations', 'Calibration Management'),
            ('calibration.create', 'Create calibrations', 'Calibration Management'),
            ('calibration.edit', 'Edit calibrations', 'Calibration Management'),
            ('calibration.delete', 'Delete calibrations', 'Calibration Management'),
            ('report.view', 'View reports', 'Reporting'),
            ('report.generate', 'Generate reports', 'Reporting'),
            ('admin.dashboard', 'Access admin dashboard', 'Administration'),
            ('admin.settings', 'Manage settings', 'Administration'),
            ('admin.announcements', 'Manage announcements', 'Administration'),
        ]
        
        # Insert permissions (ignore if they already exist)
        for perm_name, perm_desc, perm_category in default_permissions:
            cursor.execute("""
                INSERT INTO permissions (name, description, category, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (perm_name, perm_desc, perm_category, datetime.utcnow()))
        
        logger.info("✓ Created/verified permissions")
        
        # Create default roles if they don't exist
        cursor.execute("""
            INSERT INTO roles (name, description, is_system_role, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, ('Administrator', 'Full system access with all permissions', True, datetime.utcnow()))
        
        cursor.execute("""
            INSERT INTO roles (name, description, is_system_role, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, ('Materials Manager', 'Can manage tools, chemicals, and users', True, datetime.utcnow()))
        
        logger.info("✓ Created/verified roles")
        
        # Get role and permission IDs
        cursor.execute("SELECT id FROM roles WHERE name = %s", ('Administrator',))
        admin_role_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM permissions")
        permission_ids = [row[0] for row in cursor.fetchall()]
        
        # Clear existing role permissions for admin role
        cursor.execute("DELETE FROM role_permissions WHERE role_id = %s", (admin_role_id,))
        
        # Assign all permissions to Administrator role
        for perm_id in permission_ids:
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id, created_at)
                VALUES (%s, %s, %s)
            """, (admin_role_id, perm_id, datetime.utcnow()))
        
        logger.info(f"✓ Assigned {len(permission_ids)} permissions to Administrator role")
        
        # Clear existing user roles for admin user
        cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        
        # Assign Administrator role to admin user
        cursor.execute("""
            INSERT INTO user_roles (user_id, role_id, created_at)
            VALUES (%s, %s, %s)
        """, (user_id, admin_role_id, datetime.utcnow()))
        
        logger.info("✓ Assigned Administrator role to admin user")
        
        # Commit all changes
        conn.commit()
        logger.info("✓ All changes committed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing admin permissions: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function."""
    logger.info("Starting cloud admin permissions fix...")
    
    # Connect to database
    conn = connect_to_cloud_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        # Fix admin permissions
        if fix_admin_permissions(conn):
            logger.info("🎉 Cloud admin permissions fix completed successfully!")
            return True
        else:
            logger.error("❌ Failed to fix admin permissions")
            return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
