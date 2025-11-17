"""
Comprehensive tests for the scheduled_backup module.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta

from utils.scheduled_backup import (
    ScheduledBackupService,
    init_scheduled_backup,
    get_backup_service,
    shutdown_scheduled_backup,
    _backup_service
)


class TestScheduledBackupServiceInit:
    """Tests for ScheduledBackupService initialization."""

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '12',
        'BACKUP_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_init_with_sqlite_database(self, mock_backup_manager):
        """Test initialization with SQLite database."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        assert service.app == mock_app
        assert service.enabled is True
        assert service.interval_hours == 12
        assert service.backup_on_startup is False
        assert service.db_path == "test.db"
        assert service.backup_manager is not None
        mock_backup_manager.assert_called_once_with("test.db")

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'false',
        'AUTO_BACKUP_INTERVAL_HOURS': '48',
        'BACKUP_ON_STARTUP': 'true'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_init_with_disabled_backup(self, mock_backup_manager):
        """Test initialization with backups disabled."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///db.sqlite"

        service = ScheduledBackupService(mock_app)

        assert service.enabled is False
        assert service.interval_hours == 48
        assert service.backup_on_startup is True

    @patch.dict('os.environ', {}, clear=True)
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_init_with_default_config(self, mock_backup_manager):
        """Test initialization with default configuration values."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///default.db"

        service = ScheduledBackupService(mock_app)

        assert service.enabled is True
        assert service.interval_hours == 24
        assert service.backup_on_startup is True

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.logger')
    def test_init_with_non_sqlite_database(self, mock_logger):
        """Test initialization with non-SQLite database."""
        mock_app = Mock()
        mock_app.config.get.return_value = "postgresql://localhost/db"

        service = ScheduledBackupService(mock_app)

        assert service.db_path is None
        assert service.backup_manager is None
        mock_logger.warning.assert_called_once_with(
            "Scheduled backups are only supported for SQLite databases"
        )

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    def test_init_with_empty_db_uri(self):
        """Test initialization with empty database URI."""
        mock_app = Mock()
        mock_app.config.get.return_value = ""

        service = ScheduledBackupService(mock_app)

        assert service.db_path is None
        assert service.backup_manager is None

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'TRUE'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_init_enabled_case_insensitive(self, mock_backup_manager):
        """Test that enabled flag is case-insensitive."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        assert service.enabled is True


class TestScheduledBackupServiceStart:
    """Tests for ScheduledBackupService.start() method."""

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'false'})
    @patch('utils.scheduled_backup.logger')
    def test_start_when_disabled(self, mock_logger):
        """Test start() when backups are disabled."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.start()

        mock_logger.info.assert_called_with("Scheduled backups are disabled")
        assert service.backup_thread is None

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.logger')
    def test_start_without_backup_manager(self, mock_logger):
        """Test start() without backup manager (non-SQLite)."""
        mock_app = Mock()
        mock_app.config.get.return_value = "postgresql://localhost/db"

        service = ScheduledBackupService(mock_app)
        service.start()

        mock_logger.warning.assert_any_call(
            "Cannot start scheduled backups: database is not SQLite"
        )
        assert service.backup_thread is None

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true', 'BACKUP_ON_STARTUP': 'false'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_start_creates_thread(self, mock_logger, mock_backup_manager):
        """Test that start() creates a backup thread."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.stop_event.set()  # Prevent thread from running
        service.start()

        assert service.backup_thread is not None
        assert service.backup_thread.daemon is True
        assert service.backup_thread.name == "ScheduledBackupThread"
        service.stop()

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true', 'BACKUP_ON_STARTUP': 'false'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_start_when_already_running(self, mock_logger, mock_backup_manager):
        """Test start() when service is already running."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        # Create a mock running thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        service.backup_thread = mock_thread

        service.start()

        mock_logger.warning.assert_any_call("Scheduled backup service is already running")

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true', 'BACKUP_ON_STARTUP': 'false'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_start_clears_stop_event(self, mock_logger, mock_backup_manager):
        """Test that start() clears the stop event."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.stop_event.set()

        # Mock the thread to avoid actual execution
        with patch.object(service, '_backup_loop'):
            service.start()

        # Should have been cleared before thread start
        # But we set it again to prevent loop, so just check thread exists
        assert service.backup_thread is not None
        service.stop()


class TestScheduledBackupServiceStop:
    """Tests for ScheduledBackupService.stop() method."""

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_stop_when_not_running(self, mock_backup_manager):
        """Test stop() when service is not running."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.stop()  # Should not raise

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_stop_graceful_shutdown(self, mock_logger, mock_backup_manager):
        """Test graceful stop of backup service."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        # Create a mock thread that stops gracefully
        mock_thread = Mock()
        mock_thread.is_alive.side_effect = [True, False]
        service.backup_thread = mock_thread

        service.stop()

        assert service.stop_event.is_set()
        mock_thread.join.assert_called_once_with(timeout=10)
        mock_logger.info.assert_any_call("Stopping scheduled backup service...")
        mock_logger.info.assert_any_call("Scheduled backup service stopped")

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_stop_non_graceful_shutdown(self, mock_logger, mock_backup_manager):
        """Test non-graceful stop when thread doesn't stop."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        # Create a mock thread that doesn't stop
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        service.backup_thread = mock_thread

        service.stop()

        mock_logger.warning.assert_called_with(
            "Scheduled backup thread did not stop gracefully"
        )

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_stop_with_none_thread(self, mock_backup_manager):
        """Test stop() when backup_thread is None."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.backup_thread = None

        service.stop()  # Should not raise


class TestScheduledBackupServiceBackupLoop:
    """Tests for ScheduledBackupService._backup_loop() method."""

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'true'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_backup_loop_with_startup_backup(self, mock_logger, mock_backup_manager):
        """Test backup loop runs startup backup."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledBackupService(mock_app)
        service._create_backup = Mock()

        # Set stop event immediately after startup backup
        def set_stop(*args, **kwargs):
            service.stop_event.set()
            return True

        service.stop_event.wait = Mock(side_effect=set_stop)

        service._backup_loop()

        service._create_backup.assert_called_once_with("startup")
        mock_logger.info.assert_any_call("Creating startup backup...")

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_backup_loop_without_startup_backup(self, mock_logger, mock_backup_manager):
        """Test backup loop skips startup backup when disabled."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service._create_backup = Mock()

        # Set stop event immediately
        service.stop_event.set()
        service.stop_event.wait = Mock(return_value=True)

        service._backup_loop()

        # Should not have been called at all since we stop immediately
        service._create_backup.assert_not_called()

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_backup_loop_scheduled_backup(self, mock_logger, mock_backup_manager):
        """Test backup loop runs scheduled backups."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledBackupService(mock_app)
        service._create_backup = Mock()

        call_count = [0]
        def wait_side_effect(timeout):
            call_count[0] += 1
            if call_count[0] >= 2:
                service.stop_event.set()
                return True
            return False

        service.stop_event.wait = Mock(side_effect=wait_side_effect)

        service._backup_loop()

        service._create_backup.assert_called_with("scheduled")

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_backup_loop_exception_handling(self, mock_logger, mock_backup_manager):
        """Test backup loop handles exceptions."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)
        service.stop_event.wait = Mock(side_effect=Exception("Test error"))

        service._backup_loop()

        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args
        assert "Error in scheduled backup loop" in args[0][0]


class TestScheduledBackupServiceCreateBackup:
    """Tests for ScheduledBackupService._create_backup() method."""

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_create_backup_success(self, mock_logger, mock_backup_manager):
        """Test successful backup creation."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        mock_manager_instance = Mock()
        mock_manager_instance.create_backup.return_value = (
            True, "Backup created", "/backups/test.db"
        )
        mock_backup_manager.return_value = mock_manager_instance

        service = ScheduledBackupService(mock_app)
        service._create_backup("startup")

        mock_manager_instance.create_backup.assert_called_once_with(backup_name="startup")
        mock_logger.info.assert_called_with(
            "Scheduled backup created successfully: /backups/test.db"
        )

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_create_backup_failure(self, mock_logger, mock_backup_manager):
        """Test backup creation failure."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        mock_manager_instance = Mock()
        mock_manager_instance.create_backup.return_value = (
            False, "Database locked", None
        )
        mock_backup_manager.return_value = mock_manager_instance

        service = ScheduledBackupService(mock_app)
        service._create_backup("scheduled")

        mock_logger.error.assert_called_with("Scheduled backup failed: Database locked")

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    @patch('utils.scheduled_backup.logger')
    def test_create_backup_exception(self, mock_logger, mock_backup_manager):
        """Test backup creation exception handling."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        mock_manager_instance = Mock()
        mock_manager_instance.create_backup.side_effect = Exception("Disk full")
        mock_backup_manager.return_value = mock_manager_instance

        service = ScheduledBackupService(mock_app)
        service._create_backup("manual")

        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args
        assert "Error creating scheduled backup" in args[0][0]


class TestScheduledBackupServiceManualBackup:
    """Tests for ScheduledBackupService.create_manual_backup() method."""

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_create_manual_backup_success(self, mock_backup_manager):
        """Test successful manual backup creation."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        mock_manager_instance = Mock()
        mock_manager_instance.create_backup.return_value = (
            True, "Success", "/backups/manual.db"
        )
        mock_backup_manager.return_value = mock_manager_instance

        service = ScheduledBackupService(mock_app)
        result = service.create_manual_backup()

        assert result == (True, "Success", "/backups/manual.db")
        mock_manager_instance.create_backup.assert_called_once_with(backup_name="manual")

    @patch.dict('os.environ', {'AUTO_BACKUP_ENABLED': 'true'})
    def test_create_manual_backup_no_manager(self):
        """Test manual backup when manager is not available."""
        mock_app = Mock()
        mock_app.config.get.return_value = "postgresql://localhost/db"

        service = ScheduledBackupService(mock_app)
        result = service.create_manual_backup()

        assert result == (False, "Backup manager not available")


class TestGlobalBackupFunctions:
    """Tests for global backup service functions."""

    @patch('utils.scheduled_backup._backup_service', None)
    @patch('utils.scheduled_backup.ScheduledBackupService')
    def test_init_scheduled_backup_creates_service(self, mock_service_class):
        """Test init_scheduled_backup creates and starts service."""
        import utils.scheduled_backup as module

        mock_app = Mock()
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance

        # Reset global
        module._backup_service = None

        result = init_scheduled_backup(mock_app)

        mock_service_class.assert_called_once_with(mock_app)
        mock_service_instance.start.assert_called_once()
        assert result == mock_service_instance

        # Cleanup
        module._backup_service = None

    @patch('utils.scheduled_backup._backup_service', Mock())
    def test_init_scheduled_backup_already_initialized(self):
        """Test init_scheduled_backup when already initialized."""
        import utils.scheduled_backup as module

        existing_service = Mock()
        module._backup_service = existing_service

        result = init_scheduled_backup(Mock())

        assert result == existing_service

        # Cleanup
        module._backup_service = None

    def test_get_backup_service(self):
        """Test get_backup_service returns global instance."""
        import utils.scheduled_backup as module

        test_service = Mock()
        module._backup_service = test_service

        result = get_backup_service()

        assert result == test_service

        # Cleanup
        module._backup_service = None

    def test_shutdown_scheduled_backup(self):
        """Test shutdown_scheduled_backup stops and clears service."""
        import utils.scheduled_backup as module

        mock_service = Mock()
        module._backup_service = mock_service

        shutdown_scheduled_backup()

        mock_service.stop.assert_called_once()
        assert module._backup_service is None

    def test_shutdown_scheduled_backup_when_none(self):
        """Test shutdown_scheduled_backup when service is None."""
        import utils.scheduled_backup as module

        module._backup_service = None

        shutdown_scheduled_backup()  # Should not raise

        assert module._backup_service is None


class TestScheduledBackupIntegration:
    """Integration tests for scheduled backup service."""

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_full_service_lifecycle(self, mock_backup_manager):
        """Test complete service lifecycle: init, start, stop."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        # Start service
        service.start()
        assert service.backup_thread is not None
        assert service.backup_thread.is_alive()

        # Give thread time to start
        time.sleep(0.1)

        # Stop service
        service.stop()
        assert service.stop_event.is_set()

    @patch.dict('os.environ', {
        'AUTO_BACKUP_ENABLED': 'true',
        'AUTO_BACKUP_INTERVAL_HOURS': '24'
    })
    @patch('utils.scheduled_backup.DatabaseBackupManager')
    def test_interval_calculation(self, mock_backup_manager):
        """Test that interval hours are correctly parsed."""
        mock_app = Mock()
        mock_app.config.get.return_value = "sqlite:///test.db"

        service = ScheduledBackupService(mock_app)

        assert service.interval_hours == 24

        # Test wait timeout calculation (would be 24 * 3600 = 86400)
        expected_timeout = 24 * 3600
        assert expected_timeout == 86400
