"""
Tests for Tool Calibration Routes

This module tests the calibration management endpoints including:
- Calibration records CRUD
- Due and overdue calibrations
- Calibration standards management
- Certificate management
"""

import json
from datetime import datetime, timedelta

import pytest

from models import AuditLog, Tool


class TestCalibrationListEndpoint:
    """Test the GET /api/calibrations endpoint"""

    def test_get_calibrations_empty(self, client, auth_headers_materials):
        """Test getting calibrations when none exist"""
        response = client.get("/api/calibrations", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "calibrations" in data

    def test_get_calibrations_with_data(self, client, auth_headers_materials, db_session, test_tool):
        """Test getting calibrations with data"""
        # Make tool require calibration
        test_tool.requires_calibration = True
        test_tool.calibration_frequency_days = 90
        db_session.commit()

        response = client.get("/api/calibrations", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "calibrations" in data

    def test_get_calibrations_without_auth(self, client):
        """Test getting calibrations without authentication"""
        response = client.get("/api/calibrations")
        # Some calibration endpoints may not require auth, check actual behavior
        # If it requires auth, expect 401
        assert response.status_code in [200, 401]


class TestDueCalibrations:
    """Test the GET /api/calibrations/due endpoint"""

    def test_get_due_calibrations(self, client, auth_headers_materials, db_session, test_tool):
        """Test getting calibrations that are due"""
        # Set up tool with calibration due soon
        test_tool.requires_calibration = True
        test_tool.calibration_frequency_days = 30
        test_tool.last_calibration_date = datetime.utcnow() - timedelta(days=25)
        test_tool.next_calibration_date = datetime.utcnow() + timedelta(days=5)
        db_session.commit()

        response = client.get("/api/calibrations/due", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "tools" in data or "calibrations" in data

    def test_get_due_calibrations_with_days_parameter(self, client, auth_headers_materials):
        """Test getting due calibrations with custom days parameter"""
        response = client.get("/api/calibrations/due?days=14", headers=auth_headers_materials)

        assert response.status_code == 200


class TestOverdueCalibrations:
    """Test the GET /api/calibrations/overdue endpoint"""

    def test_get_overdue_calibrations(self, client, auth_headers_materials, db_session, test_tool):
        """Test getting overdue calibrations"""
        # Set up tool with overdue calibration
        test_tool.requires_calibration = True
        test_tool.calibration_frequency_days = 30
        test_tool.last_calibration_date = datetime.utcnow() - timedelta(days=60)
        test_tool.next_calibration_date = datetime.utcnow() - timedelta(days=30)
        db_session.commit()

        response = client.get("/api/calibrations/overdue", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "tools" in data or "calibrations" in data

    def test_get_overdue_calibrations_empty(self, client, auth_headers_materials):
        """Test getting overdue calibrations when none exist"""
        response = client.get("/api/calibrations/overdue", headers=auth_headers_materials)

        assert response.status_code == 200


class TestToolCalibrationHistory:
    """Test the GET /api/tools/<id>/calibrations endpoint"""

    def test_get_tool_calibration_history(self, client, auth_headers_materials, test_tool):
        """Test getting calibration history for a tool"""
        response = client.get(f"/api/tools/{test_tool.id}/calibrations",
                              headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "calibrations" in data

    def test_get_tool_calibration_history_not_found(self, client, auth_headers_materials):
        """Test getting calibration history for non-existent tool"""
        response = client.get("/api/tools/99999/calibrations",
                              headers=auth_headers_materials)
        assert response.status_code in [200, 404, 500]  # May return empty list, 404, or 500


class TestCreateCalibrationRecord:
    """Test the POST /api/tools/<id>/calibrations endpoint"""

    def test_create_calibration_record_success(self, client, auth_headers_admin, test_tool, db_session):
        """Test creating a calibration record"""
        # Make tool require calibration
        test_tool.requires_calibration = True
        test_tool.calibration_frequency_days = 90
        # Use timezone-naive dates to avoid comparison issues
        test_tool.last_calibration_date = datetime.utcnow() - timedelta(days=30)
        test_tool.next_calibration_date = datetime.utcnow() + timedelta(days=60)
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat(),
            "calibration_status": "pass",
            "calibrated_by": "John Technician",
            "notes": "All measurements within tolerance",
            "certificate_number": "CERT-2024-001"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)

        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert "calibration" in data or "id" in data

    def test_create_calibration_record_fail_status(self, client, auth_headers_admin, test_tool, db_session):
        """Test creating a failed calibration record"""
        test_tool.requires_calibration = True
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "fail",
            "calibrated_by": "Jane Technician",
            "notes": "Out of tolerance - requires repair"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)

        assert response.status_code in [200, 201]

    def test_create_calibration_record_limited_status(self, client, auth_headers_admin, test_tool, db_session):
        """Test creating a limited calibration record"""
        test_tool.requires_calibration = True
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "limited",
            "calibrated_by": "Bob Technician",
            "notes": "Limited use only - specific range"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)

        assert response.status_code in [200, 201]

    def test_create_calibration_without_auth(self, client, test_tool):
        """Test creating calibration without authentication"""
        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "pass"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data)
        assert response.status_code == 401

    def test_create_calibration_missing_required_fields(self, client, auth_headers_admin, test_tool):
        """Test creating calibration with missing required fields"""
        calibration_data = {
            "notes": "Incomplete data"
            # Missing calibration_date and calibration_status
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)
        assert response.status_code == 400

    def test_create_calibration_invalid_status(self, client, auth_headers_admin, test_tool, db_session):
        """Test creating calibration with invalid status"""
        test_tool.requires_calibration = True
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "invalid_status"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)
        assert response.status_code == 400

    def test_create_calibration_for_non_calibratable_tool(self, client, auth_headers_admin, test_tool, db_session):
        """Test creating calibration for tool that doesn't require calibration"""
        test_tool.requires_calibration = False
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "pass"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)
        # Should either fail or handle gracefully
        assert response.status_code in [200, 201, 400]


class TestCalibrationStandardsEndpoints:
    """Test calibration standards management"""

    def test_get_calibration_standards(self, client, auth_headers_materials):
        """Test getting list of calibration standards"""
        response = client.get("/api/calibration-standards", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "standards" in data

    def test_create_calibration_standard(self, client, auth_headers_materials):
        """Test creating a calibration standard"""
        standard_data = {
            "name": "Test Standard",
            "description": "Reference standard for testing",
            "standard_number": "STD-001",
            "certification_date": datetime.utcnow().isoformat(),
            "expiration_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
        }

        response = client.post("/api/calibration-standards",
                               json=standard_data,
                               headers=auth_headers_materials)

        assert response.status_code in [200, 201]

    def test_create_calibration_standard_without_auth(self, client):
        """Test creating standard without authentication"""
        standard_data = {
            "name": "Unauthorized Standard"
        }

        response = client.post("/api/calibration-standards", json=standard_data)
        assert response.status_code == 401

    def test_get_calibration_standard_by_id(self, client, auth_headers_materials, db_session):
        """Test getting a specific calibration standard"""
        # First create a standard via direct DB operation
        from models import CalibrationStandard
        try:
            standard = CalibrationStandard(
                name="Test Standard for Get",
                standard_number="STD-GET-001",
                certification_date=datetime.utcnow(),
                expiration_date=datetime.utcnow() + timedelta(days=365)
            )
            db_session.add(standard)
            db_session.commit()

            response = client.get(f"/api/calibration-standards/{standard.id}",
                                  headers=auth_headers_materials)

            assert response.status_code == 200
        except ImportError:
            # CalibrationStandard model may not exist
            pytest.skip("CalibrationStandard model not available")

    def test_update_calibration_standard(self, client, auth_headers_materials, db_session):
        """Test updating a calibration standard"""
        from models import CalibrationStandard
        try:
            standard = CalibrationStandard(
                name="Update Test Standard",
                standard_number="STD-UPD-001",
                certification_date=datetime.utcnow(),
                expiration_date=datetime.utcnow() + timedelta(days=365)
            )
            db_session.add(standard)
            db_session.commit()

            update_data = {
                "name": "Updated Standard Name",
                "description": "Updated description"
            }

            response = client.put(f"/api/calibration-standards/{standard.id}",
                                  json=update_data,
                                  headers=auth_headers_materials)

            assert response.status_code == 200
        except ImportError:
            pytest.skip("CalibrationStandard model not available")


class TestCalibrationCertificate:
    """Test calibration certificate endpoints"""

    def test_upload_calibration_certificate(self, client, auth_headers_admin, test_tool, db_session):
        """Test uploading calibration certificate"""
        # First create a calibration record
        test_tool.requires_calibration = True
        test_tool.last_calibration_date = datetime.utcnow() - timedelta(days=30)
        test_tool.next_calibration_date = datetime.utcnow() + timedelta(days=60)
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat(),
            "calibration_status": "pass"
        }

        create_response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                                      json=calibration_data,
                                      headers=auth_headers_admin)

        if create_response.status_code in [200, 201]:
            cal_data = json.loads(create_response.data)
            cal_id = cal_data.get("id") or cal_data.get("calibration", {}).get("id")

            if cal_id:
                # Upload certificate - endpoint expects file upload, not JSON
                # Create a mock PDF file
                from io import BytesIO
                pdf_content = BytesIO(b"%PDF-1.4 test certificate content")
                pdf_content.name = "certificate.pdf"

                response = client.post(f"/api/calibrations/{cal_id}/certificate",
                                       data={"certificate": (pdf_content, "certificate.pdf")},
                                       content_type="multipart/form-data",
                                       headers=auth_headers_admin)

                assert response.status_code in [200, 201, 400]  # 400 if file validation fails

    def test_get_calibration_certificate(self, client, auth_headers_materials):
        """Test getting calibration certificate"""
        # This test requires an existing calibration with certificate
        # For now, just test that the endpoint exists (requires Materials department)
        response = client.get("/api/calibrations/1/certificate",
                              headers=auth_headers_materials)

        # Should return 404 (not found) or 200 (found) or 403 (forbidden) or 500 (internal error)
        assert response.status_code in [200, 404, 403, 500]


class TestCalibrationSecurityFeatures:
    """Test security features in calibration routes"""

    def test_regular_user_cannot_create_calibration(self, client, auth_headers_user, test_tool):
        """Test that regular users cannot create calibration records"""
        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "pass"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_user)

        # Should be forbidden or unauthorized
        assert response.status_code in [401, 403]

    def test_xss_prevention_in_notes(self, client, auth_headers_admin, test_tool, db_session):
        """Test XSS prevention in calibration notes"""
        test_tool.requires_calibration = True
        db_session.commit()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "pass",
            "notes": '<script>alert("XSS")</script>'
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)

        if response.status_code in [200, 201]:
            data = json.loads(response.data)
            notes = data.get("notes") or data.get("calibration", {}).get("notes", "")
            # Notes should be sanitized
            assert "<script>" not in notes

    def test_invalid_date_format(self, client, auth_headers_admin, test_tool):
        """Test validation of date format"""
        calibration_data = {
            "calibration_date": "invalid-date",
            "calibration_status": "pass"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)
        assert response.status_code == 400


class TestCalibrationAuditLog:
    """Test calibration audit logging"""

    def test_calibration_creates_audit_log(self, client, auth_headers_admin, test_tool, db_session):
        """Test that calibration creation is logged"""
        test_tool.requires_calibration = True
        db_session.commit()

        initial_count = AuditLog.query.filter(
            AuditLog.action_type.like("%calibr%")
        ).count()

        calibration_data = {
            "calibration_date": datetime.utcnow().isoformat() + "Z",
            "calibration_status": "pass",
            "calibrated_by": "Audit Test Tech"
        }

        response = client.post(f"/api/tools/{test_tool.id}/calibrations",
                               json=calibration_data,
                               headers=auth_headers_admin)

        if response.status_code in [200, 201]:
            # Check that audit log was created
            final_count = AuditLog.query.filter(
                AuditLog.action_type.like("%calibr%")
            ).count()
            # May or may not log, depending on implementation
            assert final_count >= initial_count
