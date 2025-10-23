"""
Migration: Add Page Access Permissions
Date: 2025-10-17
Purpose: Add page-level access control permissions to restrict which pages users can access

This migration adds a new category of permissions called "Page Access" that controls
which pages/routes users can access in the application.

Note: Dashboard (/dashboard) is accessible to all authenticated users by default.
"""

import sys
import os
import io
import secrets

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for stdout to handle emoji characters on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app  # noqa: E402
from models import db, Permission, Role, RolePermission  # noqa: E402


def _ensure_security_defaults():
    """Ensure required security configuration is present for the migration."""
    # Mark the environment as testing so Config.validate_security_config
    # will allow programmatic defaults. This prevents CI/CD runs from
    # failing when SECRET_KEY/JWT_SECRET_KEY are not provided explicitly.
    os.environ.setdefault("FLASK_ENV", "testing")

    # Generate ephemeral secrets if they are missing. These values are
    # only used for the lifetime of this migration process and do not
    # persist beyond it.
    if not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = secrets.token_urlsafe(64)

    if not os.environ.get("JWT_SECRET_KEY"):
        os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)


def run_migration():
    """Add page access permissions to the database"""
    _ensure_security_defaults()

    app = create_app()
    
    with app.app_context():
        print("Starting page access permissions migration...")
        
        # Define page access permissions
        # Format: (name, description, category)
        page_permissions = [
            # Tools pages
            ('page.tools', 'Access Tools page', 'Page Access'),
            
            # Checkouts pages
            ('page.checkouts', 'Access Checkouts page', 'Page Access'),
            ('page.my_checkouts', 'Access My Checkouts page', 'Page Access'),
            
            # Kits pages
            ('page.kits', 'Access Kits page', 'Page Access'),
            
            # Chemicals pages
            ('page.chemicals', 'Access Chemicals page', 'Page Access'),
            
            # Calibration pages
            ('page.calibrations', 'Access Calibrations page', 'Page Access'),
            
            # Reports page
            ('page.reports', 'Access Reports page', 'Page Access'),
            
            # Scanner page
            ('page.scanner', 'Access Scanner page', 'Page Access'),
            
            # Warehouses page
            ('page.warehouses', 'Access Warehouses page', 'Page Access'),
            
            # Admin pages
            ('page.admin_dashboard', 'Access Admin Dashboard', 'Page Access'),
            ('page.aircraft_types', 'Access Aircraft Types Management', 'Page Access'),
            
            # Profile page (all users should have this)
            ('page.profile', 'Access Profile page', 'Page Access'),
        ]
        
        # Create permissions
        created_permissions = []
        new_count = 0
        for name, description, category in page_permissions:
            # Check if permission already exists
            existing = Permission.query.filter_by(name=name).first()
            if existing:
                print(f"  ⚠️  Permission '{name}' already exists, skipping...")
                created_permissions.append(existing)
                continue

            permission = Permission(
                name=name,
                description=description,
                category=category
            )
            db.session.add(permission)
            created_permissions.append(permission)
            new_count += 1
            print(f"  ✅ Created permission: {name}")

        db.session.commit()
        print(f"\n✅ Created {new_count} new page access permissions")
        
        # Assign page permissions to roles
        print("\nAssigning page permissions to roles...")
        
        # Get roles
        admin_role = Role.query.filter_by(name='Administrator').first()
        materials_manager_role = Role.query.filter_by(name='Materials Manager').first()
        maintenance_user_role = Role.query.filter_by(name='Maintenance User').first()
        quality_inspector_role = Role.query.filter_by(name='Quality Inspector').first()
        
        if not admin_role or not materials_manager_role or not maintenance_user_role:
            print("  ⚠️  Warning: Some default roles not found. Skipping role assignment.")
            print("     You'll need to assign page permissions manually.")
            return
        
        # Administrator gets ALL page permissions
        print("\n  Administrator Role:")
        for permission in created_permissions:
            if not any(rp.permission_id == permission.id for rp in admin_role.role_permissions):
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id
                )
                db.session.add(role_permission)
                print(f"    ✅ Added: {permission.name}")
        
        # Materials Manager gets most pages (everything except admin pages)
        print("\n  Materials Manager Role:")
        materials_pages = [
            'page.tools', 'page.checkouts', 'page.my_checkouts', 'page.kits',
            'page.chemicals', 'page.calibrations', 'page.reports', 
            'page.scanner', 'page.warehouses', 'page.profile'
        ]
        for perm_name in materials_pages:
            permission = next((p for p in created_permissions if p.name == perm_name), None)
            if permission and not any(rp.permission_id == permission.id for rp in materials_manager_role.role_permissions):
                role_permission = RolePermission(
                    role_id=materials_manager_role.id,
                    permission_id=permission.id
                )
                db.session.add(role_permission)
                print(f"    ✅ Added: {permission.name}")
        
        # Maintenance User gets ONLY dashboard, kits, and profile
        # This is the restricted role - can only access their dashboard and kits
        print("\n  Maintenance User Role:")
        maintenance_pages = [
            'page.kits',  # Can access kits
            'page.my_checkouts',  # Can see their own checkouts
            'page.profile'  # Can access their profile
        ]
        for perm_name in maintenance_pages:
            permission = next((p for p in created_permissions if p.name == perm_name), None)
            if permission and not any(rp.permission_id == permission.id for rp in maintenance_user_role.role_permissions):
                role_permission = RolePermission(
                    role_id=maintenance_user_role.id,
                    permission_id=permission.id
                )
                db.session.add(role_permission)
                print(f"    ✅ Added: {permission.name}")
        
        # Quality Inspector gets tools, checkouts, calibrations, reports, scanner, profile
        if quality_inspector_role:
            print("\n  Quality Inspector Role:")
            quality_pages = [
                'page.tools', 'page.checkouts', 'page.my_checkouts',
                'page.calibrations', 'page.reports', 'page.scanner', 'page.profile'
            ]
            for perm_name in quality_pages:
                permission = next((p for p in created_permissions if p.name == perm_name), None)
                if permission and not any(rp.permission_id == permission.id for rp in quality_inspector_role.role_permissions):
                    role_permission = RolePermission(
                        role_id=quality_inspector_role.id,
                        permission_id=permission.id
                    )
                    db.session.add(role_permission)
                    print(f"    ✅ Added: {permission.name}")
        
        db.session.commit()
        print("\n✅ Page permissions assigned to roles successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print("\nPage Access Permissions Created:")
        print("  - Total: 13 permissions")
        print("  - Category: Page Access")
        print("\nRole Assignments:")
        print("  - Administrator: ALL pages (13 permissions)")
        print("  - Materials Manager: Most pages except admin (10 permissions)")
        print("  - Maintenance User: RESTRICTED - Dashboard, Kits, My Checkouts, Profile only (3 permissions)")
        print("  - Quality Inspector: Tools, Checkouts, Calibrations, Reports, Scanner, Profile (7 permissions)")
        print("\nNote: Dashboard (/dashboard) is accessible to ALL authenticated users by default.")
        print("="*60)


if __name__ == '__main__':
    run_migration()
