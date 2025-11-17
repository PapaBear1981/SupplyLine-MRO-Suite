"""
Comprehensive tests for the scheduled_maintenance module.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call

from utils.scheduled_maintenance import (
    ScheduledMaintenanceService,
    init_scheduled_maintenance,
    shutdown_scheduled_maintenance,
    get_maintenance_service
)


class TestScheduledMaintenanceServiceInit:
    """Tests for ScheduledMaintenanceService initialization."""

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '2',
        'MAINTENANCE_ON_STARTUP': 'false'
    })
    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.app == mock_app
        assert service.enabled is True
        assert service.interval_hours == 2
        assert service.run_on_startup is False
        assert service.maintenance_thread is None
        assert isinstance(service.stop_event, threading.Event)

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'false',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '6',
        'MAINTENANCE_ON_STARTUP': 'true'
    })
    def test_init_with_disabled_maintenance(self):
        """Test initialization with maintenance disabled."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.enabled is False
        assert service.interval_hours == 6
        assert service.run_on_startup is True

    @patch.dict('os.environ', {}, clear=True)
    def test_init_with_default_values(self):
        """Test initialization with default configuration values."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.enabled is True
        assert service.interval_hours == 1
        assert service.run_on_startup is True

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'TRUE',
        'MAINTENANCE_ON_STARTUP': 'FALSE'
    })
    def test_init_case_insensitive_booleans(self):
        """Test that boolean config values are case-insensitive."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.enabled is True
        assert service.run_on_startup is False

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_INTERVAL_HOURS': '12'})
    def test_init_interval_parsing(self):
        """Test that interval hours are correctly parsed as integers."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.interval_hours == 12
        assert isinstance(service.interval_hours, int)


class TestScheduledMaintenanceServiceStart:
    """Tests for ScheduledMaintenanceService.start() method."""

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'false'})
    @patch('utils.scheduled_maintenance.logger')
    def test_start_when_disabled(self, mock_logger):
        """Test start() when maintenance is disabled."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.start()

        mock_logger.info.assert_called_with("Scheduled maintenance is disabled")
        assert service.maintenance_thread is None

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_start_when_already_running(self, mock_logger):
        """Test start() when service is already running."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        # Create a mock running thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        service.maintenance_thread = mock_thread

        service.start()

        mock_logger.warning.assert_called_with(
            "Scheduled maintenance service is already running"
        )

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '3'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_start_creates_thread(self, mock_logger):
        """Test that start() creates and starts a maintenance thread."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.stop_event.set()  # Prevent thread from running
        service.start()

        assert service.maintenance_thread is not None
        assert service.maintenance_thread.daemon is True
        assert service.maintenance_thread.name == "ScheduledMaintenanceThread"
        mock_logger.info.assert_any_call(
            "Starting scheduled maintenance service (interval: 3 hours)"
        )
        service.stop()

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_start_clears_stop_event(self, mock_logger):
        """Test that start() clears the stop event."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.stop_event.set()  # Pre-set stop event

        service.start()

        # Thread should start, check it exists
        assert service.maintenance_thread is not None
        service.stop()


class TestScheduledMaintenanceServiceStop:
    """Tests for ScheduledMaintenanceService.stop() method."""

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    def test_stop_when_not_running(self):
        """Test stop() when service is not running."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.stop()  # Should not raise

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_stop_graceful_shutdown(self, mock_logger):
        """Test graceful stop of maintenance service."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        # Create a mock thread that stops gracefully
        mock_thread = Mock()
        mock_thread.is_alive.side_effect = [True, False]
        service.maintenance_thread = mock_thread

        service.stop()

        assert service.stop_event.is_set()
        mock_thread.join.assert_called_once_with(timeout=10)
        mock_logger.info.assert_any_call("Stopping scheduled maintenance service...")
        mock_logger.info.assert_any_call("Scheduled maintenance service stopped")

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_stop_non_graceful_shutdown(self, mock_logger):
        """Test non-graceful stop when thread doesn't stop."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        # Create a mock thread that doesn't stop
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        service.maintenance_thread = mock_thread

        service.stop()

        mock_logger.warning.assert_called_with(
            "Scheduled maintenance thread did not stop gracefully"
        )

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    def test_stop_with_none_thread(self):
        """Test stop() when maintenance_thread is None."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.maintenance_thread = None

        service.stop()  # Should not raise


class TestScheduledMaintenanceServiceLoop:
    """Tests for ScheduledMaintenanceService._maintenance_loop() method."""

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'true',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '1'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_maintenance_loop_with_startup_tasks(self, mock_logger):
        """Test maintenance loop runs startup tasks."""
        mock_app = Mock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        # Set stop event after startup
        def set_stop(*args, **kwargs):
            service.stop_event.set()
            return True

        service.stop_event.wait = Mock(side_effect=set_stop)

        service._maintenance_loop()

        service._run_maintenance_tasks.assert_called_once()
        mock_logger.info.assert_any_call("Running startup maintenance tasks...")

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '1'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_maintenance_loop_without_startup_tasks(self, mock_logger):
        """Test maintenance loop skips startup tasks when disabled."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        # Set stop event immediately
        service.stop_event.set()
        service.stop_event.wait = Mock(return_value=True)

        service._maintenance_loop()

        # Should not be called since we stop immediately
        service._run_maintenance_tasks.assert_not_called()

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '2'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_maintenance_loop_scheduled_tasks(self, mock_logger):
        """Test maintenance loop runs scheduled tasks."""
        mock_app = Mock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        call_count = [0]
        def wait_side_effect(timeout):
            call_count[0] += 1
            if call_count[0] >= 2:
                service.stop_event.set()
                return True
            return False

        service.stop_event.wait = Mock(side_effect=wait_side_effect)

        service._maintenance_loop()

        service._run_maintenance_tasks.assert_called_once()
        # Check that wait was called with correct timeout
        service.stop_event.wait.assert_called_with(timeout=2 * 3600)

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_maintenance_loop_exception_handling(self, mock_logger):
        """Test maintenance loop handles exceptions."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)
        service.stop_event.wait = Mock(side_effect=Exception("Test error"))

        service._maintenance_loop()

        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Error in maintenance loop" in args[0]
        assert kwargs.get('exc_info') is True

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'MAINTENANCE_ON_STARTUP': 'false',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '1'
    })
    @patch('utils.scheduled_maintenance.logger')
    def test_maintenance_loop_logs_next_time(self, mock_logger):
        """Test that maintenance loop logs the next scheduled time."""
        mock_app = Mock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        call_count = [0]
        def wait_side_effect(timeout):
            call_count[0] += 1
            if call_count[0] >= 1:
                service.stop_event.set()
                return True
            return False

        service.stop_event.wait = Mock(side_effect=wait_side_effect)

        service._maintenance_loop()

        # Check that next maintenance time was logged
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Next scheduled maintenance at" in call for call in info_calls)


class TestScheduledMaintenanceServiceRunTasks:
    """Tests for ScheduledMaintenanceService._run_maintenance_tasks() method."""

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.bulk_update_tool_calibration_status')
    @patch('utils.scheduled_maintenance.bulk_update_chemical_status')
    @patch('utils.scheduled_maintenance.logger')
    def test_run_maintenance_tasks_success(self, mock_logger, mock_chemical_update, mock_calibration_update):
        """Test successful execution of maintenance tasks."""
        mock_app = Mock()
        mock_db = Mock()

        mock_calibration_update.return_value = {
            "overdue": 5,
            "due_soon": 10,
            "current": 85
        }
        mock_chemical_update.return_value = {
            "expired": 3,
            "expiring_soon": 7,
            "current": 90
        }

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': MagicMock(db=mock_db)}):
            service._run_maintenance_tasks()

        mock_calibration_update.assert_called_once()
        mock_chemical_update.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_logger.info.assert_any_call("Starting maintenance tasks...")
        mock_logger.info.assert_any_call("Maintenance tasks completed successfully")

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.bulk_update_tool_calibration_status')
    @patch('utils.scheduled_maintenance.bulk_update_chemical_status')
    @patch('utils.scheduled_maintenance.logger')
    def test_run_maintenance_tasks_calibration_error(self, mock_logger, mock_chemical_update, mock_calibration_update):
        """Test handling of calibration update errors."""
        mock_app = Mock()
        mock_db = Mock()

        mock_calibration_update.side_effect = Exception("Database error")
        mock_chemical_update.return_value = {"expired": 0, "expiring_soon": 0, "current": 100}

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': MagicMock(db=mock_db)}):
            service._run_maintenance_tasks()

        # Should log error but continue with chemical updates
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert any("Error updating tool calibration statuses" in str(call) for call in error_calls)
        mock_chemical_update.assert_called_once()

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.bulk_update_tool_calibration_status')
    @patch('utils.scheduled_maintenance.bulk_update_chemical_status')
    @patch('utils.scheduled_maintenance.logger')
    def test_run_maintenance_tasks_chemical_error(self, mock_logger, mock_chemical_update, mock_calibration_update):
        """Test handling of chemical update errors."""
        mock_app = Mock()
        mock_db = Mock()

        mock_calibration_update.return_value = {"overdue": 0, "due_soon": 0, "current": 100}
        mock_chemical_update.side_effect = Exception("Chemical update failed")

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': MagicMock(db=mock_db)}):
            service._run_maintenance_tasks()

        error_calls = [call for call in mock_logger.error.call_args_list]
        assert any("Error updating chemical statuses" in str(call) for call in error_calls)

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.bulk_update_tool_calibration_status')
    @patch('utils.scheduled_maintenance.bulk_update_chemical_status')
    @patch('utils.scheduled_maintenance.logger')
    def test_run_maintenance_tasks_commit_error(self, mock_logger, mock_chemical_update, mock_calibration_update):
        """Test handling of database commit errors."""
        mock_app = Mock()
        mock_db = Mock()
        mock_db.session.commit.side_effect = Exception("Commit failed")

        mock_calibration_update.return_value = {"overdue": 0, "due_soon": 0, "current": 100}
        mock_chemical_update.return_value = {"expired": 0, "expiring_soon": 0, "current": 100}

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': MagicMock(db=mock_db)}):
            service._run_maintenance_tasks()

        mock_db.session.rollback.assert_called_once()
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert any("Error committing maintenance changes" in str(call) for call in error_calls)

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_run_maintenance_tasks_import_error(self, mock_logger):
        """Test handling of db import errors."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': None}):
            # This will cause an ImportError when trying to import db
            service._run_maintenance_tasks()

        # Should handle the exception
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert any("Error running maintenance tasks" in str(call) for call in error_calls)


class TestScheduledMaintenanceServiceManual:
    """Tests for ScheduledMaintenanceService.run_manual_maintenance() method."""

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_run_manual_maintenance_success(self, mock_logger):
        """Test successful manual maintenance execution."""
        mock_app = Mock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        result = service.run_manual_maintenance()

        assert result is True
        service._run_maintenance_tasks.assert_called_once()
        mock_logger.info.assert_called_with("Running manual maintenance tasks...")

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.logger')
    def test_run_manual_maintenance_uses_app_context(self, mock_logger):
        """Test that manual maintenance uses app context."""
        mock_app = Mock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context

        service = ScheduledMaintenanceService(mock_app)
        service._run_maintenance_tasks = Mock()

        service.run_manual_maintenance()

        mock_app.app_context.assert_called_once()


class TestGlobalMaintenanceFunctions:
    """Tests for global maintenance service functions."""

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'false'})
    def test_init_scheduled_maintenance_creates_service(self):
        """Test init_scheduled_maintenance creates and starts service."""
        import utils.scheduled_maintenance as module

        mock_app = Mock()

        # Reset global
        module._maintenance_service = None

        result = init_scheduled_maintenance(mock_app)

        assert result is not None
        assert isinstance(result, ScheduledMaintenanceService)

        # Cleanup
        module._maintenance_service = None

    def test_init_scheduled_maintenance_already_initialized(self):
        """Test init_scheduled_maintenance when already initialized."""
        import utils.scheduled_maintenance as module

        existing_service = Mock()
        module._maintenance_service = existing_service

        result = init_scheduled_maintenance(Mock())

        assert result == existing_service

        # Cleanup
        module._maintenance_service = None

    def test_get_maintenance_service(self):
        """Test get_maintenance_service returns global instance."""
        import utils.scheduled_maintenance as module

        test_service = Mock()
        module._maintenance_service = test_service

        result = get_maintenance_service()

        assert result == test_service

        # Cleanup
        module._maintenance_service = None

    def test_get_maintenance_service_when_none(self):
        """Test get_maintenance_service when service is None."""
        import utils.scheduled_maintenance as module

        module._maintenance_service = None

        result = get_maintenance_service()

        assert result is None

    def test_shutdown_scheduled_maintenance(self):
        """Test shutdown_scheduled_maintenance stops and clears service."""
        import utils.scheduled_maintenance as module

        mock_service = Mock()
        module._maintenance_service = mock_service

        shutdown_scheduled_maintenance()

        mock_service.stop.assert_called_once()
        assert module._maintenance_service is None

    def test_shutdown_scheduled_maintenance_when_none(self):
        """Test shutdown_scheduled_maintenance when service is None."""
        import utils.scheduled_maintenance as module

        module._maintenance_service = None

        shutdown_scheduled_maintenance()  # Should not raise

        assert module._maintenance_service is None


class TestScheduledMaintenanceIntegration:
    """Integration tests for scheduled maintenance service."""

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '1',
        'MAINTENANCE_ON_STARTUP': 'false'
    })
    def test_full_service_lifecycle(self):
        """Test complete service lifecycle: init, start, stop."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        # Start service
        service.start()
        assert service.maintenance_thread is not None
        assert service.maintenance_thread.is_alive()

        # Give thread time to start
        time.sleep(0.1)

        # Stop service
        service.stop()
        assert service.stop_event.is_set()

    @patch.dict('os.environ', {
        'AUTO_MAINTENANCE_ENABLED': 'true',
        'AUTO_MAINTENANCE_INTERVAL_HOURS': '6'
    })
    def test_interval_calculation(self):
        """Test that interval hours are correctly applied."""
        mock_app = Mock()

        service = ScheduledMaintenanceService(mock_app)

        assert service.interval_hours == 6

        # Test wait timeout calculation (would be 6 * 3600 = 21600)
        expected_timeout = 6 * 3600
        assert expected_timeout == 21600

    @patch.dict('os.environ', {'AUTO_MAINTENANCE_ENABLED': 'true'})
    @patch('utils.scheduled_maintenance.bulk_update_tool_calibration_status')
    @patch('utils.scheduled_maintenance.bulk_update_chemical_status')
    def test_maintenance_results_logging(self, mock_chemical_update, mock_calibration_update):
        """Test that maintenance results are properly logged with extra data."""
        mock_app = Mock()
        mock_db = Mock()

        mock_calibration_update.return_value = {
            "overdue": 2,
            "due_soon": 5,
            "current": 93
        }
        mock_chemical_update.return_value = {
            "expired": 1,
            "expiring_soon": 3,
            "current": 96
        }

        service = ScheduledMaintenanceService(mock_app)

        with patch.dict('sys.modules', {'models': MagicMock(db=mock_db)}):
            with patch('utils.scheduled_maintenance.logger') as mock_logger:
                service._run_maintenance_tasks()

        # Verify extra logging data
        info_calls = mock_logger.info.call_args_list
        calibration_call = [c for c in info_calls if "Tool calibration status update complete" in str(c)]
        assert len(calibration_call) > 0

        chemical_call = [c for c in info_calls if "Chemical status update complete" in str(c)]
        assert len(chemical_call) > 0
