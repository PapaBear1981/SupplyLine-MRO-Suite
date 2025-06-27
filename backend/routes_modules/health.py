"""
Health and System Monitoring Routes for SupplyLine MRO Suite

This module provides endpoints for:
- Health checks for Docker/container monitoring
- Time API endpoints for debugging time functionality
- System resource monitoring (CPU, memory, disk usage)
"""

import os
import time
import logging
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from models import db, User, Tool, Checkout, AuditLog, UserActivity
from auth import admin_required
from utils.error_handler import handle_errors

logger = logging.getLogger(__name__)


def register_health_routes(app):
    """Register health and system monitoring routes"""

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Docker and monitoring systems"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'timezone': str(time.tzname)
        })

    @app.route('/api/time', methods=['GET'])
    def time_api_endpoint():
        """
        Time API endpoint that returns current time information.

        Returns:
            JSON response containing:
            - status: 'ok' if successful
            - utc_time: Current UTC time in ISO 8601 format
            - local_time: Current local time in ISO 8601 format
            - timezone: System timezone information
            - using_time_utils: Boolean indicating if time utilities are being used
        """
        print("Time API endpoint called!")  # Debug log
        try:
            from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
            result = {
                'status': 'ok',
                'utc_time': format_datetime(get_utc_timestamp()),
                'local_time': format_datetime(get_local_timestamp()),
                'timezone': str(time.tzname),
                'using_time_utils': True
            }
            print(f"Time API endpoint returning: {result}")  # Debug log
            return jsonify(result)
        except ImportError as e:
            print(f"Error importing time_utils in time_api_endpoint: {str(e)}")
            result = {
                'status': 'ok',
                'utc_time': datetime.now(timezone.utc).isoformat(),
                'local_time': datetime.now().isoformat(),
                'timezone': str(time.tzname),
                'using_time_utils': False
            }
            print(f"Time API endpoint fallback returning: {result}")  # Debug log
            return jsonify(result)

    @app.route('/api/time-test', methods=['GET'])
    def time_test_endpoint():
        """Time test endpoint for debugging time functionality."""
        print("Time test endpoint called!")  # Debug log
        try:
            from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
            result = {
                'status': 'ok',
                'message': 'Time test endpoint working',
                'utc_time': format_datetime(get_utc_timestamp()),
                'local_time': format_datetime(get_local_timestamp()),
                'timezone': str(time.tzname),
                'using_time_utils': True,
                'timestamp': datetime.now().isoformat()
            }
            print(f"Time test endpoint returning: {result}")  # Debug log
            return jsonify(result)
        except ImportError as e:
            print(f"Error importing time_utils in time_test_endpoint: {str(e)}")
            result = {
                'status': 'ok',
                'message': 'Time test endpoint working (fallback)',
                'utc_time': datetime.now(timezone.utc).isoformat(),
                'local_time': datetime.now().isoformat(),
                'timezone': str(time.tzname),
                'using_time_utils': False,
                'timestamp': datetime.now().isoformat()
            }
            print(f"Time test endpoint fallback returning: {result}")  # Debug log
            return jsonify(result)

    @app.route('/api/admin/system-resources', methods=['GET'])
    @admin_required
    @handle_errors
    def get_system_resources():
        """Get real-time system resource usage statistics"""
        logger.info("System resources endpoint called")

        # Get database size (approximate based on number of records)
        db_size_mb = 0
        total_records = 0  # Initialize to prevent UnboundLocalError if the try block fails
        try:
            # Count records in major tables to estimate size
            user_count = User.query.count()
            tool_count = Tool.query.count()
            checkout_count = Checkout.query.count()
            log_count = AuditLog.query.count()

            # Rough estimate: 2KB per record on average
            total_records = user_count + tool_count + checkout_count + log_count
            db_size_mb = (total_records * 2) / 1024  # Convert KB to MB
        except Exception as e:
            logger.error(f"Error estimating database size: {str(e)}")
            db_size_mb = 10  # Default fallback value
            total_records = 0  # Ensure it's defined in case of exception

        # Get active user sessions (approximate based on recent activity)
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)

        # Count users with activity in the last 5 minutes
        active_sessions = UserActivity.query.filter(
            UserActivity.timestamp >= five_minutes_ago
        ).distinct(UserActivity.user_id).count()

        # Try to import psutil for real system metrics
        try:
            logger.info("Attempting to import psutil module...")
            import psutil
            logger.info("Successfully imported psutil module")

            # Get CPU usage - use instantaneous value to avoid blocking
            logger.debug("Getting CPU usage...")
            cpu_usage = psutil.cpu_percent(interval=None)
            logger.debug(f"CPU usage: {cpu_usage}")

            logger.debug("Getting CPU cores...")
            cpu_cores = psutil.cpu_count()
            logger.debug(f"CPU cores: {cpu_cores}")

            # Get memory usage
            logger.debug("Getting memory usage...")
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            logger.debug(f"Memory usage: {memory_usage}")
            memory_total_gb = round(memory.total / (1024**3), 1)
            logger.debug(f"Memory total: {memory_total_gb} GB")

            # Get disk usage for the system drive
            logger.debug("Getting disk usage...")
            # On Windows, use 'C:\\' instead of '/'
            disk_path = 'C:\\' if os.name == 'nt' else '/'
            logger.debug(f"Using disk path: {disk_path}")
            disk = psutil.disk_usage(disk_path)
            disk_usage = disk.percent
            logger.debug(f"Disk usage: {disk_usage}")
            disk_total_gb = round(disk.total / (1024**3), 1)
            logger.debug(f"Disk total: {disk_total_gb} GB")

            # Get server uptime
            logger.debug("Getting server uptime...")
            uptime_seconds = int(time.time() - psutil.boot_time())
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{days}d {hours}h {minutes}m"
            logger.debug(f"Server uptime: {uptime_str}")

            logger.info("Using real system resource data from psutil")

            # Ensure all values are properly formatted numbers
            cpu_usage = round(float(cpu_usage), 1)
            memory_usage = round(float(memory_usage), 1)
            disk_usage = round(float(disk_usage), 1)
        except ImportError as e:
            logger.warning(f"ImportError: {str(e)}")
            logger.warning("psutil module not available. Using mock data for system resources.")
            # Use mock data when psutil is not available
            cpu_usage = 45.2  # Mock CPU usage percentage
            cpu_cores = 8     # Mock number of CPU cores
            memory_usage = 62.7  # Mock memory usage percentage
            memory_total_gb = 16.0  # Mock total memory in GB
            disk_usage = 58.3  # Mock disk usage percentage
            disk_total_gb = 512.0  # Mock total disk space in GB
            uptime_str = "3d 7h 22m"  # Mock uptime
        except Exception as e:
            logger.error(f"Unexpected error when using psutil: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {repr(e)}")
            logger.warning("Falling back to mock data for system resources.")
            # Use mock data when psutil has an error
            cpu_usage = 45.2  # Mock CPU usage percentage
            cpu_cores = 8     # Mock number of CPU cores
            memory_usage = 62.7  # Mock memory usage percentage
            memory_total_gb = 16.0  # Mock total memory in GB
            disk_usage = 58.3  # Mock disk usage percentage
            disk_total_gb = 512.0  # Mock total disk space in GB
            uptime_str = "3d 7h 22m"  # Mock uptime

        # Prepare the response data
        response_data = {
            'cpu': {
                'usage': cpu_usage,
                'cores': cpu_cores
            },
            'memory': {
                'usage': memory_usage,
                'total_gb': memory_total_gb
            },
            'disk': {
                'usage': disk_usage,
                'total_gb': disk_total_gb
            },
            'database': {
                'size_mb': round(db_size_mb, 1),
                'tables': 4,
                'total_records': total_records
            },
            'server': {
                'status': 'online',
                'uptime': uptime_str,
                'active_users': active_sessions
            },
            'timestamp': datetime.now().isoformat()
        }

        logger.debug(f"System resources response data: {response_data}")
        return jsonify(response_data), 200

    # Static file serving moved to main routes.py
