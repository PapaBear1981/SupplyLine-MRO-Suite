"""
Bulk Operations Utility

This module provides utilities for performing bulk database operations
to improve performance and avoid N+1 query problems.
"""

import logging
from datetime import datetime, timedelta, timezone
from models import db, UserActivity, AuditLog, Tool, Chemical
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


def bulk_log_activities(activities):
    """
    Log multiple activities in a single transaction

    Args:
        activities (list): List of activity dictionaries with keys:
            - user_id: User ID
            - activity_type: Type of activity
            - description: Activity description
            - timestamp: Optional timestamp (defaults to current time)
    """
    if not activities:
        return

    # Ensure all activities have timestamps
    for activity in activities:
        if 'timestamp' not in activity:
            activity['timestamp'] = datetime.now(timezone.utc)

    try:
        db.session.bulk_insert_mappings(UserActivity, activities)
        db.session.commit()
        logger.info(f"Bulk logged {len(activities)} user activities")
    except Exception as e:
        logger.error(f"Error bulk logging activities: {str(e)}")
        db.session.rollback()
        raise


def bulk_log_audit_events(audit_logs):
    """
    Log multiple audit events in a single transaction

    Args:
        audit_logs (list): List of audit log dictionaries with keys:
            - action_type: Type of action
            - action_details: Details of the action
            - timestamp: Optional timestamp (defaults to current time)
    """
    if not audit_logs:
        return

    # Ensure all logs have timestamps
    for log in audit_logs:
        if 'timestamp' not in log:
            log['timestamp'] = datetime.now(timezone.utc)

    try:
        db.session.bulk_insert_mappings(AuditLog, audit_logs)
        db.session.commit()
        logger.info(f"Bulk logged {len(audit_logs)} audit events")
    except Exception as e:
        logger.error(f"Error bulk logging audit events: {str(e)}")
        db.session.rollback()
        raise


def bulk_update_tool_calibration_status():
    """
    Update calibration status for all tools in a single operation
    instead of individual updates
    """
    try:
        now = datetime.now()

        # Update overdue calibrations
        overdue_count = db.session.query(Tool).filter(
            and_(
                Tool.next_calibration_date < now,
                Tool.calibration_status != 'overdue'
            )
        ).update(
            {Tool.calibration_status: 'overdue'},
            synchronize_session=False
        )

        # Update due soon calibrations (within 30 days)
        due_soon_date = now + timedelta(days=30)
        due_soon_count = db.session.query(Tool).filter(
            and_(
                Tool.next_calibration_date.between(now, due_soon_date),
                Tool.calibration_status != 'due_soon'
            )
        ).update(
            {Tool.calibration_status: 'due_soon'},
            synchronize_session=False
        )

        # Update current calibrations
        current_count = db.session.query(Tool).filter(
            and_(
                Tool.next_calibration_date > due_soon_date,
                Tool.calibration_status != 'current'
            )
        ).update(
            {Tool.calibration_status: 'current'},
            synchronize_session=False
        )

        logger.info(f"Bulk updated calibration status: {overdue_count} overdue, {due_soon_count} due soon, {current_count} current")

        return {
            'overdue': overdue_count,
            'due_soon': due_soon_count,
            'current': current_count
        }

    except Exception as e:
        logger.error(f"Error bulk updating tool calibration status: {str(e)}")
        raise


def bulk_update_chemical_status():
    """
    Update chemical status for all chemicals in a single operation
    """
    try:
        now = datetime.now(timezone.utc)

        # Update expired chemicals
        expired_count = db.session.query(Chemical).filter(
            and_(
                Chemical.expiration_date < now,
                Chemical.status != 'expired',
                Chemical.is_archived.is_(False)
            )
        ).update(
            {Chemical.status: 'expired'},
            synchronize_session=False
        )

        # Update out of stock chemicals
        out_of_stock_count = db.session.query(Chemical).filter(
            and_(
                Chemical.quantity <= 0,
                Chemical.status != 'out_of_stock',
                Chemical.is_archived.is_(False)
            )
        ).update(
            {Chemical.status: 'out_of_stock'},
            synchronize_session=False
        )

        logger.info(f"Bulk updated chemical status: {expired_count} expired, {out_of_stock_count} out of stock")

        return {
            'expired': expired_count,
            'out_of_stock': out_of_stock_count
        }

    except Exception as e:
        logger.error(f"Error bulk updating chemical status: {str(e)}")
        raise


def get_dashboard_stats_optimized():
    """
    Get dashboard statistics using optimized queries instead of multiple separate queries
    """
    try:
        from models import User, Checkout

        # Single query to get tool counts
        tool_stats = db.session.query(
            func.count(Tool.id).label('total_tools'),
            func.sum(func.case((Tool.status == 'available', 1), else_=0)).label('available_tools'),
            func.sum(func.case((Tool.status == 'checked_out', 1), else_=0)).label('checked_out_tools'),
            func.sum(func.case((Tool.calibration_status == 'overdue', 1), else_=0)).label('overdue_calibrations')
        ).first()

        # Single query to get user counts
        user_stats = db.session.query(
            func.count(User.id).label('total_users'),
            func.sum(func.case((User.is_active == True, 1), else_=0)).label('active_users')
        ).first()

        # Single query to get checkout counts
        checkout_stats = db.session.query(
            func.count(Checkout.id).label('total_checkouts'),
            func.sum(func.case((Checkout.return_date.is_(None), 1), else_=0)).label('active_checkouts')
        ).first()

        # Get chemical stats
        chemical_stats = db.session.query(
            func.count(Chemical.id).label('total_chemicals'),
            func.sum(func.case((Chemical.status == 'expired', 1), else_=0)).label('expired_chemicals'),
            func.sum(func.case((Chemical.status == 'low_stock', 1), else_=0)).label('low_stock_chemicals')
        ).filter(Chemical.is_archived.is_(False)).first()

        return {
            'users': {
                'total': user_stats.total_users or 0,
                'active': user_stats.active_users or 0
            },
            'tools': {
                'total': tool_stats.total_tools or 0,
                'available': tool_stats.available_tools or 0,
                'checked_out': tool_stats.checked_out_tools or 0,
                'overdue_calibrations': tool_stats.overdue_calibrations or 0
            },
            'checkouts': {
                'total': checkout_stats.total_checkouts or 0,
                'active': checkout_stats.active_checkouts or 0
            },
            'chemicals': {
                'total': chemical_stats.total_chemicals or 0,
                'expired': chemical_stats.expired_chemicals or 0,
                'low_stock': chemical_stats.low_stock_chemicals or 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting optimized dashboard stats: {str(e)}")
        raise


def get_tools_with_relationships(filters=None):
    """
    Get tools with eager loading of relationships to avoid N+1 queries

    Args:
        filters (dict): Optional filters to apply
    """
    try:
        query = Tool.query.options(
            joinedload(Tool.checkouts),
            joinedload(Tool.calibrations),
            joinedload(Tool.service_records)
        )

        if filters:
            if 'status' in filters:
                query = query.filter(Tool.status == filters['status'])
            if 'category' in filters:
                query = query.filter(Tool.category == filters['category'])
            if 'location' in filters:
                query = query.filter(Tool.location == filters['location'])

        return query.all()

    except Exception as e:
        logger.error(f"Error getting tools with relationships: {str(e)}")
        raise


def get_chemicals_with_relationships(filters=None):
    """
    Get chemicals with eager loading of relationships to avoid N+1 queries

    Args:
        filters (dict): Optional filters to apply
    """
    try:
        query = Chemical.query.options(
            joinedload(Chemical.issuances)
        )

        # Apply archived filter based on show_archived parameter
        if filters and filters.get('show_archived'):
            # Show archived chemicals - no filter needed
            pass
        else:
            # Default filter for non-archived chemicals
            query = query.filter(Chemical.is_archived.is_(False))

        if filters:
            if 'status' in filters:
                query = query.filter(Chemical.status == filters['status'])
            if 'category' in filters:
                query = query.filter(Chemical.category == filters['category'])

        return query.all()

    except Exception as e:
        logger.error(f"Error getting chemicals with relationships: {str(e)}")
        raise


def optimize_database_queries():
    """
    Run optimization tasks to improve database performance
    """
    try:
        results = {}

        # Update tool calibration status
        results['calibration_updates'] = bulk_update_tool_calibration_status()

        # Update chemical status
        results['chemical_updates'] = bulk_update_chemical_status()

        # Commit all changes
        db.session.commit()

        logger.info("Database optimization completed successfully")
        return results

    except Exception as e:
        logger.error(f"Error during database optimization: {str(e)}")
        db.session.rollback()
        raise
