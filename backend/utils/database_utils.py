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
from models import db
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
        logger.error(f"Failed to add {obj.__class__.__name__}", extra={
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

        logger.debug(f"Successfully updated {obj.__class__.__name__}", extra={
            'operation': operation_name,
            'table': obj.__tablename__,
            'object_id': getattr(obj, 'id', None)
        })

        return True

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error(f"Failed to update {obj.__class__.__name__}", extra={
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

        logger.debug(f"Successfully deleted {class_name}", extra={
            'operation': operation_name,
            'table': table_name,
            'object_id': object_id
        })

        return True

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error(f"Failed to delete {class_name}", extra={
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

        logger.info(f"Successfully bulk inserted {len(data_list)} {model_class.__name__} records", extra={
            'operation': operation_name,
            'table': model_class.__tablename__,
            'record_count': len(data_list)
        })

        return True, len(data_list)

    except SQLAlchemyError as e:
        db.session.rollback()

        duration = (time.time() - start_time) * 1000
        logger.error(f"Failed to bulk insert {model_class.__name__} records", extra={
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

        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'total_connections': pool.size() + pool.overflow()
        }
    except Exception as e:
        logger.error(f"Error getting connection stats: {e}")
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
        logger.error(f"Database health check failed: {e}")
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
                logger.warning(f"Error closing database connection: {e}")

        # Remove any session from Flask g
        db.session.remove()
