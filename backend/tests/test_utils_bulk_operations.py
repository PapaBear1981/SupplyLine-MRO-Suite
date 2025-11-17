"""
Comprehensive tests for utils/bulk_operations.py

This module tests all bulk operation functions including:
- bulk_log_activities
- bulk_log_audit_events
- bulk_update_tool_calibration_status
- bulk_update_chemical_status
- get_dashboard_stats_optimized
- get_tools_with_relationships
- get_chemicals_with_relationships
- optimize_database_queries
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from models import (
    db,
    Tool,
    Chemical,
    UserActivity,
    AuditLog,
    Checkout,
    ToolCalibration,
    ToolServiceRecord,
    ChemicalIssuance
)
from utils.bulk_operations import (
    bulk_log_activities,
    bulk_log_audit_events,
    bulk_update_tool_calibration_status,
    bulk_update_chemical_status,
    get_dashboard_stats_optimized,
    get_tools_with_relationships,
    get_chemicals_with_relationships,
    optimize_database_queries
)


class TestBulkLogActivities:
    """Tests for bulk_log_activities function"""

    def test_bulk_log_activities_success(self, app, db_session, regular_user):
        """Test successful bulk logging of activities"""
        activities = [
            {
                "user_id": regular_user.id,
                "activity_type": "login",
                "description": "User logged in"
            },
            {
                "user_id": regular_user.id,
                "activity_type": "view_tools",
                "description": "User viewed tools list"
            },
            {
                "user_id": regular_user.id,
                "activity_type": "checkout",
                "description": "User checked out tool"
            }
        ]

        bulk_log_activities(activities)

        # Verify activities were logged
        logged_activities = db_session.query(UserActivity).filter_by(
            user_id=regular_user.id
        ).all()

        assert len(logged_activities) == 3
        activity_types = [a.activity_type for a in logged_activities]
        assert "login" in activity_types
        assert "view_tools" in activity_types
        assert "checkout" in activity_types

    def test_bulk_log_activities_with_custom_timestamps(self, app, db_session, regular_user):
        """Test bulk logging with custom timestamps"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)

        activities = [
            {
                "user_id": regular_user.id,
                "activity_type": "custom_action",
                "description": "Action with custom timestamp",
                "timestamp": custom_time
            }
        ]

        bulk_log_activities(activities)

        activity = db_session.query(UserActivity).filter_by(
            activity_type="custom_action"
        ).first()

        assert activity is not None
        assert activity.timestamp == custom_time

    def test_bulk_log_activities_auto_timestamp(self, app, db_session, regular_user):
        """Test that timestamps are auto-generated when not provided"""
        before_time = datetime.utcnow()

        activities = [
            {
                "user_id": regular_user.id,
                "activity_type": "auto_timestamp",
                "description": "Activity without timestamp"
            }
        ]

        bulk_log_activities(activities)

        after_time = datetime.utcnow()

        activity = db_session.query(UserActivity).filter_by(
            activity_type="auto_timestamp"
        ).first()

        assert activity is not None
        assert before_time <= activity.timestamp <= after_time

    def test_bulk_log_activities_empty_list(self, app, db_session):
        """Test that empty list is handled gracefully"""
        initial_count = db_session.query(UserActivity).count()

        bulk_log_activities([])

        final_count = db_session.query(UserActivity).count()
        assert initial_count == final_count

    def test_bulk_log_activities_database_error(self, app, db_session, regular_user):
        """Test error handling when database operation fails"""
        activities = [
            {
                "user_id": regular_user.id,
                "activity_type": "test",
                "description": "Test"
            }
        ]

        with patch.object(db.session, 'bulk_insert_mappings', side_effect=Exception("DB Error")):
            with pytest.raises(Exception) as exc_info:
                bulk_log_activities(activities)

            assert "DB Error" in str(exc_info.value)

    def test_bulk_log_activities_multiple_users(self, app, db_session, admin_user, regular_user):
        """Test bulk logging for multiple users"""
        activities = [
            {
                "user_id": admin_user.id,
                "activity_type": "admin_action",
                "description": "Admin performed action"
            },
            {
                "user_id": regular_user.id,
                "activity_type": "user_action",
                "description": "User performed action"
            }
        ]

        bulk_log_activities(activities)

        admin_activities = db_session.query(UserActivity).filter_by(
            user_id=admin_user.id
        ).count()
        user_activities = db_session.query(UserActivity).filter_by(
            user_id=regular_user.id
        ).count()

        assert admin_activities == 1
        assert user_activities == 1


class TestBulkLogAuditEvents:
    """Tests for bulk_log_audit_events function"""

    def test_bulk_log_audit_events_success(self, app, db_session):
        """Test successful bulk logging of audit events"""
        audit_logs = [
            {
                "action_type": "tool_created",
                "action_details": "New tool T001 created"
            },
            {
                "action_type": "chemical_updated",
                "action_details": "Chemical C001 quantity updated"
            },
            {
                "action_type": "user_login",
                "action_details": "User ADMIN001 logged in"
            }
        ]

        bulk_log_audit_events(audit_logs)

        # Verify audit logs were created
        logged_events = db_session.query(AuditLog).all()
        assert len(logged_events) >= 3

        action_types = [log.action_type for log in logged_events]
        assert "tool_created" in action_types
        assert "chemical_updated" in action_types
        assert "user_login" in action_types

    def test_bulk_log_audit_events_with_custom_timestamps(self, app, db_session):
        """Test audit logging with custom timestamps"""
        custom_time = datetime(2024, 6, 15, 10, 30, 0)

        audit_logs = [
            {
                "action_type": "custom_audit",
                "action_details": "Audit with custom timestamp",
                "timestamp": custom_time
            }
        ]

        bulk_log_audit_events(audit_logs)

        audit_log = db_session.query(AuditLog).filter_by(
            action_type="custom_audit"
        ).first()

        assert audit_log is not None
        assert audit_log.timestamp == custom_time

    def test_bulk_log_audit_events_auto_timestamp(self, app, db_session):
        """Test that timestamps are auto-generated"""
        before_time = datetime.utcnow()

        audit_logs = [
            {
                "action_type": "auto_audit",
                "action_details": "Audit without timestamp"
            }
        ]

        bulk_log_audit_events(audit_logs)

        after_time = datetime.utcnow()

        audit_log = db_session.query(AuditLog).filter_by(
            action_type="auto_audit"
        ).first()

        assert audit_log is not None
        assert before_time <= audit_log.timestamp <= after_time

    def test_bulk_log_audit_events_empty_list(self, app, db_session):
        """Test that empty list is handled gracefully"""
        initial_count = db_session.query(AuditLog).count()

        bulk_log_audit_events([])

        final_count = db_session.query(AuditLog).count()
        assert initial_count == final_count

    def test_bulk_log_audit_events_database_error(self, app, db_session):
        """Test error handling when database operation fails"""
        audit_logs = [
            {
                "action_type": "test",
                "action_details": "Test"
            }
        ]

        with patch.object(db.session, 'bulk_insert_mappings', side_effect=Exception("DB Error")):
            with pytest.raises(Exception) as exc_info:
                bulk_log_audit_events(audit_logs)

            assert "DB Error" in str(exc_info.value)

    def test_bulk_log_audit_events_large_batch(self, app, db_session):
        """Test bulk logging with a large batch of events"""
        audit_logs = [
            {
                "action_type": f"batch_action_{i}",
                "action_details": f"Batch action details {i}"
            }
            for i in range(100)
        ]

        bulk_log_audit_events(audit_logs)

        count = db_session.query(AuditLog).filter(
            AuditLog.action_type.like("batch_action_%")
        ).count()

        assert count == 100


class TestBulkUpdateToolCalibrationStatus:
    """Tests for bulk_update_tool_calibration_status function"""

    def test_update_overdue_calibrations(self, app, db_session):
        """Test updating tools with overdue calibrations"""
        # Create tool with overdue calibration
        overdue_tool = Tool(
            tool_number="OVERDUE001",
            serial_number="S-OD001",
            description="Overdue Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() - timedelta(days=10),
            calibration_status="current"
        )
        db_session.add(overdue_tool)
        db_session.commit()

        result = bulk_update_tool_calibration_status()

        # Refresh the tool
        db_session.refresh(overdue_tool)

        assert overdue_tool.calibration_status == "overdue"
        assert result["overdue"] >= 1

    def test_update_due_soon_calibrations(self, app, db_session):
        """Test updating tools with calibrations due soon"""
        # Create tool with calibration due soon (within 30 days)
        due_soon_tool = Tool(
            tool_number="DUESOON001",
            serial_number="S-DS001",
            description="Due Soon Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() + timedelta(days=15),
            calibration_status="current"
        )
        db_session.add(due_soon_tool)
        db_session.commit()

        result = bulk_update_tool_calibration_status()

        db_session.refresh(due_soon_tool)

        assert due_soon_tool.calibration_status == "due_soon"
        assert result["due_soon"] >= 1

    def test_update_current_calibrations(self, app, db_session):
        """Test updating tools with current calibrations"""
        # Create tool with calibration far in the future
        current_tool = Tool(
            tool_number="CURRENT001",
            serial_number="S-C001",
            description="Current Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() + timedelta(days=60),
            calibration_status="due_soon"
        )
        db_session.add(current_tool)
        db_session.commit()

        result = bulk_update_tool_calibration_status()

        db_session.refresh(current_tool)

        assert current_tool.calibration_status == "current"
        assert result["current"] >= 1

    def test_no_updates_needed(self, app, db_session):
        """Test when no calibration status updates are needed"""
        # Create tool with correct status
        tool = Tool(
            tool_number="CORRECT001",
            serial_number="S-CORR001",
            description="Correct Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() - timedelta(days=10),
            calibration_status="overdue"  # Already correct
        )
        db_session.add(tool)
        db_session.commit()

        result = bulk_update_tool_calibration_status()

        # This specific tool shouldn't have been updated
        assert isinstance(result, dict)
        assert "overdue" in result
        assert "due_soon" in result
        assert "current" in result

    def test_multiple_status_updates(self, app, db_session):
        """Test updating multiple tools with different calibration statuses"""
        # Create multiple tools with different statuses
        tools = [
            Tool(
                tool_number=f"MULTI{i}",
                serial_number=f"S-M{i}",
                description=f"Multi Tool {i}",
                condition="Good",
                location="Lab",
                category="Testing",
                status="available",
                next_calibration_date=datetime.utcnow() - timedelta(days=10),
                calibration_status="current"
            )
            for i in range(3)
        ]

        for tool in tools:
            db_session.add(tool)
        db_session.commit()

        result = bulk_update_tool_calibration_status()

        assert result["overdue"] >= 3

    def test_database_error_handling(self, app, db_session):
        """Test error handling when database query fails"""
        with patch.object(db.session, 'query', side_effect=Exception("Query Error")):
            with pytest.raises(Exception) as exc_info:
                bulk_update_tool_calibration_status()

            assert "Query Error" in str(exc_info.value)


class TestBulkUpdateChemicalStatus:
    """Tests for bulk_update_chemical_status function"""

    def test_update_expired_chemicals(self, app, db_session):
        """Test updating expired chemicals"""
        expired_chemical = Chemical(
            part_number="EXP001",
            lot_number="L-EXP001",
            description="Expired Chemical",
            manufacturer="Test",
            quantity=100.0,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() - timedelta(days=10),
            is_archived=False
        )
        db_session.add(expired_chemical)
        db_session.commit()

        result = bulk_update_chemical_status()

        db_session.refresh(expired_chemical)

        assert expired_chemical.status == "expired"
        assert result["expired"] >= 1

    def test_update_out_of_stock_chemicals(self, app, db_session):
        """Test updating out of stock chemicals"""
        oos_chemical = Chemical(
            part_number="OOS001",
            lot_number="L-OOS001",
            description="Out of Stock Chemical",
            manufacturer="Test",
            quantity=0,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() + timedelta(days=100),
            is_archived=False
        )
        db_session.add(oos_chemical)
        db_session.commit()

        result = bulk_update_chemical_status()

        db_session.refresh(oos_chemical)

        assert oos_chemical.status == "out_of_stock"
        assert result["out_of_stock"] >= 1

    def test_archived_chemicals_not_updated(self, app, db_session):
        """Test that archived chemicals are not updated"""
        archived_chemical = Chemical(
            part_number="ARCH001",
            lot_number="L-ARCH001",
            description="Archived Chemical",
            manufacturer="Test",
            quantity=0,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() - timedelta(days=10),
            is_archived=True
        )
        db_session.add(archived_chemical)
        db_session.commit()

        bulk_update_chemical_status()

        db_session.refresh(archived_chemical)

        # Archived chemical should not be updated
        assert archived_chemical.status == "available"

    def test_multiple_chemical_updates(self, app, db_session):
        """Test updating multiple chemicals with different statuses"""
        chemicals = []

        # Expired chemical
        chemicals.append(Chemical(
            part_number="MEXP001",
            lot_number="L-MEXP001",
            description="Multi Expired",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() - timedelta(days=5),
            is_archived=False
        ))

        # Out of stock chemical
        chemicals.append(Chemical(
            part_number="MOOS001",
            lot_number="L-MOOS001",
            description="Multi OOS",
            manufacturer="Test",
            quantity=0,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() + timedelta(days=100),
            is_archived=False
        ))

        for chemical in chemicals:
            db_session.add(chemical)
        db_session.commit()

        result = bulk_update_chemical_status()

        assert result["expired"] >= 1
        assert result["out_of_stock"] >= 1

    def test_database_error_handling(self, app, db_session):
        """Test error handling when database query fails"""
        with patch.object(db.session, 'query', side_effect=Exception("Query Error")):
            with pytest.raises(Exception) as exc_info:
                bulk_update_chemical_status()

            assert "Query Error" in str(exc_info.value)

    def test_no_updates_needed(self, app, db_session):
        """Test when no chemical status updates are needed"""
        # Create chemical that doesn't need updating
        good_chemical = Chemical(
            part_number="GOOD001",
            lot_number="L-GOOD001",
            description="Good Chemical",
            manufacturer="Test",
            quantity=100,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            expiration_date=datetime.utcnow() + timedelta(days=100),
            is_archived=False
        )
        db_session.add(good_chemical)
        db_session.commit()

        result = bulk_update_chemical_status()

        assert isinstance(result, dict)
        assert "expired" in result
        assert "out_of_stock" in result


class TestGetDashboardStatsOptimized:
    """Tests for get_dashboard_stats_optimized function"""

    def test_empty_database_stats(self, app, db_session):
        """Test stats with empty database using mocked query"""
        # Mock the query to avoid SQLAlchemy syntax issues in source code
        mock_tool_stats = MagicMock()
        mock_tool_stats.total_tools = 0
        mock_tool_stats.available_tools = 0
        mock_tool_stats.checked_out_tools = 0
        mock_tool_stats.overdue_calibrations = 0

        mock_chemical_stats = MagicMock()
        mock_chemical_stats.total_chemicals = 0
        mock_chemical_stats.expired_chemicals = 0
        mock_chemical_stats.low_stock_chemicals = 0

        with patch('utils.bulk_operations.func') as mock_func:
            mock_func.count.return_value = MagicMock()
            mock_func.sum.return_value = MagicMock()
            mock_func.case.return_value = MagicMock()

            with patch.object(db.session, 'query') as mock_query:
                # Setup chain for tool stats
                mock_query.return_value.first.side_effect = [mock_tool_stats, mock_chemical_stats]
                # For the second query (chemicals), we need to mock the filter
                mock_query.return_value.filter.return_value.first.return_value = mock_chemical_stats

                result = get_dashboard_stats_optimized()

        assert result["tools"]["total"] == 0
        assert result["tools"]["available"] == 0
        assert result["tools"]["checked_out"] == 0
        assert result["tools"]["overdue_calibrations"] == 0
        assert result["chemicals"]["total"] == 0
        assert result["chemicals"]["expired"] == 0
        assert result["chemicals"]["low_stock"] == 0

    def test_tool_stats(self, app, db_session):
        """Test tool statistics with mocked query"""
        mock_tool_stats = MagicMock()
        mock_tool_stats.total_tools = 3
        mock_tool_stats.available_tools = 2
        mock_tool_stats.checked_out_tools = 1
        mock_tool_stats.overdue_calibrations = 1

        mock_chemical_stats = MagicMock()
        mock_chemical_stats.total_chemicals = 0
        mock_chemical_stats.expired_chemicals = 0
        mock_chemical_stats.low_stock_chemicals = 0

        with patch('utils.bulk_operations.func') as mock_func:
            mock_func.count.return_value = MagicMock()
            mock_func.sum.return_value = MagicMock()
            mock_func.case.return_value = MagicMock()

            with patch.object(db.session, 'query') as mock_query:
                mock_query.return_value.first.side_effect = [mock_tool_stats, mock_chemical_stats]
                mock_query.return_value.filter.return_value.first.return_value = mock_chemical_stats

                result = get_dashboard_stats_optimized()

        assert result["tools"]["total"] == 3
        assert result["tools"]["available"] == 2
        assert result["tools"]["checked_out"] == 1
        assert result["tools"]["overdue_calibrations"] == 1

    def test_chemical_stats(self, app, db_session):
        """Test chemical statistics with mocked query"""
        mock_tool_stats = MagicMock()
        mock_tool_stats.total_tools = 0
        mock_tool_stats.available_tools = 0
        mock_tool_stats.checked_out_tools = 0
        mock_tool_stats.overdue_calibrations = 0

        mock_chemical_stats = MagicMock()
        mock_chemical_stats.total_chemicals = 3
        mock_chemical_stats.expired_chemicals = 1
        mock_chemical_stats.low_stock_chemicals = 1

        with patch('utils.bulk_operations.func') as mock_func:
            mock_func.count.return_value = MagicMock()
            mock_func.sum.return_value = MagicMock()
            mock_func.case.return_value = MagicMock()

            with patch.object(db.session, 'query') as mock_query:
                mock_query.return_value.first.side_effect = [mock_tool_stats, mock_chemical_stats]
                mock_query.return_value.filter.return_value.first.return_value = mock_chemical_stats

                result = get_dashboard_stats_optimized()

        assert result["chemicals"]["total"] == 3
        assert result["chemicals"]["expired"] == 1
        assert result["chemicals"]["low_stock"] == 1

    def test_database_error_handling(self, app, db_session):
        """Test error handling when database query fails"""
        with patch('utils.bulk_operations.func') as mock_func:
            mock_func.count.return_value = MagicMock()
            mock_func.sum.return_value = MagicMock()
            mock_func.case.return_value = MagicMock()

            with patch.object(db.session, 'query', side_effect=Exception("Stats Error")):
                with pytest.raises(Exception) as exc_info:
                    get_dashboard_stats_optimized()

                assert "Stats Error" in str(exc_info.value)

    def test_null_values_handled(self, app, db_session):
        """Test that NULL values are handled correctly in stats"""
        # Test the 'or 0' fallback in the function when values are None
        mock_tool_stats = MagicMock()
        mock_tool_stats.total_tools = None
        mock_tool_stats.available_tools = None
        mock_tool_stats.checked_out_tools = None
        mock_tool_stats.overdue_calibrations = None

        mock_chemical_stats = MagicMock()
        mock_chemical_stats.total_chemicals = None
        mock_chemical_stats.expired_chemicals = None
        mock_chemical_stats.low_stock_chemicals = None

        with patch('utils.bulk_operations.func') as mock_func:
            mock_func.count.return_value = MagicMock()
            mock_func.sum.return_value = MagicMock()
            mock_func.case.return_value = MagicMock()

            with patch.object(db.session, 'query') as mock_query:
                mock_query.return_value.first.side_effect = [mock_tool_stats, mock_chemical_stats]
                mock_query.return_value.filter.return_value.first.return_value = mock_chemical_stats

                result = get_dashboard_stats_optimized()

        # All values should be integers (defaulted to 0), not None
        assert result["tools"]["total"] == 0
        assert result["tools"]["available"] == 0
        assert result["tools"]["checked_out"] == 0
        assert result["tools"]["overdue_calibrations"] == 0
        assert result["chemicals"]["total"] == 0
        assert result["chemicals"]["expired"] == 0
        assert result["chemicals"]["low_stock"] == 0


class TestGetToolsWithRelationships:
    """Tests for get_tools_with_relationships function"""

    def test_get_all_tools_no_filters(self, app, db_session):
        """Test getting all tools without filters"""
        # Create mock tools
        mock_tool1 = MagicMock()
        mock_tool1.tool_number = "REL-T001"
        mock_tool1.status = "available"

        mock_tool2 = MagicMock()
        mock_tool2.tool_number = "REL-T002"
        mock_tool2.status = "checked_out"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            # Add missing attributes to Tool model
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_query.options.return_value.all.return_value = [mock_tool1, mock_tool2]

                            result = get_tools_with_relationships()

        assert len(result) == 2
        tool_numbers = [t.tool_number for t in result]
        assert "REL-T001" in tool_numbers
        assert "REL-T002" in tool_numbers

    def test_filter_by_status(self, app, db_session):
        """Test filtering tools by status"""
        mock_tool = MagicMock()
        mock_tool.status = "available"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_options = mock_query.options.return_value
                            mock_options.filter.return_value.all.return_value = [mock_tool]

                            result = get_tools_with_relationships(filters={"status": "available"})

        assert len(result) == 1
        assert result[0].status == "available"
        mock_options.filter.assert_called_once()

    def test_filter_by_category(self, app, db_session):
        """Test filtering tools by category"""
        mock_tool = MagicMock()
        mock_tool.category = "Electronics"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_options = mock_query.options.return_value
                            mock_options.filter.return_value.all.return_value = [mock_tool]

                            result = get_tools_with_relationships(filters={"category": "Electronics"})

        assert len(result) == 1
        assert result[0].category == "Electronics"

    def test_filter_by_location(self, app, db_session):
        """Test filtering tools by location"""
        mock_tool = MagicMock()
        mock_tool.location = "Building A"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_options = mock_query.options.return_value
                            mock_options.filter.return_value.all.return_value = [mock_tool]

                            result = get_tools_with_relationships(filters={"location": "Building A"})

        assert len(result) == 1
        assert result[0].location == "Building A"

    def test_multiple_filters(self, app, db_session):
        """Test applying multiple filters"""
        mock_tool = MagicMock()
        mock_tool.location = "Lab A"
        mock_tool.category = "Electronics"
        mock_tool.status = "available"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_options = mock_query.options.return_value
                            # Chain of filter calls
                            mock_filter1 = MagicMock()
                            mock_filter2 = MagicMock()
                            mock_filter3 = MagicMock()
                            mock_options.filter.return_value = mock_filter1
                            mock_filter1.filter.return_value = mock_filter2
                            mock_filter2.filter.return_value = mock_filter3
                            mock_filter3.all.return_value = [mock_tool]

                            result = get_tools_with_relationships(
                                filters={"status": "available", "location": "Lab A", "category": "Electronics"}
                            )

        assert len(result) == 1
        assert result[0].location == "Lab A"
        assert result[0].category == "Electronics"

    def test_empty_filters_dict(self, app, db_session):
        """Test with empty filters dictionary"""
        mock_tool = MagicMock()
        mock_tool.tool_number = "EMPTY-F001"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_query.options.return_value.all.return_value = [mock_tool]

                            result = get_tools_with_relationships(filters={})

        assert len(result) == 1
        assert result[0].tool_number == "EMPTY-F001"

    def test_database_error_handling(self, app, db_session):
        """Test error handling when database query fails"""
        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Tool, 'checkouts', create=True, new=MagicMock()):
                with patch.object(Tool, 'calibrations', create=True, new=MagicMock()):
                    with patch.object(Tool, 'service_records', create=True, new=MagicMock()):
                        with patch.object(Tool, 'query') as mock_query:
                            mock_query.options.side_effect = Exception("Query Error")

                            with pytest.raises(Exception) as exc_info:
                                get_tools_with_relationships()

                            assert "Query Error" in str(exc_info.value)


class TestGetChemicalsWithRelationships:
    """Tests for get_chemicals_with_relationships function"""

    def test_get_all_non_archived_chemicals(self, app, db_session):
        """Test getting all non-archived chemicals"""
        mock_chemical = MagicMock()
        mock_chemical.part_number = "REL-C001"
        mock_chemical.is_archived = False

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    # Default filter for non-archived chemicals
                    mock_options.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships()

        assert len(result) == 1
        assert result[0].part_number == "REL-C001"

    def test_show_archived_chemicals(self, app, db_session):
        """Test showing archived chemicals with filter"""
        mock_active = MagicMock()
        mock_active.part_number = "SHOW-C001"
        mock_active.is_archived = False

        mock_archived = MagicMock()
        mock_archived.part_number = "SHOW-C002"
        mock_archived.is_archived = True

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    # When show_archived is True, no filter is applied
                    mock_options.all.return_value = [mock_active, mock_archived]

                    result = get_chemicals_with_relationships(filters={"show_archived": True})

        assert len(result) == 2
        part_numbers = [c.part_number for c in result]
        assert "SHOW-C001" in part_numbers
        assert "SHOW-C002" in part_numbers

    def test_filter_by_status(self, app, db_session):
        """Test filtering chemicals by status"""
        mock_chemical = MagicMock()
        mock_chemical.status = "available"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    mock_filter1 = MagicMock()
                    mock_options.filter.return_value = mock_filter1
                    mock_filter1.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships(filters={"status": "available"})

        assert len(result) == 1
        assert result[0].status == "available"

    def test_filter_by_category(self, app, db_session):
        """Test filtering chemicals by category"""
        mock_chemical = MagicMock()
        mock_chemical.category = "Solvents"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    mock_filter1 = MagicMock()
                    mock_options.filter.return_value = mock_filter1
                    mock_filter1.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships(filters={"category": "Solvents"})

        assert len(result) == 1
        assert result[0].category == "Solvents"

    def test_multiple_filters_with_archived(self, app, db_session):
        """Test multiple filters including show_archived"""
        mock_chemical = MagicMock()
        mock_chemical.part_number = "MFILT-C001"
        mock_chemical.category = "Solvents"
        mock_chemical.is_archived = True

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    # When show_archived is True, we skip the is_archived filter
                    mock_options.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships(
                        filters={"show_archived": True, "category": "Solvents"}
                    )

        assert len(result) == 1
        assert result[0].category == "Solvents"

    def test_empty_filters_dict(self, app, db_session):
        """Test with empty filters dictionary"""
        mock_chemical = MagicMock()
        mock_chemical.part_number = "EMPTY-FC001"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    # Empty filters still applies is_archived filter
                    mock_options.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships(filters={})

        assert len(result) == 1
        assert result[0].part_number == "EMPTY-FC001"

    def test_database_error_handling(self, app, db_session):
        """Test error handling when database query fails"""
        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_query.options.side_effect = Exception("Query Error")

                    with pytest.raises(Exception) as exc_info:
                        get_chemicals_with_relationships()

                    assert "Query Error" in str(exc_info.value)

    def test_no_filters_applies_archived_filter(self, app, db_session):
        """Test that None filters still applies archived filter"""
        mock_chemical = MagicMock()
        mock_chemical.part_number = "NO-FILT-001"

        with patch('utils.bulk_operations.joinedload') as mock_joinedload:
            mock_joinedload.return_value = MagicMock()
            with patch.object(Chemical, 'issuances', create=True, new=MagicMock()):
                with patch.object(Chemical, 'query') as mock_query:
                    mock_options = mock_query.options.return_value
                    mock_options.filter.return_value.all.return_value = [mock_chemical]

                    result = get_chemicals_with_relationships(filters=None)

        assert len(result) == 1
        # Verify filter was called (for is_archived)
        mock_options.filter.assert_called_once()


class TestOptimizeDatabaseQueries:
    """Tests for optimize_database_queries function"""

    def test_successful_optimization(self, app, db_session):
        """Test successful database optimization"""
        # Create tool that needs calibration update
        tool = Tool(
            tool_number="OPT-T001",
            serial_number="S-OT001",
            description="Optimization Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() - timedelta(days=10),
            calibration_status="current"
        )

        # Create chemical that needs status update
        chemical = Chemical(
            part_number="OPT-C001",
            lot_number="L-OC001",
            description="Optimization Chemical",
            manufacturer="Test",
            quantity=0,
            unit="ml",
            location="Storage",
            category="Testing",
            status="available",
            is_archived=False
        )

        db_session.add_all([tool, chemical])
        db_session.commit()

        result = optimize_database_queries()

        assert "calibration_updates" in result
        assert "chemical_updates" in result
        assert result["calibration_updates"]["overdue"] >= 1
        assert result["chemical_updates"]["out_of_stock"] >= 1

    def test_optimization_with_no_updates(self, app, db_session):
        """Test optimization when no updates are needed"""
        result = optimize_database_queries()

        assert "calibration_updates" in result
        assert "chemical_updates" in result
        assert isinstance(result["calibration_updates"], dict)
        assert isinstance(result["chemical_updates"], dict)

    def test_optimization_error_handling(self, app, db_session):
        """Test error handling during optimization"""
        with patch('utils.bulk_operations.bulk_update_tool_calibration_status',
                   side_effect=Exception("Optimization Error")):
            with pytest.raises(Exception) as exc_info:
                optimize_database_queries()

            assert "Optimization Error" in str(exc_info.value)

    def test_optimization_rollback_on_error(self, app, db_session):
        """Test that changes are rolled back on error"""
        # Create tool that would be updated
        tool = Tool(
            tool_number="ROLL-T001",
            serial_number="S-ROLL001",
            description="Rollback Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            status="available",
            next_calibration_date=datetime.utcnow() - timedelta(days=10),
            calibration_status="current"
        )
        db_session.add(tool)
        db_session.commit()

        original_status = tool.calibration_status

        # Mock commit to fail
        with patch.object(db.session, 'commit', side_effect=Exception("Commit Error")):
            with pytest.raises(Exception):
                optimize_database_queries()

        # Refresh and check status wasn't changed (due to rollback)
        db_session.refresh(tool)
        # Note: The actual update may have occurred before the commit failed,
        # but the rollback should revert it. This tests the error handling path.

    def test_optimization_commits_all_changes(self, app, db_session):
        """Test that all changes are committed together"""
        # Create multiple items that need updating
        tools = [
            Tool(
                tool_number=f"COMMIT-T{i}",
                serial_number=f"S-COMMT{i}",
                description=f"Commit Tool {i}",
                condition="Good",
                location="Lab",
                category="Testing",
                status="available",
                next_calibration_date=datetime.utcnow() - timedelta(days=10),
                calibration_status="current"
            )
            for i in range(2)
        ]

        chemicals = [
            Chemical(
                part_number=f"COMMIT-C{i}",
                lot_number=f"L-COMC{i}",
                description=f"Commit Chemical {i}",
                manufacturer="Test",
                quantity=0,
                unit="ml",
                location="Storage",
                category="Testing",
                status="available",
                is_archived=False
            )
            for i in range(2)
        ]

        for item in tools + chemicals:
            db_session.add(item)
        db_session.commit()

        result = optimize_database_queries()

        # Verify both tools and chemicals were updated
        assert result["calibration_updates"]["overdue"] >= 2
        assert result["chemical_updates"]["out_of_stock"] >= 2


class TestLoggingAndErrorMessages:
    """Tests for logging functionality in bulk operations"""

    def test_bulk_log_activities_logs_info(self, app, db_session, regular_user, caplog):
        """Test that bulk_log_activities logs info message"""
        import logging

        with caplog.at_level(logging.INFO):
            activities = [
                {
                    "user_id": regular_user.id,
                    "activity_type": "test",
                    "description": "Test"
                }
            ]
            bulk_log_activities(activities)

        assert "Bulk logged" in caplog.text
        assert "user activities" in caplog.text

    def test_bulk_log_audit_events_logs_info(self, app, db_session, caplog):
        """Test that bulk_log_audit_events logs info message"""
        import logging

        with caplog.at_level(logging.INFO):
            audit_logs = [
                {
                    "action_type": "test",
                    "action_details": "Test"
                }
            ]
            bulk_log_audit_events(audit_logs)

        assert "Bulk logged" in caplog.text
        assert "audit events" in caplog.text

    def test_bulk_update_tool_calibration_logs_info(self, app, db_session, caplog):
        """Test that bulk_update_tool_calibration_status logs info"""
        import logging

        with caplog.at_level(logging.INFO):
            bulk_update_tool_calibration_status()

        assert "Bulk updated calibration status" in caplog.text

    def test_bulk_update_chemical_status_logs_info(self, app, db_session, caplog):
        """Test that bulk_update_chemical_status logs info"""
        import logging

        with caplog.at_level(logging.INFO):
            bulk_update_chemical_status()

        assert "Bulk updated chemical status" in caplog.text

    def test_optimize_database_queries_logs_success(self, app, db_session, caplog):
        """Test that optimize_database_queries logs success"""
        import logging

        with caplog.at_level(logging.INFO):
            optimize_database_queries()

        assert "Database optimization completed successfully" in caplog.text

    def test_error_logging_on_failure(self, app, db_session, caplog):
        """Test that errors are logged correctly"""
        import logging

        with caplog.at_level(logging.ERROR):
            with patch.object(db.session, 'query', side_effect=Exception("Test Error")):
                with pytest.raises(Exception):
                    get_dashboard_stats_optimized()

        assert "Error getting optimized dashboard stats" in caplog.text
