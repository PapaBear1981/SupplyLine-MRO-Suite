"""
Scheduled Maintenance Service

Provides automatic periodic maintenance tasks for the database.
Runs in a background thread to avoid blocking the main application.
"""

import logging
import os
import threading
from datetime import datetime, timedelta

from utils.bulk_operations import bulk_update_chemical_status, bulk_update_tool_calibration_status


logger = logging.getLogger(__name__)


class ScheduledMaintenanceService:
    """Service for running automatic database maintenance tasks on a schedule."""

    def __init__(self, app):
        """
        Initialize the scheduled maintenance service.

        Args:
            app: Flask application instance
        """
        self.app = app
        self.maintenance_thread = None
        self.stop_event = threading.Event()

        # Configuration from environment variables
        self.enabled = os.environ.get("AUTO_MAINTENANCE_ENABLED", "true").lower() == "true"
        # Default to 1 hour interval for maintenance tasks
        self.interval_hours = int(os.environ.get("AUTO_MAINTENANCE_INTERVAL_HOURS", "1"))
        self.run_on_startup = os.environ.get("MAINTENANCE_ON_STARTUP", "true").lower() == "true"

    def start(self):
        """Start the scheduled maintenance service."""
        if not self.enabled:
            logger.info("Scheduled maintenance is disabled")
            return

        if self.maintenance_thread and self.maintenance_thread.is_alive():
            logger.warning("Scheduled maintenance service is already running")
            return

        logger.info(f"Starting scheduled maintenance service (interval: {self.interval_hours} hours)")

        self.stop_event.clear()
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True,
            name="ScheduledMaintenanceThread"
        )
        self.maintenance_thread.start()

    def stop(self):
        """Stop the scheduled maintenance service."""
        if not self.maintenance_thread or not self.maintenance_thread.is_alive():
            return

        logger.info("Stopping scheduled maintenance service...")
        self.stop_event.set()

        # Wait for thread to finish (with timeout)
        self.maintenance_thread.join(timeout=10)

        if self.maintenance_thread.is_alive():
            logger.warning("Scheduled maintenance thread did not stop gracefully")
        else:
            logger.info("Scheduled maintenance service stopped")

    def _maintenance_loop(self):
        """Main loop for scheduled maintenance."""
        try:
            # Run initial maintenance on startup if enabled
            if self.run_on_startup:
                logger.info("Running startup maintenance tasks...")
                with self.app.app_context():
                    self._run_maintenance_tasks()

            # Main maintenance loop
            while not self.stop_event.is_set():
                # Calculate next maintenance time
                next_maintenance = datetime.now() + timedelta(hours=self.interval_hours)
                logger.info(f"Next scheduled maintenance at: {next_maintenance.strftime('%Y-%m-%d %H:%M:%S')}")

                # Wait for the interval (or until stop event is set)
                if self.stop_event.wait(timeout=self.interval_hours * 3600):
                    # Stop event was set
                    break

                # Run scheduled maintenance
                with self.app.app_context():
                    self._run_maintenance_tasks()

        except Exception as e:
            logger.error("Error in maintenance loop", exc_info=True, extra={
                "error_message": str(e)
            })

    def _run_maintenance_tasks(self):
        """Run all maintenance tasks."""
        try:
            from models import db

            logger.info("Starting maintenance tasks...")

            # Update tool calibration statuses
            try:
                logger.info("Updating tool calibration statuses...")
                calibration_results = bulk_update_tool_calibration_status()
                logger.info("Tool calibration status update complete", extra={
                    "overdue_count": calibration_results.get("overdue", 0),
                    "due_soon_count": calibration_results.get("due_soon", 0),
                    "current_count": calibration_results.get("current", 0)
                })
            except Exception as e:
                logger.error("Error updating tool calibration statuses", exc_info=True, extra={
                    "error_message": str(e)
                })

            # Update chemical statuses
            try:
                logger.info("Updating chemical statuses...")
                chemical_results = bulk_update_chemical_status()
                logger.info("Chemical status update complete", extra={
                    "expired_count": chemical_results.get("expired", 0),
                    "expiring_soon_count": chemical_results.get("expiring_soon", 0),
                    "current_count": chemical_results.get("current", 0)
                })
            except Exception as e:
                logger.error("Error updating chemical statuses", exc_info=True, extra={
                    "error_message": str(e)
                })

            # Commit all changes
            try:
                db.session.commit()
                logger.info("Maintenance tasks completed successfully")
            except Exception as e:
                logger.error("Error committing maintenance changes", exc_info=True, extra={
                    "error_message": str(e)
                })
                db.session.rollback()

        except Exception as e:
            logger.error("Error running maintenance tasks", exc_info=True, extra={
                "error_message": str(e)
            })

    def run_manual_maintenance(self):
        """Run maintenance tasks immediately (for testing or admin use)."""
        logger.info("Running manual maintenance tasks...")
        with self.app.app_context():
            self._run_maintenance_tasks()
        return True


# Global instance
_maintenance_service = None


def init_scheduled_maintenance(app):
    """
    Initialize and start the scheduled maintenance service.

    Args:
        app: Flask application instance
    """
    global _maintenance_service

    if _maintenance_service is None:
        _maintenance_service = ScheduledMaintenanceService(app)
        _maintenance_service.start()

    return _maintenance_service


def shutdown_scheduled_maintenance():
    """Shutdown the scheduled maintenance service."""
    global _maintenance_service

    if _maintenance_service:
        _maintenance_service.stop()
        _maintenance_service = None


def get_maintenance_service():
    """Get the global maintenance service instance."""
    return _maintenance_service

