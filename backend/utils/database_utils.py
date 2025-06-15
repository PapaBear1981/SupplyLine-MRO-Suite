"""
Database Transaction Utilities

This module provides utilities for safe database operations with proper
transaction management, rollback handling, and connection management.
"""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from flask import g
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from backend.models import db
from .logging_utils import log_database_operation

logger = logging.getLogger(__name__)


@contextmanager
def database_transaction():
    """
    Context manager for database transactions with automatic rollback.

    Usage:
        with database_transaction():
            # Database operations here
            db.session.add(object)
            # Automatic commit on success, rollback on exception
    """
    start_time = time.time()

    try:
        # Begin transaction (SQLAlchemy handles this automatically)
        yield db.session

        # Commit if no exceptions
        db.session.commit()

        duration = (time.time() - start_time) * 1000
        log_database_operation('TRANSACTION', 'multiple_tables', duration)

    except Exception as e:
        # Rollback on any exception
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error("Transaction failed, rolled back", extra={
            'operation': 'database_transaction',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'duration_ms': round(duration, 2)
        })

        raise


def transactional(f):
    """
    Decorator to wrap function in a database transaction.

    Usage:
        @transactional
        def my_function():
            # Database operations here
            # Automatic commit/rollback
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with database_transaction():
            return f(*args, **kwargs)
    return wrapper


def safe_add_and_commit(obj, operation_name="add_object"):
    """
    Safely add an object to the database with proper error handling.

    Args:
        obj: SQLAlchemy model instance to add
        operation_name: Name of the operation for logging

    Returns:
        bool: True if successful, False otherwise
    """
    start_time = time.time()

    try:
        db.session.add(obj)
        db.session.commit()

        duration = (time.time() - start_time) * 1000
        log_database_operation('INSERT', obj.__tablename__, duration, 1)

        logger.debug(f"Successfully added {obj.__class__.__name__}", extra={
            'operation': operation_name,
            'table': obj.__tablename__,
            'object_id': getattr(obj, 'id', None)
        })

        return True

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error("Failed to add %s", obj.__class__.__name__, extra={
            'operation': operation_name,
            'table': obj.__tablename__,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'duration_ms': round(duration, 2)
        })

        return False


def safe_update_and_commit(obj, operation_name="update_object"):
    """
    Safely update an object in the database with proper error handling.

    Args:
        obj: SQLAlchemy model instance to update
        operation_name: Name of the operation for logging

    Returns:
        bool: True if successful, False otherwise
    """
    start_time = time.time()

    try:
        db.session.commit()

        duration = (time.time() - start_time) * 1000
        log_database_operation('UPDATE', obj.__tablename__, duration, 1)

        logger.debug("Successfully updated %s", obj.__class__.__name__, extra={
            'operation': operation_name,
            'table': obj.__tablename__,
            'object_id': getattr(obj, 'id', None)
        })

        return True

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error("Failed to update %s", obj.__class__.__name__, extra={
            'operation': operation_name,
            'table': obj.__tablename__,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'duration_ms': round(duration, 2)
        })

        return False


def safe_delete_and_commit(obj, operation_name="delete_object"):
    """
    Safely delete an object from the database with proper error handling.

    Args:
        obj: SQLAlchemy model instance to delete
        operation_name: Name of the operation for logging

    Returns:
        bool: True if successful, False otherwise
    """
    start_time = time.time()
    object_id = getattr(obj, 'id', None)
    table_name = obj.__tablename__
    class_name = obj.__class__.__name__

    try:
        db.session.delete(obj)
        db.session.commit()

        duration = (time.time() - start_time) * 1000
        log_database_operation('DELETE', table_name, duration, 1)

        logger.debug("Successfully deleted %s", class_name, extra={
            'operation': operation_name,
            'table': table_name,
            'object_id': object_id
        })

        return True

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error("Failed to delete %s", class_name, extra={
            'operation': operation_name,
            'table': table_name,
            'object_id': object_id,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'duration_ms': round(duration, 2)
        })

        return False


def bulk_insert_with_rollback(model_class, data_list, operation_name="bulk_insert"):
    """
    Safely perform bulk insert with proper error handling.

    Args:
        model_class: SQLAlchemy model class
        data_list: List of dictionaries with data to insert
        operation_name: Name of the operation for logging

    Returns:
        tuple: (success: bool, inserted_count: int)
    """
    start_time = time.time()

    try:
        db.session.bulk_insert_mappings(model_class, data_list)
        db.session.commit()

        duration = (time.time() - start_time) * 1000
        log_database_operation('BULK_INSERT', model_class.__tablename__, duration, len(data_list))

        logger.info("Successfully bulk inserted %d %s records", len(data_list), model_class.__name__, extra={
            'operation': operation_name,
            'table': model_class.__tablename__,
            'record_count': len(data_list)
        })

        return True, len(data_list)

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error("Failed to bulk insert %s records", model_class.__name__, extra={
            'operation': operation_name,
            'table': model_class.__tablename__,
            'record_count': len(data_list),
            'error_type': type(e).__name__,
            'error_message': str(e),
            'duration_ms': round(duration, 2)
        })

        return False, 0


def get_connection_stats():
    """
    Get database connection statistics.

    Returns:
        dict: Connection pool statistics
    """
    try:
        engine = db.engine
        pool = engine.pool

        # Check if pool has the required methods (not available for NullPool/SingletonThreadPool)
        stats = {}
        if hasattr(pool, 'size'):
            stats['pool_size'] = pool.size()
        if hasattr(pool, 'checkedin'):
            stats['checked_in'] = pool.checkedin()
        if hasattr(pool, 'checkedout'):
            stats['checked_out'] = pool.checkedout()
        if hasattr(pool, 'overflow'):
            stats['overflow'] = pool.overflow()
        if hasattr(pool, 'invalid'):
            stats['invalid'] = pool.invalid()

        # Calculate total if we have the required values
        if 'pool_size' in stats and 'overflow' in stats:
            stats['total_connections'] = stats['pool_size'] + stats['overflow']

        return stats
    except Exception as e:
        logger.error("Error getting connection stats: %s", e)
        return {'error': str(e)}


def check_database_health():
    """
    Check database health and connection status.

    Returns:
        dict: Database health status
    """
    try:
        # Simple query to test connection
        start_time = time.time()
        db.session.execute(text("SELECT 1"))
        duration = (time.time() - start_time) * 1000

        connection_stats = get_connection_stats()

        return {
            'healthy': True,
            'response_time_ms': round(duration, 2),
            'connection_stats': connection_stats
        }

    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return {
            'healthy': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


@contextmanager
def db_connection_cleanup():
    """
    Context manager to ensure database connections are properly cleaned up.

    Usage:
        with db_connection_cleanup():
            # Database operations
            # Connection automatically cleaned up
    """
    try:
        yield
    finally:
        # Ensure connection is returned to pool
        if hasattr(g, 'db_connection'):
            try:
                g.db_connection.close()
                delattr(g, 'db_connection')
            except Exception as e:
                logger.warning("Error closing database connection: %s", e)

        # Remove any session from Flask g
        db.session.remove()
