"""
Database Performance Indexes Migration

This script adds missing database indexes to improve query performance.
"""

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_database_path():
    """Get the database path"""
    # Check if we're in Docker environment
    if os.path.exists('/database'):
        return os.path.join('/database', 'tools.db')
    else:
        # Local development path
        return os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'database', 
            'tools.db'
        ))

def create_indexes():
    """Create performance indexes"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        ]
        
        # Composite indexes for complex queries
        composite_indexes = [
            ("idx_tools_status_category", "tools", ["status", "category"]),
            ("idx_chemicals_archived_status", "chemicals", ["is_archived", "status"]),
            ("idx_checkouts_return_tool", "checkouts", ["return_date", "tool_id"]),
        ]
        
        created_count = 0
        
        # Create single-column indexes
        for index_name, table_name, column_name in indexes:
            try:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    logger.warning(f"Table {table_name} does not exist, skipping index {index_name}")
                    continue
                
                # Check if column exists
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                if column_name not in columns:
                    logger.warning(f"Column {column_name} does not exist in table {table_name}, skipping index {index_name}")
                    continue
                
                # Check if index already exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
                if cursor.fetchone():
                    logger.info(f"Index {index_name} already exists, skipping")
                    continue
                
                # Create the index
                sql = f"CREATE INDEX {index_name} ON {table_name} ({column_name})"
                cursor.execute(sql)
                logger.info(f"Created index: {index_name}")
                created_count += 1
                
            except Exception as e:
                logger.error(f"Error creating index {index_name}: {str(e)}")
        
        # Create composite indexes
        for index_name, table_name, column_names in composite_indexes:
            try:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    logger.warning(f"Table {table_name} does not exist, skipping index {index_name}")
                    continue
                
                # Check if all columns exist
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [row[1] for row in cursor.fetchall()]
                missing_columns = [col for col in column_names if col not in existing_columns]
                if missing_columns:
                    logger.warning(f"Columns {missing_columns} do not exist in table {table_name}, skipping index {index_name}")
                    continue
                
                # Check if index already exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
                if cursor.fetchone():
                    logger.info(f"Index {index_name} already exists, skipping")
                    continue
                
                # Create the composite index
                columns_str = ", ".join(column_names)
                sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
                cursor.execute(sql)
                logger.info(f"Created composite index: {index_name}")
                created_count += 1
                
            except Exception as e:
                logger.error(f"Error creating composite index {index_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        
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
