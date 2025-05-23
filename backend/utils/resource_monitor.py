"""
Resource Monitoring Utility

This module provides system resource monitoring to detect memory leaks,
high resource usage, and potential performance issues.
"""

import psutil
import threading
import time
import logging
import os

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """
    System resource monitoring manager.

    This class monitors system resources and logs warnings when
    thresholds are exceeded.
    """

    def __init__(self, check_interval=60, thresholds=None):
        """
        Initialize the resource monitor.

        Args:
            check_interval (int): Time between checks in seconds (default: 60)
            thresholds (dict): Resource thresholds for warnings
        """
        self.check_interval = check_interval
        self.running = False
        self._thread = None

        # Default thresholds
        self.thresholds = {
            'memory_percent': 80,
            'disk_percent': 85,
            'open_files': 1000,
            'db_connections': 8
        }

        if thresholds:
            self.thresholds.update(thresholds)

    def start_monitoring(self):
        """Start the background monitoring thread."""
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info(f"Resource monitoring started with interval: {self.check_interval}s")

    def stop_monitoring(self):
        """Stop the background monitoring thread."""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Resource monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop that runs in the background thread."""
        while self.running:
            try:
                self._check_resources()
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}", exc_info=True)

            time.sleep(self.check_interval)

    def _check_resources(self):
        """Check all system resources and log warnings if thresholds exceeded."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds['memory_percent']:
                logger.warning("High memory usage detected", extra={
                    'metric_type': 'memory_usage',
                    'current_percent': memory.percent,
                    'threshold_percent': self.thresholds['memory_percent'],
                    'available_mb': round(memory.available / (1024 * 1024), 1),
                    'total_mb': round(memory.total / (1024 * 1024), 1)
                })

            # Disk usage (use appropriate path for OS)
            disk_path = 'C:' if os.name == 'nt' else '/'
            disk = psutil.disk_usage(disk_path)
            if disk.percent > self.thresholds['disk_percent']:
                logger.warning("High disk usage detected", extra={
                    'metric_type': 'disk_usage',
                    'current_percent': disk.percent,
                    'threshold_percent': self.thresholds['disk_percent'],
                    'free_gb': round(disk.free / (1024 * 1024 * 1024), 1),
                    'total_gb': round(disk.total / (1024 * 1024 * 1024), 1)
                })

            # Open files
            try:
                process = psutil.Process()
                open_files = len(process.open_files())
                if open_files > self.thresholds['open_files']:
                    logger.warning("High open file count detected", extra={
                        'metric_type': 'open_files',
                        'current_count': open_files,
                        'threshold_count': self.thresholds['open_files'],
                        'process_pid': process.pid
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Database connection pool usage
            try:
                from .database_utils import get_connection_stats
                conn_stats = get_connection_stats()
                if (
                    isinstance(conn_stats, dict)
                    and conn_stats.get("checked_out", 0) > self.thresholds["db_connections"]
                ):
                    logger.warning(
                        "High database connection usage detected",
                        extra={
                            "metric_type": "db_connections",
                            "checked_out": conn_stats.get("checked_out"),
                            "threshold": self.thresholds["db_connections"],
                        },
                    )
            except ImportError:
                # database_utils not available
                pass
            except Exception as e:
                logger.debug(f"Could not check database connections: {e}")

            # Log periodic resource stats (debug level)
            logger.debug("Resource check completed", extra={
                'metric_type': 'resource_check',
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'cpu_percent': psutil.cpu_percent(interval=1)
            })

        except Exception as e:
            logger.error(f"Error checking resources: {e}", exc_info=True)

    def get_current_stats(self):
        """
        Get current resource statistics.

        Returns:
            dict: Current resource usage statistics
        """
        try:
            # Memory
            memory = psutil.virtual_memory()

            # Disk (use appropriate path for OS)
            disk_path = 'C:' if os.name == 'nt' else '/'
            disk = psutil.disk_usage(disk_path)

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Process info
            process = psutil.Process()
            open_files_count = len(process.open_files())

            # Network connections
            try:
                connections = len(psutil.net_connections())
            except (psutil.AccessDenied, OSError):
                connections = -1  # Indicate unavailable

            return {
                'memory': {
                    'percent': memory.percent,
                    'available_mb': round(memory.available / (1024 * 1024), 1),
                    'total_mb': round(memory.total / (1024 * 1024), 1),
                    'used_mb': round(memory.used / (1024 * 1024), 1)
                },
                'disk': {
                    'percent': disk.percent,
                    'free_gb': round(disk.free / (1024 * 1024 * 1024), 1),
                    'total_gb': round(disk.total / (1024 * 1024 * 1024), 1),
                    'used_gb': round(disk.used / (1024 * 1024 * 1024), 1)
                },
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'process': {
                    'open_files': open_files_count,
                    'connections': connections,
                    'pid': process.pid
                },
                'thresholds': self.thresholds,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"Error getting resource stats: {e}", exc_info=True)
            return {
                'error': str(e),
                'timestamp': time.time()
            }

    def check_health(self):
        """
        Check if system is healthy based on thresholds.

        Returns:
            dict: Health status and any issues
        """
        stats = self.get_current_stats()

        if 'error' in stats:
            return {
                'healthy': False,
                'issues': [f"Error getting stats: {stats['error']}"]
            }

        issues = []

        # Check memory
        if stats['memory']['percent'] > self.thresholds['memory_percent']:
            issues.append(f"High memory usage: {stats['memory']['percent']}%")

        # Check disk
        if stats['disk']['percent'] > self.thresholds['disk_percent']:
            issues.append(f"High disk usage: {stats['disk']['percent']}%")

        # Check open files
        if stats['process']['open_files'] > self.thresholds['open_files']:
            issues.append(f"High open file count: {stats['process']['open_files']}")

        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'stats': stats
        }


# Global resource monitor instance
_resource_monitor = None


def init_resource_monitoring(app):
    """
    Initialize resource monitoring for the Flask application.

    Args:
        app: Flask application instance
    """
    global _resource_monitor

    check_interval = app.config.get('RESOURCE_CHECK_INTERVAL', 60)
    thresholds = app.config.get('RESOURCE_THRESHOLDS', {})

    _resource_monitor = ResourceMonitor(check_interval, thresholds)
    _resource_monitor.start_monitoring()

    logger.info(f"Resource monitoring initialized with thresholds: {thresholds}")


def get_resource_monitor():
    """Get the global resource monitor instance."""
    return _resource_monitor


def get_resource_stats():
    """Get current resource statistics."""
    if _resource_monitor:
        return _resource_monitor.get_current_stats()
    return {'error': 'Resource monitoring not initialized'}


def check_system_health():
    """Check system health status."""
    if _resource_monitor:
        return _resource_monitor.check_health()
    return {'healthy': False, 'issues': ['Resource monitoring not initialized']}
