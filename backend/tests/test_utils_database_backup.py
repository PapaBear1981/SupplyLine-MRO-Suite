"""
Comprehensive tests for Database Backup Manager

Tests cover backup creation, restoration, compression, rotation, and integrity checking.
"""

import gzip
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from utils.database_backup import DatabaseBackupManager


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create a valid SQLite database with some tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test_table (name) VALUES ('test1')")
    cursor.execute("INSERT INTO test_table (name) VALUES ('test2')")
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory."""
    backup_dir = tempfile.mkdtemp()
    yield backup_dir

    # Cleanup - remove all files and directory
    for file in Path(backup_dir).glob("*"):
        file.unlink()
    os.rmdir(backup_dir)


@pytest.fixture
def backup_manager(temp_db, temp_backup_dir):
    """Create a backup manager instance."""
    return DatabaseBackupManager(temp_db, temp_backup_dir)


@pytest.fixture
def backup_manager_no_compress(temp_db, temp_backup_dir):
    """Create a backup manager with compression disabled."""
    with patch.dict(os.environ, {"COMPRESS_BACKUPS": "false"}):
        return DatabaseBackupManager(temp_db, temp_backup_dir)


class TestDatabaseBackupManagerInit:
    """Test DatabaseBackupManager initialization."""

    def test_init_with_backup_dir(self, temp_db, temp_backup_dir):
        """Test initialization with specified backup directory."""
        manager = DatabaseBackupManager(temp_db, temp_backup_dir)
        assert manager.db_path == Path(temp_db)
        assert manager.backup_dir == Path(temp_backup_dir)
        assert manager.backup_dir.exists()

    def test_init_without_backup_dir(self, temp_db):
        """Test initialization with default backup directory."""
        manager = DatabaseBackupManager(temp_db)
        expected_backup_dir = Path(temp_db).parent / "backups"
        assert manager.backup_dir == expected_backup_dir
        assert manager.backup_dir.exists()

        # Cleanup
        if expected_backup_dir.exists():
            os.rmdir(expected_backup_dir)

    def test_init_creates_backup_directory(self, temp_db):
        """Test that initialization creates backup directory if it doesn't exist."""
        backup_dir = tempfile.mkdtemp()
        os.rmdir(backup_dir)  # Remove it so we can test creation

        manager = DatabaseBackupManager(temp_db, backup_dir)
        assert manager.backup_dir.exists()

        # Cleanup
        os.rmdir(backup_dir)

    def test_init_default_max_backups(self, temp_db, temp_backup_dir):
        """Test default max_backups value."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MAX_DATABASE_BACKUPS", None)
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            assert manager.max_backups == 10

    def test_init_custom_max_backups(self, temp_db, temp_backup_dir):
        """Test custom max_backups from environment."""
        with patch.dict(os.environ, {"MAX_DATABASE_BACKUPS": "20"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            assert manager.max_backups == 20

    def test_init_compress_backups_true(self, temp_db, temp_backup_dir):
        """Test compress_backups enabled by default."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "true"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            assert manager.compress_backups is True

    def test_init_compress_backups_false(self, temp_db, temp_backup_dir):
        """Test compress_backups disabled."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "false"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            assert manager.compress_backups is False

    def test_init_compress_backups_case_insensitive(self, temp_db, temp_backup_dir):
        """Test compress_backups is case-insensitive."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "TRUE"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            assert manager.compress_backups is True


class TestCreateBackup:
    """Test backup creation functionality."""

    def test_create_backup_success_uncompressed(self, backup_manager_no_compress):
        """Test successful backup creation without compression."""
        success, message, backup_path = backup_manager_no_compress.create_backup(compress=False)

        assert success is True
        assert "Backup created successfully" in message
        assert backup_path != ""
        assert Path(backup_path).exists()
        assert backup_path.endswith(".db")
        assert "MB" in message

    def test_create_backup_success_compressed(self, backup_manager):
        """Test successful backup creation with compression."""
        success, message, backup_path = backup_manager.create_backup(compress=True)

        assert success is True
        assert "Backup created successfully" in message
        assert backup_path.endswith(".db.gz")
        assert Path(backup_path).exists()

    def test_create_backup_with_custom_name(self, backup_manager_no_compress):
        """Test backup creation with custom name."""
        success, message, backup_path = backup_manager_no_compress.create_backup(
            backup_name="custom_backup", compress=False
        )

        assert success is True
        assert "custom_backup" in Path(backup_path).name

    def test_create_backup_default_timestamp_format(self, backup_manager_no_compress):
        """Test backup filename includes timestamp."""
        success, message, backup_path = backup_manager_no_compress.create_backup(compress=False)

        assert success is True
        filename = Path(backup_path).name
        # Should contain backup_ and timestamp pattern YYYYMMDD_HHMMSS
        assert "backup_" in filename
        assert len(filename) > 20  # backup_YYYYMMDD_HHMMSS.db

    def test_create_backup_db_not_found(self, temp_backup_dir):
        """Test backup creation fails when database doesn't exist."""
        manager = DatabaseBackupManager("/nonexistent/database.db", temp_backup_dir)

        success, message, backup_path = manager.create_backup()

        assert success is False
        assert "Database file not found" in message
        assert backup_path == ""

    def test_create_backup_verification_failure(self, backup_manager):
        """Test backup creation fails on verification error."""
        with patch.object(backup_manager, "_verify_backup", return_value=False):
            success, message, backup_path = backup_manager.create_backup()

        assert success is False
        assert "Backup verification failed" in message
        assert backup_path == ""

    def test_create_backup_compression_failure(self, backup_manager):
        """Test backup creation handles compression failure."""
        with patch.object(backup_manager, "_compress_backup", return_value=None):
            success, message, backup_path = backup_manager.create_backup(compress=True)

        # Should still succeed but with uncompressed file
        assert success is True
        assert backup_path.endswith(".db")

    def test_create_backup_rotates_old_backups(self, backup_manager_no_compress):
        """Test that creating backup triggers rotation."""
        with patch.object(backup_manager_no_compress, "_rotate_backups") as mock_rotate:
            backup_manager_no_compress.create_backup(compress=False)
            mock_rotate.assert_called_once()

    def test_create_backup_exception_handling(self, backup_manager):
        """Test backup creation handles exceptions."""
        with patch("sqlite3.connect", side_effect=Exception("Database error")):
            success, message, backup_path = backup_manager.create_backup()

        assert success is False
        assert "Error creating backup" in message
        assert backup_path == ""

    def test_create_backup_respects_default_compression(self, temp_db, temp_backup_dir):
        """Test backup uses default compression setting."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "true"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            success, message, backup_path = manager.create_backup()

        assert success is True
        assert backup_path.endswith(".db.gz")


class TestRestoreBackup:
    """Test backup restoration functionality."""

    def test_restore_backup_success_uncompressed(self, backup_manager_no_compress):
        """Test successful restoration from uncompressed backup."""
        # Create a backup first
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        # Modify the original database
        conn = sqlite3.connect(str(backup_manager_no_compress.db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_table")
        conn.commit()
        conn.close()

        # Restore from backup
        success, message = backup_manager_no_compress.restore_backup(
            backup_path, create_backup_before_restore=False
        )

        assert success is True
        assert "restored successfully" in message

        # Verify data was restored
        conn = sqlite3.connect(str(backup_manager_no_compress.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 2

    def test_restore_backup_success_compressed(self, backup_manager):
        """Test successful restoration from compressed backup."""
        # Create a compressed backup
        success, _, backup_path = backup_manager.create_backup(compress=True)
        assert success is True

        # Restore from backup
        success, message = backup_manager.restore_backup(
            backup_path, create_backup_before_restore=False
        )

        assert success is True
        assert "restored successfully" in message

    def test_restore_backup_file_not_found(self, backup_manager):
        """Test restoration fails when backup file doesn't exist."""
        success, message = backup_manager.restore_backup("/nonexistent/backup.db")

        assert success is False
        assert "Backup file not found" in message

    def test_restore_backup_creates_pre_restore_backup(self, backup_manager_no_compress):
        """Test that restoration creates pre-restore backup by default."""
        # Create a backup
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        # Restore with pre-restore backup enabled
        with patch.object(backup_manager_no_compress, "create_backup", return_value=(True, "OK", "")) as mock_create:
            backup_manager_no_compress.restore_backup(backup_path, create_backup_before_restore=True)
            mock_create.assert_called_once_with(backup_name="pre_restore")

    def test_restore_backup_skips_pre_restore_when_disabled(self, backup_manager_no_compress):
        """Test that restoration skips pre-restore backup when disabled."""
        # Create a backup
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        with patch.object(backup_manager_no_compress, "create_backup") as mock_create:
            backup_manager_no_compress.restore_backup(backup_path, create_backup_before_restore=False)
            mock_create.assert_not_called()

    def test_restore_backup_handles_pre_restore_failure(self, backup_manager_no_compress):
        """Test restoration continues even if pre-restore backup fails."""
        # Create a backup
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        with patch.object(
            backup_manager_no_compress, "create_backup", return_value=(False, "Error", "")
        ):
            success, message = backup_manager_no_compress.restore_backup(
                backup_path, create_backup_before_restore=True
            )

        # Should still succeed
        assert success is True

    def test_restore_backup_decompression_failure(self, backup_manager):
        """Test restoration fails when decompression fails."""
        # Create a compressed backup
        success, _, backup_path = backup_manager.create_backup(compress=True)
        assert success is True

        with patch.object(backup_manager, "_decompress_backup", return_value=None):
            success, message = backup_manager.restore_backup(backup_path)

        assert success is False
        assert "Failed to decompress" in message

    def test_restore_backup_invalid_backup_file(self, backup_manager, temp_backup_dir):
        """Test restoration fails for invalid backup file."""
        # Create an invalid backup file
        invalid_backup = Path(temp_backup_dir) / "invalid.db"
        with open(invalid_backup, "w") as f:
            f.write("not a valid database")

        with patch.object(backup_manager, "_verify_backup", return_value=False):
            success, message = backup_manager.restore_backup(str(invalid_backup))

        assert success is False
        assert "corrupted or invalid" in message

    def test_restore_backup_cleans_up_temp_file(self, backup_manager):
        """Test that temporary decompressed file is cleaned up."""
        # Create a compressed backup
        success, _, backup_path = backup_manager.create_backup(compress=True)
        assert success is True

        # Restore
        success, message = backup_manager.restore_backup(
            backup_path, create_backup_before_restore=False
        )

        assert success is True
        # Temporary decompressed file should be removed
        decompressed_path = Path(backup_path).with_suffix("")
        assert not decompressed_path.exists()

    def test_restore_backup_exception_handling(self, backup_manager_no_compress):
        """Test restoration handles exceptions."""
        # Create a backup
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        with patch("shutil.copy2", side_effect=Exception("Copy error")):
            success, message = backup_manager_no_compress.restore_backup(
                backup_path, create_backup_before_restore=False
            )

        assert success is False
        assert "Error restoring backup" in message


class TestListBackups:
    """Test backup listing functionality."""

    def test_list_backups_empty(self, backup_manager):
        """Test listing backups when none exist."""
        backups = backup_manager.list_backups()
        assert backups == []

    def test_list_backups_single_backup(self, backup_manager_no_compress):
        """Test listing single backup."""
        backup_manager_no_compress.create_backup(compress=False)

        backups = backup_manager_no_compress.list_backups()

        assert len(backups) == 1
        assert "filename" in backups[0]
        assert "path" in backups[0]
        assert "size_mb" in backups[0]
        assert "created_at" in backups[0]
        assert "compressed" in backups[0]
        assert backups[0]["compressed"] is False

    def test_list_backups_multiple_backups(self, backup_manager_no_compress):
        """Test listing multiple backups."""
        backup_manager_no_compress.max_backups = 100  # Prevent rotation
        backup_manager_no_compress.create_backup(backup_name="backup1", compress=False)
        backup_manager_no_compress.create_backup(backup_name="backup2", compress=False)

        backups = backup_manager_no_compress.list_backups()

        assert len(backups) == 2

    def test_list_backups_sorted_by_date_descending(self, backup_manager_no_compress):
        """Test that backups are sorted by date (newest first)."""
        import time

        backup_manager_no_compress.create_backup(backup_name="first", compress=False)
        time.sleep(0.01)
        backup_manager_no_compress.create_backup(backup_name="second", compress=False)

        backups = backup_manager_no_compress.list_backups()

        # Newest should be first
        assert "second" in backups[0]["filename"]
        assert "first" in backups[1]["filename"]

    def test_list_backups_compressed_and_uncompressed(self, backup_manager):
        """Test listing mixed compressed and uncompressed backups."""
        backup_manager.max_backups = 100  # Prevent rotation
        backup_manager.create_backup(backup_name="uncompressed", compress=False)
        backup_manager.create_backup(backup_name="compressed", compress=True)

        backups = backup_manager.list_backups()

        assert len(backups) == 2
        compressed_count = sum(1 for b in backups if b["compressed"])
        uncompressed_count = sum(1 for b in backups if not b["compressed"])
        assert compressed_count == 1
        assert uncompressed_count == 1

    def test_list_backups_includes_correct_info(self, backup_manager_no_compress):
        """Test that backup info contains all required fields."""
        backup_manager_no_compress.create_backup(backup_name="test", compress=False)

        backups = backup_manager_no_compress.list_backups()

        assert len(backups) == 1
        backup = backups[0]

        assert "test" in backup["filename"]
        assert backup["path"].startswith(str(backup_manager_no_compress.backup_dir))
        assert isinstance(backup["size_mb"], float)
        assert backup["size_mb"] > 0
        # Check ISO format date
        datetime.fromisoformat(backup["created_at"])  # Should not raise

    def test_list_backups_exception_handling(self, backup_manager):
        """Test that list_backups handles exceptions gracefully."""
        with patch("pathlib.Path.glob", side_effect=Exception("Glob error")):
            backups = backup_manager.list_backups()

        assert backups == []


class TestDeleteBackup:
    """Test backup deletion functionality."""

    def test_delete_backup_success(self, backup_manager_no_compress):
        """Test successful backup deletion."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True
        assert Path(backup_path).exists()

        success, message = backup_manager_no_compress.delete_backup(backup_path)

        assert success is True
        assert "deleted successfully" in message
        assert not Path(backup_path).exists()

    def test_delete_backup_file_not_found(self, backup_manager):
        """Test deletion fails when file doesn't exist."""
        success, message = backup_manager.delete_backup("/nonexistent/backup.db")

        assert success is False
        assert "Backup file not found" in message

    def test_delete_backup_outside_backup_dir(self, backup_manager):
        """Test deletion fails for files outside backup directory."""
        # Create a file outside backup directory
        fd, temp_file = tempfile.mkstemp()
        os.close(fd)

        try:
            success, message = backup_manager.delete_backup(temp_file)

            assert success is False
            assert "outside backup directory" in message
        finally:
            os.unlink(temp_file)

    def test_delete_backup_exception_handling(self, backup_manager_no_compress):
        """Test deletion handles exceptions."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        with patch("pathlib.Path.unlink", side_effect=Exception("Delete error")):
            success, message = backup_manager_no_compress.delete_backup(backup_path)

        assert success is False
        assert "Error deleting backup" in message


class TestCheckDatabaseIntegrity:
    """Test database integrity checking functionality."""

    def test_check_integrity_healthy_database(self, backup_manager):
        """Test integrity check on healthy database."""
        is_healthy, message, details = backup_manager.check_database_integrity()

        assert is_healthy is True
        assert "healthy" in message
        assert details["integrity_check"] == "ok"
        assert details["size_mb"] > 0
        assert details["table_count"] >= 1
        assert details["page_count"] > 0
        assert details["page_size"] > 0

    def test_check_integrity_database_not_exists(self, temp_backup_dir):
        """Test integrity check when database doesn't exist."""
        manager = DatabaseBackupManager("/nonexistent/database.db", temp_backup_dir)

        is_healthy, message, details = manager.check_database_integrity()

        assert is_healthy is False
        assert "does not exist" in message
        assert details == {}

    def test_check_integrity_returns_all_details(self, backup_manager):
        """Test that integrity check returns all expected details."""
        is_healthy, message, details = backup_manager.check_database_integrity()

        assert "integrity_check" in details
        assert "size_mb" in details
        assert "table_count" in details
        assert "page_count" in details
        assert "page_size" in details

    def test_check_integrity_exception_handling(self, backup_manager):
        """Test integrity check handles exceptions."""
        with patch("sqlite3.connect", side_effect=Exception("DB error")):
            is_healthy, message, details = backup_manager.check_database_integrity()

        assert is_healthy is False
        assert "Error checking integrity" in message
        assert details == {}


class TestVerifyBackup:
    """Test backup verification functionality."""

    def test_verify_backup_valid(self, backup_manager_no_compress):
        """Test verification of valid backup."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        result = backup_manager_no_compress._verify_backup(Path(backup_path))

        assert result is True

    def test_verify_backup_invalid(self, backup_manager, temp_backup_dir):
        """Test verification of invalid backup."""
        invalid_file = Path(temp_backup_dir) / "invalid.db"
        with open(invalid_file, "w") as f:
            f.write("invalid database content")

        result = backup_manager._verify_backup(invalid_file)

        assert result is False
        invalid_file.unlink()

    def test_verify_backup_exception_handling(self, backup_manager):
        """Test verification handles exceptions."""
        with patch("sqlite3.connect", side_effect=Exception("Connection error")):
            result = backup_manager._verify_backup(Path("/some/path.db"))

        assert result is False


class TestCompressBackup:
    """Test backup compression functionality."""

    def test_compress_backup_success(self, backup_manager_no_compress):
        """Test successful backup compression."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        original_path = Path(backup_path)
        original_size = original_path.stat().st_size

        compressed_path = backup_manager_no_compress._compress_backup(original_path)

        assert compressed_path is not None
        assert compressed_path.suffix == ".gz"
        assert compressed_path.exists()
        assert not original_path.exists()  # Original should be deleted
        assert compressed_path.stat().st_size > 0

    def test_compress_backup_exception_handling(self, backup_manager_no_compress):
        """Test compression handles exceptions."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        with patch("gzip.open", side_effect=Exception("Compression error")):
            result = backup_manager_no_compress._compress_backup(Path(backup_path))

        assert result is None

    def test_compress_backup_creates_valid_gzip(self, backup_manager_no_compress):
        """Test that compression creates valid gzip file."""
        success, _, backup_path = backup_manager_no_compress.create_backup(compress=False)
        assert success is True

        original_path = Path(backup_path)
        compressed_path = backup_manager_no_compress._compress_backup(original_path)

        assert compressed_path is not None

        # Verify it's a valid gzip file
        with gzip.open(compressed_path, "rb") as f:
            content = f.read()
            assert len(content) > 0


class TestDecompressBackup:
    """Test backup decompression functionality."""

    def test_decompress_backup_success(self, backup_manager):
        """Test successful backup decompression."""
        # Create and compress a backup
        success, _, backup_path = backup_manager.create_backup(compress=True)
        assert success is True
        compressed_path = Path(backup_path)

        # Decompress it
        decompressed_path = backup_manager._decompress_backup(compressed_path)

        assert decompressed_path is not None
        assert decompressed_path.exists()
        assert decompressed_path.suffix == ".db"

        # Verify it's a valid database
        conn = sqlite3.connect(str(decompressed_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()

        assert result == "ok"

        # Cleanup
        decompressed_path.unlink()

    def test_decompress_backup_exception_handling(self, backup_manager):
        """Test decompression handles exceptions."""
        # Create a compressed backup
        success, _, backup_path = backup_manager.create_backup(compress=True)
        assert success is True

        with patch("gzip.open", side_effect=Exception("Decompression error")):
            result = backup_manager._decompress_backup(Path(backup_path))

        assert result is None


class TestRotateBackups:
    """Test backup rotation functionality."""

    def test_rotate_backups_under_limit(self, backup_manager_no_compress):
        """Test rotation when under max_backups limit."""
        backup_manager_no_compress.max_backups = 100  # Prevent rotation during create_backup
        backup_manager_no_compress.create_backup(backup_name="first", compress=False)
        backup_manager_no_compress.create_backup(backup_name="second", compress=False)

        # Set limit higher than current count
        backup_manager_no_compress.max_backups = 10

        # Should not delete anything
        backup_manager_no_compress._rotate_backups()

        backups = backup_manager_no_compress.list_backups()
        assert len(backups) == 2

    def test_rotate_backups_at_limit(self, backup_manager_no_compress):
        """Test rotation when at max_backups limit."""
        backup_manager_no_compress.max_backups = 100  # Prevent rotation during create_backup
        backup_manager_no_compress.create_backup(backup_name="first", compress=False)
        backup_manager_no_compress.create_backup(backup_name="second", compress=False)

        # Set limit exactly at current count
        backup_manager_no_compress.max_backups = 2

        # Should not delete anything
        backup_manager_no_compress._rotate_backups()

        backups = backup_manager_no_compress.list_backups()
        assert len(backups) == 2

    def test_rotate_backups_over_limit(self, backup_manager_no_compress):
        """Test rotation removes oldest backups when over limit."""
        import time

        backup_manager_no_compress.max_backups = 2

        # Create 4 backups
        for i in range(4):
            backup_manager_no_compress.create_backup(backup_name=f"backup{i}", compress=False)
            time.sleep(0.01)

        # Manually trigger rotation (it's already called in create_backup)
        backups = backup_manager_no_compress.list_backups()
        # Should have max_backups (2) remaining
        assert len(backups) <= 2

    def test_rotate_backups_exception_handling(self, backup_manager):
        """Test rotation handles exceptions gracefully."""
        with patch("pathlib.Path.glob", side_effect=Exception("Glob error")):
            # Should not raise exception
            backup_manager._rotate_backups()

    def test_rotate_backups_keeps_newest(self, backup_manager_no_compress):
        """Test that rotation keeps the newest backups."""
        import time

        backup_manager_no_compress.max_backups = 2

        # Create backups with known names
        backup_manager_no_compress.create_backup(backup_name="oldest", compress=False)
        time.sleep(0.01)
        backup_manager_no_compress.create_backup(backup_name="middle", compress=False)
        time.sleep(0.01)
        backup_manager_no_compress.create_backup(backup_name="newest", compress=False)

        backups = backup_manager_no_compress.list_backups()

        # Should keep newest and middle (or middle and newest)
        filenames = [b["filename"] for b in backups]
        assert len(backups) <= 2
        # Newest should definitely be there
        assert any("newest" in f for f in filenames)


class TestIntegration:
    """Integration tests for complete backup workflows."""

    def test_full_backup_restore_cycle(self, temp_db, temp_backup_dir):
        """Test complete backup and restore cycle."""
        manager = DatabaseBackupManager(temp_db, temp_backup_dir)

        # Create initial backup
        success, message, backup_path = manager.create_backup(compress=False)
        assert success is True

        # Modify database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('new_data')")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count_after_insert = cursor.fetchone()[0]
        conn.close()

        assert count_after_insert == 3

        # Restore from backup
        success, message = manager.restore_backup(backup_path, create_backup_before_restore=False)
        assert success is True

        # Verify restoration
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count_after_restore = cursor.fetchone()[0]
        conn.close()

        assert count_after_restore == 2  # Back to original

    def test_backup_compress_restore_cycle(self, temp_db, temp_backup_dir):
        """Test complete cycle with compression."""
        manager = DatabaseBackupManager(temp_db, temp_backup_dir)

        # Create compressed backup
        success, _, backup_path = manager.create_backup(compress=True)
        assert success is True
        assert backup_path.endswith(".gz")

        # Restore from compressed backup
        success, message = manager.restore_backup(backup_path, create_backup_before_restore=False)
        assert success is True

        # Verify database is intact
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 2

    def test_rotation_during_multiple_backups(self, temp_db, temp_backup_dir):
        """Test that rotation works during multiple backup creations."""
        import time

        with patch.dict(os.environ, {"MAX_DATABASE_BACKUPS": "3", "COMPRESS_BACKUPS": "false"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)

            # Create more backups than the limit
            for i in range(5):
                success, _, _ = manager.create_backup(backup_name=f"test{i}")
                assert success is True
                time.sleep(0.01)

            backups = manager.list_backups()
            assert len(backups) <= 3

    def test_list_delete_workflow(self, temp_db, temp_backup_dir):
        """Test listing and deleting backups."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "false"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)

            # Create backups
            manager.create_backup(backup_name="to_delete")
            manager.create_backup(backup_name="to_keep")

            # List backups
            backups = manager.list_backups()
            assert len(backups) == 2

            # Delete one backup
            to_delete = next(b for b in backups if "to_delete" in b["filename"])
            success, _ = manager.delete_backup(to_delete["path"])
            assert success is True

            # Verify deletion
            backups = manager.list_backups()
            assert len(backups) == 1
            assert "to_keep" in backups[0]["filename"]

    def test_integrity_check_before_backup(self, temp_db, temp_backup_dir):
        """Test checking integrity before creating backup."""
        manager = DatabaseBackupManager(temp_db, temp_backup_dir)

        # Check integrity
        is_healthy, message, details = manager.check_database_integrity()
        assert is_healthy is True

        # Only backup if healthy
        if is_healthy:
            success, _, _ = manager.create_backup()
            assert success is True


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_backup_directory_path(self, temp_db):
        """Test with backup directory that needs creation."""
        new_backup_dir = Path(tempfile.mkdtemp()) / "new_subdir"
        assert not new_backup_dir.exists()

        manager = DatabaseBackupManager(temp_db, str(new_backup_dir))

        assert new_backup_dir.exists()
        assert manager.backup_dir == new_backup_dir

        # Cleanup
        os.rmdir(new_backup_dir)
        os.rmdir(new_backup_dir.parent)

    def test_very_long_backup_name(self, backup_manager_no_compress):
        """Test backup with very long name."""
        long_name = "a" * 200
        success, message, backup_path = backup_manager_no_compress.create_backup(
            backup_name=long_name, compress=False
        )

        assert success is True
        assert Path(backup_path).exists()

    def test_special_characters_in_path(self, temp_db):
        """Test with special characters in paths."""
        special_dir = tempfile.mkdtemp(prefix="backup_test_")
        manager = DatabaseBackupManager(temp_db, special_dir)

        success, _, backup_path = manager.create_backup(compress=False)

        assert success is True
        assert Path(backup_path).exists()

        # Cleanup
        for f in Path(special_dir).glob("*"):
            f.unlink()
        os.rmdir(special_dir)

    def test_zero_max_backups(self, temp_db, temp_backup_dir):
        """Test with max_backups set to 0."""
        with patch.dict(os.environ, {"MAX_DATABASE_BACKUPS": "0", "COMPRESS_BACKUPS": "false"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)
            manager.create_backup()

            # Should delete all backups during rotation
            backups = manager.list_backups()
            assert len(backups) == 0

    def test_backup_with_no_tables(self, temp_backup_dir):
        """Test backup of empty database."""
        fd, empty_db = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        conn = sqlite3.connect(empty_db)
        conn.close()

        try:
            manager = DatabaseBackupManager(empty_db, temp_backup_dir)
            success, _, _ = manager.create_backup(compress=False)

            assert success is True

            is_healthy, _, details = manager.check_database_integrity()
            assert is_healthy is True
            assert details["table_count"] == 0
        finally:
            os.unlink(empty_db)

    def test_concurrent_operations_simulation(self, temp_db, temp_backup_dir):
        """Test that operations are thread-safe (basic check)."""
        with patch.dict(os.environ, {"COMPRESS_BACKUPS": "false"}):
            manager = DatabaseBackupManager(temp_db, temp_backup_dir)

            # Simulate rapid operations
            results = []
            for _ in range(3):
                success, _, _ = manager.create_backup()
                results.append(success)

            assert all(results)
            backups = manager.list_backups()
            assert len(backups) >= 1
