"""
Database Constraints and Indexes Migration

This migration adds proper database constraints, indexes, and optimizations
to improve data integrity and performance.
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)


def get_database_path():
    """Get the database path from config"""
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))


def migrate_database():
    """Apply database constraints and indexes migration"""
    db_path = get_database_path()

    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False

    logger.info(f"Starting database constraints migration on: {db_path}")

    try:
        # Connect directly to SQLite
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Add indexes for performance
            indexes_to_create = [
                # Tool indexes
                ("idx_tools_status", "CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status)"),
                ("idx_tools_tool_number", "CREATE UNIQUE INDEX IF NOT EXISTS idx_tools_tool_number ON tools(tool_number)"),
                ("idx_tools_serial_number", "CREATE UNIQUE INDEX IF NOT EXISTS idx_tools_serial_number ON tools(serial_number)"),
                ("idx_tools_calibration_status", "CREATE INDEX IF NOT EXISTS idx_tools_calibration_status ON tools(calibration_status)"),
                ("idx_tools_next_calibration", "CREATE INDEX IF NOT EXISTS idx_tools_next_calibration ON tools(next_calibration_date)"),

                # User indexes
                ("idx_users_employee_number", "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_employee_number ON users(employee_number)"),
                ("idx_users_department", "CREATE INDEX IF NOT EXISTS idx_users_department ON users(department)"),
                ("idx_users_is_admin", "CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin)"),
                ("idx_users_is_active", "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)"),

                # Checkout indexes
                ("idx_checkouts_tool_id", "CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id)"),
                ("idx_checkouts_user_id", "CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id)"),
                ("idx_checkouts_return_date", "CREATE INDEX IF NOT EXISTS idx_checkouts_return_date ON checkouts(return_date)"),
                ("idx_checkouts_checkout_date", "CREATE INDEX IF NOT EXISTS idx_checkouts_checkout_date ON checkouts(checkout_date)"),

                # Audit log indexes
                ("idx_audit_logs_timestamp", "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_log(timestamp)"),
                ("idx_audit_logs_action_type", "CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_log(action_type)"),

                # User activity indexes
                ("idx_user_activity_user_id", "CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id)"),
                ("idx_user_activity_timestamp", "CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp)"),
                ("idx_user_activity_type", "CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type)"),

                # Chemical indexes
                ("idx_chemicals_status", "CREATE INDEX IF NOT EXISTS idx_chemicals_status ON chemicals(status)"),
                ("idx_chemicals_part_number", "CREATE INDEX IF NOT EXISTS idx_chemicals_part_number ON chemicals(part_number)"),
                ("idx_chemicals_expiration", "CREATE INDEX IF NOT EXISTS idx_chemicals_expiration ON chemicals(expiration_date)"),
                ("idx_chemicals_category", "CREATE INDEX IF NOT EXISTS idx_chemicals_category ON chemicals(category)"),

                # Chemical issuance indexes
                ("idx_chemical_issuances_chemical_id", "CREATE INDEX IF NOT EXISTS idx_chemical_issuances_chemical_id ON chemical_issuances(chemical_id)"),
                ("idx_chemical_issuances_user_id", "CREATE INDEX IF NOT EXISTS idx_chemical_issuances_user_id ON chemical_issuances(user_id)"),
                ("idx_chemical_issuances_date", "CREATE INDEX IF NOT EXISTS idx_chemical_issuances_date ON chemical_issuances(issue_date)"),

                # Tool calibration indexes
                ("idx_tool_calibrations_tool_id", "CREATE INDEX IF NOT EXISTS idx_tool_calibrations_tool_id ON tool_calibrations(tool_id)"),
                ("idx_tool_calibrations_date", "CREATE INDEX IF NOT EXISTS idx_tool_calibrations_date ON tool_calibrations(calibration_date)"),
                ("idx_tool_calibrations_next_date", "CREATE INDEX IF NOT EXISTS idx_tool_calibrations_next_date ON tool_calibrations(next_calibration_date)"),
                ("idx_tool_calibrations_status", "CREATE INDEX IF NOT EXISTS idx_tool_calibrations_status ON tool_calibrations(calibration_status)"),
            ]

            # Create indexes
            for index_name, sql in indexes_to_create:
                try:
                    cursor.execute(sql)
                    logger.info(f"Created index: {index_name}")
                except sqlite3.Error as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Could not create index {index_name}: {e}")

            # Add check constraints (SQLite supports these in newer versions)
            constraints_to_add = [
                # Tool status constraint
                ("ALTER TABLE tools ADD CONSTRAINT chk_tool_status CHECK (status IN ('available', 'checked_out', 'maintenance', 'retired'))", "tools", "status"),

                # Tool calibration status constraint
                ("ALTER TABLE tools ADD CONSTRAINT chk_calibration_status CHECK (calibration_status IN ('current', 'due_soon', 'overdue', 'not_applicable'))", "tools", "calibration_status"),

                # User department constraint
                ("ALTER TABLE users ADD CONSTRAINT chk_user_department CHECK (department IN ('Materials', 'Maintenance', 'Quality', 'Production', 'IT', 'Admin'))", "users", "department"),

                # Chemical status constraint
                ("ALTER TABLE chemicals ADD CONSTRAINT chk_chemical_status CHECK (status IN ('available', 'low_stock', 'out_of_stock', 'expired'))", "chemicals", "status"),

                # Chemical reorder status constraint
                ("ALTER TABLE chemicals ADD CONSTRAINT chk_reorder_status CHECK (reorder_status IN ('not_needed', 'needed', 'ordered'))", "chemicals", "reorder_status"),
            ]

            # Note: SQLite has limited support for adding constraints to existing tables
            # Check SQLite version before attempting constraints
            if sqlite3.sqlite_version_info >= (3, 25, 0):
                for constraint_sql, table, column in constraints_to_add:
                    try:
                        cursor.execute(constraint_sql)
                        logger.info(f"Added constraint to {table}.{column}")
                    except sqlite3.Error as e:
                        logger.info(f"Constraint not added to {table}.{column} (SQLite limitation): {e}")
            else:
                logger.debug(f"Skipping constraints - SQLite version {sqlite3.sqlite_version} too old (need 3.25.0+)")

            # Commit all changes
            conn.commit()

            # Analyze tables for better query planning
            analyze_tables = [
                "tools", "users", "checkouts", "audit_log", "user_activity",
                "chemicals", "chemical_issuances", "tool_calibrations"
            ]

            for table in analyze_tables:
                try:
                    cursor.execute(f"ANALYZE {table}")
                    logger.debug(f"Analyzed table: {table}")
                except sqlite3.Error as e:
                    logger.warning(f"Could not analyze table {table}: {e}")

            conn.commit()

        logger.info("Database constraints and indexes migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during database constraints migration: {e}", exc_info=True)
        return False


def verify_migration():
    """Verify that the migration was applied correctly"""
    db_path = get_database_path()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if indexes exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indexes = cursor.fetchall()

            logger.info(f"Found {len(indexes)} custom indexes in database")
            for index in indexes:
                logger.debug(f"Index: {index[0]}")

            # Check table info for some key tables
            tables_to_check = ['tools', 'users', 'checkouts']
            for table in tables_to_check:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                logger.debug(f"Table {table} has {len(columns)} columns")

        return True

    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # Run migration
    success = migrate_database()
    if success:
        verify_migration()
        print("Database constraints and indexes migration completed successfully")
    else:
        print("Database constraints and indexes migration failed")
        exit(1)
