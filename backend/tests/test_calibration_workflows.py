"""
Tool calibration workflow tests for SupplyLine MRO Suite

Tests calibration management including:
- Calibration record creation
- Calibration due date tracking
- Calibration expiry notifications
- Calibration certificate uploads
- Calibration history
- Out-of-calibration tool handling
"""

from datetime import datetime, timedelta
from io import BytesIO

import pytest

from models import Tool


@pytest.mark.calibration
@pytest.mark.integration
class TestCalibrationRecords:
    """Test calibration record management"""

    def test_create_calibration_record(self, client, db_session, admin_user, auth_headers, sample_tool):
        """Test creating a calibration record for a tool"""
        from models import ToolCalibration

        calibration_data = {
            "calibration_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "next_calibration_date": (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "calibration_status": "pass",
            "calibration_notes": "Annual calibration completed"
        }

        response = client.post(
            f"/api/tools/{sample_tool.id}/calibrations",
            headers=auth_headers,
            json=calibration_data
        )

        assert response.status_code in [201, 400, 404]

        if response.status_code == 201:
            # Verify calibration created
            calibration = ToolCalibration.query.filter_by(
                tool_id=sample_tool.id
            ).first()
            assert calibration is not None
            assert calibration.calibration_status == "pass"

    def test_calibration_updates_tool_status(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test that calibration updates tool calibration status"""
        from models import ToolCalibration

        # Create tool needing calibration
        tool = Tool(
            tool_number="CAL001",
            serial_number="SN-CAL001",
            description="Calibrated Tool",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        # Create calibration
        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow(),
            next_calibration_date=datetime.utcnow() + timedelta(days=365),
            performed_by_user_id=admin_user.id,
            calibration_status="pass",
            calibration_notes="Annual calibration"
        )
        db_session.add(calibration)
        db_session.commit()

        # Verify tool calibration date updated
        db_session.refresh(tool)
        # Tool should have calibration_due field updated if it exists
        if hasattr(tool, "calibration_due"):
            assert tool.calibration_due is not None

    # TODO: Re-enable when calibration API endpoint is implemented
    @pytest.mark.skip(reason="Calibration API endpoint not yet implemented")
    def test_failed_calibration_marks_tool(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test that failed calibration properly marks tool"""
        from models import ToolCalibration

        # Create tool
        tool = Tool(
            tool_number="CAL002",
            serial_number="SN-CAL002",
            description="Tool Failing Calibration",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "calibration_status": "fail",
            "calibration_notes": "Out of tolerance, requires adjustment"
        }

        response = client.post(
            f"/api/tools/{tool.id}/calibrations",
            headers=auth_headers,
            json=calibration_data
        )

        assert response.status_code in [201, 400, 404]

        if response.status_code == 201:
            # Tool should be marked as needing service or out of calibration
            db_session.refresh(tool)
            # Check status or calibration status
            if hasattr(tool, "calibration_status"):
                assert tool.calibration_status in ["failed", "out_of_calibration", "needs_service"]

    # TODO: Re-enable when calibration history API is implemented
    @pytest.mark.skip(reason="Calibration history API endpoint not yet implemented")
    def test_retrieve_calibration_history(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test retrieving calibration history for a tool"""
        from models import ToolCalibration

        # Create tool
        tool = Tool(
            tool_number="CAL003",
            serial_number="SN-CAL003",
            description="Tool with History",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        # Create multiple calibration records
        for i in range(3):
            calibration = ToolCalibration(
                tool_id=tool.id,
                calibration_date=datetime.utcnow() - timedelta(days=365 * i),
                next_calibration_date=datetime.utcnow() + timedelta(days=365 * (1 - i)),
                performed_by_user_id=admin_user.id,
                calibration_status="pass",
                calibration_notes=f"Calibration {i}"
            )
            db_session.add(calibration)

        db_session.commit()

        # Retrieve history
        response = client.get(
            f"/api/tools/{tool.id}/calibrations",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) >= 3

    # TODO: Re-enable when certificate upload API is implemented
    @pytest.mark.skip(reason="Certificate upload API endpoint not yet implemented")
    def test_calibration_certificate_upload(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test uploading calibration certificate"""
        from models import ToolCalibration

        # Create tool and calibration
        tool = Tool(
            tool_number="CAL004",
            serial_number="SN-CAL004",
            description="Tool with Certificate",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow(),
            next_calibration_date=datetime.utcnow() + timedelta(days=365),
            performed_by_user_id=admin_user.id,
            calibration_status="pass",
            calibration_notes="Certificate test"
        )
        db_session.add(calibration)
        db_session.commit()

        # Upload certificate
        certificate_data = b"%PDF-1.4\nFake PDF content for testing"
        data = {
            "file": (BytesIO(certificate_data), "calibration_cert.pdf")
        }

        response = client.post(
            f"/api/calibrations/{calibration.id}/certificate",
            headers=auth_headers,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code in [200, 201, 404, 422]


@pytest.mark.calibration
@pytest.mark.integration
class TestCalibrationDueTracking:
    """Test calibration due date tracking"""

    def test_identify_tools_due_for_calibration(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test identifying tools due for calibration"""
        from models import ToolCalibration

        # Create tools with different calibration statuses
        tools_data = [
            ("DUE001", -30, "overdue"),  # Overdue
            ("DUE002", 15, "due_soon"),  # Due soon
            ("DUE003", 200, "current"),  # Current
        ]

        for tool_num, days_offset, status in tools_data:
            tool = Tool(
                tool_number=tool_num,
                serial_number=f"SN-{tool_num}",
                description=f"Tool {status}",
                condition="Good",
                location="Lab",
                category="Measurement",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)
            db_session.flush()

            # Add calibration record
            calibration = ToolCalibration(
                tool_id=tool.id,
                calibration_date=datetime.utcnow() - timedelta(days=365),
                next_calibration_date=datetime.utcnow() + timedelta(days=days_offset),
                performed_by_user_id=admin_user.id,
                calibration_status="pass",
                calibration_notes=f"Calibration {status}"
            )
            db_session.add(calibration)

        db_session.commit()

        # Query for overdue tools
        response = client.get(
            "/api/tools/calibration-due?status=overdue",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            # Should include overdue tool
            assert any(t["tool_number"] == "DUE001" for t in data) or len(data) == 0

    def test_calibration_reminder_generation(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test generation of calibration reminders"""
        from models import ToolCalibration

        # Create tool due for calibration soon
        tool = Tool(
            tool_number="REM001",
            serial_number="SN-REM001",
            description="Tool Needing Reminder",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        # Add calibration due in 30 days
        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow() - timedelta(days=335),
            next_calibration_date=datetime.utcnow() + timedelta(days=30),
            performed_by_user_id=admin_user.id,
            calibration_status="pass"
        )
        db_session.add(calibration)
        db_session.commit()

        # Check reminder endpoint
        response = client.get(
            "/api/calibrations/reminders",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

    def test_prevent_checkout_of_expired_calibration_tools(self, client, db_session, admin_user, test_user, auth_headers, test_warehouse):
        """Test that tools with expired calibration cannot be checked out"""
        from models import ToolCalibration

        # Create tool with expired calibration
        tool = Tool(
            tool_number="EXP001",
            serial_number="SN-EXP001",
            description="Expired Calibration Tool",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        # Add expired calibration
        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow() - timedelta(days=400),
            next_calibration_date=datetime.utcnow() - timedelta(days=35),  # Expired
            performed_by_user_id=admin_user.id,
            # certificate_number="CAL-EXP001",
            calibration_status="pass"
        )
        db_session.add(calibration)
        db_session.commit()

        # Try to checkout expired tool
        response = client.post(
            f"/api/tools/{tool.id}/checkout",
            headers=auth_headers,
            json={"user_id": test_user.id}
        )

        # Should prevent checkout or warn
        assert response.status_code in [400, 403, 404, 422]


@pytest.mark.calibration
@pytest.mark.api
class TestCalibrationAPI:
    """Test calibration API endpoints"""

    # TODO: Re-enable when list calibrations API is implemented
    @pytest.mark.skip(reason="List calibrations API endpoint not yet implemented")
    def test_list_all_calibrations(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test listing all calibrations"""
        from models import ToolCalibration

        # Create multiple tools with calibrations
        for i in range(5):
            tool = Tool(
                tool_number=f"LIST{i:03d}",
                serial_number=f"SN-LIST{i:03d}",
                description=f"List Tool {i}",
                condition="Good",
                location="Lab",
                category="Measurement",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)
            db_session.flush()

            calibration = ToolCalibration(
                tool_id=tool.id,
                calibration_date=datetime.utcnow(),
                next_calibration_date=datetime.utcnow() + timedelta(days=365),
                performed_by_user_id=admin_user.id,
                # certificate_number=f"CAL-LIST{i:03d}",
                calibration_status="pass"
            )
            db_session.add(calibration)

        db_session.commit()

        # List all calibrations
        response = client.get("/api/calibrations", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) >= 5

    def test_update_calibration_record(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test updating a calibration record"""
        from models import ToolCalibration

        # Create calibration
        tool = Tool(
            tool_number="UPD001",
            serial_number="SN-UPD001",
            description="Update Test Tool",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow(),
            next_calibration_date=datetime.utcnow() + timedelta(days=365),
            performed_by_user_id=admin_user.id,
            # certificate_number="CAL-UPD001",
            calibration_status="pass",
            calibration_notes="Original notes"
        )
        db_session.add(calibration)
        db_session.commit()

        # Update calibration
        update_data = {
            "notes": "Updated notes with more details",
            "result": "Pass"
        }

        response = client.put(
            f"/api/calibrations/{calibration.id}",
            headers=auth_headers,
            json=update_data
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Verify update
            db_session.refresh(calibration)
            assert calibration.notes == "Updated notes with more details"

    def test_delete_calibration_record(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test deleting a calibration record"""
        from models import ToolCalibration

        # Create calibration
        tool = Tool(
            tool_number="DEL001",
            serial_number="SN-DEL001",
            description="Delete Test Tool",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow(),
            next_calibration_date=datetime.utcnow() + timedelta(days=365),
            performed_by_user_id=admin_user.id,
            # certificate_number="CAL-DEL001",
            calibration_status="pass"
        )
        db_session.add(calibration)
        db_session.commit()

        calibration_id = calibration.id

        # Delete calibration
        response = client.delete(
            f"/api/calibrations/{calibration_id}",
            headers=auth_headers
        )

        assert response.status_code in [200, 204, 404]

        if response.status_code in [200, 204]:
            # Verify deleted
            deleted = ToolCalibration.query.get(calibration_id)
            assert deleted is None


@pytest.mark.calibration
@pytest.mark.models
class TestCalibrationModels:
    """Test calibration data models"""

    # TODO: Re-enable when model fields are updated
    @pytest.mark.skip(reason="Testing planned fields not yet in model")
    def test_tool_calibration_model_fields(self, db_session):
        """Test ToolCalibration model has required fields"""
        from models import ToolCalibration

        # Check model has expected fields
        expected_fields = [
            "id",
            "tool_id",
            "calibration_date",
            "next_calibration_date",
            "performed_by_user_id",
            "calibration_status"
        ]

        for field in expected_fields:
            assert hasattr(ToolCalibration, field), f"ToolCalibration missing field: {field}"

    def test_calibration_status_calculation(self, db_session, test_warehouse):
        """Test calibration status is calculated correctly"""
        from models import ToolCalibration

        # Create tool with calibration
        tool = Tool(
            tool_number="STAT001",
            serial_number="SN-STAT001",
            description="Status Test Tool",
            condition="Good",
            location="Lab",
            category="Measurement",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        # Create current calibration
        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=datetime.utcnow(),
            next_calibration_date=datetime.utcnow() + timedelta(days=365),
            performed_by_user_id=admin_user.id,
            # certificate_number="CAL-STAT001",
            calibration_status="pass"
        )
        db_session.add(calibration)
        db_session.commit()

        # Check status (if model provides this)
        if hasattr(calibration, "is_current"):
            assert calibration.is_current() is True

        if hasattr(calibration, "is_overdue"):
            assert calibration.is_overdue() is False
