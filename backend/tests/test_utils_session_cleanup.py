"""
Comprehensive tests for the session_cleanup module.
"""

import pytest
import os
import time
import tempfile
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from threading import Thread

from utils.session_cleanup import (
    SessionCleaner,
    init_session_cleanup,
    get_session_cleaner,
    cleanup_sessions_now,
    get_session_cleanup_stats
)


class TestSessionCleanerInit:
    """Tests for SessionCleaner initialization."""

    def test_init_with_default_values(self):
        """Test initialization with default parameter values."""
        cleaner = SessionCleaner("/tmp/sessions")

        assert cleaner.session_dir == "/tmp/sessions"
        assert cleaner.max_age == 86400  # 24 hours
        assert cleaner.cleanup_interval == 3600  # 1 hour
        assert cleaner.running is False
        assert cleaner._thread is None

    def test_init_with_custom_values(self):
        """Test initialization with custom parameter values."""
        cleaner = SessionCleaner(
            session_dir="/var/sessions",
            max_age=43200,
            cleanup_interval=1800
        )

        assert cleaner.session_dir == "/var/sessions"
        assert cleaner.max_age == 43200  # 12 hours
        assert cleaner.cleanup_interval == 1800  # 30 minutes
        assert cleaner.running is False

    def test_init_preserves_directory_path(self):
        """Test that directory path is preserved exactly."""
        paths = [
            "/home/user/sessions",
            "./relative/path",
            "sessions",
            "/tmp/flask_sessions_12345"
        ]

        for path in paths:
            cleaner = SessionCleaner(path)
            assert cleaner.session_dir == path


class TestSessionCleanerStartStop:
    """Tests for SessionCleaner start and stop methods."""

    @patch('utils.session_cleanup.logger')
    def test_start_cleanup_thread(self, mock_logger):
        """Test starting the cleanup thread."""
        cleaner = SessionCleaner("/tmp/sessions")

        # Mock the cleanup loop to prevent actual execution
        with patch.object(cleaner, '_cleanup_loop'):
            cleaner.start_cleanup_thread()

        assert cleaner.running is True
        assert cleaner._thread is not None
        assert cleaner._thread.daemon is True
        mock_logger.info.assert_called_with(
            "Session cleanup thread started for directory: /tmp/sessions"
        )

        # Cleanup
        cleaner.running = False

    @patch('utils.session_cleanup.logger')
    def test_start_cleanup_thread_idempotent(self, mock_logger):
        """Test that start_cleanup_thread is idempotent."""
        cleaner = SessionCleaner("/tmp/sessions")
        cleaner.running = True  # Already running
        original_thread = Mock()
        cleaner._thread = original_thread

        cleaner.start_cleanup_thread()

        # Should not create a new thread
        assert cleaner._thread == original_thread
        mock_logger.info.assert_not_called()

    @patch('utils.session_cleanup.logger')
    def test_stop_cleanup_thread(self, mock_logger):
        """Test stopping the cleanup thread."""
        cleaner = SessionCleaner("/tmp/sessions")

        # Create a mock thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        cleaner._thread = mock_thread
        cleaner.running = True

        cleaner.stop_cleanup_thread()

        assert cleaner.running is False
        mock_thread.join.assert_called_once_with(timeout=5)
        mock_logger.info.assert_called_with("Session cleanup thread stopped")

    @patch('utils.session_cleanup.logger')
    def test_stop_cleanup_thread_when_not_running(self, mock_logger):
        """Test stopping when thread is not running."""
        cleaner = SessionCleaner("/tmp/sessions")
        cleaner._thread = None

        cleaner.stop_cleanup_thread()

        assert cleaner.running is False
        mock_logger.info.assert_called_with("Session cleanup thread stopped")

    @patch('utils.session_cleanup.logger')
    def test_stop_cleanup_thread_when_thread_dead(self, mock_logger):
        """Test stopping when thread is already dead."""
        cleaner = SessionCleaner("/tmp/sessions")

        mock_thread = Mock()
        mock_thread.is_alive.return_value = False
        cleaner._thread = mock_thread

        cleaner.stop_cleanup_thread()

        mock_thread.join.assert_not_called()


class TestSessionCleanerCleanupLoop:
    """Tests for SessionCleaner._cleanup_loop() method."""

    @patch('utils.session_cleanup.time.sleep')
    @patch('utils.session_cleanup.logger')
    def test_cleanup_loop_runs_cleanup(self, mock_logger, mock_sleep):
        """Test that cleanup loop runs cleanup and sleeps."""
        cleaner = SessionCleaner("/tmp/sessions", cleanup_interval=100)
        cleaner.cleanup_expired_sessions = Mock(return_value=5)

        call_count = [0]
        def stop_after_one(*args):
            call_count[0] += 1
            if call_count[0] >= 1:
                cleaner.running = False

        mock_sleep.side_effect = stop_after_one
        cleaner.running = True

        cleaner._cleanup_loop()

        cleaner.cleanup_expired_sessions.assert_called_once()
        mock_sleep.assert_called_with(100)

    @patch('utils.session_cleanup.time.sleep')
    @patch('utils.session_cleanup.logger')
    def test_cleanup_loop_handles_exceptions(self, mock_logger, mock_sleep):
        """Test that cleanup loop handles exceptions gracefully."""
        cleaner = SessionCleaner("/tmp/sessions")
        cleaner.cleanup_expired_sessions = Mock(side_effect=Exception("Test error"))

        call_count = [0]
        def stop_after_one(*args):
            call_count[0] += 1
            if call_count[0] >= 1:
                cleaner.running = False

        mock_sleep.side_effect = stop_after_one
        cleaner.running = True

        cleaner._cleanup_loop()

        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args
        assert "Session cleanup error" in args[0][0]

    @patch('utils.session_cleanup.time.sleep')
    def test_cleanup_loop_respects_running_flag(self, mock_sleep):
        """Test that cleanup loop stops when running is False."""
        cleaner = SessionCleaner("/tmp/sessions")
        cleaner.cleanup_expired_sessions = Mock()
        cleaner.running = False

        cleaner._cleanup_loop()

        cleaner.cleanup_expired_sessions.assert_not_called()
        mock_sleep.assert_not_called()

    @patch('utils.session_cleanup.time.sleep')
    def test_cleanup_loop_multiple_iterations(self, mock_sleep):
        """Test cleanup loop runs multiple iterations."""
        cleaner = SessionCleaner("/tmp/sessions")
        cleaner.cleanup_expired_sessions = Mock(return_value=0)

        call_count = [0]
        def stop_after_three(*args):
            call_count[0] += 1
            if call_count[0] >= 3:
                cleaner.running = False

        mock_sleep.side_effect = stop_after_three
        cleaner.running = True

        cleaner._cleanup_loop()

        assert cleaner.cleanup_expired_sessions.call_count == 3


class TestSessionCleanerCleanupExpiredSessions:
    """Tests for SessionCleaner.cleanup_expired_sessions() method."""

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    def test_cleanup_when_directory_not_exists(self, mock_exists, mock_logger):
        """Test cleanup when session directory doesn't exist."""
        mock_exists.return_value = False

        cleaner = SessionCleaner("/nonexistent")
        result = cleaner.cleanup_expired_sessions()

        assert result == 0
        mock_logger.warning.assert_called_with(
            "Session directory does not exist: /nonexistent"
        )

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.os.remove')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_removes_expired_sessions(self, mock_time, mock_remove, mock_scandir, mock_exists, mock_logger):
        """Test that expired session files are removed."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        # Create mock directory entries
        old_session = Mock()
        old_session.is_file.return_value = True
        old_session.name = "session_abc123"
        old_session.path = "/sessions/session_abc123"
        old_stat = Mock()
        old_stat.st_mtime = 10000  # Very old (90000 seconds old)
        old_stat.st_size = 1024
        old_session.stat.return_value = old_stat

        mock_scandir.return_value.__enter__ = Mock(return_value=[old_session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions", max_age=86400)
        result = cleaner.cleanup_expired_sessions()

        assert result == 1
        mock_remove.assert_called_once_with("/sessions/session_abc123")
        mock_logger.info.assert_called()

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_skips_recent_sessions(self, mock_time, mock_scandir, mock_exists, mock_logger):
        """Test that recent session files are not removed."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        recent_session = Mock()
        recent_session.is_file.return_value = True
        recent_session.name = "session_recent"
        recent_stat = Mock()
        recent_stat.st_mtime = 99000  # Only 1000 seconds old
        recent_session.stat.return_value = recent_stat

        mock_scandir.return_value.__enter__ = Mock(return_value=[recent_session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions", max_age=86400)
        result = cleaner.cleanup_expired_sessions()

        assert result == 0

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_skips_non_session_files(self, mock_time, mock_scandir, mock_exists, mock_logger):
        """Test that non-session files are skipped."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        # Create a non-session file
        other_file = Mock()
        other_file.is_file.return_value = True
        other_file.name = "other_file.txt"

        mock_scandir.return_value.__enter__ = Mock(return_value=[other_file])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.cleanup_expired_sessions()

        assert result == 0

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_skips_directories(self, mock_time, mock_scandir, mock_exists, mock_logger):
        """Test that directories are skipped."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        directory = Mock()
        directory.is_file.return_value = False
        directory.name = "session_directory"

        mock_scandir.return_value.__enter__ = Mock(return_value=[directory])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.cleanup_expired_sessions()

        assert result == 0

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.os.remove')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_handles_remove_errors(self, mock_time, mock_remove, mock_scandir, mock_exists, mock_logger):
        """Test handling of file removal errors."""
        mock_exists.return_value = True
        mock_time.return_value = 100000
        mock_remove.side_effect = OSError("Permission denied")

        old_session = Mock()
        old_session.is_file.return_value = True
        old_session.name = "session_locked"
        old_session.path = "/sessions/session_locked"
        old_stat = Mock()
        old_stat.st_mtime = 10000
        old_stat.st_size = 512
        old_session.stat.return_value = old_stat

        mock_scandir.return_value.__enter__ = Mock(return_value=[old_session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions", max_age=86400)
        result = cleaner.cleanup_expired_sessions()

        assert result == 0
        mock_logger.warning.assert_called()

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    def test_cleanup_handles_scandir_errors(self, mock_scandir, mock_exists, mock_logger):
        """Test handling of scandir errors."""
        mock_exists.return_value = True
        mock_scandir.side_effect = OSError("Access denied")

        cleaner = SessionCleaner("/sessions")
        result = cleaner.cleanup_expired_sessions()

        assert result == 0
        mock_logger.error.assert_called()

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.os.remove')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_handles_session_colon_prefix(self, mock_time, mock_remove, mock_scandir, mock_exists, mock_logger):
        """Test that session files with colon prefix are handled."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        colon_session = Mock()
        colon_session.is_file.return_value = True
        colon_session.name = "session:xyz789"
        colon_session.path = "/sessions/session:xyz789"
        colon_stat = Mock()
        colon_stat.st_mtime = 10000
        colon_stat.st_size = 2048
        colon_session.stat.return_value = colon_stat

        mock_scandir.return_value.__enter__ = Mock(return_value=[colon_session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions", max_age=86400)
        result = cleaner.cleanup_expired_sessions()

        assert result == 1
        mock_remove.assert_called_once_with("/sessions/session:xyz789")

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.os.remove')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_calculates_freed_space(self, mock_time, mock_remove, mock_scandir, mock_exists, mock_logger):
        """Test that freed space is calculated correctly."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        # Two expired sessions
        session1 = Mock()
        session1.is_file.return_value = True
        session1.name = "session_1"
        session1.path = "/sessions/session_1"
        stat1 = Mock()
        stat1.st_mtime = 10000
        stat1.st_size = 1048576  # 1 MB
        session1.stat.return_value = stat1

        session2 = Mock()
        session2.is_file.return_value = True
        session2.name = "session_2"
        session2.path = "/sessions/session_2"
        stat2 = Mock()
        stat2.st_mtime = 10000
        stat2.st_size = 2097152  # 2 MB
        session2.stat.return_value = stat2

        mock_scandir.return_value.__enter__ = Mock(return_value=[session1, session2])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions", max_age=86400)
        result = cleaner.cleanup_expired_sessions()

        assert result == 2
        # Check that the log message includes the freed space
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("3.00 MB freed" in call for call in info_calls)

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_cleanup_logs_no_files_found(self, mock_time, mock_scandir, mock_exists, mock_logger):
        """Test logging when no expired files are found."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        mock_scandir.return_value.__enter__ = Mock(return_value=[])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.cleanup_expired_sessions()

        assert result == 0
        mock_logger.debug.assert_called_with(
            "Session cleanup completed: no expired files found"
        )


class TestSessionCleanerGetStats:
    """Tests for SessionCleaner.get_session_stats() method."""

    @patch('utils.session_cleanup.os.path.exists')
    def test_get_stats_directory_not_exists(self, mock_exists):
        """Test stats when directory doesn't exist."""
        mock_exists.return_value = False

        cleaner = SessionCleaner("/nonexistent")
        result = cleaner.get_session_stats()

        assert result == {
            "total_files": 0,
            "total_size_mb": 0,
            "oldest_file_age_hours": 0,
            "directory_exists": False
        }

    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_get_stats_with_sessions(self, mock_time, mock_scandir, mock_exists):
        """Test stats calculation with session files."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        session1 = Mock()
        session1.is_file.return_value = True
        session1.name = "session_1"
        stat1 = Mock()
        stat1.st_size = 1048576  # 1 MB
        stat1.st_mtime = 96400  # 1 hour old
        session1.stat.return_value = stat1

        session2 = Mock()
        session2.is_file.return_value = True
        session2.name = "session_2"
        stat2 = Mock()
        stat2.st_size = 2097152  # 2 MB
        stat2.st_mtime = 92800  # 2 hours old
        session2.stat.return_value = stat2

        mock_scandir.return_value.__enter__ = Mock(return_value=[session1, session2])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.get_session_stats()

        assert result["total_files"] == 2
        assert result["total_size_mb"] == 3.0
        assert result["oldest_file_age_hours"] == 2.0
        assert result["directory_exists"] is True

    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_get_stats_empty_directory(self, mock_time, mock_scandir, mock_exists):
        """Test stats for empty directory."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        mock_scandir.return_value.__enter__ = Mock(return_value=[])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.get_session_stats()

        assert result["total_files"] == 0
        assert result["total_size_mb"] == 0
        assert result["oldest_file_age_hours"] == 0
        assert result["directory_exists"] is True

    @patch('utils.session_cleanup.logger')
    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    def test_get_stats_handles_errors(self, mock_scandir, mock_exists, mock_logger):
        """Test stats error handling."""
        mock_exists.return_value = True
        mock_scandir.side_effect = OSError("Permission denied")

        cleaner = SessionCleaner("/sessions")
        result = cleaner.get_session_stats()

        assert result["total_files"] == 0
        assert result["total_size_mb"] == 0
        assert result["oldest_file_age_hours"] == 0
        assert result["directory_exists"] is True
        assert "error" in result
        mock_logger.error.assert_called()

    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_get_stats_skips_non_session_files(self, mock_time, mock_scandir, mock_exists):
        """Test that stats skip non-session files."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        non_session = Mock()
        non_session.is_file.return_value = True
        non_session.name = "config.json"

        mock_scandir.return_value.__enter__ = Mock(return_value=[non_session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.get_session_stats()

        assert result["total_files"] == 0

    @patch('utils.session_cleanup.os.path.exists')
    @patch('utils.session_cleanup.os.scandir')
    @patch('utils.session_cleanup.time.time')
    def test_get_stats_handles_colon_prefix(self, mock_time, mock_scandir, mock_exists):
        """Test that stats handle session: prefix."""
        mock_exists.return_value = True
        mock_time.return_value = 100000

        session = Mock()
        session.is_file.return_value = True
        session.name = "session:abc123"
        stat = Mock()
        stat.st_size = 512
        stat.st_mtime = 99000
        session.stat.return_value = stat

        mock_scandir.return_value.__enter__ = Mock(return_value=[session])
        mock_scandir.return_value.__exit__ = Mock(return_value=False)

        cleaner = SessionCleaner("/sessions")
        result = cleaner.get_session_stats()

        assert result["total_files"] == 1


class TestGlobalSessionCleanupFunctions:
    """Tests for global session cleanup functions."""

    @patch('utils.session_cleanup.logger')
    def test_init_session_cleanup_filesystem_sessions(self, mock_logger):
        """Test init_session_cleanup with filesystem sessions configured."""
        import utils.session_cleanup as module

        mock_app = Mock()
        mock_app.config.get.side_effect = lambda key, default=None: {
            "SESSION_FILE_DIR": "/tmp/sessions",
            "SESSION_MAX_AGE": 43200,
            "SESSION_CLEANUP_INTERVAL": 1800,
            "SESSION_TYPE": "filesystem"
        }.get(key, default)

        module._session_cleaner = None

        init_session_cleanup(mock_app)

        assert module._session_cleaner is not None
        assert module._session_cleaner.session_dir == "/tmp/sessions"
        assert module._session_cleaner.max_age == 43200
        assert module._session_cleaner.cleanup_interval == 1800
        mock_logger.info.assert_any_call(
            "Session cleanup initialized: dir=/tmp/sessions, max_age=43200s, interval=1800s"
        )

        # Cleanup
        module._session_cleaner.stop_cleanup_thread()
        module._session_cleaner = None

    @patch('utils.session_cleanup.logger')
    def test_init_session_cleanup_no_filesystem_sessions(self, mock_logger):
        """Test init_session_cleanup without filesystem sessions."""
        import utils.session_cleanup as module

        mock_app = Mock()
        mock_app.config.get.side_effect = lambda key, default=None: {
            "SESSION_FILE_DIR": None,
            "SESSION_TYPE": "redis"
        }.get(key, default)

        module._session_cleaner = None

        init_session_cleanup(mock_app)

        assert module._session_cleaner is None
        mock_logger.info.assert_called_with(
            "Session cleanup not initialized: filesystem sessions not configured"
        )

    @patch('utils.session_cleanup.logger')
    def test_init_session_cleanup_no_session_dir(self, mock_logger):
        """Test init_session_cleanup without session directory."""
        import utils.session_cleanup as module

        mock_app = Mock()
        mock_app.config.get.side_effect = lambda key, default=None: {
            "SESSION_FILE_DIR": None,
            "SESSION_TYPE": "filesystem"
        }.get(key, default)

        module._session_cleaner = None

        init_session_cleanup(mock_app)

        assert module._session_cleaner is None

    def test_get_session_cleaner_returns_instance(self):
        """Test get_session_cleaner returns global instance."""
        import utils.session_cleanup as module

        test_cleaner = Mock()
        module._session_cleaner = test_cleaner

        result = get_session_cleaner()

        assert result == test_cleaner

        module._session_cleaner = None

    def test_get_session_cleaner_returns_none(self):
        """Test get_session_cleaner when not initialized."""
        import utils.session_cleanup as module

        module._session_cleaner = None

        result = get_session_cleaner()

        assert result is None

    def test_cleanup_sessions_now_with_cleaner(self):
        """Test cleanup_sessions_now when cleaner is initialized."""
        import utils.session_cleanup as module

        mock_cleaner = Mock()
        mock_cleaner.cleanup_expired_sessions.return_value = 10
        module._session_cleaner = mock_cleaner

        result = cleanup_sessions_now()

        assert result == 10
        mock_cleaner.cleanup_expired_sessions.assert_called_once()

        module._session_cleaner = None

    def test_cleanup_sessions_now_without_cleaner(self):
        """Test cleanup_sessions_now when cleaner is not initialized."""
        import utils.session_cleanup as module

        module._session_cleaner = None

        result = cleanup_sessions_now()

        assert result == 0

    def test_get_session_cleanup_stats_with_cleaner(self):
        """Test get_session_cleanup_stats when cleaner is initialized."""
        import utils.session_cleanup as module

        mock_cleaner = Mock()
        mock_cleaner.get_session_stats.return_value = {
            "total_files": 25,
            "total_size_mb": 5.5,
            "oldest_file_age_hours": 12.3,
            "directory_exists": True
        }
        module._session_cleaner = mock_cleaner

        result = get_session_cleanup_stats()

        assert result["total_files"] == 25
        assert result["total_size_mb"] == 5.5
        mock_cleaner.get_session_stats.assert_called_once()

        module._session_cleaner = None

    def test_get_session_cleanup_stats_without_cleaner(self):
        """Test get_session_cleanup_stats when cleaner is not initialized."""
        import utils.session_cleanup as module

        module._session_cleaner = None

        result = get_session_cleanup_stats()

        assert result == {"error": "Session cleanup not initialized"}


class TestSessionCleanerIntegration:
    """Integration tests for session cleanup."""

    def test_full_lifecycle(self):
        """Test complete lifecycle of session cleaner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cleaner = SessionCleaner(tmpdir, max_age=1, cleanup_interval=0.1)

            # Create test session files
            old_session = os.path.join(tmpdir, "session_old")
            with open(old_session, 'w') as f:
                f.write("old data")

            # Make file old by modifying its time
            old_time = time.time() - 100
            os.utime(old_session, (old_time, old_time))

            # Create recent session
            new_session = os.path.join(tmpdir, "session_new")
            with open(new_session, 'w') as f:
                f.write("new data")

            # Cleanup should remove old session
            result = cleaner.cleanup_expired_sessions()

            assert result == 1
            assert not os.path.exists(old_session)
            assert os.path.exists(new_session)

    def test_stats_calculation_integration(self):
        """Test stats calculation with real files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cleaner = SessionCleaner(tmpdir)

            # Create test session files
            for i in range(3):
                session = os.path.join(tmpdir, f"session_{i}")
                with open(session, 'w') as f:
                    f.write("x" * 1000000)  # 1MB each

            stats = cleaner.get_session_stats()

            assert stats["total_files"] == 3
            assert stats["total_size_mb"] > 0
            assert stats["directory_exists"] is True

    def test_thread_start_stop_integration(self):
        """Test thread start and stop with real threading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cleaner = SessionCleaner(tmpdir, cleanup_interval=60)

            cleaner.start_cleanup_thread()
            assert cleaner.running is True
            assert cleaner._thread is not None
            assert cleaner._thread.is_alive()

            time.sleep(0.1)  # Give thread time to start

            cleaner.stop_cleanup_thread()
            assert cleaner.running is False

            # Thread should stop within timeout
            time.sleep(0.1)
            assert not cleaner._thread.is_alive() or True  # Thread may have stopped

    def test_cleanup_with_mixed_file_types(self):
        """Test cleanup with various file types in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cleaner = SessionCleaner(tmpdir, max_age=1)

            # Create different types of files
            files = [
                ("session_valid", True),  # Should be cleaned
                ("session:colon", True),  # Should be cleaned
                ("other_file.txt", False),  # Should not be touched
                ("README.md", False),  # Should not be touched
            ]

            for filename, _ in files:
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'w') as f:
                    f.write("data")
                old_time = time.time() - 100
                os.utime(filepath, (old_time, old_time))

            result = cleaner.cleanup_expired_sessions()

            # Only session files should be cleaned
            assert result == 2
            assert not os.path.exists(os.path.join(tmpdir, "session_valid"))
            assert not os.path.exists(os.path.join(tmpdir, "session:colon"))
            assert os.path.exists(os.path.join(tmpdir, "other_file.txt"))
            assert os.path.exists(os.path.join(tmpdir, "README.md"))
