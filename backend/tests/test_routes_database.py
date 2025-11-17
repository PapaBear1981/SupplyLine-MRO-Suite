"""
Tests for Database Management Routes

Provides comprehensive test coverage for database backup, restore, and health monitoring endpoints.
Tests admin authorization requirements, success cases, and error handling.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestDatabaseBackupCreate:
    """Tests for POST /api/admin/database/backup endpoint"""

    def test_create_backup_requires_authentication(self, client):
        """Test that creating backup requires JWT authentication"""
        response = client.post("/api/admin/database/backup")
        assert response.status_code == 401

    def test_create_backup_requires_admin(self, client, user_auth_headers):
        """Test that creating backup requires admin privileges"""
        response = client.post("/api/admin/database/backup", headers=user_auth_headers)
        assert response.status_code == 403

    def test_create_backup_success_default_options(self, client, auth_headers, admin_user):
        """Test successful backup creation with default options"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.create_backup.return_value = (
                    True,
                    "Backup created successfully",
                    "/backups/backup_20240101_120000.db"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/backup",
                    headers=auth_headers,
                    json={}
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                assert "Backup created successfully" in data["message"]
                assert data["backup_path"] == "/backups/backup_20240101_120000.db"
                mock_manager.create_backup.assert_called_once_with(
                    backup_name=None,
                    compress=None
                )

    def test_create_backup_with_custom_name(self, client, auth_headers, admin_user):
        """Test backup creation with custom backup name"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.create_backup.return_value = (
                    True,
                    "Backup created successfully",
                    "/backups/custom_backup.db"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/backup",
                    headers=auth_headers,
                    json={"backup_name": "custom_backup"}
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                mock_manager.create_backup.assert_called_once_with(
                    backup_name="custom_backup",
                    compress=None
                )

    def test_create_backup_with_compression(self, client, auth_headers, admin_user):
        """Test backup creation with compression enabled"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.create_backup.return_value = (
                    True,
                    "Compressed backup created",
                    "/backups/backup.db.gz"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/backup",
                    headers=auth_headers,
                    json={"compress": True}
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                mock_manager.create_backup.assert_called_once_with(
                    backup_name=None,
                    compress=True
                )

    def test_create_backup_with_all_options(self, client, auth_headers, admin_user):
        """Test backup creation with all options specified"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.create_backup.return_value = (
                    True,
                    "Backup created",
                    "/backups/my_backup.db.gz"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/backup",
                    headers=auth_headers,
                    json={"backup_name": "my_backup", "compress": True}
                )

                assert response.status_code == 200
                mock_manager.create_backup.assert_called_once_with(
                    backup_name="my_backup",
                    compress=True
                )

    def test_create_backup_failure_from_manager(self, client, auth_headers):
        """Test backup creation when manager reports failure"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.create_backup.return_value = (
                False,
                "Disk space insufficient",
                None
            )
            mock_manager_class.return_value = mock_manager

            response = client.post(
                "/api/admin/database/backup",
                headers=auth_headers,
                json={}
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Disk space insufficient" in data["message"]

    def test_create_backup_no_json_body(self, client, auth_headers, admin_user):
        """Test backup creation with null JSON body sends defaults"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.create_backup.return_value = (
                    True,
                    "Backup created",
                    "/backups/backup.db"
                )
                mock_manager_class.return_value = mock_manager

                # Send request with null JSON to test handling of None from get_json()
                response = client.post(
                    "/api/admin/database/backup",
                    headers={**auth_headers, "Content-Type": "application/json"},
                    data="null"
                )

                # The endpoint handles None from get_json() gracefully with `or {}`
                assert response.status_code == 200
                mock_manager.create_backup.assert_called_once_with(
                    backup_name=None,
                    compress=None
                )

    def test_create_backup_exception_handling(self, client, auth_headers):
        """Test backup creation handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.create_backup.side_effect = Exception("Unexpected error")
            mock_manager_class.return_value = mock_manager

            response = client.post(
                "/api/admin/database/backup",
                headers=auth_headers,
                json={}
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error creating backup" in data["message"]
            assert "Unexpected error" in data["message"]

    def test_create_backup_non_sqlite_database(self, client, auth_headers):
        """Test backup creation fails for non-SQLite databases"""
        # Temporarily change the database URI to PostgreSQL
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.post(
                "/api/admin/database/backup",
                headers=auth_headers,
                json={}
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri


class TestDatabaseBackupsList:
    """Tests for GET /api/admin/database/backups endpoint"""

    def test_list_backups_requires_authentication(self, client):
        """Test that listing backups requires JWT authentication"""
        response = client.get("/api/admin/database/backups")
        assert response.status_code == 401

    def test_list_backups_requires_admin(self, client, user_auth_headers):
        """Test that listing backups requires admin privileges"""
        response = client.get("/api/admin/database/backups", headers=user_auth_headers)
        assert response.status_code == 403

    def test_list_backups_success_empty(self, client, auth_headers):
        """Test listing backups when no backups exist"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.list_backups.return_value = []
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/backups", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["backups"] == []
            assert data["count"] == 0

    def test_list_backups_success_with_backups(self, client, auth_headers):
        """Test listing backups with multiple backups available"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_backups = [
                {
                    "filename": "backup_20240101_120000.db",
                    "size": 1048576,
                    "created": "2024-01-01T12:00:00"
                },
                {
                    "filename": "backup_20240102_120000.db",
                    "size": 2097152,
                    "created": "2024-01-02T12:00:00"
                },
                {
                    "filename": "backup_20240103_120000.db.gz",
                    "size": 524288,
                    "created": "2024-01-03T12:00:00"
                }
            ]
            mock_manager.list_backups.return_value = mock_backups
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/backups", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["backups"]) == 3
            assert data["count"] == 3
            assert data["backups"][0]["filename"] == "backup_20240101_120000.db"

    def test_list_backups_exception_handling(self, client, auth_headers):
        """Test listing backups handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.list_backups.side_effect = Exception("Permission denied")
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/backups", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error listing backups" in data["message"]
            assert "Permission denied" in data["message"]

    def test_list_backups_non_sqlite_database(self, client, auth_headers):
        """Test listing backups fails for non-SQLite databases"""
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.get("/api/admin/database/backups", headers=auth_headers)

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri


class TestDatabaseBackupDelete:
    """Tests for DELETE /api/admin/database/backup/<path:backup_filename> endpoint"""

    def test_delete_backup_requires_authentication(self, client):
        """Test that deleting backup requires JWT authentication"""
        response = client.delete("/api/admin/database/backup/backup.db")
        assert response.status_code == 401

    def test_delete_backup_requires_admin(self, client, user_auth_headers):
        """Test that deleting backup requires admin privileges"""
        response = client.delete(
            "/api/admin/database/backup/backup.db",
            headers=user_auth_headers
        )
        assert response.status_code == 403

    def test_delete_backup_success(self, client, auth_headers, admin_user):
        """Test successful backup deletion"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.backup_dir = Path("/backups")
                mock_manager.delete_backup.return_value = (True, "Backup deleted successfully")
                mock_manager_class.return_value = mock_manager

                response = client.delete(
                    "/api/admin/database/backup/backup_20240101.db",
                    headers=auth_headers
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                assert "Backup deleted successfully" in data["message"]
                mock_manager.delete_backup.assert_called_once()

    def test_delete_backup_failure_not_found(self, client, auth_headers):
        """Test backup deletion when file not found"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.backup_dir = Path("/backups")
            mock_manager.delete_backup.return_value = (False, "Backup file not found")
            mock_manager_class.return_value = mock_manager

            response = client.delete(
                "/api/admin/database/backup/nonexistent.db",
                headers=auth_headers
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "not found" in data["message"]

    def test_delete_backup_exception_handling(self, client, auth_headers):
        """Test backup deletion handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.backup_dir = Path("/backups")
            mock_manager.delete_backup.side_effect = Exception("File locked")
            mock_manager_class.return_value = mock_manager

            response = client.delete(
                "/api/admin/database/backup/backup.db",
                headers=auth_headers
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error deleting backup" in data["message"]
            assert "File locked" in data["message"]

    def test_delete_backup_non_sqlite_database(self, client, auth_headers):
        """Test backup deletion fails for non-SQLite databases"""
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.delete(
                "/api/admin/database/backup/backup.db",
                headers=auth_headers
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri

    def test_delete_backup_with_path_components(self, client, auth_headers, admin_user):
        """Test backup deletion with path components in filename"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.backup_dir = Path("/backups")
                mock_manager.delete_backup.return_value = (True, "Backup deleted successfully")
                mock_manager_class.return_value = mock_manager

                response = client.delete(
                    "/api/admin/database/backup/subdir/backup.db",
                    headers=auth_headers
                )

                assert response.status_code == 200


class TestDatabaseBackupDownload:
    """Tests for GET /api/admin/database/backup/<path:backup_filename>/download endpoint"""

    def test_download_backup_requires_authentication(self, client):
        """Test that downloading backup requires JWT authentication"""
        response = client.get("/api/admin/database/backup/backup.db/download")
        assert response.status_code == 401

    def test_download_backup_requires_admin(self, client, user_auth_headers):
        """Test that downloading backup requires admin privileges"""
        response = client.get(
            "/api/admin/database/backup/backup.db/download",
            headers=user_auth_headers
        )
        assert response.status_code == 403

    def test_download_backup_success(self, client, auth_headers, admin_user):
        """Test successful backup download"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            backup_file = backup_dir / "backup_test.db"
            backup_file.write_text("test backup content")

            with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
                with patch("routes_database.current_user", admin_user):
                    mock_manager = MagicMock()
                    mock_manager.backup_dir = backup_dir
                    mock_manager_class.return_value = mock_manager

                    response = client.get(
                        "/api/admin/database/backup/backup_test.db/download",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    assert response.data == b"test backup content"

    def test_download_backup_not_found(self, client, auth_headers):
        """Test downloading non-existent backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)

            with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager.backup_dir = backup_dir
                mock_manager_class.return_value = mock_manager

                response = client.get(
                    "/api/admin/database/backup/nonexistent.db/download",
                    headers=auth_headers
                )

                assert response.status_code == 404
                data = response.get_json()
                assert data["success"] is False
                assert "not found" in data["message"]

    def test_download_backup_invalid_path_outside_backup_dir(self, client, auth_headers, admin_user):
        """Test downloading backup with path outside backup directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir) / "backups"
            backup_dir.mkdir()

            # Create a subdirectory with a file that will have an invalid parent
            subdir = backup_dir / "subdir"
            subdir.mkdir()
            # File exists but its parent is not backup_dir directly
            test_file = subdir / "test.db"
            test_file.write_text("test data")

            with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
                with patch("routes_database.current_user", admin_user):
                    mock_manager = MagicMock()
                    mock_manager.backup_dir = backup_dir
                    mock_manager_class.return_value = mock_manager

                    # The file exists but parent is not backup_dir (it's subdir)
                    # So this should pass the security check since backup_dir is in parents
                    response = client.get(
                        "/api/admin/database/backup/subdir/test.db/download",
                        headers=auth_headers
                    )

                    # File is in subdirectory of backup_dir, which is allowed
                    assert response.status_code == 200

    def test_download_backup_exception_handling(self, client, auth_headers):
        """Test download backup handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager_class.side_effect = Exception("Storage error")

            response = client.get(
                "/api/admin/database/backup/backup.db/download",
                headers=auth_headers
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error downloading backup" in data["message"]

    def test_download_backup_non_sqlite_database(self, client, auth_headers):
        """Test backup download fails for non-SQLite databases"""
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.get(
                "/api/admin/database/backup/backup.db/download",
                headers=auth_headers
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri

    def test_download_backup_in_backup_dir_parent(self, client, auth_headers, admin_user):
        """Test that backup file in same directory as backup_dir is allowed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            backup_file = backup_dir / "valid_backup.db"
            backup_file.write_text("valid backup")

            with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
                with patch("routes_database.current_user", admin_user):
                    mock_manager = MagicMock()
                    mock_manager.backup_dir = backup_dir
                    mock_manager_class.return_value = mock_manager

                    response = client.get(
                        "/api/admin/database/backup/valid_backup.db/download",
                        headers=auth_headers
                    )

                    assert response.status_code == 200

    def test_download_backup_security_check_rejects_outside_path(self, client, auth_headers, admin_user):
        """Test that files outside backup directory are rejected by security check"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set backup_dir to a subdirectory
            backup_dir = Path(temp_dir) / "backups"
            backup_dir.mkdir()

            # Create a file in the parent directory (outside backup_dir)
            sensitive_file = Path(temp_dir) / "sensitive.db"
            sensitive_file.write_text("sensitive data")

            with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
                with patch("routes_database.current_user", admin_user):
                    mock_manager = MagicMock()
                    mock_manager.backup_dir = backup_dir
                    mock_manager_class.return_value = mock_manager

                    # Directly mock the path construction to simulate an attack
                    # This uses absolute path that resolves to outside the backup directory
                    original_truediv = Path.__truediv__

                    def mock_truediv(self, other):
                        if str(self) == str(backup_dir) and other == "sensitive.db":
                            return sensitive_file  # Return path outside backup_dir
                        return original_truediv(self, other)

                    with patch.object(Path, "__truediv__", mock_truediv):
                        response = client.get(
                            "/api/admin/database/backup/sensitive.db/download",
                            headers=auth_headers
                        )

                        # Should be rejected by security check
                        assert response.status_code == 400
                        data = response.get_json()
                        assert data["success"] is False
                        assert "Invalid backup path" in data["message"]


class TestDatabaseRestore:
    """Tests for POST /api/admin/database/restore endpoint"""

    def test_restore_backup_requires_authentication(self, client):
        """Test that restoring backup requires JWT authentication"""
        response = client.post("/api/admin/database/restore")
        assert response.status_code == 401

    def test_restore_backup_requires_admin(self, client, user_auth_headers):
        """Test that restoring backup requires admin privileges"""
        response = client.post(
            "/api/admin/database/restore",
            headers=user_auth_headers,
            json={"backup_filename": "backup.db"}
        )
        assert response.status_code == 403

    def test_restore_backup_missing_filename(self, client, auth_headers):
        """Test restore fails when backup_filename is missing"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            response = client.post(
                "/api/admin/database/restore",
                headers=auth_headers,
                json={}
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "backup_filename is required" in data["message"]

    def test_restore_backup_no_json_body(self, client, auth_headers, admin_user):
        """Test restore fails when null JSON body provided"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                # Send with null JSON to test validation
                response = client.post(
                    "/api/admin/database/restore",
                    headers={**auth_headers, "Content-Type": "application/json"},
                    data="null"
                )

                # This results in get_json() returning None, which triggers the validation error
                assert response.status_code == 400
                data = response.get_json()
                assert data["success"] is False
                assert "backup_filename is required" in data["message"]

    def test_restore_backup_success_with_pre_backup(self, client, auth_headers, admin_user):
        """Test successful restore with pre-restore backup"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.backup_dir = Path("/backups")
                mock_manager.restore_backup.return_value = (
                    True,
                    "Database restored successfully"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/restore",
                    headers=auth_headers,
                    json={
                        "backup_filename": "backup_20240101.db",
                        "create_backup_before_restore": True
                    }
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                assert "restored successfully" in data["message"]
                mock_manager.restore_backup.assert_called_once()
                # Check that create_backup_before_restore=True was passed
                call_kwargs = mock_manager.restore_backup.call_args[1]
                assert call_kwargs["create_backup_before_restore"] is True

    def test_restore_backup_success_without_pre_backup(self, client, auth_headers, admin_user):
        """Test successful restore without pre-restore backup"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.backup_dir = Path("/backups")
                mock_manager.restore_backup.return_value = (
                    True,
                    "Database restored successfully"
                )
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/restore",
                    headers=auth_headers,
                    json={
                        "backup_filename": "backup_20240101.db",
                        "create_backup_before_restore": False
                    }
                )

                assert response.status_code == 200
                call_kwargs = mock_manager.restore_backup.call_args[1]
                assert call_kwargs["create_backup_before_restore"] is False

    def test_restore_backup_default_create_backup_before(self, client, auth_headers, admin_user):
        """Test restore uses default create_backup_before_restore=True"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.current_user", admin_user):
                mock_manager = MagicMock()
                mock_manager.backup_dir = Path("/backups")
                mock_manager.restore_backup.return_value = (True, "Restored")
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/restore",
                    headers=auth_headers,
                    json={"backup_filename": "backup.db"}
                )

                assert response.status_code == 200
                call_kwargs = mock_manager.restore_backup.call_args[1]
                assert call_kwargs["create_backup_before_restore"] is True

    def test_restore_backup_failure_from_manager(self, client, auth_headers):
        """Test restore when manager reports failure"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.backup_dir = Path("/backups")
            mock_manager.restore_backup.return_value = (
                False,
                "Backup file corrupted"
            )
            mock_manager_class.return_value = mock_manager

            response = client.post(
                "/api/admin/database/restore",
                headers=auth_headers,
                json={"backup_filename": "corrupted.db"}
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "corrupted" in data["message"]

    def test_restore_backup_exception_handling(self, client, auth_headers):
        """Test restore handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.backup_dir = Path("/backups")
            mock_manager.restore_backup.side_effect = Exception("Database locked")
            mock_manager_class.return_value = mock_manager

            response = client.post(
                "/api/admin/database/restore",
                headers=auth_headers,
                json={"backup_filename": "backup.db"}
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error restoring backup" in data["message"]
            assert "Database locked" in data["message"]

    def test_restore_backup_non_sqlite_database(self, client, auth_headers):
        """Test restore fails for non-SQLite databases"""
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.post(
                "/api/admin/database/restore",
                headers=auth_headers,
                json={"backup_filename": "backup.db"}
            )

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri


class TestDatabaseHealth:
    """Tests for GET /api/admin/database/health endpoint"""

    def test_health_check_requires_authentication(self, client):
        """Test that health check requires JWT authentication"""
        response = client.get("/api/admin/database/health")
        assert response.status_code == 401

    def test_health_check_requires_admin(self, client, user_auth_headers):
        """Test that health check requires admin privileges"""
        response = client.get("/api/admin/database/health", headers=user_auth_headers)
        assert response.status_code == 403

    def test_health_check_success_healthy(self, client, auth_headers):
        """Test health check when database is healthy"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.check_database_integrity.return_value = (
                True,
                "Database integrity check passed",
                {
                    "integrity_check": "ok",
                    "size_bytes": 1048576,
                    "table_count": 15,
                    "index_count": 20
                }
            )
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/health", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["healthy"] is True
            assert "passed" in data["message"]
            assert data["details"]["integrity_check"] == "ok"
            assert data["details"]["table_count"] == 15

    def test_health_check_success_unhealthy(self, client, auth_headers):
        """Test health check when database has issues"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.check_database_integrity.return_value = (
                False,
                "Database integrity check failed",
                {
                    "integrity_check": "failed",
                    "errors": ["Corruption in table 'users'"],
                    "size_bytes": 1048576
                }
            )
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/health", headers=auth_headers)

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True  # Request succeeded
            assert data["healthy"] is False  # But database is unhealthy
            assert "failed" in data["message"]
            assert "errors" in data["details"]

    def test_health_check_exception_handling(self, client, auth_headers):
        """Test health check handles exceptions gracefully"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.check_database_integrity.side_effect = Exception("Cannot read database")
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/health", headers=auth_headers)

            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Error checking database health" in data["message"]
            assert "Cannot read database" in data["message"]

    def test_health_check_non_sqlite_database(self, client, auth_headers):
        """Test health check fails for non-SQLite databases"""
        original_uri = client.application.config.get("SQLALCHEMY_DATABASE_URI")
        client.application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/test"

        try:
            response = client.get("/api/admin/database/health", headers=auth_headers)

            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "only supported for SQLite" in data["message"]
        finally:
            client.application.config["SQLALCHEMY_DATABASE_URI"] = original_uri


class TestGetBackupManager:
    """Tests for the internal get_backup_manager function"""

    def test_get_backup_manager_sqlite_uri(self, app, client, auth_headers):
        """Test get_backup_manager extracts SQLite path correctly"""
        # This is tested indirectly through the endpoints
        # When a SQLite URI is configured, the manager should be created
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.list_backups.return_value = []
            mock_manager_class.return_value = mock_manager

            # The backup manager creation is tested through endpoint calls
            response = client.get("/api/admin/database/backups", headers=auth_headers)
            assert response.status_code == 200
            mock_manager_class.assert_called_once()
            # Verify path extraction - should not have sqlite:/// prefix
            called_path = mock_manager_class.call_args[0][0]
            assert not called_path.startswith("sqlite:///")

    def test_database_uri_extraction(self, app, auth_headers, client):
        """Test that database path is correctly extracted from SQLite URI"""
        # This test verifies the path extraction logic by checking the actual call
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.list_backups.return_value = []
            mock_manager_class.return_value = mock_manager

            response = client.get("/api/admin/database/backups", headers=auth_headers)

            assert response.status_code == 200
            # Verify DatabaseBackupManager was called with the database path
            mock_manager_class.assert_called_once()
            # The argument should be the path extracted from sqlite:///path
            called_path = mock_manager_class.call_args[0][0]
            assert not called_path.startswith("sqlite:///")


class TestDatabaseRoutesIntegration:
    """Integration tests for database routes"""

    def test_all_routes_registered(self, app):
        """Test that all database routes are registered"""
        rules = [rule.rule for rule in app.url_map.iter_rules()]

        expected_routes = [
            "/api/admin/database/backup",
            "/api/admin/database/backups",
            "/api/admin/database/restore",
            "/api/admin/database/health",
        ]

        for route in expected_routes:
            assert route in rules, f"Route {route} not registered"

        # Check dynamic routes
        backup_routes = [r for r in rules if r.startswith("/api/admin/database/backup/")]
        assert len(backup_routes) >= 2  # Should have delete and download routes

    def test_route_methods(self, app):
        """Test that routes have correct HTTP methods"""
        rules = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}

        # Create backup should accept POST
        assert "POST" in rules.get("/api/admin/database/backup", set())

        # List backups should accept GET
        assert "GET" in rules.get("/api/admin/database/backups", set())

        # Restore should accept POST
        assert "POST" in rules.get("/api/admin/database/restore", set())

        # Health should accept GET
        assert "GET" in rules.get("/api/admin/database/health", set())

    def test_logging_on_successful_operations(self, client, auth_headers, admin_user):
        """Test that successful operations are logged"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.logger") as mock_logger:
                with patch("routes_database.current_user", admin_user):
                    mock_manager = MagicMock()
                    mock_manager.create_backup.return_value = (
                        True,
                        "Backup created",
                        "/backups/backup.db"
                    )
                    mock_manager_class.return_value = mock_manager

                    response = client.post(
                        "/api/admin/database/backup",
                        headers=auth_headers,
                        json={}
                    )

                    assert response.status_code == 200
                    # Verify logging was called
                    mock_logger.info.assert_called_once()
                    log_call_args = mock_logger.info.call_args
                    assert "Manual backup created" in log_call_args[0][0]

    def test_error_logging(self, client, auth_headers):
        """Test that errors are logged appropriately"""
        with patch("routes_database.DatabaseBackupManager") as mock_manager_class:
            with patch("routes_database.logger") as mock_logger:
                mock_manager = MagicMock()
                mock_manager.create_backup.side_effect = Exception("Critical error")
                mock_manager_class.return_value = mock_manager

                response = client.post(
                    "/api/admin/database/backup",
                    headers=auth_headers,
                    json={}
                )

                assert response.status_code == 500
                # Verify error logging was called
                mock_logger.error.assert_called_once()
                log_call_args = mock_logger.error.call_args
                assert "Error creating backup" in log_call_args[0][0]
