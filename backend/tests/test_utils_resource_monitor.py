"""
Comprehensive tests for utils/resource_monitor.py

This module provides tests for system resource monitoring including
CPU, memory, disk usage tracking, alerting, and health checks.
"""

import logging
import threading
import time
from unittest import mock
from unittest.mock import MagicMock, Mock, patch, PropertyMock

import pytest

from utils import resource_monitor
from utils.resource_monitor import (
    ResourceMonitor,
    init_resource_monitoring,
    get_resource_monitor,
    get_resource_stats,
    check_system_health,
)


class TestResourceMonitorInit:
    """Test ResourceMonitor initialization."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        monitor = ResourceMonitor()

        assert monitor.check_interval == 60
        assert monitor.running is False
        assert monitor._thread is None
        assert monitor.thresholds["memory_percent"] == 80
        assert monitor.thresholds["disk_percent"] == 85
        assert monitor.thresholds["open_files"] == 1000
        assert monitor.thresholds["db_connections"] == 8

    def test_init_custom_interval(self):
        """Test initialization with custom check interval."""
        monitor = ResourceMonitor(check_interval=30)

        assert monitor.check_interval == 30

    def test_init_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        custom_thresholds = {
            "memory_percent": 90,
            "disk_percent": 95,
            "open_files": 500,
            "db_connections": 10
        }
        monitor = ResourceMonitor(thresholds=custom_thresholds)

        assert monitor.thresholds["memory_percent"] == 90
        assert monitor.thresholds["disk_percent"] == 95
        assert monitor.thresholds["open_files"] == 500
        assert monitor.thresholds["db_connections"] == 10

    def test_init_partial_custom_thresholds(self):
        """Test initialization with partial custom thresholds."""
        custom_thresholds = {"memory_percent": 75}
        monitor = ResourceMonitor(thresholds=custom_thresholds)

        assert monitor.thresholds["memory_percent"] == 75
        # Other values should remain default
        assert monitor.thresholds["disk_percent"] == 85
        assert monitor.thresholds["open_files"] == 1000
        assert monitor.thresholds["db_connections"] == 8

    def test_init_empty_thresholds(self):
        """Test initialization with empty thresholds dictionary."""
        monitor = ResourceMonitor(thresholds={})

        # Should retain all defaults
        assert monitor.thresholds["memory_percent"] == 80
        assert monitor.thresholds["disk_percent"] == 85


class TestResourceMonitorStartStop:
    """Test ResourceMonitor start and stop functionality."""

    def test_start_monitoring(self):
        """Test starting the monitoring thread."""
        monitor = ResourceMonitor(check_interval=1)

        assert monitor.running is False
        assert monitor._thread is None

        monitor.start_monitoring()

        assert monitor.running is True
        assert monitor._thread is not None
        assert monitor._thread.is_alive()
        assert monitor._thread.daemon is True

        # Clean up
        monitor.stop_monitoring()

    def test_start_monitoring_when_already_running(self):
        """Test that starting monitoring when already running does nothing."""
        monitor = ResourceMonitor(check_interval=1)

        monitor.start_monitoring()
        original_thread = monitor._thread

        # Try to start again
        monitor.start_monitoring()

        # Should be the same thread
        assert monitor._thread is original_thread

        # Clean up
        monitor.stop_monitoring()

    def test_stop_monitoring(self):
        """Test stopping the monitoring thread."""
        monitor = ResourceMonitor(check_interval=1)
        monitor.start_monitoring()

        assert monitor.running is True

        monitor.stop_monitoring()

        assert monitor.running is False
        # Thread should have stopped
        time.sleep(0.1)
        assert not monitor._thread.is_alive()

    def test_stop_monitoring_when_not_running(self):
        """Test stopping monitoring when not running."""
        monitor = ResourceMonitor()

        # Should not raise an error
        monitor.stop_monitoring()

        assert monitor.running is False
        assert monitor._thread is None

    def test_stop_monitoring_thread_join_timeout(self):
        """Test that stop_monitoring handles thread join with timeout."""
        monitor = ResourceMonitor(check_interval=1)

        with patch.object(threading.Thread, 'is_alive', return_value=True):
            monitor.running = True
            monitor._thread = Mock(spec=threading.Thread)
            monitor._thread.is_alive.return_value = True

            monitor.stop_monitoring()

            monitor._thread.join.assert_called_once_with(timeout=5)


class TestResourceMonitorLoop:
    """Test the monitoring loop functionality."""

    @patch('utils.resource_monitor.time.sleep')
    @patch.object(ResourceMonitor, '_check_resources')
    def test_monitor_loop_calls_check_resources(self, mock_check, mock_sleep):
        """Test that monitor loop calls _check_resources."""
        monitor = ResourceMonitor(check_interval=1)

        # Make the loop exit after first iteration
        call_count = [0]
        def stop_after_one(*args):
            call_count[0] += 1
            if call_count[0] >= 1:
                monitor.running = False

        mock_sleep.side_effect = stop_after_one
        monitor.running = True

        monitor._monitor_loop()

        assert mock_check.called

    @patch('utils.resource_monitor.time.sleep')
    @patch.object(ResourceMonitor, '_check_resources')
    def test_monitor_loop_handles_exception(self, mock_check, mock_sleep):
        """Test that monitor loop handles exceptions gracefully."""
        monitor = ResourceMonitor(check_interval=1)

        # Make _check_resources raise an exception
        mock_check.side_effect = Exception("Test error")

        # Make the loop exit after first iteration
        call_count = [0]
        def stop_after_one(*args):
            call_count[0] += 1
            if call_count[0] >= 1:
                monitor.running = False

        mock_sleep.side_effect = stop_after_one
        monitor.running = True

        # Should not raise exception
        monitor._monitor_loop()

        # Should have tried to check resources
        assert mock_check.called


class TestCheckResources:
    """Test the _check_resources method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = ResourceMonitor()

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_normal_usage(self, mock_psutil):
        """Test resource check with normal usage levels."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024  # 100GB
        mock_disk.total = 250 * 1024 * 1024 * 1024  # 250GB
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        # Mock CPU
        mock_psutil.cpu_percent.return_value = 25

        # Should not log any warnings
        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            self.monitor._check_resources()

            # No warnings should be logged for normal usage
            warning_calls = [c for c in mock_warning.call_args_list
                           if 'High' in str(c)]
            assert len(warning_calls) == 0

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_high_memory_usage(self, mock_psutil):
        """Test resource check with high memory usage."""
        # Mock high memory usage
        mock_memory = Mock()
        mock_memory.percent = 85  # Above threshold
        mock_memory.available = 2 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk (normal)
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        mock_psutil.cpu_percent.return_value = 25

        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            self.monitor._check_resources()

            # Should log warning for high memory
            assert any('High memory usage' in str(c) for c in mock_warning.call_args_list)

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_high_disk_usage(self, mock_psutil):
        """Test resource check with high disk usage."""
        # Mock memory (normal)
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock high disk usage
        mock_disk = Mock()
        mock_disk.percent = 90  # Above threshold
        mock_disk.free = 25 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        mock_psutil.cpu_percent.return_value = 25

        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            self.monitor._check_resources()

            # Should log warning for high disk
            assert any('High disk usage' in str(c) for c in mock_warning.call_args_list)

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_high_open_files(self, mock_psutil):
        """Test resource check with high open file count."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process with many open files
        mock_process = Mock()
        mock_process.open_files.return_value = [Mock()] * 1500  # Above threshold
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        mock_psutil.cpu_percent.return_value = 25

        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            self.monitor._check_resources()

            # Should log warning for high open file count
            assert any('High open file count' in str(c) for c in mock_warning.call_args_list)

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_process_access_denied(self, mock_psutil):
        """Test resource check handles process access denied."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process with access denied on open_files()
        mock_process = Mock()
        mock_psutil.AccessDenied = PermissionError
        mock_psutil.NoSuchProcess = ProcessLookupError
        mock_process.open_files.side_effect = mock_psutil.AccessDenied("Access denied")
        mock_psutil.Process.return_value = mock_process

        mock_psutil.cpu_percent.return_value = 25

        # Should not raise exception
        self.monitor._check_resources()

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_process_no_such_process(self, mock_psutil):
        """Test resource check handles NoSuchProcess exception."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process with NoSuchProcess on open_files()
        mock_process = Mock()
        mock_psutil.AccessDenied = PermissionError
        mock_psutil.NoSuchProcess = ProcessLookupError
        mock_process.open_files.side_effect = mock_psutil.NoSuchProcess("Process not found")
        mock_psutil.Process.return_value = mock_process

        mock_psutil.cpu_percent.return_value = 25

        # Should not raise exception
        self.monitor._check_resources()

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_disk_usage_error(self, mock_psutil):
        """Test resource check handles disk usage error."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk usage to raise error
        mock_psutil.disk_usage.side_effect = Exception("Disk error")

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        # Should not raise exception
        self.monitor._check_resources()

    @patch('utils.resource_monitor.psutil')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_resources_high_db_connections(self, mock_conn_stats, mock_psutil):
        """Test resource check with high database connections."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        # Mock high database connections
        mock_conn_stats.return_value = {"checked_out": 15}  # Above threshold

        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            self.monitor._check_resources()

            # Should log warning for high db connections
            assert any('High database connection' in str(c) for c in mock_warning.call_args_list)

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_db_import_error(self, mock_psutil):
        """Test resource check handles database utils import error."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        # Should handle ImportError gracefully
        with patch.dict('sys.modules', {'utils.database_utils': None}):
            self.monitor._check_resources()

    @patch('utils.resource_monitor.psutil')
    def test_check_resources_general_exception(self, mock_psutil):
        """Test resource check handles general exception."""
        # Mock psutil to raise exception
        mock_psutil.virtual_memory.side_effect = Exception("General error")

        with patch.object(resource_monitor.logger, 'error') as mock_error:
            self.monitor._check_resources()

            # Should log error
            assert mock_error.called

    @patch('utils.resource_monitor.psutil')
    @patch('os.name', 'nt')
    def test_check_resources_windows_disk_path(self, mock_psutil):
        """Test resource check uses Windows disk path."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        with patch('os.getcwd', return_value='C:\\Users\\Test'):
            self.monitor._check_resources()
            # Should have called disk_usage with Windows path
            mock_psutil.disk_usage.assert_called()


class TestGetCurrentStats:
    """Test the get_current_stats method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = ResourceMonitor()

    @patch('utils.resource_monitor.psutil')
    @patch('utils.resource_monitor.time.time')
    def test_get_current_stats_success(self, mock_time, mock_psutil):
        """Test getting current stats successfully."""
        mock_time.return_value = 1234567890.123

        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 65.5
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 70.2
        mock_disk.free = 75 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_disk.used = 175 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock CPU
        mock_psutil.cpu_percent.return_value = 45.3
        mock_psutil.cpu_count.return_value = 8

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = [Mock()] * 25
        mock_process.pid = 98765
        mock_psutil.Process.return_value = mock_process

        # Mock network connections
        mock_psutil.net_connections.return_value = [Mock()] * 10

        stats = self.monitor.get_current_stats()

        assert stats["memory"]["percent"] == 65.5
        assert stats["memory"]["available_mb"] == 8192.0
        assert stats["memory"]["total_mb"] == 16384.0
        assert stats["memory"]["used_mb"] == 8192.0

        assert stats["disk"]["percent"] == 70.2
        assert stats["disk"]["free_gb"] == 75.0
        assert stats["disk"]["total_gb"] == 250.0
        assert stats["disk"]["used_gb"] == 175.0

        assert stats["cpu"]["percent"] == 45.3
        assert stats["cpu"]["count"] == 8

        assert stats["process"]["open_files"] == 25
        assert stats["process"]["connections"] == 10
        assert stats["process"]["pid"] == 98765

        assert stats["thresholds"] == self.monitor.thresholds
        assert stats["timestamp"] == 1234567890.123

    @patch('utils.resource_monitor.psutil')
    @patch('utils.resource_monitor.time.time')
    def test_get_current_stats_network_access_denied(self, mock_time, mock_psutil):
        """Test getting stats when network connections access denied."""
        mock_time.return_value = 1234567890.123

        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_disk.used = 150 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock CPU
        mock_psutil.cpu_percent.return_value = 25
        mock_psutil.cpu_count.return_value = 4

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        # Mock network connections with access denied
        mock_psutil.AccessDenied = PermissionError
        mock_psutil.net_connections.side_effect = PermissionError("Access denied")

        stats = self.monitor.get_current_stats()

        # Should return -1 for unavailable connections
        assert stats["process"]["connections"] == -1

    @patch('utils.resource_monitor.psutil')
    @patch('utils.resource_monitor.time.time')
    def test_get_current_stats_disk_error(self, mock_time, mock_psutil):
        """Test getting stats when disk usage fails."""
        mock_time.return_value = 1234567890.123

        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk to fail
        mock_psutil.disk_usage.side_effect = Exception("Disk error")

        # Mock CPU
        mock_psutil.cpu_percent.return_value = 25
        mock_psutil.cpu_count.return_value = 4

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        mock_psutil.net_connections.return_value = []

        stats = self.monitor.get_current_stats()

        # Should use mock disk data
        assert stats["disk"]["percent"] == 0
        assert stats["disk"]["free_gb"] == 0.0
        assert stats["disk"]["total_gb"] == 0.0

    @patch('utils.resource_monitor.psutil')
    @patch('utils.resource_monitor.time.time')
    def test_get_current_stats_general_exception(self, mock_time, mock_psutil):
        """Test getting stats with general exception."""
        mock_time.return_value = 1234567890.123

        # Mock psutil to raise exception
        mock_psutil.virtual_memory.side_effect = Exception("General error")

        stats = self.monitor.get_current_stats()

        assert "error" in stats
        assert stats["error"] == "General error"
        assert stats["timestamp"] == 1234567890.123

    @patch('utils.resource_monitor.psutil')
    @patch('os.name', 'nt')
    def test_get_current_stats_windows_path(self, mock_psutil):
        """Test getting stats uses Windows disk path."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_disk.used = 150 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock CPU
        mock_psutil.cpu_percent.return_value = 25
        mock_psutil.cpu_count.return_value = 4

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process

        mock_psutil.net_connections.return_value = []

        with patch('os.getcwd', return_value='D:\\Projects\\Test'):
            stats = self.monitor.get_current_stats()
            assert "disk" in stats


class TestCheckHealth:
    """Test the check_health method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = ResourceMonitor()

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_healthy(self, mock_stats):
        """Test check_health when system is healthy."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is True
        assert health["issues"] == []
        assert "stats" in health

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_high_memory(self, mock_stats):
        """Test check_health with high memory usage."""
        mock_stats.return_value = {
            "memory": {"percent": 85},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 1
        assert "High memory usage: 85%" in health["issues"][0]

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_high_disk(self, mock_stats):
        """Test check_health with high disk usage."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 90},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 1
        assert "High disk usage: 90%" in health["issues"][0]

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_high_open_files(self, mock_stats):
        """Test check_health with high open file count."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 1500},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 1
        assert "High open file count: 1500" in health["issues"][0]

    @patch.object(ResourceMonitor, 'get_current_stats')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_health_high_db_connections(self, mock_conn_stats, mock_stats):
        """Test check_health with high database connections."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        mock_conn_stats.return_value = {"checked_out": 15}

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 1
        assert "High database connection usage: 15" in health["issues"][0]

    @patch.object(ResourceMonitor, 'get_current_stats')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_health_db_stats_with_error(self, mock_conn_stats, mock_stats):
        """Test check_health when database stats contain error."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        mock_conn_stats.return_value = {"error": "Database not available"}

        health = self.monitor.check_health()

        # Should be healthy since db error stats are ignored
        assert health["healthy"] is True

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_multiple_issues(self, mock_stats):
        """Test check_health with multiple issues."""
        mock_stats.return_value = {
            "memory": {"percent": 85},
            "disk": {"percent": 90},
            "process": {"open_files": 1500},
            "cpu": {"percent": 95, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 3
        assert any("memory" in issue for issue in health["issues"])
        assert any("disk" in issue for issue in health["issues"])
        assert any("file" in issue for issue in health["issues"])

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_stats_error(self, mock_stats):
        """Test check_health when stats return error."""
        mock_stats.return_value = {
            "error": "Failed to get stats",
            "timestamp": 1234567890
        }

        health = self.monitor.check_health()

        assert health["healthy"] is False
        assert len(health["issues"]) == 1
        assert "Error getting stats" in health["issues"][0]

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_db_import_error(self, mock_stats):
        """Test check_health handles database utils import error."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": self.monitor.thresholds,
            "timestamp": 1234567890
        }

        # Should handle ImportError gracefully
        with patch.dict('sys.modules', {'utils.database_utils': None}):
            health = self.monitor.check_health()

            assert health["healthy"] is True


class TestGlobalFunctions:
    """Test global module functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Save the original global monitor
        self.original_monitor = resource_monitor._resource_monitor
        resource_monitor._resource_monitor = None

    def teardown_method(self):
        """Clean up after tests."""
        # Restore the original global monitor
        if resource_monitor._resource_monitor:
            resource_monitor._resource_monitor.stop_monitoring()
        resource_monitor._resource_monitor = self.original_monitor

    def test_init_resource_monitoring(self):
        """Test initializing resource monitoring with Flask app."""
        mock_app = Mock()
        mock_app.config = {
            "RESOURCE_CHECK_INTERVAL": 30,
            "RESOURCE_THRESHOLDS": {"memory_percent": 90}
        }

        init_resource_monitoring(mock_app)

        monitor = get_resource_monitor()
        assert monitor is not None
        assert monitor.check_interval == 30
        assert monitor.thresholds["memory_percent"] == 90
        assert monitor.running is True

        # Clean up
        monitor.stop_monitoring()

    def test_init_resource_monitoring_default_config(self):
        """Test initializing resource monitoring with default config."""
        mock_app = Mock()
        mock_config = MagicMock()
        mock_config.get = lambda key, default=None: default
        mock_app.config = mock_config

        init_resource_monitoring(mock_app)

        monitor = get_resource_monitor()
        assert monitor is not None
        assert monitor.check_interval == 60
        assert monitor.running is True

        # Clean up
        monitor.stop_monitoring()

    def test_get_resource_monitor_none(self):
        """Test getting monitor when not initialized."""
        resource_monitor._resource_monitor = None

        monitor = get_resource_monitor()

        assert monitor is None

    def test_get_resource_monitor_initialized(self):
        """Test getting monitor when initialized."""
        test_monitor = ResourceMonitor()
        resource_monitor._resource_monitor = test_monitor

        monitor = get_resource_monitor()

        assert monitor is test_monitor

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_get_resource_stats_initialized(self, mock_stats):
        """Test getting resource stats when monitor initialized."""
        mock_stats.return_value = {"memory": {"percent": 50}}
        resource_monitor._resource_monitor = ResourceMonitor()

        stats = get_resource_stats()

        assert "memory" in stats
        mock_stats.assert_called_once()

    def test_get_resource_stats_not_initialized(self):
        """Test getting resource stats when monitor not initialized."""
        resource_monitor._resource_monitor = None

        stats = get_resource_stats()

        assert "error" in stats
        assert stats["error"] == "Resource monitoring not initialized"

    @patch.object(ResourceMonitor, 'check_health')
    def test_check_system_health_initialized(self, mock_health):
        """Test checking system health when monitor initialized."""
        mock_health.return_value = {"healthy": True, "issues": []}
        resource_monitor._resource_monitor = ResourceMonitor()

        health = check_system_health()

        assert health["healthy"] is True
        mock_health.assert_called_once()

    def test_check_system_health_not_initialized(self):
        """Test checking system health when monitor not initialized."""
        resource_monitor._resource_monitor = None

        health = check_system_health()

        assert health["healthy"] is False
        assert "Resource monitoring not initialized" in health["issues"]


class TestIntegration:
    """Integration tests for resource monitoring."""

    @patch('utils.resource_monitor.psutil')
    def test_full_monitoring_cycle(self, mock_psutil):
        """Test a complete monitoring cycle."""
        # Mock all psutil calls
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_disk.used = 150 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        mock_psutil.cpu_percent.return_value = 25
        mock_psutil.cpu_count.return_value = 4

        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = PermissionError
        mock_psutil.NoSuchProcess = ProcessLookupError

        mock_psutil.net_connections.return_value = []

        # Create monitor with custom thresholds
        monitor = ResourceMonitor(
            check_interval=1,
            thresholds={"memory_percent": 70, "disk_percent": 80}
        )

        # Get stats
        stats = monitor.get_current_stats()
        assert stats["memory"]["percent"] == 50
        assert stats["disk"]["percent"] == 60

        # Check health
        health = monitor.check_health()
        assert health["healthy"] is True
        assert len(health["issues"]) == 0

        # Check resources directly
        monitor._check_resources()

    def test_thread_safety(self):
        """Test that monitoring is thread-safe."""
        monitor = ResourceMonitor(check_interval=0.1)

        results = []

        def get_stats():
            with patch('utils.resource_monitor.psutil') as mock_psutil:
                mock_memory = Mock()
                mock_memory.percent = 50
                mock_memory.available = 8 * 1024 * 1024 * 1024
                mock_memory.total = 16 * 1024 * 1024 * 1024
                mock_memory.used = 8 * 1024 * 1024 * 1024
                mock_psutil.virtual_memory.return_value = mock_memory

                mock_disk = Mock()
                mock_disk.percent = 60
                mock_disk.free = 100 * 1024 * 1024 * 1024
                mock_disk.total = 250 * 1024 * 1024 * 1024
                mock_disk.used = 150 * 1024 * 1024 * 1024
                mock_psutil.disk_usage.return_value = mock_disk

                mock_psutil.cpu_percent.return_value = 25
                mock_psutil.cpu_count.return_value = 4

                mock_process = Mock()
                mock_process.open_files.return_value = []
                mock_process.pid = 12345
                mock_psutil.Process.return_value = mock_process

                mock_psutil.net_connections.return_value = []

                stats = monitor.get_current_stats()
                results.append(stats)

        threads = [threading.Thread(target=get_stats) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        for result in results:
            assert "memory" in result

    @patch('utils.resource_monitor.psutil')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_resources_db_exception(self, mock_conn_stats, mock_psutil):
        """Test _check_resources handles database connection stats exception."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        # Mock database connection stats to raise generic exception
        mock_conn_stats.side_effect = RuntimeError("Database connection error")

        monitor = ResourceMonitor()

        # Should not raise exception
        monitor._check_resources()

    @patch('utils.resource_monitor.psutil')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_resources_db_returns_non_dict(self, mock_conn_stats, mock_psutil):
        """Test _check_resources handles non-dict database stats."""
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 50
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_memory.total = 16 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        # Mock disk
        mock_disk = Mock()
        mock_disk.percent = 60
        mock_disk.free = 100 * 1024 * 1024 * 1024
        mock_disk.total = 250 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk

        # Mock process
        mock_process = Mock()
        mock_process.open_files.return_value = []
        mock_process.pid = 12345
        mock_psutil.Process.return_value = mock_process
        mock_psutil.AccessDenied = Exception
        mock_psutil.NoSuchProcess = Exception

        mock_psutil.cpu_percent.return_value = 25

        # Mock database connection stats to return non-dict
        mock_conn_stats.return_value = "not a dict"

        monitor = ResourceMonitor()

        with patch.object(resource_monitor.logger, 'warning') as mock_warning:
            monitor._check_resources()

            # Should not log warning about high db connections
            db_warnings = [c for c in mock_warning.call_args_list
                          if 'High database connection' in str(c)]
            assert len(db_warnings) == 0

    @patch.object(ResourceMonitor, 'get_current_stats')
    @patch('utils.database_utils.get_connection_stats')
    def test_check_health_db_stats_not_dict(self, mock_conn_stats, mock_stats):
        """Test check_health when database stats is not a dict."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": {"memory_percent": 80, "disk_percent": 85, "open_files": 1000, "db_connections": 8},
            "timestamp": 1234567890
        }

        mock_conn_stats.return_value = "not a dict"

        monitor = ResourceMonitor()
        health = monitor.check_health()

        # Should be healthy since non-dict stats are ignored
        assert health["healthy"] is True

    @patch.object(ResourceMonitor, 'get_current_stats')
    def test_check_health_db_generic_exception(self, mock_stats):
        """Test check_health handles generic database exception."""
        mock_stats.return_value = {
            "memory": {"percent": 50},
            "disk": {"percent": 60},
            "process": {"open_files": 100},
            "cpu": {"percent": 25, "count": 8},
            "thresholds": {"memory_percent": 80, "disk_percent": 85, "open_files": 1000, "db_connections": 8},
            "timestamp": 1234567890
        }

        monitor = ResourceMonitor()

        # Mock the import to raise a generic exception
        with patch('utils.database_utils.get_connection_stats', side_effect=RuntimeError("DB error")):
            health = monitor.check_health()

            # Should handle exception gracefully and report healthy
            assert health["healthy"] is True
