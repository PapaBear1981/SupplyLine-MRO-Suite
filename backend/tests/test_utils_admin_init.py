"""
Tests for utils/admin_init.py - Secure Admin Initialization Utility
"""

import os
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from utils.admin_init import (
    create_secure_admin,
    reset_admin_password,
    validate_admin_setup,
)


class TestCreateSecureAdmin:
    """Tests for create_secure_admin function"""

    def test_admin_already_exists(self, app, db_session, admin_user):
        """Test when admin user already exists"""
        with app.app_context():
            success, message, password = create_secure_admin()

        assert success is True
        assert message == "Admin user already exists"
        assert password is None

    def test_create_admin_with_generated_password(self, app, db_session, capsys):
        """Test creating admin with auto-generated password when no env var"""
        from models import User

        with app.app_context():
            # Ensure no admin exists
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            # Remove env var if set
            env_backup = os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

            try:
                success, message, password = create_secure_admin()

                assert success is True
                assert message == "Admin user created successfully"
                assert password is not None
                assert len(password) >= 16  # token_urlsafe(16) generates ~22 chars

                # Verify admin was created
                admin = User.query.filter_by(is_admin=True).first()
                assert admin is not None
                assert admin.name == "System Administrator"
                assert admin.employee_number == "ADMIN001"
                assert admin.department == "IT"
                assert admin.is_active is True

                # Check password was printed
                captured = capsys.readouterr()
                assert "IMPORTANT: Generated admin password:" in captured.out
                assert password in captured.out

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup

    def test_create_admin_with_env_password(self, app, db_session):
        """Test creating admin with password from environment variable"""
        from models import User

        with app.app_context():
            # Ensure no admin exists
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            env_backup = os.environ.get("INITIAL_ADMIN_PASSWORD")
            # Strong password meeting requirements
            os.environ["INITIAL_ADMIN_PASSWORD"] = "StrongP@ssw0rd123!"

            try:
                success, message, password = create_secure_admin()

                assert success is True
                assert message == "Admin user created successfully"
                assert password is None  # No password returned when using env var

                # Verify admin was created
                admin = User.query.filter_by(is_admin=True).first()
                assert admin is not None
                assert admin.check_password("StrongP@ssw0rd123!")

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup
                else:
                    os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

    def test_create_admin_with_weak_env_password(self, app, db_session):
        """Test that weak password from env var is rejected"""
        from models import User

        with app.app_context():
            # Ensure no admin exists
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            env_backup = os.environ.get("INITIAL_ADMIN_PASSWORD")
            os.environ["INITIAL_ADMIN_PASSWORD"] = "weak"

            try:
                success, message, password = create_secure_admin()

                assert success is False
                assert "minimum complexity requirements" in message
                assert password is None

                # Verify no admin was created
                admin = User.query.filter_by(is_admin=True).first()
                assert admin is None

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup
                else:
                    os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

    def test_password_complexity_requirements(self, app, db_session):
        """Test various password complexity scenarios"""
        from models import User

        test_cases = [
            ("short", False),  # Too short
            ("nouppercase123!", False),  # No uppercase
            ("NOLOWERCASE123!", False),  # No lowercase
            ("NoNumbers!!!!!!", False),  # No numbers
            ("NoSpecialChar123", False),  # No special characters
            ("ValidP@ssw0rd!", True),  # Valid
            ("Another$trong1Pass", True),  # Valid
        ]

        env_backup = os.environ.get("INITIAL_ADMIN_PASSWORD")

        try:
            for password, should_succeed in test_cases:
                with app.app_context():
                    # Clean up
                    User.query.filter_by(is_admin=True).delete()
                    db_session.commit()

                    os.environ["INITIAL_ADMIN_PASSWORD"] = password
                    success, message, _ = create_secure_admin()

                    if should_succeed:
                        assert success is True, f"Password '{password}' should be accepted"
                    else:
                        assert success is False, f"Password '{password}' should be rejected"
                        assert "complexity" in message

        finally:
            if env_backup:
                os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup
            else:
                os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

    def test_create_admin_database_error(self, app, db_session):
        """Test handling of database errors during admin creation"""
        from models import User, db

        with app.app_context():
            # Ensure no admin exists
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            env_backup = os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

            try:
                with patch.object(db.session, "commit", side_effect=Exception("Database error")):
                    success, message, password = create_secure_admin()

                assert success is False
                assert "Error creating admin user" in message
                assert "Database error" in message
                assert password is None

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup


class TestValidateAdminSetup:
    """Tests for validate_admin_setup function"""

    def test_no_admin_user(self, app, db_session):
        """Test validation when no admin user exists"""
        from models import User

        with app.app_context():
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            is_secure, issues = validate_admin_setup()

            assert is_secure is False
            assert "No admin user found" in issues

    def test_admin_with_default_password(self, app, db_session, admin_user):
        """Test detection of default password usage"""
        with app.app_context():
            # admin_user fixture uses 'admin123' password
            is_secure, issues = validate_admin_setup()

            assert is_secure is False
            critical_issues = [i for i in issues if "CRITICAL" in i]
            assert any("default password" in i for i in critical_issues)

    def test_admin_with_secure_password(self, app, db_session):
        """Test validation with secure password"""
        from models import User

        with app.app_context():
            # Create admin with secure password
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            admin = User(
                name="Secure Admin",
                employee_number="ADMIN002",
                department="IT",
                is_admin=True,
                is_active=True
            )
            admin.set_password("SecureP@ssword123!")
            db_session.add(admin)
            db_session.commit()

            env_backup = os.environ.get("INITIAL_ADMIN_PASSWORD")
            os.environ["INITIAL_ADMIN_PASSWORD"] = "SomePassword123!"

            try:
                is_secure, issues = validate_admin_setup()

                # Should not have critical issues about default password
                assert not any("default password" in i for i in issues)

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup
                else:
                    os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

    def test_missing_force_password_change_attribute(self, app, db_session):
        """Test warning when force_password_change attribute is missing"""
        from models import User

        with app.app_context():
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            admin = User(
                name="Test Admin",
                employee_number="ADMIN003",
                department="IT",
                is_admin=True,
                is_active=True
            )
            admin.set_password("SecureP@ssword123!")
            db_session.add(admin)
            db_session.commit()

            # Mock hasattr to return False for force_password_change
            original_hasattr = hasattr

            def mock_hasattr(obj, name):
                if name == "force_password_change":
                    return False
                return original_hasattr(obj, name)

            with patch("utils.admin_init.hasattr", side_effect=mock_hasattr):
                is_secure, issues = validate_admin_setup()
                assert any("force_password_change attribute" in i for i in issues)

    def test_force_password_change_not_enabled(self, app, db_session):
        """Test critical issue when force_password_change is False"""
        from models import User

        with app.app_context():
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            admin = User(
                name="Test Admin",
                employee_number="ADMIN004",
                department="IT",
                is_admin=True,
                is_active=True
            )
            admin.set_password("SecureP@ssword123!")

            # Set force_password_change if attribute exists
            if hasattr(admin, "force_password_change"):
                admin.force_password_change = False

            db_session.add(admin)
            db_session.commit()

            is_secure, issues = validate_admin_setup()

            if hasattr(admin, "force_password_change"):
                assert any("not forced to change bootstrap password" in i for i in issues)

    def test_missing_env_variable_warning(self, app, db_session, admin_user):
        """Test warning when INITIAL_ADMIN_PASSWORD env var is not set"""
        with app.app_context():
            env_backup = os.environ.pop("INITIAL_ADMIN_PASSWORD", None)

            try:
                is_secure, issues = validate_admin_setup()
                assert any("INITIAL_ADMIN_PASSWORD environment variable not set" in i for i in issues)

            finally:
                if env_backup:
                    os.environ["INITIAL_ADMIN_PASSWORD"] = env_backup

    def test_validation_with_exception(self, app, db_session):
        """Test handling of exceptions during validation"""
        from models import User

        with app.app_context():
            # Patch at a level that will cause exception
            with patch("utils.admin_init.User") as mock_user:
                mock_user.query.filter_by.side_effect = Exception("Query error")
                is_secure, issues = validate_admin_setup()

                assert is_secure is False
                assert any("Error validating admin setup" in i for i in issues)

    def test_security_classification(self, app, db_session, admin_user):
        """Test that is_secure is based on CRITICAL issues only"""
        with app.app_context():
            # Admin with default password should have CRITICAL issues
            is_secure, issues = validate_admin_setup()

            # Should have CRITICAL issues
            critical_issues = [i for i in issues if i.startswith("CRITICAL")]
            warning_issues = [i for i in issues if i.startswith("WARNING")]

            # is_secure should be False if there are CRITICAL issues
            if critical_issues:
                assert is_secure is False
            else:
                # Warnings alone don't make it insecure
                assert is_secure is True or len(critical_issues) > 0


class TestResetAdminPassword:
    """Tests for reset_admin_password function"""

    def test_reset_password_success(self, app, db_session, admin_user):
        """Test successful password reset"""
        from models import User

        with app.app_context():
            old_password = "admin123"
            assert admin_user.check_password(old_password)

            success, message, new_password = reset_admin_password()

            assert success is True
            assert message == "Admin password reset successfully"
            assert new_password is not None
            assert len(new_password) >= 16

            # Verify old password no longer works - re-query instead of refresh
            updated_admin = User.query.filter_by(is_admin=True).first()
            assert not updated_admin.check_password(old_password)
            assert updated_admin.check_password(new_password)

    def test_reset_sets_force_password_change(self, app, db_session, admin_user):
        """Test that reset sets force_password_change flag"""
        from models import User

        with app.app_context():
            if hasattr(admin_user, "force_password_change"):
                admin_user.force_password_change = False
                db_session.commit()

                success, message, new_password = reset_admin_password()

                assert success is True
                # Re-query instead of refresh
                updated_admin = User.query.filter_by(is_admin=True).first()
                assert updated_admin.force_password_change is True

    def test_reset_no_admin_user(self, app, db_session):
        """Test reset when no admin user exists"""
        from models import User

        with app.app_context():
            User.query.filter_by(is_admin=True).delete()
            db_session.commit()

            success, message, new_password = reset_admin_password()

            assert success is False
            assert message == "No admin user found"
            assert new_password is None

    def test_reset_database_error(self, app, db_session, admin_user):
        """Test handling of database errors during reset"""
        from models import db

        with app.app_context():
            with patch.object(db.session, "commit", side_effect=Exception("Commit failed")):
                success, message, new_password = reset_admin_password()

                assert success is False
                assert "Error resetting admin password" in message
                assert "Commit failed" in message
                assert new_password is None

    def test_reset_generates_unique_passwords(self, app, db_session, admin_user):
        """Test that each reset generates a unique password"""
        with app.app_context():
            passwords = []
            for _ in range(3):
                success, message, new_password = reset_admin_password()
                assert success is True
                passwords.append(new_password)

            # All passwords should be unique
            assert len(set(passwords)) == len(passwords)
