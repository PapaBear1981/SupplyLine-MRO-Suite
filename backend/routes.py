from flask import request, jsonify, current_app, session
from models import db, Tool, User, Checkout, AuditLog, UserActivity, ToolServiceRecord, Chemical
from models import ToolCalibration, ToolCalibrationStandard
from datetime import datetime, timedelta, timezone
import secrets
import string
import os
import uuid
import time
from werkzeug.utils import secure_filename
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
from routes_modules.health import register_health_routes
from routes_modules.admin import register_admin_routes
from routes_modules.tools import register_tool_routes
from routes_modules.users import register_user_routes
from routes_modules.checkouts import register_checkout_routes
from auth import login_required, admin_required, tool_manager_required, materials_manager_required
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
import logging

logger = logging.getLogger(__name__)

# Authentication decorators are now imported from auth module

def register_routes(app):
    db.init_app(app)
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

    # Register health and system monitoring routes
    register_health_routes(app)

    # Register admin dashboard routes
    register_admin_routes(app)

    # Register tool management routes
    register_tool_routes(app)

    # Register user management routes
    register_user_routes(app)

    # Register checkout and return routes
    register_checkout_routes(app)

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

    # Chemical management endpoints moved to routes_chemicals.py

    # Health and system monitoring endpoints moved to routes/health.py

    # Admin dashboard endpoints moved to routes/admin.py

    # System resources endpoint moved to routes/health.py

    # Tool management endpoints moved to routes/tools.py

    # Individual tool management endpoints moved to routes/tools.py

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
            print(f"Error getting calibration notifications: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # User management endpoints moved to routes/users.py

    # Checkout and return management endpoints moved to routes/checkouts.py

    # Return route moved to routes/checkouts.py

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

    # User audit logs endpoint moved to routes/users.py

    # Tool audit logs endpoint moved to routes_modules/tools.py

    # Logout and auth status endpoints removed - using JWT-based versions from routes_auth.py

    # All auth-related endpoints moved to routes_auth.py for JWT-based authentication

    # User profile endpoints moved to routes_auth.py for JWT-based authentication

    # Tool search and form endpoints moved to routes/tools.py

    # User checkouts and overdue checkouts endpoints moved to routes/checkouts.py

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
                print(f"Error getting department data: {str(e)}")
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
                print(f"Error getting daily data: {str(e)}")
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
                print(f"Error getting category data: {str(e)}")
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
                print(f"Error getting top tools data: {str(e)}")
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
                print(f"Error getting overall stats: {str(e)}")
                # Continue even if this query fails

            return jsonify(response_data), 200

        except Exception as e:
            print(f"Error in analytics endpoint: {str(e)}")
            return jsonify({
                'error': 'An error occurred while generating analytics data',
                'message': str(e)
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

    # Tool checkout history and checkout details endpoints moved to routes/checkouts.py

    # Tool service management endpoints moved to routes_modules/tools.py

    # Tool service history endpoint moved to routes_modules/tools.py