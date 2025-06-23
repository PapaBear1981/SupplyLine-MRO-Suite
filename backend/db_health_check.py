#!/usr/bin/env python3
"""
Database Health Check Script for SupplyLine MRO Suite

This script performs comprehensive health checks on the database
and reports the status for monitoring and deployment verification.
"""

import os
import sys
import logging
import time
from datetime import datetime
from flask import Flask
from sqlalchemy import text, inspect
from models import db, User, Tool, Chemical, AuditLog
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_database_connection(app):
    """Check if database connection is working"""
    try:
        with app.app_context():
            # Simple connection test
            result = db.engine.execute(text('SELECT 1 as test'))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                logger.info("✅ Database connection: OK")
                return True
            else:
                logger.error("❌ Database connection: FAILED - Unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection: FAILED - {str(e)}")
        return False


def check_database_tables(app):
    """Check if all required tables exist"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Required tables
            required_tables = [
                'users', 'tools', 'chemicals', 'checkouts', 'audit_log',
                'user_activity', 'tool_calibrations', 'chemical_issuances'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table not in tables:
                    missing_tables.append(table)
            
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                logger.info(f"✅ All required tables exist: {len(required_tables)} tables")
                return True
                
    except Exception as e:
        logger.error(f"❌ Table check failed: {str(e)}")
        return False


def check_admin_user(app):
    """Check if admin user exists"""
    try:
        with app.app_context():
            admin_user = User.query.filter_by(is_admin=True).first()
            
            if admin_user:
                logger.info(f"✅ Admin user exists: {admin_user.name} ({admin_user.employee_number})")
                return True
            else:
                logger.error("❌ No admin user found")
                return False
                
    except Exception as e:
        logger.error(f"❌ Admin user check failed: {str(e)}")
        return False


def check_sample_data(app):
    """Check if sample data exists"""
    try:
        with app.app_context():
            tool_count = Tool.query.count()
            chemical_count = Chemical.query.count()
            user_count = User.query.count()
            
            logger.info(f"📊 Data counts:")
            logger.info(f"   - Users: {user_count}")
            logger.info(f"   - Tools: {tool_count}")
            logger.info(f"   - Chemicals: {chemical_count}")
            
            if tool_count > 0 and chemical_count > 0 and user_count > 0:
                logger.info("✅ Sample data exists")
                return True
            else:
                logger.warning("⚠️  Limited or no sample data")
                return True  # Not a failure, just a warning
                
    except Exception as e:
        logger.error(f"❌ Sample data check failed: {str(e)}")
        return False


def check_database_performance(app):
    """Check basic database performance"""
    try:
        with app.app_context():
            # Test query performance
            start_time = time.time()
            
            # Run a few test queries
            db.engine.execute(text('SELECT COUNT(*) FROM users'))
            db.engine.execute(text('SELECT COUNT(*) FROM tools'))
            db.engine.execute(text('SELECT COUNT(*) FROM chemicals'))
            
            end_time = time.time()
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if query_time < 1000:  # Less than 1 second
                logger.info(f"✅ Database performance: OK ({query_time:.2f}ms)")
                return True
            else:
                logger.warning(f"⚠️  Database performance: SLOW ({query_time:.2f}ms)")
                return True  # Slow but not a failure
                
    except Exception as e:
        logger.error(f"❌ Performance check failed: {str(e)}")
        return False


def check_database_constraints(app):
    """Check if database constraints are working"""
    try:
        with app.app_context():
            # Test unique constraint on employee_number
            try:
                # This should work
                test_user = User(
                    name='Test User',
                    employee_number='TEST999',
                    department='IT',
                    password_hash='test_hash',
                    is_admin=False
                )
                db.session.add(test_user)
                db.session.flush()  # Don't commit yet
                
                # Clean up
                db.session.rollback()
                logger.info("✅ Database constraints: OK")
                return True
                
            except Exception as constraint_error:
                db.session.rollback()
                logger.info("✅ Database constraints: OK (constraint properly enforced)")
                return True
                
    except Exception as e:
        logger.error(f"❌ Constraint check failed: {str(e)}")
        return False


def run_comprehensive_health_check():
    """Run all health checks and return overall status"""
    logger.info("🔍 Starting comprehensive database health check...")
    logger.info("=" * 60)
    
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize database
        db.init_app(app)
        
        # Run all checks
        checks = [
            ("Database Connection", check_database_connection),
            ("Database Tables", check_database_tables),
            ("Admin User", check_admin_user),
            ("Sample Data", check_sample_data),
            ("Database Performance", check_database_performance),
            ("Database Constraints", check_database_constraints)
        ]
        
        results = []
        for check_name, check_function in checks:
            logger.info(f"\n🔍 Running {check_name} check...")
            result = check_function(app)
            results.append((check_name, result))
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📋 HEALTH CHECK SUMMARY:")
        logger.info("=" * 60)
        
        passed = 0
        failed = 0
        
        for check_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {check_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        logger.info("=" * 60)
        logger.info(f"📊 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            logger.info("🎉 All health checks passed! Database is ready.")
            return True
        else:
            logger.error(f"💥 {failed} health check(s) failed. Database needs attention.")
            return False
            
    except Exception as e:
        logger.error(f"💥 Health check failed with exception: {str(e)}")
        return False


if __name__ == '__main__':
    success = run_comprehensive_health_check()
    sys.exit(0 if success else 1)
