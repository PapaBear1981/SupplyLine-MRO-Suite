from flask import request, jsonify, session, make_response, current_app
from models import db, Tool, User, Checkout, AuditLog, UserActivity, ToolServiceRecord, Chemical, ChemicalIssuance
from models import ToolCalibration, CalibrationStandard, ToolCalibrationStandard
from datetime import datetime, timedelta, timezone
from functools import wraps
import secrets
import string
import os
import time
from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload
from routes_reports import register_report_routes
from routes_chemicals import register_chemical_routes
from routes_chemical_analytics import register_chemical_analytics_routes
from routes_calibration import register_calibration_routes
from routes_bulk_import import register_bulk_import_routes
from routes_rbac import register_rbac_routes, permission_required
from routes_announcements import register_announcement_routes
from routes_scanner import register_scanner_routes
from routes_auth import register_auth_routes
from routes_password_reset import register_password_reset_routes
from routes_kits import register_kit_routes
from routes_kit_transfers import register_kit_transfer_routes
from routes_kit_reorders import register_kit_reorder_routes
from routes_kit_messages import register_kit_message_routes
from routes_inventory import register_inventory_routes
from routes_warehouses import warehouses_bp
from routes_transfers import transfers_bp
from utils.rate_limiter import rate_limit
from utils.password_reset_security import get_password_reset_tracker
# CYCLE COUNT SYSTEM - TEMPORARILY DISABLED
# =====================================
# The cycle count system has been temporarily disabled due to production issues.
#
# REASON FOR DISABLING:
# - GitHub Issue #366: Cycle count system was completely non-functional
# - Missing database tables causing "Unable to Load Cycle Count System" errors
# - Preventing users from accessing inventory cycle count operations
# - Affecting user experience with error messages displayed to all users
#
# WHAT WAS DISABLED:
# - All cycle count API routes and endpoints
# - Frontend cycle count pages and navigation
# - Cycle count reports and analytics
# - Database operations for cycle counts
#
# TO RE-ENABLE IN THE FUTURE:
# 1. Uncomment the import below
# 2. Uncomment the register_cycle_count_routes(app) call in register_routes()
# 3. Ensure cycle count database tables are properly created/migrated
# 4. Test all cycle count functionality thoroughly
# 5. Update frontend routes and navigation (see App.jsx and MainLayout.jsx)
#
# RELATED FILES TO UPDATE WHEN RE-ENABLING:
# - frontend/src/App.jsx (uncomment cycle count routes)
# - frontend/src/components/common/MainLayout.jsx (uncomment navigation item)
# - frontend/src/pages/ReportingPage.jsx (uncomment cycle count reports)
#
# DISABLED: 2025-06-22 - Issue #366 Resolution
# from routes_cycle_count import register_cycle_count_routes
import utils as password_utils
from utils.session_manager import SessionManager
from utils.error_handler import log_security_event, handle_errors, ValidationError, DatabaseError, setup_global_error_handlers
from utils.bulk_operations import get_dashboard_stats_optimized, bulk_log_activities
from utils.file_validation import FileValidationError, validate_image_upload
from utils.validation import validate_serial_number_format, validate_lot_number_format, validate_warehouse_id
import logging

logger = logging.getLogger(__name__)

# Removed duplicate materials_manager_required - using secure version below

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use JWT authentication
        from auth.jwt_manager import JWTManager
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            log_security_event('unauthorized_access_attempt', 'Login required access denied: No valid JWT token')
            return jsonify({'error': 'Authentication required', 'reason': 'No valid JWT token'}), 401

        # Add user info to request context
        request.current_user = user_payload
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use JWT authentication
        from auth.jwt_manager import JWTManager
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(f"Admin access attempted for {f.__name__}")

        user_payload = JWTManager.get_current_user()
        if not user_payload:
            logger.warning(f"Admin access denied - No valid JWT token")
            return jsonify({'error': 'Authentication required', 'reason': 'No valid JWT token'}), 401

        if not user_payload.get('is_admin', False):
            logger.warning(f"Admin access denied - insufficient privileges for user {user_payload.get('user_id')}")
            return jsonify({'error': 'Admin privileges required'}), 403

        logger.debug(f"Admin access granted for user {user_payload.get('user_id')}")
        # Add user info to request context
        request.current_user = user_payload
        return f(*args, **kwargs)
    return decorated_function

def tool_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use JWT authentication
        from auth.jwt_manager import JWTManager
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            log_security_event('unauthorized_access_attempt', 'Tool management access denied: No valid JWT token')
            return jsonify({'error': 'Authentication required', 'reason': 'No valid JWT token'}), 401

        # Allow access for admins or Materials department users
        if user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials':
            # Add user info to request context
            request.current_user = user_payload
            return f(*args, **kwargs)

        log_security_event('insufficient_permissions', f'Tool management access denied for user {user_payload.get("user_id")}')
        return jsonify({'error': 'Tool management privileges required'}), 403
    return decorated_function

def materials_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use JWT authentication
        from auth.jwt_manager import JWTManager
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            log_security_event('unauthorized_access_attempt', 'Materials management access denied: No valid JWT token')
            return jsonify({'error': 'Authentication required', 'reason': 'No valid JWT token'}), 401

        # Check if user is admin or Materials department
        if not (user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials'):
            log_security_event('insufficient_permissions', f'Materials management access denied for user {user_payload.get("user_id")}')
            return jsonify({'error': 'Materials management privileges required'}), 403

        # Add user info to request context
        request.current_user = user_payload
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):
    # db.init_app(app) is now called in app.py, not here
    with app.app_context():
        db.create_all()

        # Create admin user if none exists - using secure initialization
        from utils.admin_init import create_secure_admin
        success, message, password = create_secure_admin()
        if success and password:
            current_app.logger.warning("SECURITY NOTICE: %s", message)
            # Emit a *single* structured log entry flagged as secret; do not expose raw password.
            current_app.logger.warning(
                "INITIAL ADMIN PASSWORD GENERATED – copy from env-var not from logs"
            )
        elif not success:
            logger.error("Admin user creation failed", extra={
                'operation': 'admin_initialization',
                'error_message': message
            })

    # Register report routes
    register_report_routes(app)

    # Register chemical routes
    register_chemical_routes(app)

    # Register chemical analytics routes
    register_chemical_analytics_routes(app)

    # Register calibration routes
    register_calibration_routes(app)

    # Register RBAC routes
    register_rbac_routes(app)

    # Register announcement routes
    register_announcement_routes(app)

    # Register scanner routes
    register_scanner_routes(app)

    # Register bulk import routes
    register_bulk_import_routes(app)

    # Register JWT authentication routes
    register_auth_routes(app)

    # Register password reset routes
    register_password_reset_routes(app)

    # Register kit/mobile warehouse routes
    register_kit_routes(app)
    register_kit_transfer_routes(app)
    register_kit_reorder_routes(app)
    register_kit_message_routes(app)

    # Register inventory tracking routes (lot/serial numbers, transactions)
    register_inventory_routes(app)

    # Register warehouse management routes
    app.register_blueprint(warehouses_bp, url_prefix='/api')

    # Register warehouse transfer routes
    app.register_blueprint(transfers_bp, url_prefix='/api')

    # Register cycle count routes
    # CYCLE COUNT SYSTEM DISABLED - Issue #366 Resolution
    # ===================================================
    # The cycle count routes registration has been disabled due to production issues.
    #
    # ORIGINAL ISSUE:
    # - Users experiencing "Unable to Load Cycle Count System" errors
    # - Missing database tables causing system failures
    # - Non-functional cycle count operations affecting inventory management
    #
    # SOLUTION IMPLEMENTED:
    # - Temporarily disabled all cycle count functionality
    # - Preserved code for future implementation
    # - Eliminated user-facing errors and system instability
    #
    # TO RE-ENABLE:
    # 1. Uncomment the line below
    # 2. Ensure cycle count database tables exist and are properly structured
    # 3. Test all cycle count endpoints thoroughly
    # 4. Verify frontend integration works correctly
    # 5. Update related frontend files (see comments in routes import section above)
    #
    # DISABLED DATE: 2025-06-22
    # GITHUB ISSUE: #366
    # register_cycle_count_routes(app)  # DISABLED - Cycle count system temporarily disabled

    # Add direct routes for chemicals management
    @app.route('/api/chemicals/reorder-needed', methods=['GET'])
    @materials_manager_required
    def chemicals_reorder_needed_direct_route():
        try:
            logger.debug("Chemicals reorder-needed requested", extra={
                'user_id': request.current_user.get('user_id') if hasattr(request, 'current_user') else session.get('user_id'),
                'department': request.current_user.get('department') if hasattr(request, 'current_user') else session.get('department')
            })
            # Get chemicals that need to be reordered
            chemicals = Chemical.query.filter_by(needs_reorder=True, reorder_status='needed').all()

            # Convert to list of dictionaries
            result = [c.to_dict() for c in chemicals]

            return jsonify(result)
        except Exception as e:
            logger.exception("Error in chemicals reorder needed route")
            return jsonify({'error': 'An error occurred while fetching chemicals that need reordering'}), 500

    @app.route('/api/chemicals/on-order', methods=['GET'])
    @materials_manager_required
    @handle_errors
    def chemicals_on_order_direct_route():
        logger.info(f"Chemicals on order requested by user {request.current_user.get('user_id')}")

        # Get chemicals that are on order
        chemicals = Chemical.query.filter_by(reorder_status='ordered').all()

        # Convert to list of dictionaries
        result = [c.to_dict() for c in chemicals]

        return jsonify(result)

    @app.route('/api/chemicals/expiring-soon', methods=['GET'])
    @materials_manager_required
    def chemicals_expiring_soon_direct_route():
        try:
            logger.debug("Chemicals expiring-soon requested", extra={
                'user_id': request.current_user.get('user_id'),
                'department': request.current_user.get('department')
            })
            # Get days parameter (default to 30)
            days = request.args.get('days', 30, type=int)

            # Get all non-archived chemicals
            chemicals = Chemical.query.filter_by(is_archived=False).all()

            # Filter to only those expiring soon
            expiring_soon = [c for c in chemicals if c.is_expiring_soon(days)]

            # Convert to list of dictionaries
            result = [c.to_dict() for c in expiring_soon]

            return jsonify(result)
        except Exception as e:
            logger.exception("Error in chemicals expiring soon route")
            return jsonify({'error': 'An error occurred while fetching chemicals expiring soon'}), 500

    @app.route('/api/chemicals/archived', methods=['GET'])
    @materials_manager_required
    def archived_chemicals_direct_route():
        try:
            # Get query parameters for filtering
            category = request.args.get('category')
            reason = request.args.get('reason')
            search = request.args.get('q')

            # Start with base query for archived chemicals
            try:
                query = Chemical.query.filter(Chemical.is_archived == True)
            except:
                # If the column doesn't exist, return an empty list
                return jsonify([])

            # Apply filters if provided
            if category:
                query = query.filter(Chemical.category == category)
            if reason:
                query = query.filter(Chemical.archived_reason.ilike(f'%{reason}%'))
            if search:
                query = query.filter(
                    db.or_(
                        Chemical.part_number.ilike(f'%{search}%'),
                        Chemical.lot_number.ilike(f'%{search}%'),
                        Chemical.description.ilike(f'%{search}%'),
                        Chemical.manufacturer.ilike(f'%{search}%')
                    )
                )

            # Execute query and convert to list of dictionaries
            chemicals = query.order_by(Chemical.archived_date.desc()).all()
            result = [c.to_dict() for c in chemicals]

            return jsonify(result)
        except Exception as e:
            logger.exception("Error in archived chemicals route")
            return jsonify({'error': 'An error occurred while fetching archived chemicals'}), 500

    # Health check endpoint for Docker
    @app.route('/api/health', methods=['GET'])
    def health_check():
        # Use standard datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'timezone': str(time.tzname)
        })

    # Database initialization endpoint
    @app.route('/api/admin/init-database', methods=['POST'])
    def init_database():
        """Initialize the database with tables and default data"""
        try:
            # Check if database is already initialized
            try:
                user_count = User.query.count()
                if user_count > 0:
                    return jsonify({
                        'success': False,
                        'message': 'Database already initialized',
                        'user_count': user_count
                    }), 400
            except Exception:
                # Tables don't exist, proceed with initialization
                pass

            # Create all tables
            db.create_all()
            logger.info("Database tables created")

            # Run the initialization script
            from init_db import init_db
            init_db()

            return jsonify({
                'success': True,
                'message': 'Database initialized successfully'
            })

        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Database initialization failed: {str(e)}'
            }), 500

    # Time API endpoint
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
        logger.debug("Time API endpoint called")
        try:
            from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
            result = {
                'status': 'ok',
                'utc_time': format_datetime(get_utc_timestamp()),
                'local_time': format_datetime(get_local_timestamp()),
                'timezone': str(time.tzname),
                'using_time_utils': True
            }
            logger.debug("Time API endpoint executed successfully")
            return jsonify(result)
        except ImportError as e:
            logger.exception("time_utils import failed in time_api_endpoint")
            result = {
                'status': 'ok',
                'utc_time': datetime.now(timezone.utc).isoformat(),
                'local_time': datetime.now().isoformat(),
                'timezone': str(time.tzname),
                'using_time_utils': False
            }
            logger.debug("Time API endpoint fallback executed")
            return jsonify(result)

    # Time test endpoint
    @app.route('/api/time-test', methods=['GET'])
    def time_test_endpoint():
        """
        Time test endpoint for debugging time functionality.
        """
        logger.debug("Time test endpoint called")
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
            logger.debug("Time test endpoint executed successfully")
            return jsonify(result)
        except ImportError as e:
            logger.exception("time_utils import failed in time_test_endpoint")
            result = {
                'status': 'ok',
                'message': 'Time test endpoint working (fallback)',
                'utc_time': datetime.now(timezone.utc).isoformat(),
                'local_time': datetime.now().isoformat(),
                'timezone': str(time.tzname),
                'using_time_utils': False,
                'timestamp': datetime.now().isoformat()
            }
            logger.debug("Time test endpoint fallback executed")
            return jsonify(result)

    # Test endpoint for admin dashboard
    @app.route('/api/admin/dashboard/test', methods=['GET'])
    def admin_dashboard_test():
        logger.debug("Admin dashboard test endpoint called")
        return jsonify({
            'status': 'success',
            'message': 'Admin dashboard test endpoint works',
            'timestamp': datetime.now().isoformat()
        })

    # Admin dashboard endpoints
    @app.route('/api/admin/registration-requests', methods=['GET'])
    @admin_required
    def get_registration_requests():
        from models import RegistrationRequest

        # Get status filter (default to 'pending')
        status = request.args.get('status', 'pending')

        if status == 'all':
            requests = RegistrationRequest.query.order_by(RegistrationRequest.created_at.desc()).all()
        else:
            requests = RegistrationRequest.query.filter_by(status=status).order_by(RegistrationRequest.created_at.desc()).all()

        return jsonify([req.to_dict() for req in requests]), 200

    @app.route('/api/admin/registration-requests/<int:id>/approve', methods=['POST'])
    @admin_required
    def approve_registration_request(id):
        from models import RegistrationRequest

        # Get the registration request
        reg_request = RegistrationRequest.query.get_or_404(id)

        # Check if it's already processed
        if reg_request.status != 'pending':
            return jsonify({'error': f'Registration request is already {reg_request.status}'}), 400

        # Create a new user from the registration request
        user = User(
            name=reg_request.name,
            employee_number=reg_request.employee_number,
            department=reg_request.department,
            password_hash=reg_request.password_hash,  # Copy the hashed password
            is_admin=False,
            is_active=True
        )

        # Update the registration request status
        reg_request.status = 'approved'
        reg_request.processed_at = datetime.utcnow()
        reg_request.processed_by = request.current_user['user_id']
        reg_request.admin_notes = request.json.get('notes', '')

        # Save changes
        db.session.add(user)
        db.session.commit()

        # Log the approval
        log = AuditLog(
            action_type='approve_registration',
            action_details=f'Approved registration request {reg_request.id} ({reg_request.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Registration request approved',
            'user_id': user.id,
            'request_id': reg_request.id
        }), 200

    @app.route('/api/admin/registration-requests/<int:id>/deny', methods=['POST'])
    @admin_required
    def deny_registration_request(id):
        from models import RegistrationRequest

        # Get the registration request
        reg_request = RegistrationRequest.query.get_or_404(id)

        # Check if it's already processed
        if reg_request.status != 'pending':
            return jsonify({'error': f'Registration request is already {reg_request.status}'}), 400

        # Update the registration request status
        reg_request.status = 'denied'
        reg_request.processed_at = datetime.utcnow()
        reg_request.processed_by = request.current_user['user_id']
        reg_request.admin_notes = request.json.get('notes', '')

        # Save changes
        db.session.commit()

        # Log the denial
        log = AuditLog(
            action_type='deny_registration',
            action_details=f'Denied registration request {reg_request.id} ({reg_request.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Registration request denied',
            'request_id': reg_request.id
        }), 200

    @app.route('/api/admin/dashboard/stats', methods=['GET'])
    @admin_required
    def get_admin_dashboard_stats():
        logger.debug("Admin dashboard stats requested", extra={'user_id': request.current_user.get('user_id')})

        # Get counts from various tables
        user_count = User.query.count()
        active_user_count = User.query.filter_by(is_active=True).count()
        tool_count = Tool.query.count()
        available_tool_count = Tool.query.filter_by(status='available').count()
        checkout_count = Checkout.query.count()
        active_checkout_count = Checkout.query.filter(Checkout.return_date.is_(None)).count()

        # Get pending registration requests count
        from models import RegistrationRequest
        pending_requests_count = RegistrationRequest.query.filter_by(status='pending').count()

        # Get recent activity
        recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

        # Get system activity over time (last 30 days)
        from sqlalchemy import func

        start_date = datetime.now() - timedelta(days=30)

        # Get activity counts by day
        daily_activity = db.session.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count().label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.date(AuditLog.timestamp)
        ).all()

        # Format the results
        activity_data = [{
            'date': str(day.date),
            'count': day.count
        } for day in daily_activity]

        # Get department distribution
        dept_distribution = db.session.query(
            User.department.label('department'),
            func.count(User.id).label('count')
        ).group_by(
            User.department
        ).all()

        dept_data = [{
            'department': dept.department or 'Unknown',
            'count': dept.count
        } for dept in dept_distribution]

        return jsonify({
            'counts': {
                'users': user_count,
                'activeUsers': active_user_count,
                'tools': tool_count,
                'availableTools': available_tool_count,
                'checkouts': checkout_count,
                'activeCheckouts': active_checkout_count,
                'pendingRegistrations': pending_requests_count
            },
            'recentActivity': [{
                'id': log.id,
                'action_type': log.action_type,
                'action_details': log.action_details,
                'timestamp': log.timestamp.isoformat()
            } for log in recent_logs],
            'activityOverTime': activity_data,
            'departmentDistribution': dept_data
        }), 200

    # SYSTEM RESOURCES ENDPOINT - DISABLED
    # This endpoint has been removed from the Admin Dashboard UI
    # The entire function has been commented out to prevent unnecessary backend processing
    # If you need to re-enable this feature, uncomment the code below

    # @app.route('/api/admin/system-resources', methods=['GET'])
    # @admin_required
    # @handle_errors
    # def get_system_resources():
    #     """Get real-time system resource usage statistics"""
    #     logger.info("System resources endpoint called")
    #
    #     # Get database size (approximate based on number of records)
    #     db_size_mb = 0
    #     total_records = 0  # Initialize to prevent UnboundLocalError if the try block fails
    #     try:
    #         # Count records in major tables to estimate size
    #         user_count = User.query.count()
    #         tool_count = Tool.query.count()
    #         checkout_count = Checkout.query.count()
    #         log_count = AuditLog.query.count()
    #
    #         # Rough estimate: 2KB per record on average
    #         total_records = user_count + tool_count + checkout_count + log_count
    #         db_size_mb = (total_records * 2) / 1024  # Convert KB to MB
    #     except Exception as e:
    #         logger.error(f"Error estimating database size: {str(e)}")
    #         db_size_mb = 10  # Default fallback value
    #         total_records = 0  # Ensure it's defined in case of exception
    #
    #     # Get active user sessions (approximate based on recent activity)
    #     now = datetime.now()
    #     five_minutes_ago = now - timedelta(minutes=5)
    #
    #     # Count users with activity in the last 5 minutes
    #     active_sessions = UserActivity.query.filter(
    #         UserActivity.timestamp >= five_minutes_ago
    #     ).distinct(UserActivity.user_id).count()

    #     # Try to import psutil
    #     try:
    #         logger.info("Attempting to import psutil module...")
    #         import psutil
    #         logger.info("Successfully imported psutil module")
    #
    #         # Get CPU usage - use instantaneous value to avoid blocking
    #         # Note: This will return the usage since the last call or 0.0 on first call
    #         logger.debug("Getting CPU usage...")
    #         cpu_usage = psutil.cpu_percent(interval=None)
    #         logger.debug(f"CPU usage: {cpu_usage}")
    #
    #         logger.debug("Getting CPU cores...")
    #         cpu_cores = psutil.cpu_count()
    #         logger.debug(f"CPU cores: {cpu_cores}")
    #
    #         # Get memory usage
    #         logger.debug("Getting memory usage...")
    #         memory = psutil.virtual_memory()
    #         memory_usage = memory.percent
    #         logger.debug(f"Memory usage: {memory_usage}")
    #         memory_total_gb = round(memory.total / (1024**3), 1)
    #         logger.debug(f"Memory total: {memory_total_gb} GB")
    #
    #         # Get disk usage for the system drive
    #         logger.debug("Getting disk usage...")
    #         # On Windows, use 'C:\\' instead of '/'
    #         disk_path = 'C:\\' if os.name == 'nt' else '/'
    #         logger.debug(f"Using disk path: {disk_path}")
    #         disk = psutil.disk_usage(disk_path)
    #         disk_usage = disk.percent
    #         logger.debug(f"Disk usage: {disk_usage}")
    #         disk_total_gb = round(disk.total / (1024**3), 1)
    #         logger.debug(f"Disk total: {disk_total_gb} GB")
    #
    #         # Get server uptime
    #         logger.debug("Getting server uptime...")
    #         uptime_seconds = int(time.time() - psutil.boot_time())
    #         days, remainder = divmod(uptime_seconds, 86400)
    #         hours, remainder = divmod(remainder, 3600)
    #         minutes, seconds = divmod(remainder, 60)
    #         uptime_str = f"{days}d {hours}h {minutes}m"
    #         logger.debug(f"Server uptime: {uptime_str}")
    #
    #         logger.info("Using real system resource data from psutil")
    #
    #         # Ensure all values are properly formatted numbers
    #         cpu_usage = round(float(cpu_usage), 1)
    #         memory_usage = round(float(memory_usage), 1)
    #         disk_usage = round(float(disk_usage), 1)
    #
    #     except ImportError as e:
    #         logger.warning(f"ImportError: {str(e)}")
    #         logger.warning("psutil module not available. Using mock data for system resources.")
    #         # Use mock data when psutil is not available
    #         cpu_usage = 45.2  # Mock CPU usage percentage
    #         logger.debug(f"Mock CPU usage: {cpu_usage}")
    #         cpu_cores = 8     # Mock number of CPU cores
    #         logger.debug(f"Mock CPU cores: {cpu_cores}")
    #
    #         memory_usage = 62.7  # Mock memory usage percentage
    #         logger.debug(f"Mock memory usage: {memory_usage}")
    #         memory_total_gb = 16.0  # Mock total memory in GB
    #         logger.debug(f"Mock memory total: {memory_total_gb} GB")
    #
    #         disk_usage = 58.3  # Mock disk usage percentage
    #         logger.debug(f"Mock disk usage: {disk_usage}")
    #         disk_total_gb = 512.0  # Mock total disk space in GB
    #         logger.debug(f"Mock disk total: {disk_total_gb} GB")
    #
    #         # Mock uptime (3 days, 7 hours, 22 minutes)
    #         uptime_str = "3d 7h 22m"
    #         logger.debug(f"Mock server uptime: {uptime_str}")
    #     except Exception as e:
    #         logger.error(f"Unexpected error when using psutil: {str(e)}")
    #         logger.error(f"Error type: {type(e)}")
    #         logger.error(f"Error details: {repr(e)}")
    #         logger.warning("Falling back to mock data for system resources.")
    #         # Use mock data when psutil has an error
    #         cpu_usage = 45.2  # Mock CPU usage percentage
    #         logger.debug(f"Mock CPU usage: {cpu_usage}")
    #         cpu_cores = 8     # Mock number of CPU cores
    #         logger.debug(f"Mock CPU cores: {cpu_cores}")
    #
    #         memory_usage = 62.7  # Mock memory usage percentage
    #         logger.debug(f"Mock memory usage: {memory_usage}")
    #         memory_total_gb = 16.0  # Mock total memory in GB
    #         logger.debug(f"Mock memory total: {memory_total_gb} GB")
    #
    #         disk_usage = 58.3  # Mock disk usage percentage
    #         logger.debug(f"Mock disk usage: {disk_usage}")
    #         disk_total_gb = 512.0  # Mock total disk space in GB
    #         logger.debug(f"Mock disk total: {disk_total_gb} GB")
    #
    #         # Mock uptime (3 days, 7 hours, 22 minutes)
    #         uptime_str = "3d 7h 22m"
    #         logger.debug(f"Mock server uptime: {uptime_str}")

    #     # Prepare the response data
    #     response_data = {
    #         'cpu': {
    #             'usage': cpu_usage,
    #             'cores': cpu_cores
    #         },
    #         'memory': {
    #             'usage': memory_usage,
    #             'total_gb': memory_total_gb
    #         },
    #         'disk': {
    #             'usage': disk_usage,
    #             'total_gb': disk_total_gb
    #         },
    #         'database': {
    #             'size_mb': round(db_size_mb, 1),
    #             'tables': 4,
    #             'total_records': total_records
    #         },
    #         'server': {
    #             'status': 'online',
    #             'uptime': uptime_str,
    #             'active_users': active_sessions
    #         },
    #         'timestamp': datetime.now().isoformat()
    #     }
    #
    #     logger.debug(f"System resources response data: {response_data}")
    #     return jsonify(response_data), 200

    # Serve static files
    @app.route('/api/static/<path:filename>')
    def serve_static(filename):
        return current_app.send_static_file(filename)

    @app.route('/api/tools', methods=['GET', 'POST'])
    def tools_route():
        # GET - List all tools
        if request.method == 'GET':
            search_query = request.args.get('q')
            logger.debug("Tools list requested", extra={'has_search_query': bool(search_query)})

            if search_query:
                search_term = f'%{search_query.lower()}%'

                try:
                    tools = Tool.query.filter(
                        db.or_(
                            db.func.lower(Tool.tool_number).like(search_term),
                            db.func.lower(Tool.serial_number).like(search_term),
                            db.func.lower(Tool.description).like(search_term),
                            db.func.lower(Tool.location).like(search_term)
                        )
                    ).all()
                    logger.debug("Tools search executed", extra={'result_count': len(tools)})
                except Exception as e:
                    logger.exception("Error during tools search")
                    tools = Tool.query.all()
                    logger.debug("Falling back to full tools list", extra={'result_count': len(tools)})
            else:
                tools = Tool.query.all()
                logger.debug("Tools retrieved without search", extra={'result_count': len(tools)})

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
            logger.debug("Active checkouts fetched", extra={'active_checkout_count': len(active_checkouts)})

            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'

            result = [{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'category': getattr(t, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
                'status': tool_status.get(t.id, getattr(t, 'status', 'available')),  # Use 'available' if status attribute doesn't exist
                'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
                'warehouse_id': t.warehouse_id,
                'created_at': t.created_at.isoformat(),
                'requires_calibration': getattr(t, 'requires_calibration', False),
                'calibration_frequency_days': getattr(t, 'calibration_frequency_days', None),
                'last_calibration_date': t.last_calibration_date.isoformat() if hasattr(t, 'last_calibration_date') and t.last_calibration_date else None,
                'next_calibration_date': t.next_calibration_date.isoformat() if hasattr(t, 'next_calibration_date') and t.next_calibration_date else None,
                'calibration_status': getattr(t, 'calibration_status', 'not_applicable')
            } for t in tools]

            logger.debug("Tools response ready", extra={'result_count': len(result)})
            return jsonify(result)

        # POST - Create new tool (requires tool manager privileges)
        from auth.jwt_manager import JWTManager
        user_payload = JWTManager.get_current_user()
        if not user_payload:
            return jsonify({'error': 'Authentication required'}), 401
        if not (user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}

        # Validate required fields - warehouse_id is now required for all tools
        required_fields = ['tool_number', 'serial_number', 'warehouse_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate serial number format
        try:
            validate_serial_number_format(data['serial_number'])
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Validate warehouse exists and is active
        try:
            warehouse = validate_warehouse_id(data['warehouse_id'])
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Check if tool with same tool number AND serial number already exists
        if Tool.query.filter_by(tool_number=data['tool_number'], serial_number=data['serial_number']).first():
            return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

        # Create new tool - warehouse_id is required
        t = Tool(
            tool_number=data.get('tool_number'),
            serial_number=data.get('serial_number'),
            lot_number=data.get('lot_number'),  # Support for consumable tools
            description=data.get('description'),
            condition=data.get('condition'),
            location=data.get('location'),
            category=data.get('category', 'General'),
            warehouse_id=data['warehouse_id'],  # Required field
            requires_calibration=data.get('requires_calibration', False),
            calibration_frequency_days=data.get('calibration_frequency_days')
        )

        # Set calibration status based on requires_calibration
        if t.requires_calibration:
            t.calibration_status = 'due_soon'  # Default to due_soon until first calibration
        else:
            t.calibration_status = 'not_applicable'
        db.session.add(t)
        db.session.commit()

        # Record transaction
        from utils.transaction_helper import record_item_receipt
        try:
            record_item_receipt(
                item_type='tool',
                item_id=t.id,
                user_id=user_payload['user_id'],
                quantity=1.0,
                location=t.location or 'Unknown',
                notes='Initial tool creation'
            )
            db.session.commit()
        except Exception as e:
            logger.error(f"Error recording tool creation transaction: {str(e)}")
            # Don't fail the tool creation if transaction recording fails

        # Log the action
        log = AuditLog(
            action_type='create_tool',
            action_details=f'Created tool {t.id} ({t.tool_number})'
        )
        db.session.add(log)
        db.session.commit()

        # Return the complete tool object for the frontend
        return jsonify({
            'id': t.id,
            'tool_number': t.tool_number,
            'serial_number': t.serial_number,
            'lot_number': t.lot_number,
            'description': t.description,
            'condition': t.condition,
            'location': t.location,
            'category': t.category,
            'status': getattr(t, 'status', 'available'),
            'status_reason': getattr(t, 'status_reason', None),
            'warehouse_id': t.warehouse_id,
            'warehouse_name': warehouse.name,
            'created_at': t.created_at.isoformat(),
            'requires_calibration': getattr(t, 'requires_calibration', False),
            'calibration_frequency_days': getattr(t, 'calibration_frequency_days', None),
            'last_calibration_date': t.last_calibration_date.isoformat() if hasattr(t, 'last_calibration_date') and t.last_calibration_date else None,
            'next_calibration_date': t.next_calibration_date.isoformat() if hasattr(t, 'next_calibration_date') and t.next_calibration_date else None,
            'calibration_status': getattr(t, 'calibration_status', 'not_applicable'),
            'message': 'Tool created successfully in warehouse'
        }), 201

    @app.route('/api/tools/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def get_tool(id):
        tool = Tool.query.get_or_404(id)

        # GET - Get tool details
        if request.method == 'GET':
            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()

            # Determine status - checkout status takes precedence over tool status
            status = 'checked_out' if active_checkout else getattr(tool, 'status', 'available')
            has_category = hasattr(tool, 'category')
            category_value = tool.category if has_category else 'General'
            logger.debug("Tool detail requested", extra={'tool_id': id, 'status': status})

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'condition': tool.condition,
                'location': tool.location,
                'category': category_value,  # Use actual category value
                'status': status,
                'status_reason': getattr(tool, 'status_reason', None) if status in ['maintenance', 'retired'] else None,
                'created_at': tool.created_at.isoformat(),
                'requires_calibration': getattr(tool, 'requires_calibration', False),
                'calibration_frequency_days': getattr(tool, 'calibration_frequency_days', None),
                'last_calibration_date': tool.last_calibration_date.isoformat() if hasattr(tool, 'last_calibration_date') and tool.last_calibration_date else None,
                'next_calibration_date': tool.next_calibration_date.isoformat() if hasattr(tool, 'next_calibration_date') and tool.next_calibration_date else None,
                'calibration_status': getattr(tool, 'calibration_status', 'not_applicable')
            })

        elif request.method == 'DELETE':
            # DELETE - Delete tool (requires admin privileges)
            from auth.jwt_manager import JWTManager
            user_payload = JWTManager.get_current_user()
            if not user_payload:
                return jsonify({'error': 'Authentication required'}), 401
            if not user_payload.get('is_admin', False):
                return jsonify({'error': 'Admin privileges required to delete tools'}), 403

            # Accept force_delete from query parameters or JSON body
            force_delete = (
                request.args.get('force_delete', '').lower() in ('1', 'true')
                or (request.get_json(silent=True) or {}).get('force_delete', False)
            )

            # Check if tool has history (checkouts, calibrations, service records)
            has_checkouts = Checkout.query.filter_by(tool_id=id).count() > 0
            has_calibrations = ToolCalibration.query.filter_by(tool_id=id).count() > 0
            has_service_records = ToolServiceRecord.query.filter_by(tool_id=id).count() > 0

            if (has_checkouts or has_calibrations or has_service_records) and not force_delete:
                return jsonify({
                    'error': 'Tool has history and cannot be deleted',
                    'has_history': True,
                    'has_checkouts': has_checkouts,
                    'has_calibrations': has_calibrations,
                    'has_service_records': has_service_records,
                    'suggestion': 'Consider retiring the tool instead to preserve history'
                }), 400

            # Store tool details for audit log before deletion
            tool_number = tool.tool_number
            tool_description = tool.description

            try:
                # Delete related records if force_delete is True
                if force_delete:
                    # Delete calibration standards associations first
                    ToolCalibrationStandard.query.filter(
                        ToolCalibrationStandard.calibration_id.in_(
                            db.session.query(ToolCalibration.id).filter_by(tool_id=id)
                        )
                    ).delete(synchronize_session=False)

                    # Delete calibrations
                    ToolCalibration.query.filter_by(tool_id=id).delete()

                    # Delete checkouts
                    Checkout.query.filter_by(tool_id=id).delete()

                    # Delete service records
                    ToolServiceRecord.query.filter_by(tool_id=id).delete()

                # Delete the tool
                db.session.delete(tool)
                db.session.commit()

                # Log the action
                log = AuditLog(
                    action_type='delete_tool',
                    action_details=f'Deleted tool {id} ({tool_number}) - {tool_description}. Force delete: {force_delete}'
                )
                db.session.add(log)
                db.session.commit()

                return jsonify({'message': 'Tool deleted successfully'}), 200

            except Exception as e:
                db.session.rollback()
                logger.exception("Failed to delete tool", extra={'tool_id': id})
                return jsonify({'error': 'Failed to delete tool'}), 500

        # PUT - Update tool (requires tool manager privileges)

        data = request.get_json() or {}
        logger.debug("Received tool update request", extra={
            'tool_id': id,
            'request_content_type': request.content_type
        })

        # Update fields
        if 'tool_number' in data or 'serial_number' in data:
            # If either tool_number or serial_number is being updated, we need to check for duplicates
            new_tool_number = data.get('tool_number', tool.tool_number)
            new_serial_number = data.get('serial_number', tool.serial_number)

            # Check if the combination of tool_number and serial_number already exists for another tool
            existing_tool = Tool.query.filter_by(tool_number=new_tool_number, serial_number=new_serial_number).first()
            if existing_tool and existing_tool.id != id:
                return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

            # Update the fields if they were provided
            if 'tool_number' in data:
                tool.tool_number = data['tool_number']
            if 'serial_number' in data:
                tool.serial_number = data['serial_number']

        if 'description' in data:
            tool.description = data['description']

        if 'condition' in data:
            tool.condition = data['condition']

        if 'location' in data:
            tool.location = data['location']

        if 'category' in data:
            old_category = tool.category
            tool.category = data['category']
            logger.debug("Updated tool category", extra={'tool_id': id, 'old_category': old_category, 'new_category': tool.category})

        # Update calibration fields
        if 'requires_calibration' in data:
            tool.requires_calibration = data['requires_calibration']

            # If requires_calibration is being turned off, reset calibration status
            if not tool.requires_calibration:
                tool.calibration_status = 'not_applicable'
            # If requires_calibration is being turned on, set initial calibration status
            elif tool.requires_calibration and not tool.calibration_status:
                tool.calibration_status = 'due_soon'

        if 'calibration_frequency_days' in data:
            tool.calibration_frequency_days = data['calibration_frequency_days']

            # If we have a last calibration date and frequency, update the next calibration date
            if tool.last_calibration_date and tool.calibration_frequency_days:
                tool.next_calibration_date = tool.last_calibration_date + timedelta(days=tool.calibration_frequency_days)

                # Update calibration status based on new next_calibration_date
                if hasattr(tool, 'update_calibration_status'):
                    tool.update_calibration_status()

        db.session.commit()

        # Verify the update in the database
        updated_tool = Tool.query.get(id)
        logger.debug("Tool updated successfully", extra={'tool_id': id})

        # Log the action
        log = AuditLog(
            action_type='update_tool',
            action_details=f'Updated tool {tool.id} ({tool.tool_number})'
        )
        db.session.add(log)
        db.session.commit()

        # Get the updated tool from the database
        updated_tool = Tool.query.get(id)

        response_data = {
            'id': updated_tool.id,
            'tool_number': updated_tool.tool_number,
            'serial_number': updated_tool.serial_number,
            'description': updated_tool.description,
            'condition': updated_tool.condition,
            'location': updated_tool.location,
            'category': updated_tool.category,  # Use the actual category value
            'requires_calibration': getattr(updated_tool, 'requires_calibration', False),
            'calibration_frequency_days': getattr(updated_tool, 'calibration_frequency_days', None),
            'last_calibration_date': updated_tool.last_calibration_date.isoformat() if hasattr(updated_tool, 'last_calibration_date') and updated_tool.last_calibration_date else None,
            'next_calibration_date': updated_tool.next_calibration_date.isoformat() if hasattr(updated_tool, 'next_calibration_date') and updated_tool.next_calibration_date else None,
            'calibration_status': getattr(updated_tool, 'calibration_status', 'not_applicable'),
            'message': 'Tool updated successfully'
        }

        return jsonify(response_data)

    @app.route('/api/tools/<int:id>/retire', methods=['POST'])
    @admin_required
    def retire_tool(id):
        """Retire a tool instead of deleting it to preserve history."""
        tool = Tool.query.get_or_404(id)

        data = request.get_json() or {}
        reason = data.get('reason', 'Tool retired by admin')

        # Update tool status to retired
        tool.status = 'retired'
        tool.status_reason = reason

        # Create service record for retirement (use user_id from JWT token)
        service_record = ToolServiceRecord(
            tool_id=id,
            action_type='remove_permanent',
            user_id=request.current_user['user_id'],
            reason=reason,
            comments=data.get('comments', '')
        )

        db.session.add(service_record)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='retire_tool',
            action_details=f'Retired tool {id} ({tool.tool_number}) - {reason}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Tool retired successfully',
            'tool': tool.to_dict()
        }), 200

    @app.route('/api/calibrations/notifications', methods=['GET'])
    def get_calibration_notifications():
        """Get calibration notifications for tools due for calibration."""
        try:
            now = datetime.now()

            # Get tools that require calibration
            tools_requiring_calibration = Tool.query.filter_by(requires_calibration=True).all()

            notifications = []

            for tool in tools_requiring_calibration:
                # Check calibration status
                if tool.calibration_status == 'overdue':
                    notifications.append({
                        'id': tool.id,
                        'tool_number': tool.tool_number,
                        'description': tool.description,
                        'type': 'overdue',
                        'message': f'Tool {tool.tool_number} calibration is overdue',
                        'priority': 'high',
                        'last_calibration_date': tool.last_calibration_date.isoformat() if tool.last_calibration_date else None,
                        'next_calibration_date': tool.next_calibration_date.isoformat() if tool.next_calibration_date else None
                    })
                elif tool.calibration_status == 'due_soon':
                    # Check if due within 30 days
                    if tool.next_calibration_date and tool.next_calibration_date <= now + timedelta(days=30):
                        days_until_due = (tool.next_calibration_date - now).days
                        notifications.append({
                            'id': tool.id,
                            'tool_number': tool.tool_number,
                            'description': tool.description,
                            'type': 'due_soon',
                            'message': f'Tool {tool.tool_number} calibration due in {days_until_due} days',
                            'priority': 'medium',
                            'days_until_due': days_until_due,
                            'last_calibration_date': tool.last_calibration_date.isoformat() if tool.last_calibration_date else None,
                            'next_calibration_date': tool.next_calibration_date.isoformat() if tool.next_calibration_date else None
                        })

            # Sort by priority (overdue first, then by days until due)
            notifications.sort(key=lambda x: (
                0 if x['type'] == 'overdue' else 1,
                x.get('days_until_due', 999)
            ))

            return jsonify({
                'notifications': notifications,
                'count': len(notifications),
                'overdue_count': len([n for n in notifications if n['type'] == 'overdue']),
                'due_soon_count': len([n for n in notifications if n['type'] == 'due_soon'])
            }), 200

        except Exception as e:
            logger.exception("Error getting calibration notifications")
            return jsonify({'error': 'Unable to fetch calibration notifications'}), 500

    @app.route('/api/users', methods=['GET', 'POST'])
    @login_required
    def users_route():
        # Check if user is admin or Materials department (from JWT token)
        user_payload = request.current_user
        if not (user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        if request.method == 'GET':
            # Check if there's a search query for employee number
            search_query = request.args.get('q')

            # Check if we should include lockout info (admin only)
            include_lockout_info = user_payload.get('is_admin', False)

            if search_query:
                # Search for users by employee number
                search_term = f'%{search_query}%'
                users = User.query.filter(User.employee_number.like(search_term)).all()
                return jsonify([u.to_dict(include_roles=True, include_lockout_info=include_lockout_info) for u in users])
            else:
                # Get all users, including inactive ones
                users = User.query.all()
                return jsonify([u.to_dict(include_roles=True, include_lockout_info=include_lockout_info) for u in users])

        # POST - Create a new user
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['name', 'employee_number', 'department', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if employee number already exists
        if User.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'error': 'Employee number already exists'}), 400

        # Validate password strength
        is_valid, errors = password_utils.validate_password_strength(data.get('password'))
        if not is_valid:
            return jsonify({'error': 'Password does not meet security requirements', 'details': errors}), 400

        # Create new user
        u = User(
            name=data.get('name'),
            employee_number=data.get('employee_number'),
            department=data.get('department'),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True)
        )
        u.set_password(data.get('password'))

        db.session.add(u)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='create_user',
            action_details=f'Created user {u.id} ({u.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(u.to_dict()), 201

    @app.route('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    @login_required
    def user_detail_route(id):
        # Check if user is admin or Materials department (from JWT token)
        user_payload = request.current_user
        if not (user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials'):
            return jsonify({'error': 'User management privileges required'}), 403

        # Get the user
        user = User.query.get_or_404(id)

        if request.method == 'GET':
            # Return user details with roles and lockout info for admins
            include_lockout_info = user_payload.get('is_admin', False)
            return jsonify(user.to_dict(include_roles=True, include_lockout_info=include_lockout_info))

        elif request.method == 'PUT':
            # Update user
            data = request.get_json() or {}

            # Update fields
            if 'name' in data:
                user.name = data['name']
            if 'department' in data:
                user.department = data['department']
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'password' in data and data['password']:
                # Validate password strength
                is_valid, errors = password_utils.validate_password_strength(data['password'])
                if not is_valid:
                    return jsonify({'error': 'Password does not meet security requirements', 'details': errors}), 400
                user.set_password(data['password'])

            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='update_user',
                action_details=f'Updated user {user.id} ({user.name})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify(user.to_dict(include_roles=True))

        elif request.method == 'DELETE':
            # Deactivate user instead of deleting
            user.is_active = False
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='deactivate_user',
                action_details=f'Deactivated user {user.id} ({user.name})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({'message': f'User {user.name} deactivated successfully'})

    @app.route('/api/users/<int:id>/unlock', methods=['POST'])
    @admin_required
    def unlock_user_account(id):
        """Unlock a user account that has been locked due to failed login attempts."""
        # Get the user
        user = User.query.get_or_404(id)

        # Check if the account is actually locked
        if not user.is_locked():
            return jsonify({'message': f'Account for {user.name} is not locked'}), 400

        # Unlock the account
        user.unlock_account()

        # Log the action (get admin info from JWT token)
        user_payload = request.current_user
        log = AuditLog(
            action_type='account_unlocked',
            action_details=f'Admin {user_payload.get("user_name", "Unknown")} (ID: {user_payload.get("user_id")}) manually unlocked account for user {user.name} (ID: {user.id})'
        )
        db.session.add(log)

        # Add user activity
        activity = UserActivity(
            user_id=user.id,
            activity_type='account_unlocked',
            description=f'Account unlocked by admin {user_payload.get("user_name", "Unknown")}',
            ip_address=request.remote_addr
        )
        db.session.add(activity)

        db.session.commit()

        return jsonify({
            'message': f'Account for {user.name} has been successfully unlocked',
            'user': user.to_dict(include_roles=True, include_lockout_info=True)
        }), 200

    @app.route('/api/checkouts', methods=['GET', 'POST'])
    def checkouts_route():
        try:
            if request.method == 'GET':
                checkouts = Checkout.query.all()
                return jsonify([{
                    'id': c.id,
                    'tool_id': c.tool_id,
                    'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                    'serial_number': c.tool.serial_number if c.tool else 'Unknown',
                    'description': c.tool.description if c.tool else '',
                    'user_id': c.user_id,
                    'user_name': c.user.name if c.user else 'Unknown',
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'status': 'Returned' if c.return_date else 'Checked Out'
                } for c in checkouts])

            # POST - Create new checkout
            data = request.get_json() or {}
            logger.debug("Checkout request received", extra={'tool_id': data.get('tool_id')})

            # Validate required fields
            required_fields = ['tool_id']
            for field in required_fields:
                if field not in data or data.get(field) is None:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate tool exists
            try:
                tool_id = int(data.get('tool_id'))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid tool ID format'}), 400

            tool = Tool.query.get(tool_id)
            if not tool:
                return jsonify({'error': f'Tool with ID {tool_id} does not exist'}), 404

            # Get user ID - either from request data or from session
            user_id = data.get('user_id')

            # Convert user_id to integer if it's a string
            if user_id is not None:
                try:
                    user_id = int(user_id)
                except (ValueError, TypeError):
                    user_id = None

            if not user_id:
                # If user_id not provided in request, use the logged-in user's ID from JWT
                from auth.jwt_manager import JWTManager
                user_payload = JWTManager.get_current_user()
                if not user_payload:
                    return jsonify({'error': 'Authentication required'}), 401
                user_id = user_payload['user_id']

            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': f'User with ID {user_id} does not exist'}), 404

            logger.debug("Checkout user validated", extra={'user_id': user.id})

            # Check if tool is already checked out
            active_checkout = Checkout.query.filter_by(tool_id=tool_id, return_date=None).first()
            if active_checkout:
                return jsonify({'error': f'Tool {tool.tool_number} is already checked out'}), 400

            # Create checkout
            expected_return_date = data.get('expected_return_date')
            logger.debug("Creating checkout", extra={'tool_id': tool_id, 'user_id': user_id})

            # Parse expected_return_date if it's a string
            parsed_date = None
            if expected_return_date:
                try:
                    if isinstance(expected_return_date, str):
                        # Handle different date formats
                        if 'Z' in expected_return_date:
                            parsed_date = datetime.fromisoformat(expected_return_date.replace('Z', '+00:00'))
                        elif 'T' in expected_return_date:
                            parsed_date = datetime.fromisoformat(expected_return_date)
                        else:
                            # Simple date format (YYYY-MM-DD)
                            parsed_date = datetime.strptime(expected_return_date, '%Y-%m-%d')
                    else:
                        parsed_date = expected_return_date
                except Exception as e:
                    # Use a default date (7 days from now) if parsing fails
                    parsed_date = datetime.now() + timedelta(days=7)
            else:
                # Default to 7 days from now if no date provided
                parsed_date = datetime.now() + timedelta(days=7)

            # Create and save the checkout
            try:
                c = Checkout(
                    tool_id=tool_id,
                    user_id=user_id,
                    expected_return_date=parsed_date
                )
                db.session.add(c)
                db.session.commit()
                logger.debug("Checkout created", extra={'checkout_id': c.id})

                # Record transaction
                from utils.transaction_helper import record_tool_checkout
                try:
                    record_tool_checkout(
                        tool_id=tool_id,
                        user_id=user_id,
                        expected_return_date=parsed_date,
                        notes=f'Checked out to {user.name}'
                    )
                except Exception as e:
                    logger.error(f"Error recording checkout transaction: {str(e)}")

                # Log the action
                log = AuditLog(
                    action_type='checkout_tool',
                    action_details=f'User {user.name} (ID: {user_id}) checked out tool {tool.tool_number} (ID: {tool_id})'
                )
                db.session.add(log)

                # Add user activity (use user_id from checkout, not session)
                activity = UserActivity(
                    user_id=user_id,
                    activity_type='tool_checkout',
                    description=f'Checked out tool {tool.tool_number}',
                    ip_address=request.remote_addr
                )
                db.session.add(activity)

                db.session.commit()

                return jsonify({
                    'id': c.id,
                    'message': f'Tool {tool.tool_number} checked out successfully'
                }), 201
            except Exception as e:
                db.session.rollback()
                logger.exception("Database error during checkout")
                return jsonify({'error': 'Database error during checkout'}), 500

        except Exception as e:
            logger.exception("Unexpected error in checkouts route")
            return jsonify({'error': 'An unexpected error occurred while processing the checkout request'}), 500

    @app.route('/api/checkouts/<int:id>/return', methods=['POST', 'PUT'])
    @login_required
    def return_route(id):
        try:
            logger.debug("Return request received", extra={'checkout_id': id, 'method': request.method})

            # Check if user is admin or Materials department (from JWT token)
            user_payload = request.current_user
            if not (user_payload.get('is_admin', False) or user_payload.get('department') == 'Materials'):
                return jsonify({'error': 'Only Materials and Admin personnel can return tools'}), 403

            # Validate checkout exists
            c = Checkout.query.get(id)
            if not c:
                return jsonify({'error': f'Checkout with ID {id} not found'}), 404
            logger.debug("Checkout record found", extra={'checkout_id': c.id, 'tool_id': c.tool_id, 'user_id': c.user_id})

            # Check if already returned
            if c.return_date:
                return jsonify({'error': 'This tool has already been returned'}), 400

            # Get tool and user info for better logging
            tool = Tool.query.get(c.tool_id)
            user = User.query.get(c.user_id)

            if not tool:
                return jsonify({'error': f'Tool with ID {c.tool_id} not found'}), 404

            if not user:
                logger.warning("Return processing user not found", extra={'checkout_id': c.id, 'missing_user_id': c.user_id})

            logger.debug("Processing return", extra={'tool_id': tool.id if tool else None, 'user_id': user.id if user else None})

            # Get data from request if provided
            data = request.get_json() or {}
            condition = data.get('condition')
            returned_by = data.get('returned_by')
            found = data.get('found', False)
            notes = data.get('notes', '')
            logger.debug("Return details parsed", extra={'checkout_id': id, 'has_condition': bool(condition), 'found_flag': bool(found)})

            try:
                # Mark as returned
                c.return_date = datetime.now()

                # Update tool condition if provided
                if condition and tool:
                    old_condition = tool.condition
                    tool.condition = condition

                # Update tool status to available
                if tool:
                    old_status = tool.status
                    tool.status = 'available'

                # Store return details in the database
                # We'll add these as attributes to the checkout record
                c.return_condition = condition
                c.returned_by = returned_by
                c.found = found
                c.return_notes = notes

                db.session.commit()

                # Record transaction
                from utils.transaction_helper import record_tool_return
                try:
                    record_tool_return(
                        tool_id=c.tool_id,
                        user_id=user_payload['user_id'],
                        condition=condition,
                        notes=notes
                    )
                except Exception as e:
                    logger.error(f"Error recording return transaction: {str(e)}")

                # Prepare action details for logging
                action_details = f'User {user.name if user else "Unknown"} (ID: {c.user_id}) returned tool {tool.tool_number if tool else "Unknown"} (ID: {c.tool_id})'

                # Add additional return details to the log
                if returned_by:
                    action_details += f', returned by: {returned_by}'
                if found:
                    action_details += ', tool was found on production floor'
                if notes:
                    action_details += f', notes: {notes}'

                # Log the action
                log = AuditLog(
                    action_type='return_tool',
                    action_details=action_details
                )
                db.session.add(log)

                # Add user activity (use user_id from JWT token)
                activity = UserActivity(
                    user_id=user_payload['user_id'],
                    activity_type='tool_return',
                    description=f'Returned tool {tool.tool_number if tool else "Unknown"}',
                    ip_address=request.remote_addr
                )
                db.session.add(activity)

                db.session.commit()

                # Return a more detailed response
                return jsonify({
                    'id': c.id,
                    'tool_id': c.tool_id,
                    'tool_number': tool.tool_number if tool else 'Unknown',
                    'serial_number': tool.serial_number if tool else 'Unknown',
                    'description': tool.description if tool else '',
                    'condition': tool.condition if tool else '',
                    'user_id': c.user_id,
                    'user_name': user.name if user else 'Unknown',
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'returned_by': returned_by,
                    'found': found,
                    'return_notes': notes,
                    'status': 'Returned',
                    'message': f'Tool {tool.tool_number if tool else "Unknown"} returned successfully'
                }), 200
            except Exception as e:
                db.session.rollback()
                logger.error("Database error during tool return", exc_info=True, extra={
                    'operation': 'tool_return',
                    'tool_id': c.tool_id,
                    'user_id': user_payload.get('user_id'),
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                return jsonify({'error': 'Database error during tool return'}), 500

        except Exception as e:
            checkout_record = locals().get('c')
            logger.error("Unexpected error in return route", exc_info=True, extra={
                'operation': 'tool_return',
                'tool_id': checkout_record.tool_id if checkout_record else None,
                'user_id': user_payload.get('user_id') if 'user_payload' in locals() else None,
                'error_type': type(e).__name__
            })
            return jsonify({'error': 'An unexpected error occurred while processing the return'}), 500

    @app.route('/api/audit', methods=['GET'])
    @admin_required
    def audit_route():
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
        return jsonify([{
            'id': a.id,
            'action_type': a.action_type,
            'action_details': a.action_details,
            'timestamp': a.timestamp.isoformat()
        } for a in logs])

    @app.route('/api/audit/logs', methods=['GET'])
    def audit_logs_route():
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get logs with pagination
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

        return jsonify([{
            'id': a.id,
            'action_type': a.action_type,
            'action_details': a.action_details,
            'timestamp': a.timestamp.isoformat()
        } for a in logs])

    @app.route('/api/audit/metrics', methods=['GET'])
    def audit_metrics_route():
        # Get timeframe parameter (default to 'week')
        timeframe = request.args.get('timeframe', 'week')

        # Calculate date range based on timeframe
        now = datetime.now()
        if timeframe == 'day':
            start_date = now - timedelta(days=1)
        elif timeframe == 'week':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(weeks=1)  # Default to week

        # Get counts for different action types
        checkout_count = AuditLog.query.filter(
            AuditLog.action_type == 'checkout_tool',
            AuditLog.timestamp >= start_date
        ).count()

        return_count = AuditLog.query.filter(
            AuditLog.action_type == 'return_tool',
            AuditLog.timestamp >= start_date
        ).count()

        login_count = AuditLog.query.filter(
            AuditLog.action_type == 'user_login',
            AuditLog.timestamp >= start_date
        ).count()

        # Get total activity count
        total_activity = AuditLog.query.filter(
            AuditLog.timestamp >= start_date
        ).count()

        # Get recent activity by day
        from sqlalchemy import func

        # This query gets counts by day
        daily_activity = db.session.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count().label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(
            func.date(AuditLog.timestamp)
        ).all()

        # Format the results
        daily_data = [{
            'date': str(day.date),
            'count': day.count
        } for day in daily_activity]

        return jsonify({
            'timeframe': timeframe,
            'total_activity': total_activity,
            'checkouts': checkout_count,
            'returns': return_count,
            'logins': login_count,
            'daily_activity': daily_data
        })

    @app.route('/api/audit/users/<int:user_id>', methods=['GET'])
    def user_audit_logs_route(user_id):
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get user activities with pagination
        activities = UserActivity.query.filter_by(user_id=user_id).order_by(
            UserActivity.timestamp.desc()
        ).offset(offset).limit(limit).all()

        return jsonify([activity.to_dict() for activity in activities])

    @app.route('/api/audit/tools/<int:tool_id>', methods=['GET'])
    def tool_audit_logs_route(tool_id):
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get tool-related audit logs with pagination
        # This is a simplified approach - in a real app, you might want to
        # search for tool ID in action_details or have a more structured way
        # to track tool-specific actions
        logs = AuditLog.query.filter(
            AuditLog.action_details.like(f'%tool%{tool_id}%')
        ).order_by(
            AuditLog.timestamp.desc()
        ).offset(offset).limit(limit).all()

        return jsonify([{
            'id': a.id,
            'action_type': a.action_type,
            'action_details': a.action_details,
            'timestamp': a.timestamp.isoformat()
        } for a in logs])

    # JWT-based login route is now handled by routes_auth.py

    # JWT-based logout route is now handled by routes_auth.py

    # JWT-based auth status route is now handled by routes_auth.py

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['name', 'employee_number', 'department', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if employee number already exists in users or registration requests
        if User.query.filter_by(employee_number=data['employee_number']).first():
            return jsonify({'error': 'Employee number already registered'}), 400

        from models import RegistrationRequest
        if RegistrationRequest.query.filter_by(employee_number=data['employee_number'], status='pending').first():
            return jsonify({'error': 'A registration request with this employee number is already pending approval'}), 400

        # Validate password strength
        is_valid, errors = password_utils.validate_password_strength(data.get('password'))
        if not is_valid:
            return jsonify({'error': 'Password does not meet security requirements', 'details': errors}), 400

        # Create new registration request instead of user
        reg_request = RegistrationRequest(
            name=data['name'],
            employee_number=data['employee_number'],
            department=data['department'],
            status='pending'
        )
        reg_request.set_password(data['password'])

        db.session.add(reg_request)
        db.session.commit()

        # Log the registration request
        log = AuditLog(
            action_type='registration_request',
            action_details=f'New registration request: {reg_request.id} ({reg_request.name})'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'message': 'Registration request submitted. An administrator will review your request.'}), 201

    @app.route('/api/auth/reset-password/request', methods=['POST'])
    @rate_limit(limit=3, window=3600)  # 3 requests per hour per IP
    def request_password_reset():
        data = request.get_json() or {}

        if not data.get('employee_number'):
            return jsonify({'error': 'Employee number is required'}), 400

        # Generic response message to prevent user enumeration
        # This message is returned for both existing and non-existing users
        generic_message = 'If your employee number is registered, a password reset code has been sent to your registered contact method'

        user = User.query.filter_by(employee_number=data['employee_number']).first()
        if not user:
            # Don't reveal that the user doesn't exist - return same message
            app.logger.info(
                f'Password reset requested for non-existent employee number. '
                f'IP: {request.remote_addr}'
            )
            return jsonify({'message': generic_message}), 200

        # Generate reset token
        reset_code = user.generate_reset_token()
        db.session.commit()

        # TODO: Implement email/SMS delivery for password reset codes
        # For now, log the reset code for admin retrieval
        # SECURITY: Never return reset codes in API responses
        app.logger.warning(
            f'Password reset requested for user {user.employee_number}. '
            f'Reset code: {reset_code} (expires in 15 minutes). '
            f'IP: {request.remote_addr}'
        )

        # Log the password reset request
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_reset_request',
            description='Password reset requested',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        # Return same generic message to prevent user enumeration
        return jsonify({'message': generic_message}), 200

    @app.route('/api/auth/reset-password/confirm', methods=['POST'])
    @rate_limit(limit=5, window=3600)  # 5 attempts per hour per IP
    def confirm_password_reset():
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['employee_number', 'reset_code', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        user = User.query.filter_by(employee_number=data['employee_number']).first()
        if not user:
            return jsonify({'error': 'Invalid employee number'}), 400

        tracker = get_password_reset_tracker()

        # Enforce account-level exponential backoff
        is_locked, retry_after = tracker.is_locked(user.employee_number)
        if is_locked:
            return jsonify({
                'error': 'Too many password reset attempts. Please try again later.',
                'retry_after': retry_after
            }), 429

        # Verify reset code
        if not user.check_reset_token(data['reset_code']):
            remaining_attempts, delay_seconds = tracker.record_failure(user.employee_number)

            # Invalidate the reset token after repeated failures
            if tracker.should_invalidate_token(user.employee_number):
                user.clear_reset_token()
                db.session.commit()
                tracker.reset(user.employee_number)
                return jsonify({
                    'error': 'Invalid or expired reset code. Reset token invalidated after multiple failed attempts.'
                }), 400

            return jsonify({
                'error': 'Invalid or expired reset code',
                'attempts_remaining': remaining_attempts,
                'retry_after': delay_seconds
            }), 400

        # Validate password strength
        is_valid, errors = password_utils.validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': 'Password does not meet security requirements', 'details': errors}), 400

        if hasattr(user, 'is_password_reused') and user.is_password_reused(data['new_password']):
            return jsonify({'error': 'New password cannot match any of your last 5 passwords'}), 400

        # Update password
        user.set_password(data['new_password'])
        user.clear_reset_token()
        if hasattr(user, 'force_password_change'):
            user.force_password_change = False
        db.session.commit()

        # Successful reset clears any tracking
        tracker.reset(user.employee_number)

        # Log the password reset
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_reset',
            description='Password reset completed',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    @app.route('/api/auth/user', methods=['GET'])
    @login_required
    def get_profile():
        # Get user_id from JWT token
        user = User.query.get(request.current_user['user_id'])
        return jsonify(user.to_dict(include_roles=True, include_permissions=True)), 200

    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        # Get user_id from JWT token
        user = User.query.get(request.current_user['user_id'])
        data = request.get_json() or {}

        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'department' in data:
            user.department = data['department']
        if 'avatar' in data:
            user.avatar = data['avatar']

        db.session.commit()

        # Log the profile update
        activity = UserActivity(
            user_id=user.id,
            activity_type='profile_update',
            description='Profile information updated',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify(user.to_dict()), 200

    @app.route('/api/user/avatar', methods=['POST'])
    @login_required
    def upload_avatar():
        # Get user_id from JWT token
        user = User.query.get(request.current_user['user_id'])

        if 'avatar' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['avatar']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            try:
                max_size = current_app.config.get('MAX_AVATAR_FILE_SIZE')
                safe_filename = validate_image_upload(file, max_size=max_size)
            except FileValidationError as exc:
                return jsonify({'error': str(exc)}), getattr(exc, 'status_code', 400)

            avatar_dir = os.path.join(current_app.static_folder, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)

            file_path = os.path.join(avatar_dir, safe_filename)
            file.save(file_path)

            # Update user's avatar field with the relative path
            avatar_url = f"/api/static/avatars/{safe_filename}"
            user.avatar = avatar_url
            db.session.commit()

            # Log the avatar update
            activity = UserActivity(
                user_id=user.id,
                activity_type='avatar_update',
                description='Profile avatar updated',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'message': 'Avatar uploaded successfully',
                'avatar': avatar_url
            }), 200

        return jsonify({'error': 'Failed to upload avatar'}), 400

    @app.route('/api/user/password', methods=['PUT'])
    @login_required
    def change_password():
        # Get user_id from JWT token
        user = User.query.get(request.current_user['user_id'])
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Validate password strength
        is_valid, errors = password_utils.validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': 'Password does not meet security requirements', 'details': errors}), 400

        if hasattr(user, 'is_password_reused') and user.is_password_reused(data['new_password']):
            return jsonify({'error': 'New password cannot match any of your last 5 passwords'}), 400

        # Update password
        user.set_password(data['new_password'])
        if hasattr(user, 'force_password_change'):
            user.force_password_change = False
        db.session.commit()

        # Log the password change
        activity = UserActivity(
            user_id=user.id,
            activity_type='password_change',
            description='Password changed',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    @app.route('/api/user/activity', methods=['GET'])
    @login_required
    def get_user_activity():
        # Get user_id from JWT token
        user_id = request.current_user['user_id']
        activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).limit(50).all()
        return jsonify([activity.to_dict() for activity in activities]), 200

    @app.route('/api/tools/search', methods=['GET'])
    def search_tools():
        # Get search query from request parameters
        query = request.args.get('q', '')
        logger.debug("Tools search endpoint called", extra={'has_query': bool(query)})

        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        # Convert query to lowercase for case-insensitive search
        search_term = f'%{query.lower()}%'

        # Search in tool_number, serial_number, description, and location
        try:
            tools = Tool.query.filter(
                db.or_(
                    db.func.lower(Tool.tool_number).like(search_term),
                    db.func.lower(Tool.serial_number).like(search_term),
                    db.func.lower(Tool.description).like(search_term),
                    db.func.lower(Tool.location).like(search_term)
                )
            ).all()
            logger.debug("Tools search results", extra={'result_count': len(tools)})
        except Exception as e:
            logger.exception("Error during tools search endpoint")
            return jsonify({'error': 'Search error'}), 500

        # Get checkout status for each tool
        tool_status = {}
        active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()

        for checkout in active_checkouts:
            tool_status[checkout.tool_id] = 'checked_out'

        # Format the results
        result = [{
            'id': t.id,
            'tool_number': t.tool_number,
            'serial_number': t.serial_number,
            'description': t.description,
            'condition': t.condition,
            'location': t.location,
            'category': getattr(t, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
            'status': tool_status.get(t.id, getattr(t, 'status', 'available')),  # Use 'available' if status attribute doesn't exist
            'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
            'created_at': t.created_at.isoformat()
        } for t in tools]

        return jsonify(result)

    @app.route('/api/tools/new', methods=['GET'])
    @tool_manager_required
    def get_new_tool_form():
        # This endpoint returns the form data needed to create a new tool
        # It can include any default values or validation rules
        return jsonify({
            'form_fields': [
                {'name': 'tool_number', 'type': 'text', 'required': True, 'label': 'Tool Number'},
                {'name': 'serial_number', 'type': 'text', 'required': True, 'label': 'Serial Number'},
                {'name': 'description', 'type': 'text', 'required': False, 'label': 'Description'},
                {'name': 'condition', 'type': 'select', 'required': False, 'label': 'Condition',
                 'options': ['New', 'Good', 'Fair', 'Poor']},
                {'name': 'location', 'type': 'text', 'required': False, 'label': 'Location'}
            ]
        }), 200

    @app.route('/api/tools/new/checkouts', methods=['GET'])
    @login_required
    def get_new_tool_checkouts():
        # This endpoint returns checkout history for a new tool (which should be empty)
        return jsonify([]), 200

    @app.route('/api/checkouts/user', methods=['GET'])
    @login_required
    def get_user_checkouts():
        # Get the current user's checkouts from JWT token
        user_id = request.current_user['user_id']

        # Get all checkouts for the user (both active and past)
        checkouts = Checkout.query.filter_by(user_id=user_id).all()

        return jsonify([{
            'id': c.id,
            'tool_id': c.tool_id,
            'tool_number': c.tool.tool_number if c.tool else 'Unknown',
            'serial_number': c.tool.serial_number if c.tool else 'Unknown',
            'description': c.tool.description if c.tool else '',
            'status': 'Checked Out' if not c.return_date else 'Returned',
            'checkout_date': c.checkout_date.isoformat(),
            'return_date': c.return_date.isoformat() if c.return_date else None,
            'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None
        } for c in checkouts]), 200

    @app.route('/api/checkouts/overdue', methods=['GET'])
    @tool_manager_required
    def get_overdue_checkouts():
        # Get all overdue checkouts (expected_return_date < current date and not returned)
        now = datetime.now()
        overdue_checkouts = Checkout.query.filter(
            Checkout.return_date.is_(None),
            Checkout.expected_return_date < now
        ).all()

        result = []
        for c in overdue_checkouts:
            # Calculate days overdue
            expected_date = c.expected_return_date
            days_overdue = (now - expected_date).days if expected_date else 0

            result.append({
                'id': c.id,
                'tool_id': c.tool_id,
                'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                'serial_number': c.tool.serial_number if c.tool else 'Unknown',
                'description': c.tool.description if c.tool else '',
                'user_id': c.user_id,
                'user_name': c.user.name if c.user else 'Unknown',
                'checkout_date': c.checkout_date.isoformat(),
                'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                'days_overdue': days_overdue
            })

        return jsonify(result), 200

    @app.route('/api/analytics/usage', methods=['GET'])
    @tool_manager_required
    def get_usage_analytics():
        try:
            # Get timeframe parameter (default to 'week')
            timeframe = request.args.get('timeframe', 'week')

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = now - timedelta(days=90)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(weeks=1)  # Default to week

            # Initialize response data structure
            response_data = {
                'timeframe': timeframe,
                'checkoutsByDepartment': [],
                'checkoutsByDay': [],
                'toolUsageByCategory': [],
                'mostFrequentlyCheckedOut': [],
                'overallStats': {}
            }

            # 1. Get checkouts by department
            try:
                from sqlalchemy import func

                # Query to get checkout counts by department
                dept_checkouts = db.session.query(
                    User.department.label('department'),
                    func.count(Checkout.id).label('count')
                ).join(
                    User, User.id == Checkout.user_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    User.department
                ).all()

                # Format the results for the frontend
                dept_data = [{
                    'name': dept.department or 'Unknown',
                    'value': dept.count
                } for dept in dept_checkouts]

                response_data['checkoutsByDepartment'] = dept_data
            except Exception as e:
                logger.exception("Error getting department data")
                # Continue with other queries even if this one fails

            # 2. Get daily checkout and return data
            try:
                # Get checkouts by day
                daily_checkouts = db.session.query(
                    func.date(Checkout.checkout_date).label('date'),
                    func.count().label('count')
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    func.date(Checkout.checkout_date)
                ).all()

                # Get returns by day
                daily_returns = db.session.query(
                    func.date(Checkout.return_date).label('date'),
                    func.count().label('count')
                ).filter(
                    Checkout.return_date >= start_date
                ).group_by(
                    func.date(Checkout.return_date)
                ).all()

                # Create a dictionary to store daily data
                daily_data_dict = {}

                # Process checkout data
                for day in daily_checkouts:
                    date_str = str(day.date)
                    weekday = datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')

                    if date_str not in daily_data_dict:
                        daily_data_dict[date_str] = {
                            'name': weekday,
                            'date': date_str,
                            'checkouts': 0,
                            'returns': 0
                        }

                    daily_data_dict[date_str]['checkouts'] = day.count

                # Process return data
                for day in daily_returns:
                    if day.date:  # Ensure date is not None
                        date_str = str(day.date)
                        weekday = datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')

                        if date_str not in daily_data_dict:
                            daily_data_dict[date_str] = {
                                'name': weekday,
                                'date': date_str,
                                'checkouts': 0,
                                'returns': 0
                            }

                        daily_data_dict[date_str]['returns'] = day.count

                # Convert dictionary to sorted list
                daily_data = sorted(daily_data_dict.values(), key=lambda x: x['date'])

                response_data['checkoutsByDay'] = daily_data
            except Exception as e:
                logger.exception("Error getting daily checkout data")
                # Continue with other queries even if this one fails

            # 3. Get tool usage by category
            try:
                # First, get all tools with their checkout counts
                tool_usage = db.session.query(
                    Tool.id,
                    Tool.tool_number,
                    Tool.description,
                    func.count(Checkout.id).label('checkout_count')
                ).join(
                    Checkout, Tool.id == Checkout.tool_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    Tool.id
                ).all()

                # Categorize tools based on their tool number or description
                category_counts = {}

                for tool in tool_usage:
                    # Determine category from tool number prefix or description
                    category = get_category_name(tool.tool_number[:3] if tool.tool_number else '')

                    if category not in category_counts:
                        category_counts[category] = 0

                    category_counts[category] += tool.checkout_count

                # Convert to list format for the frontend
                category_data = [{'name': cat, 'checkouts': count} for cat, count in category_counts.items()]

                # Sort by checkout count (descending)
                category_data.sort(key=lambda x: x['checkouts'], reverse=True)

                response_data['toolUsageByCategory'] = category_data
            except Exception as e:
                logger.exception("Error getting tool usage by category")
                # Continue with other queries even if this one fails

            # 4. Get most frequently checked out tools
            try:
                top_tools = db.session.query(
                    Tool.id,
                    Tool.tool_number,
                    Tool.description,
                    func.count(Checkout.id).label('checkout_count')
                ).join(
                    Checkout, Tool.id == Checkout.tool_id
                ).filter(
                    Checkout.checkout_date >= start_date
                ).group_by(
                    Tool.id
                ).order_by(
                    func.count(Checkout.id).desc()
                ).limit(5).all()

                top_tools_data = [{
                    'id': tool.id,
                    'tool_number': tool.tool_number,
                    'description': tool.description or '',
                    'checkouts': tool.checkout_count
                } for tool in top_tools]

                response_data['mostFrequentlyCheckedOut'] = top_tools_data
            except Exception as e:
                logger.exception("Error getting top tools data")
                # Continue with other queries even if this one fails

            # 5. Get overall statistics
            try:
                # Total checkouts in period
                total_checkouts = Checkout.query.filter(
                    Checkout.checkout_date >= start_date
                ).count()

                # Total returns in period
                total_returns = Checkout.query.filter(
                    Checkout.return_date >= start_date
                ).count()

                # Currently checked out
                currently_checked_out = Checkout.query.filter(
                    Checkout.return_date.is_(None)
                ).count()

                # Average checkout duration (for returned items)
                from sqlalchemy import func, extract

                avg_duration_query = db.session.query(
                    func.avg(
                        func.julianday(Checkout.return_date) - func.julianday(Checkout.checkout_date)
                    ).label('avg_days')
                ).filter(
                    Checkout.checkout_date >= start_date,
                    Checkout.return_date.isnot(None)
                ).scalar()

                avg_duration = round(float(avg_duration_query or 0), 1)

                # Overdue checkouts
                overdue_count = Checkout.query.filter(
                    Checkout.return_date.is_(None),
                    Checkout.expected_return_date < now
                ).count()

                response_data['overallStats'] = {
                    'totalCheckouts': total_checkouts,
                    'totalReturns': total_returns,
                    'currentlyCheckedOut': currently_checked_out,
                    'averageDuration': avg_duration,
                    'overdueCount': overdue_count
                }
            except Exception as e:
                logger.exception("Error getting overall checkout stats")
                # Continue even if this query fails

            return jsonify(response_data), 200

        except Exception as e:
            logger.exception("Error in analytics endpoint")
            return jsonify({
                'error': 'An error occurred while generating analytics data'
            }), 500

    # Helper function for analytics
    def get_category_name(code):
        """Convert category code to readable name"""
        categories = {
            'DRL': 'Power Tools',
            'SAW': 'Power Tools',
            'WRN': 'Hand Tools',
            'PLR': 'Hand Tools',
            'HAM': 'Hand Tools',
            'MSR': 'Measurement',
            'SFT': 'Safety Equipment',
            'ELC': 'Electrical',
            'PLM': 'Plumbing',
            'WLD': 'Welding'
        }
        return categories.get(code, 'Other')

    @app.route('/api/tools/<int:id>/checkouts', methods=['GET'])
    def get_tool_checkouts(id):
        # Get checkout history for a specific tool
        tool = Tool.query.get_or_404(id)
        checkouts = Checkout.query.filter_by(tool_id=id).order_by(Checkout.checkout_date.desc()).all()

        return jsonify([{
            'id': c.id,
            'user_id': c.user_id,
            'user_name': c.user.name if c.user else 'Unknown',
            'user_department': c.user.department if c.user else 'Unknown',
            'checkout_date': c.checkout_date.isoformat(),
            'return_date': c.return_date.isoformat() if c.return_date else None,
            'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
            'condition_at_return': getattr(c, 'return_condition', None),
            'returned_by': getattr(c, 'returned_by', None),
            'found': getattr(c, 'found', None),
            'return_notes': getattr(c, 'return_notes', None),
            'is_overdue': c.return_date is None and c.expected_return_date and c.expected_return_date < datetime.now(),
            'duration_days': (c.return_date - c.checkout_date).days if c.return_date else None,
            'status': 'Returned' if c.return_date else ('Overdue' if c.expected_return_date and c.expected_return_date < datetime.now() else 'Checked Out')
        } for c in checkouts]), 200

    @app.route('/api/checkouts/<int:id>/details', methods=['GET'])
    def get_checkout_details(id):
        """Get detailed information about a specific checkout transaction."""
        checkout = Checkout.query.get_or_404(id)

        # Get tool and user information
        tool = checkout.tool
        user = checkout.user

        # Calculate duration if returned
        duration_days = None
        if checkout.return_date:
            duration_days = (checkout.return_date - checkout.checkout_date).days

        # Check if overdue
        is_overdue = (checkout.return_date is None and
                     checkout.expected_return_date and
                     checkout.expected_return_date < datetime.now())

        return jsonify({
            'id': checkout.id,
            'tool': {
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'category': tool.category,
                'location': tool.location
            } if tool else None,
            'user': {
                'id': user.id,
                'name': user.name,
                'employee_number': user.employee_number,
                'department': user.department
            } if user else None,
            'checkout_date': checkout.checkout_date.isoformat(),
            'return_date': checkout.return_date.isoformat() if checkout.return_date else None,
            'expected_return_date': checkout.expected_return_date.isoformat() if checkout.expected_return_date else None,
            'condition_at_return': getattr(checkout, 'return_condition', None),
            'returned_by': getattr(checkout, 'returned_by', None),
            'found': getattr(checkout, 'found', None),
            'return_notes': getattr(checkout, 'return_notes', None),
            'duration_days': duration_days,
            'is_overdue': is_overdue,
            'status': 'Returned' if checkout.return_date else ('Overdue' if is_overdue else 'Checked Out')
        }), 200

    @app.route('/api/tools/<int:id>/service/remove', methods=['POST'])
    @tool_manager_required
    def remove_tool_from_service(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Check if tool is already out of service
            if tool.status in ['maintenance', 'retired']:
                return jsonify({'error': f'Tool is already out of service with status: {tool.status}'}), 400

            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()
            if active_checkout:
                return jsonify({'error': 'Cannot remove a tool that is currently checked out'}), 400

            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['action_type', 'reason']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate action type
            action_type = data.get('action_type')
            if action_type not in ['remove_maintenance', 'remove_permanent']:
                return jsonify({'error': 'Invalid action type. Must be "remove_maintenance" or "remove_permanent"'}), 400

            # Update tool status
            if action_type == 'remove_maintenance':
                tool.status = 'maintenance'
            else:  # remove_permanent
                tool.status = 'retired'

            tool.status_reason = data.get('reason')

            # Create service record (use user_id from JWT token)
            service_record = ToolServiceRecord(
                tool_id=id,
                user_id=request.current_user['user_id'],
                action_type=action_type,
                reason=data.get('reason'),
                comments=data.get('comments', '')
            )

            # Create audit log (use user info from JWT token)
            user_payload = request.current_user
            log = AuditLog(
                action_type=action_type,
                action_details=f'User {user_payload.get("user_name", "Unknown")} (ID: {user_payload["user_id"]}) removed tool {tool.tool_number} (ID: {id}) from service. Reason: {data.get("reason")}'
            )

            # Create user activity
            activity = UserActivity(
                user_id=user_payload['user_id'],
                activity_type=action_type,
                description=f'Removed tool {tool.tool_number} from service',
                ip_address=request.remote_addr
            )

            # Save changes
            db.session.add(service_record)
            db.session.add(log)
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'status': tool.status,
                'status_reason': tool.status_reason,
                'message': f'Tool successfully removed from service with status: {tool.status}'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.exception("Error removing tool from service", extra={'tool_id': id})
            return jsonify({'error': 'An error occurred while updating tool service status'}), 500

    @app.route('/api/tools/<int:id>/service/return', methods=['POST'])
    @tool_manager_required
    def return_tool_to_service(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Check if tool is out of service
            if tool.status not in ['maintenance', 'retired']:
                return jsonify({'error': f'Tool is not out of service. Current status: {tool.status}'}), 400

            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('reason'):
                return jsonify({'error': 'Missing required field: reason'}), 400

            # Update tool status
            tool.status = 'available'
            tool.status_reason = None

            # Create service record (use user_id from JWT token)
            user_payload = request.current_user
            service_record = ToolServiceRecord(
                tool_id=id,
                user_id=user_payload['user_id'],
                action_type='return_service',
                reason=data.get('reason'),
                comments=data.get('comments', '')
            )

            # Create audit log
            log = AuditLog(
                action_type='return_service',
                action_details=f'User {user_payload.get("user_name", "Unknown")} (ID: {user_payload["user_id"]}) returned tool {tool.tool_number} (ID: {id}) to service. Reason: {data.get("reason")}'
            )

            # Create user activity
            activity = UserActivity(
                user_id=user_payload['user_id'],
                activity_type='return_service',
                description=f'Returned tool {tool.tool_number} to service',
                ip_address=request.remote_addr
            )

            # Save changes
            db.session.add(service_record)
            db.session.add(log)
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'status': tool.status,
                'message': 'Tool successfully returned to service'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.exception("Error returning tool to service", extra={'tool_id': id})
            return jsonify({'error': 'An error occurred while returning the tool to service'}), 500

    @app.route('/api/tools/<int:id>/service/history', methods=['GET'])
    def get_tool_service_history(id):
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get service history
            service_records = ToolServiceRecord.query.filter_by(tool_id=id).order_by(
                ToolServiceRecord.timestamp.desc()
            ).offset(offset).limit(limit).all()

            return jsonify([record.to_dict() for record in service_records]), 200

        except Exception as e:
            logger.exception("Error getting tool service history", extra={'tool_id': id})
            return jsonify({'error': 'An error occurred while retrieving tool service history'}), 500
