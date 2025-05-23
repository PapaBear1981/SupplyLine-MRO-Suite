"""
Session Cleanup Utility

This module provides automatic cleanup of expired session files to prevent
disk space exhaustion and maintain system performance.
"""

import os
import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)


class SessionCleaner:
    """
    Automatic session file cleanup manager.

    This class runs a background thread that periodically cleans up
    expired session files to prevent disk space issues.
    """

    def __init__(self, session_dir, max_age=86400, cleanup_interval=3600):
        """
        Initialize the session cleaner.

        Args:
            session_dir (str): Directory containing session files
            max_age (int): Maximum age of session files in seconds (default: 24 hours)
            cleanup_interval (int): Time between cleanup runs in seconds (default: 1 hour)
        """
        self.session_dir = session_dir
        self.max_age = max_age
        self.cleanup_interval = cleanup_interval
        self.running = False
        self._thread = None

    def start_cleanup_thread(self):
        """Start the background cleanup thread."""
        if not self.running:
            self.running = True
            self._thread = Thread(target=self._cleanup_loop, daemon=True)
            self._thread.start()
            logger.info(f"Session cleanup thread started for directory: {self.session_dir}")

    def stop_cleanup_thread(self):
        """Stop the background cleanup thread."""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Session cleanup thread stopped")

    def _cleanup_loop(self):
        """Main cleanup loop that runs in the background thread."""
        while self.running:
            try:
                self.cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"Session cleanup error: {e}", exc_info=True)

            # Sleep for the cleanup interval
            time.sleep(self.cleanup_interval)

    def cleanup_expired_sessions(self):
        """
        Clean up expired session files.

        Returns:
            int: Number of files cleaned up
        """
        if not os.path.exists(self.session_dir):
            logger.warning(f"Session directory does not exist: {self.session_dir}")
            return 0

        now = time.time()
        cleaned = 0
        total_size_freed = 0

        try:
            with os.scandir(self.session_dir) as entries:
                for entry in entries:
                    # Skip directories and non-session files
                    if (
                        not entry.is_file()
                        or not (entry.name.startswith("session_") or entry.name.startswith("session:"))
                    ):
                        continue

                    try:
                        # Check file age using cached stat info
                        file_age = now - entry.stat().st_mtime
                        if file_age > self.max_age:
                            # Get file size before deletion
                            file_size = entry.stat().st_size
                            os.remove(entry.path)
                            cleaned += 1
                            total_size_freed += file_size

                            logger.debug(f"Removed expired session file: {entry.name} (age: {file_age:.0f}s)")

                    except OSError as e:
                        logger.warning(f"Could not remove session file {entry.name}: {e}")
                        continue

        except OSError as e:
            logger.error(f"Error accessing session directory {self.session_dir}: {e}")
            return 0

        if cleaned > 0:
            size_mb = total_size_freed / (1024 * 1024)
            logger.info(f"Session cleanup completed: {cleaned} files removed, {size_mb:.2f} MB freed")
        else:
            logger.debug("Session cleanup completed: no expired files found")

        return cleaned

    def get_session_stats(self):
        """
        Get statistics about session files.

        Returns:
            dict: Statistics including file count, total size, oldest file age
        """
        if not os.path.exists(self.session_dir):
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'oldest_file_age_hours': 0,
                'directory_exists': False
            }

        now = time.time()
        total_files = 0
        total_size = 0
        oldest_age = 0

        try:
            with os.scandir(self.session_dir) as entries:
                for entry in entries:
                    if entry.is_file() and (entry.name.startswith('session_') or entry.name.startswith('session:')):
                        total_files += 1
                        stat_info = entry.stat()
                        total_size += stat_info.st_size

                        file_age = now - stat_info.st_mtime
                        oldest_age = max(oldest_age, file_age)

        except OSError as e:
            logger.error(f"Error getting session stats: {e}")
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'oldest_file_age_hours': 0,
                'directory_exists': True,
                'error': str(e)
            }

        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_file_age_hours': round(oldest_age / 3600, 1),
            'directory_exists': True
        }


# Global session cleaner instance
_session_cleaner = None


def init_session_cleanup(app):
    """
    Initialize session cleanup for the Flask application.

    Args:
        app: Flask application instance
    """
    global _session_cleaner

    session_dir = app.config.get('SESSION_FILE_DIR')
    max_age = app.config.get('SESSION_MAX_AGE', 86400)
    cleanup_interval = app.config.get('SESSION_CLEANUP_INTERVAL', 3600)

    if session_dir and app.config.get('SESSION_TYPE') == 'filesystem':
        _session_cleaner = SessionCleaner(session_dir, max_age, cleanup_interval)
        _session_cleaner.start_cleanup_thread()

        logger.info(f"Session cleanup initialized: dir={session_dir}, max_age={max_age}s, interval={cleanup_interval}s")
    else:
        logger.info("Session cleanup not initialized: filesystem sessions not configured")


def get_session_cleaner():
    """Get the global session cleaner instance."""
    return _session_cleaner


def cleanup_sessions_now():
    """Manually trigger session cleanup."""
    if _session_cleaner:
        return _session_cleaner.cleanup_expired_sessions()
    return 0


def get_session_cleanup_stats():
    """Get session cleanup statistics."""
    if _session_cleaner:
        return _session_cleaner.get_session_stats()
    return {'error': 'Session cleanup not initialized'}
