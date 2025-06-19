"""
Database Performance Indexes Migration

This script adds missing database indexes to improve query performance.
Works with both SQLite (local) and PostgreSQL (production).
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from config import Config

logger = logging.getLogger(__name__)

def create_indexes():
    """Create performance indexes using SQLAlchemy"""
    try:
        # Create Flask app context
        app = create_app()

        with app.app_context():
            # Get database engine
            engine = db.engine
            is_postgresql = 'postgresql' in str(engine.url)

            logger.info(f"Creating indexes for {'PostgreSQL' if is_postgresql else 'SQLite'} database")

            # Use raw SQL connection for index creation
            with engine.connect() as conn:

                # List of indexes to create
                indexes = [
                    # User indexes
                    ("idx_users_employee_number", "users", "employee_number"),
                    ("idx_users_is_admin", "users", "is_admin"),
                    ("idx_users_is_active", "users", "is_active"),
                    ("idx_users_department", "users", "department"),

                    # Tool indexes
                    ("idx_tools_status", "tools", "status"),
                    ("idx_tools_category", "tools", "category"),
                    ("idx_tools_location", "tools", "location"),
                    ("idx_tools_tool_number", "tools", "tool_number"),
                    ("idx_tools_calibration_status", "tools", "calibration_status"),
                    ("idx_tools_next_calibration_date", "tools", "next_calibration_date"),

                    # Chemical indexes
                    ("idx_chemicals_status", "chemicals", "status"),
                    ("idx_chemicals_category", "chemicals", "category"),
                    ("idx_chemicals_is_archived", "chemicals", "is_archived"),
                    ("idx_chemicals_expiration_date", "chemicals", "expiration_date"),
                    ("idx_chemicals_part_number", "chemicals", "part_number"),
                    ("idx_chemicals_reorder_status", "chemicals", "reorder_status"),

                    # Checkout indexes
                    ("idx_checkouts_return_date", "checkouts", "return_date"),
                    ("idx_checkouts_checkout_date", "checkouts", "checkout_date"),
                    ("idx_checkouts_tool_id", "checkouts", "tool_id"),
                    ("idx_checkouts_user_id", "checkouts", "user_id"),

                    # Audit log indexes
                    ("idx_audit_log_timestamp", "audit_log", "timestamp"),
                    ("idx_audit_log_action_type", "audit_log", "action_type"),

                    # User activity indexes
                    ("idx_user_activity_timestamp", "user_activity", "timestamp"),
                    ("idx_user_activity_user_id", "user_activity", "user_id"),
                    ("idx_user_activity_activity_type", "user_activity", "activity_type"),

                    # Cycle count indexes
                    ("idx_cycle_count_schedules_is_active", "cycle_count_schedules", "is_active"),
                    ("idx_cycle_count_schedules_created_by", "cycle_count_schedules", "created_by"),
                    ("idx_cycle_count_schedules_frequency", "cycle_count_schedules", "frequency"),
                    ("idx_cycle_count_schedules_method", "cycle_count_schedules", "method"),

                    ("idx_cycle_count_batches_status", "cycle_count_batches", "status"),
                    ("idx_cycle_count_batches_schedule_id", "cycle_count_batches", "schedule_id"),
                    ("idx_cycle_count_batches_created_by", "cycle_count_batches", "created_by"),
                    ("idx_cycle_count_batches_start_date", "cycle_count_batches", "start_date"),
                    ("idx_cycle_count_batches_end_date", "cycle_count_batches", "end_date"),

                    ("idx_cycle_count_items_batch_id", "cycle_count_items", "batch_id"),
                    ("idx_cycle_count_items_status", "cycle_count_items", "status"),
                    ("idx_cycle_count_items_item_type", "cycle_count_items", "item_type"),
                    ("idx_cycle_count_items_assigned_to", "cycle_count_items", "assigned_to"),

                    ("idx_cycle_count_results_item_id", "cycle_count_results", "item_id"),
                    ("idx_cycle_count_results_counted_by", "cycle_count_results", "counted_by"),
                    ("idx_cycle_count_results_counted_at", "cycle_count_results", "counted_at"),
                    ("idx_cycle_count_results_has_discrepancy", "cycle_count_results", "has_discrepancy"),
                    ("idx_cycle_count_results_discrepancy_type", "cycle_count_results", "discrepancy_type"),

                    ("idx_cycle_count_adjustments_result_id", "cycle_count_adjustments", "result_id"),
                    ("idx_cycle_count_adjustments_approved_by", "cycle_count_adjustments", "approved_by"),
                    ("idx_cycle_count_adjustments_approved_at", "cycle_count_adjustments", "approved_at"),
                ]

                # Composite indexes for complex queries
                composite_indexes = [
                    ("idx_tools_status_category", "tools", ["status", "category"]),
                    ("idx_chemicals_archived_status", "chemicals", ["is_archived", "status"]),
                    ("idx_checkouts_return_tool", "checkouts", ["return_date", "tool_id"]),

                    # Cycle count composite indexes
                    ("idx_cycle_count_items_batch_status", "cycle_count_items", ["batch_id", "status"]),
                    ("idx_cycle_count_items_type_id", "cycle_count_items", ["item_type", "item_id"]),
                    ("idx_cycle_count_items_assigned_status", "cycle_count_items", ["assigned_to", "status"]),
                    ("idx_cycle_count_results_discrepancy", "cycle_count_results", ["has_discrepancy", "discrepancy_type"]),
                    ("idx_cycle_count_batches_schedule_status", "cycle_count_batches", ["schedule_id", "status"]),
                ]

                created_count = 0

                # Create single-column indexes
                for index_name, table_name, column_name in indexes:
                    try:
                        # Check if table exists
                        if is_postgresql:
                            from sqlalchemy import text
                            result = conn.execute(
                                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"),
                                {"table_name": table_name}
                            ).fetchone()
                            table_exists = result[0] if result else False
                        else:
                            from sqlalchemy import text
                            result = conn.execute(
                                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
                                {"table_name": table_name}
                            ).fetchone()
                            table_exists = result is not None

                        if not table_exists:
                            logger.warning(f"Table {table_name} does not exist, skipping index {index_name}")
                            continue

                        # Check if column exists
                        if is_postgresql:
                            result = conn.execute(
                                text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = :table_name AND column_name = :column_name)"),
                                {"table_name": table_name, "column_name": column_name}
                            ).fetchone()
                            column_exists = result[0] if result else False
                        else:
                            columns_result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                            columns = [row[1] for row in columns_result]
                            column_exists = column_name in columns

                        if not column_exists:
                            logger.warning(f"Column {column_name} does not exist in table {table_name}, skipping index {index_name}")
                            continue

                        # Check if index already exists
                        if is_postgresql:
                            result = conn.execute(
                                text("SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = :index_name)"),
                                {"index_name": index_name}
                            ).fetchone()
                            index_exists = result[0] if result else False
                        else:
                            result = conn.execute(
                                text("SELECT name FROM sqlite_master WHERE type='index' AND name=:index_name"),
                                {"index_name": index_name}
                            ).fetchone()
                            index_exists = result is not None

                        if index_exists:
                            logger.info(f"Index {index_name} already exists, skipping")
                            continue

                        # Create the index
                        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
                        conn.execute(text(sql))
                        logger.info(f"Created index: {index_name}")
                        created_count += 1

                    except Exception as e:
                        logger.error(f"Error creating index {index_name}: {str(e)}")

                # Create composite indexes
                for index_name, table_name, column_names in composite_indexes:
                    try:
                        # Check if table exists
                        if is_postgresql:
                            result = conn.execute(
                                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"),
                                {"table_name": table_name}
                            ).fetchone()
                            table_exists = result[0] if result else False
                        else:
                            result = conn.execute(
                                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
                                {"table_name": table_name}
                            ).fetchone()
                            table_exists = result is not None

                        if not table_exists:
                            logger.warning(f"Table {table_name} does not exist, skipping index {index_name}")
                            continue

                        # Check if all columns exist
                        if is_postgresql:
                            missing_columns = []
                            for col in column_names:
                                result = conn.execute(
                                    text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = :table_name AND column_name = :column_name)"),
                                    {"table_name": table_name, "column_name": col}
                                ).fetchone()
                                if not (result and result[0]):
                                    missing_columns.append(col)
                        else:
                            columns_result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                            existing_columns = [row[1] for row in columns_result]
                            missing_columns = [col for col in column_names if col not in existing_columns]

                        if missing_columns:
                            logger.warning(f"Columns {missing_columns} do not exist in table {table_name}, skipping index {index_name}")
                            continue

                        # Check if index already exists
                        if is_postgresql:
                            result = conn.execute(
                                text("SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = :index_name)"),
                                {"index_name": index_name}
                            ).fetchone()
                            index_exists = result[0] if result else False
                        else:
                            result = conn.execute(
                                text("SELECT name FROM sqlite_master WHERE type='index' AND name=:index_name"),
                                {"index_name": index_name}
                            ).fetchone()
                            index_exists = result is not None

                        if index_exists:
                            logger.info(f"Index {index_name} already exists, skipping")
                            continue

                        # Create the composite index
                        columns_str = ", ".join(column_names)
                        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
                        conn.execute(text(sql))
                        logger.info(f"Created composite index: {index_name}")
                        created_count += 1

                    except Exception as e:
                        logger.error(f"Error creating composite index {index_name}: {str(e)}")

                conn.commit()
                logger.info(f"Successfully created {created_count} database indexes")
                return True

    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False

def migrate_database():
    """Main migration function"""
    logger.info("Starting performance indexes migration...")

    success = create_indexes()

    if success:
        logger.info("Performance indexes migration completed successfully")
    else:
        logger.error("Performance indexes migration failed")

    return success

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    migrate_database()
