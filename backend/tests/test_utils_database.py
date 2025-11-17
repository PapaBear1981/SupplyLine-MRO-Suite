"""
Tests for utils/database_utils.py - Database Transaction Utilities
"""

from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from utils.database_utils import (
    bulk_insert_with_rollback,
    check_database_health,
    database_transaction,
    db_connection_cleanup,
    get_connection_stats,
    safe_add_and_commit,
    safe_delete_and_commit,
    safe_update_and_commit,
    transactional,
)


class TestDatabaseTransaction:
    """Tests for database_transaction context manager"""

    def test_successful_transaction(self, app, db_session):
        """Test successful transaction with auto-commit"""
        from models import User

        with app.app_context():
            initial_count = User.query.count()

            with database_transaction() as session:
                user = User(
                    name="Transaction User",
                    employee_number="TRANS001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")
                session.add(user)

            # Should be committed
            final_count = User.query.count()
            assert final_count == initial_count + 1

    def test_failed_transaction_rollback(self, app, db_session):
        """Test that exceptions cause rollback"""
        from models import User

        with app.app_context():
            initial_count = User.query.count()

            with pytest.raises(ValueError):
                with database_transaction() as session:
                    user = User(
                        name="Rollback User",
                        employee_number="ROLL001",
                        department="Testing",
                        is_admin=False,
                        is_active=True
                    )
                    user.set_password("test123")
                    session.add(user)
                    raise ValueError("Intentional error")

            # Should be rolled back
            final_count = User.query.count()
            assert final_count == initial_count

    def test_transaction_logs_operation(self, app, db_session):
        """Test that transaction logs database operation"""
        with app.app_context():
            with patch("utils.database_utils.log_database_operation") as mock_log:
                with database_transaction():
                    pass  # Empty transaction

                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == "TRANSACTION"
                assert args[1] == "multiple_tables"

    def test_failed_transaction_logs_error(self, app, db_session):
        """Test that failed transaction logs error"""
        with app.app_context():
            with patch("utils.database_utils.logger") as mock_logger:
                with pytest.raises(RuntimeError):
                    with database_transaction():
                        raise RuntimeError("Test error")

                mock_logger.error.assert_called_once()
                call_kwargs = mock_logger.error.call_args[1]
                assert call_kwargs["extra"]["error_type"] == "RuntimeError"


class TestTransactionalDecorator:
    """Tests for transactional decorator"""

    def test_decorator_commits_on_success(self, app, db_session):
        """Test decorator commits transaction on success"""
        from models import User

        with app.app_context():
            @transactional
            def create_user():
                user = User(
                    name="Decorator User",
                    employee_number="DEC001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")
                db_session.add(user)
                return user

            initial_count = User.query.count()
            result = create_user()
            final_count = User.query.count()

            assert final_count == initial_count + 1
            assert result is not None

    def test_decorator_rollback_on_error(self, app, db_session):
        """Test decorator rolls back on error"""
        from models import User

        with app.app_context():
            @transactional
            def create_user_with_error():
                user = User(
                    name="Error User",
                    employee_number="ERR001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")
                db_session.add(user)
                raise ValueError("Intentional error")

            initial_count = User.query.count()

            with pytest.raises(ValueError):
                create_user_with_error()

            final_count = User.query.count()
            assert final_count == initial_count

    def test_decorator_preserves_function_metadata(self, app):
        """Test decorator preserves original function metadata"""
        with app.app_context():
            @transactional
            def my_function():
                """My docstring"""
                pass

            assert my_function.__name__ == "my_function"
            assert my_function.__doc__ == "My docstring"


class TestSafeAddAndCommit:
    """Tests for safe_add_and_commit function"""

    def test_successful_add(self, app, db_session):
        """Test successful object addition"""
        from models import User

        with app.app_context():
            user = User(
                name="Safe Add User",
                employee_number="SAFE001",
                department="Testing",
                is_admin=False,
                is_active=True
            )
            user.set_password("test123")

            result = safe_add_and_commit(user, "test_add")

            assert result is True
            assert user.id is not None

            # Verify in database
            saved_user = User.query.get(user.id)
            assert saved_user is not None
            assert saved_user.name == "Safe Add User"

    def test_failed_add_returns_false(self, app, db_session):
        """Test that failed add returns False"""
        from models import User, db

        with app.app_context():
            user = User(
                name="Failed Add",
                employee_number="FAIL001",
                department="Testing",
                is_admin=False,
                is_active=True
            )
            user.set_password("test123")

            with patch.object(db.session, "commit", side_effect=SQLAlchemyError("Constraint violation")):
                result = safe_add_and_commit(user, "test_fail_add")

            assert result is False

    def test_add_logs_database_operation(self, app, db_session):
        """Test that successful add logs operation"""
        from models import User

        with app.app_context():
            with patch("utils.database_utils.log_database_operation") as mock_log:
                user = User(
                    name="Log Add User",
                    employee_number="LOG001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")

                safe_add_and_commit(user, "test_log_add")

                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == "INSERT"
                assert args[3] == 1  # row count

    def test_failed_add_logs_error(self, app, db_session):
        """Test that failed add logs error"""
        from models import User, db

        with app.app_context():
            with patch("utils.database_utils.logger") as mock_logger:
                user = User(
                    name="Error Log User",
                    employee_number="ERRLOG001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")

                with patch.object(db.session, "commit", side_effect=SQLAlchemyError("Test error")):
                    safe_add_and_commit(user, "test_error_log")

                mock_logger.error.assert_called_once()


class TestSafeUpdateAndCommit:
    """Tests for safe_update_and_commit function"""

    def test_successful_update(self, app, db_session, test_user):
        """Test successful object update"""
        from models import User

        with app.app_context():
            user_id = test_user.id
            # Query the user in the current context
            user_to_update = db_session.get(User, user_id)
            user_to_update.department = "Updated Department"

            result = safe_update_and_commit(user_to_update, "test_update")

            assert result is True

            # Verify in database - expire the object to force reload
            db_session.expire(user_to_update)
            assert user_to_update.department == "Updated Department"

    def test_failed_update_returns_false(self, app, db_session, test_user):
        """Test that failed update returns False"""
        from models import db

        with app.app_context():
            test_user.department = "New Dept"

            with patch.object(db.session, "commit", side_effect=SQLAlchemyError("Update failed")):
                result = safe_update_and_commit(test_user, "test_fail_update")

            assert result is False

    def test_update_logs_database_operation(self, app, db_session, test_user):
        """Test that successful update logs operation"""
        with app.app_context():
            with patch("utils.database_utils.log_database_operation") as mock_log:
                test_user.name = "Updated Name"
                safe_update_and_commit(test_user, "test_log_update")

                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == "UPDATE"
                assert args[3] == 1


class TestSafeDeleteAndCommit:
    """Tests for safe_delete_and_commit function"""

    def test_successful_delete(self, app, db_session):
        """Test successful object deletion"""
        from models import User

        with app.app_context():
            user = User(
                name="Delete User",
                employee_number="DEL001",
                department="Testing",
                is_admin=False,
                is_active=True
            )
            user.set_password("test123")
            db_session.add(user)
            db_session.commit()

            user_id = user.id
            result = safe_delete_and_commit(user, "test_delete")

            assert result is True

            # Verify deleted
            deleted_user = User.query.get(user_id)
            assert deleted_user is None

    def test_failed_delete_returns_false(self, app, db_session, test_user):
        """Test that failed delete returns False"""
        from models import db

        with app.app_context():
            with patch.object(db.session, "commit", side_effect=SQLAlchemyError("Delete failed")):
                result = safe_delete_and_commit(test_user, "test_fail_delete")

            assert result is False

    def test_delete_logs_database_operation(self, app, db_session):
        """Test that successful delete logs operation"""
        from models import User

        with app.app_context():
            with patch("utils.database_utils.log_database_operation") as mock_log:
                user = User(
                    name="Log Delete User",
                    employee_number="LOGDEL001",
                    department="Testing",
                    is_admin=False,
                    is_active=True
                )
                user.set_password("test123")
                db_session.add(user)
                db_session.commit()

                safe_delete_and_commit(user, "test_log_delete")

                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == "DELETE"
                assert args[3] == 1


class TestBulkInsertWithRollback:
    """Tests for bulk_insert_with_rollback function"""

    def test_successful_bulk_insert(self, app, db_session):
        """Test successful bulk insert"""
        from models import User

        with app.app_context():
            data_list = [
                {
                    "name": f"Bulk User {i}",
                    "employee_number": f"BULK{i:03d}",
                    "department": "Bulk Testing",
                    "is_admin": False,
                    "is_active": True,
                    "password_hash": "placeholder"
                }
                for i in range(1, 4)
            ]

            success, count = bulk_insert_with_rollback(User, data_list, "test_bulk")

            assert success is True
            assert count == 3

            # Verify in database
            bulk_users = User.query.filter(
                User.employee_number.like("BULK%")
            ).all()
            assert len(bulk_users) == 3

    def test_failed_bulk_insert(self, app, db_session):
        """Test failed bulk insert returns False"""
        from models import User, db

        with app.app_context():
            data_list = [{"name": "Test"}]

            with patch.object(db.session, "bulk_insert_mappings", side_effect=SQLAlchemyError("Bulk error")):
                success, count = bulk_insert_with_rollback(User, data_list, "test_bulk_fail")

            assert success is False
            assert count == 0

    def test_bulk_insert_logs_operation(self, app, db_session):
        """Test that bulk insert logs operation"""
        from models import User

        with app.app_context():
            with patch("utils.database_utils.log_database_operation") as mock_log:
                data_list = [
                    {
                        "name": "Bulk Log User",
                        "employee_number": "BULKLOG001",
                        "department": "Testing",
                        "is_admin": False,
                        "is_active": True,
                        "password_hash": "hash"
                    }
                ]

                bulk_insert_with_rollback(User, data_list, "test_bulk_log")

                mock_log.assert_called_once()
                args = mock_log.call_args[0]
                assert args[0] == "BULK_INSERT"
                assert args[3] == 1


class TestGetConnectionStats:
    """Tests for get_connection_stats function"""

    def test_get_stats_with_pool_methods(self, app, db_session):
        """Test getting stats when pool has all methods"""
        with app.app_context():
            stats = get_connection_stats()

            # Should return a dictionary
            assert isinstance(stats, dict)
            # May have some stats or be empty depending on pool type
            assert "error" not in stats or isinstance(stats.get("error"), str)

    def test_get_stats_calculates_total(self, app, db_session):
        """Test that total_connections is calculated correctly"""
        from models import db

        with app.app_context():
            mock_pool = MagicMock()
            mock_pool.size.return_value = 5
            mock_pool.checkedin.return_value = 3
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 1
            mock_pool.invalid.return_value = 0

            with patch.object(db.engine, "pool", mock_pool):
                stats = get_connection_stats()

            assert stats["pool_size"] == 5
            assert stats["checked_in"] == 3
            assert stats["checked_out"] == 2
            assert stats["overflow"] == 1
            assert stats["invalid"] == 0
            assert stats["total_connections"] == 6  # pool_size + overflow

    def test_get_stats_without_pool_methods(self, app, db_session):
        """Test getting stats when pool lacks methods"""
        from models import db

        with app.app_context():
            mock_pool = MagicMock(spec=[])  # No methods

            with patch.object(db.engine, "pool", mock_pool):
                stats = get_connection_stats()

            # Should return empty dict (no stats available)
            assert isinstance(stats, dict)
            assert "pool_size" not in stats

    def test_get_stats_with_exception(self, app, db_session):
        """Test error handling in get_connection_stats"""
        from models import db

        with app.app_context():
            # Patch the entire db module's engine to raise exception
            with patch("utils.database_utils.db") as mock_db:
                # Make accessing engine.pool raise an exception
                mock_db.engine.pool.size.side_effect = Exception("Pool error")
                stats = get_connection_stats()

            assert "error" in stats
            assert "Pool error" in stats["error"]


class TestCheckDatabaseHealth:
    """Tests for check_database_health function"""

    def test_healthy_database(self, app, db_session):
        """Test health check on healthy database"""
        with app.app_context():
            health = check_database_health()

            assert health["healthy"] is True
            assert "response_time_ms" in health
            assert isinstance(health["response_time_ms"], float)
            assert health["response_time_ms"] >= 0
            assert "connection_stats" in health

    def test_unhealthy_database(self, app, db_session):
        """Test health check when database query fails"""
        from models import db

        with app.app_context():
            with patch.object(db.session, "execute", side_effect=Exception("Connection failed")):
                health = check_database_health()

            assert health["healthy"] is False
            assert "error" in health
            assert "Connection failed" in health["error"]
            assert health["error_type"] == "Exception"

    def test_health_check_includes_connection_stats(self, app, db_session):
        """Test that health check includes connection statistics"""
        with app.app_context():
            health = check_database_health()

            assert "connection_stats" in health
            assert isinstance(health["connection_stats"], dict)


class TestDbConnectionCleanup:
    """Tests for db_connection_cleanup context manager"""

    def test_cleanup_without_g_connection(self, app, db_session):
        """Test cleanup when g.db_connection doesn't exist"""
        with app.app_context():
            # Should not raise any errors
            with db_connection_cleanup():
                pass

    def test_cleanup_with_g_connection(self, app, db_session):
        """Test cleanup when g.db_connection exists"""
        from flask import g

        with app.app_context():
            # Create mock connection
            mock_conn = MagicMock()
            g.db_connection = mock_conn

            with db_connection_cleanup():
                pass

            # Connection should be closed
            mock_conn.close.assert_called_once()
            # g.db_connection should be removed
            assert not hasattr(g, "db_connection")

    def test_cleanup_handles_close_error(self, app, db_session):
        """Test cleanup handles errors when closing connection"""
        from flask import g

        with app.app_context():
            mock_conn = MagicMock()
            mock_conn.close.side_effect = Exception("Close error")
            g.db_connection = mock_conn

            # Should not raise, just log warning
            with db_connection_cleanup():
                pass

            # Should still attempt to close and remove attribute
            mock_conn.close.assert_called_once()

    def test_cleanup_removes_session(self, app, db_session):
        """Test that cleanup removes SQLAlchemy session"""
        from models import db

        with app.app_context():
            with patch.object(db.session, "remove") as mock_remove:
                with db_connection_cleanup():
                    pass

                mock_remove.assert_called_once()

    def test_cleanup_on_exception(self, app, db_session):
        """Test cleanup runs even when exception occurs"""
        from models import db

        with app.app_context():
            with patch.object(db.session, "remove") as mock_remove:
                with pytest.raises(ValueError):
                    with db_connection_cleanup():
                        raise ValueError("Test error")

                # Cleanup should still run
                mock_remove.assert_called_once()
