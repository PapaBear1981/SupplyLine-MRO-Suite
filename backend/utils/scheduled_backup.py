"""
Scheduled Database Backup Service

Provides automatic periodic backups of the database.
Runs in a background thread to avoid blocking the main application.
"""

import threading
import time
import logging
import os
from datetime import datetime, timedelta
from utils.database_backup import DatabaseBackupManager

logger = logging.getLogger(__name__)


class ScheduledBackupService:
    """Service for running automatic database backups on a schedule."""
    
    def __init__(self, app):
        """
        Initialize the scheduled backup service.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.backup_thread = None
        self.stop_event = threading.Event()
        
        # Configuration from environment variables
        self.enabled = os.environ.get('AUTO_BACKUP_ENABLED', 'true').lower() == 'true'
        self.interval_hours = int(os.environ.get('AUTO_BACKUP_INTERVAL_HOURS', '24'))
        self.backup_on_startup = os.environ.get('BACKUP_ON_STARTUP', 'true').lower() == 'true'
        
        # Get database path from app config
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            self.db_path = db_uri.replace('sqlite:///', '')
            self.backup_manager = DatabaseBackupManager(self.db_path)
        else:
            self.db_path = None
            self.backup_manager = None
            logger.warning("Scheduled backups are only supported for SQLite databases")
    
    def start(self):
        """Start the scheduled backup service."""
        if not self.enabled:
            logger.info("Scheduled backups are disabled")
            return
        
        if not self.backup_manager:
            logger.warning("Cannot start scheduled backups: database is not SQLite")
            return
        
        if self.backup_thread and self.backup_thread.is_alive():
            logger.warning("Scheduled backup service is already running")
            return
        
        logger.info(f"Starting scheduled backup service (interval: {self.interval_hours} hours)")
        
        self.stop_event.clear()
        self.backup_thread = threading.Thread(
            target=self._backup_loop,
            daemon=True,
            name="ScheduledBackupThread"
        )
        self.backup_thread.start()
    
    def stop(self):
        """Stop the scheduled backup service."""
        if not self.backup_thread or not self.backup_thread.is_alive():
            return
        
        logger.info("Stopping scheduled backup service...")
        self.stop_event.set()
        
        # Wait for thread to finish (with timeout)
        self.backup_thread.join(timeout=10)
        
        if self.backup_thread.is_alive():
            logger.warning("Scheduled backup thread did not stop gracefully")
        else:
            logger.info("Scheduled backup service stopped")
    
    def _backup_loop(self):
        """Main loop for scheduled backups."""
        try:
            # Create initial backup on startup if enabled
            if self.backup_on_startup:
                logger.info("Creating startup backup...")
                with self.app.app_context():
                    self._create_backup("startup")
            
            # Main backup loop
            while not self.stop_event.is_set():
                # Calculate next backup time
                next_backup = datetime.now() + timedelta(hours=self.interval_hours)
                logger.info(f"Next scheduled backup at: {next_backup.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Wait for the interval (or until stop event is set)
                if self.stop_event.wait(timeout=self.interval_hours * 3600):
                    # Stop event was set
                    break
                
                # Create scheduled backup
                with self.app.app_context():
                    self._create_backup("scheduled")
        
        except Exception as e:
            logger.error(f"Error in scheduled backup loop: {e}", exc_info=True)
    
    def _create_backup(self, backup_type: str):
        """
        Create a backup with the specified type.
        
        Args:
            backup_type: Type of backup (startup, scheduled, etc.)
        """
        try:
            success, message, backup_path = self.backup_manager.create_backup(
                backup_name=backup_type
            )
            
            if success:
                logger.info(f"Scheduled backup created successfully: {backup_path}")
            else:
                logger.error(f"Scheduled backup failed: {message}")
        
        except Exception as e:
            logger.error(f"Error creating scheduled backup: {e}", exc_info=True)
    
    def create_manual_backup(self):
        """Create a manual backup immediately (for testing or admin use)."""
        if not self.backup_manager:
            return False, "Backup manager not available"
        
        with self.app.app_context():
            return self.backup_manager.create_backup(backup_name="manual")


# Global instance
_backup_service = None


def init_scheduled_backup(app):
    """
    Initialize and start the scheduled backup service.
    
    Args:
        app: Flask application instance
    """
    global _backup_service
    
    if _backup_service is None:
        _backup_service = ScheduledBackupService(app)
        _backup_service.start()
    
    return _backup_service


def get_backup_service():
    """Get the global backup service instance."""
    return _backup_service


def shutdown_scheduled_backup():
    """Shutdown the scheduled backup service."""
    global _backup_service
    
    if _backup_service:
        _backup_service.stop()
        _backup_service = None

