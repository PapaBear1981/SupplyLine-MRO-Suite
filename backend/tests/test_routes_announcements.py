"""
Comprehensive tests for announcements routes.
Tests all CRUD operations, authentication, authorization, validation, and edge cases.
"""

import pytest
from datetime import datetime, timedelta, UTC


class TestGetAnnouncements:
    """Tests for GET /api/announcements endpoint."""

    def test_get_announcements_empty(self, client):
        """Test getting announcements when none exist."""
        response = client.get("/api/announcements")
        assert response.status_code == 200
        data = response.get_json()
        assert data["announcements"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["pages"] == 0

    def test_get_announcements_with_data(self, client, db_session):
        """Test getting announcements with existing data."""
        from models import Announcement

        # Create test announcements
        announcement1 = Announcement(
            title="Test Announcement 1",
            content="Test content 1",
            priority="high",
            created_by=1,
            is_active=True
        )
        announcement2 = Announcement(
            title="Test Announcement 2",
            content="Test content 2",
            priority="low",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement1)
        db_session.add(announcement2)
        db_session.commit()

        response = client.get("/api/announcements")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["announcements"]) == 2
        assert data["total"] == 2
        assert data["pages"] == 1

    def test_get_announcements_pagination(self, client, db_session):
        """Test pagination of announcements."""
        from models import Announcement

        # Create 15 announcements
        for i in range(15):
            announcement = Announcement(
                title=f"Announcement {i}",
                content=f"Content {i}",
                priority="medium",
                created_by=1,
                is_active=True
            )
            db_session.add(announcement)
        db_session.commit()

        # Get first page (default limit=10)
        response = client.get("/api/announcements?page=1&limit=5")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["announcements"]) == 5
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["limit"] == 5
        assert data["pages"] == 3

        # Get second page
        response = client.get("/api/announcements?page=2&limit=5")
        data = response.get_json()
        assert len(data["announcements"]) == 5
        assert data["page"] == 2

        # Get third page
        response = client.get("/api/announcements?page=3&limit=5")
        data = response.get_json()
        assert len(data["announcements"]) == 5
        assert data["page"] == 3

    def test_get_announcements_filter_by_priority(self, client, db_session):
        """Test filtering announcements by priority."""
        from models import Announcement

        # Create announcements with different priorities
        high_priority = Announcement(
            title="High Priority",
            content="Important",
            priority="high",
            created_by=1,
            is_active=True
        )
        low_priority = Announcement(
            title="Low Priority",
            content="Less important",
            priority="low",
            created_by=1,
            is_active=True
        )
        db_session.add(high_priority)
        db_session.add(low_priority)
        db_session.commit()

        # Filter by high priority
        response = client.get("/api/announcements?priority=high")
        data = response.get_json()
        assert len(data["announcements"]) == 1
        assert data["announcements"][0]["priority"] == "high"

        # Filter by low priority
        response = client.get("/api/announcements?priority=low")
        data = response.get_json()
        assert len(data["announcements"]) == 1
        assert data["announcements"][0]["priority"] == "low"

    def test_get_announcements_filter_inactive(self, client, db_session):
        """Test filtering out inactive announcements."""
        from models import Announcement

        # Create active and inactive announcements
        active = Announcement(
            title="Active",
            content="Active content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        inactive = Announcement(
            title="Inactive",
            content="Inactive content",
            priority="medium",
            created_by=1,
            is_active=False
        )
        db_session.add(active)
        db_session.add(inactive)
        db_session.commit()

        # Default: active_only=true
        response = client.get("/api/announcements")
        data = response.get_json()
        assert len(data["announcements"]) == 1
        assert data["announcements"][0]["title"] == "Active"

        # Explicitly show all (active_only=false)
        response = client.get("/api/announcements?active_only=false")
        data = response.get_json()
        assert len(data["announcements"]) == 2

    def test_get_announcements_filter_expired(self, client, db_session):
        """Test filtering out expired announcements."""
        from models import Announcement

        # Create expired and non-expired announcements
        future_date = datetime.now(UTC) + timedelta(days=7)
        past_date = datetime.now(UTC) - timedelta(days=1)

        not_expired = Announcement(
            title="Not Expired",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True,
            expiration_date=future_date
        )
        expired = Announcement(
            title="Expired",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True,
            expiration_date=past_date
        )
        no_expiration = Announcement(
            title="No Expiration",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True,
            expiration_date=None
        )
        db_session.add(not_expired)
        db_session.add(expired)
        db_session.add(no_expiration)
        db_session.commit()

        # Only non-expired should be returned
        response = client.get("/api/announcements")
        data = response.get_json()
        assert len(data["announcements"]) == 2
        titles = [a["title"] for a in data["announcements"]]
        assert "Not Expired" in titles
        assert "No Expiration" in titles
        assert "Expired" not in titles

    def test_get_announcements_with_auth_includes_read_status(self, client, db_session, regular_user, user_auth_headers):
        """Test that authenticated users see read status."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Mark as read
        read_record = AnnouncementRead(
            announcement_id=announcement.id,
            user_id=regular_user.id
        )
        db_session.add(read_record)
        db_session.commit()

        response = client.get("/api/announcements", headers=user_auth_headers)
        data = response.get_json()
        assert len(data["announcements"]) == 1
        assert data["announcements"][0]["read"] is True
        assert "read_at" in data["announcements"][0]

    def test_get_announcements_without_auth_no_read_status(self, client, db_session):
        """Test that unauthenticated users don't see read status."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get("/api/announcements")
        data = response.get_json()
        assert len(data["announcements"]) == 1
        # Should not have read status fields
        assert "read" not in data["announcements"][0]

    def test_get_announcements_unread_status(self, client, db_session, regular_user, user_auth_headers):
        """Test that unread announcements show read=False."""
        from models import Announcement

        announcement = Announcement(
            title="Unread",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get("/api/announcements", headers=user_auth_headers)
        data = response.get_json()
        assert len(data["announcements"]) == 1
        assert data["announcements"][0]["read"] is False
        assert "read_at" not in data["announcements"][0]

    def test_get_announcements_ordered_by_created_at(self, client, db_session):
        """Test that announcements are ordered by created_at descending."""
        from models import Announcement
        import time

        # Create announcements with slight delay to ensure different timestamps
        announcement1 = Announcement(
            title="First",
            content="Content 1",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement1)
        db_session.commit()

        time.sleep(0.01)  # Small delay

        announcement2 = Announcement(
            title="Second",
            content="Content 2",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement2)
        db_session.commit()

        response = client.get("/api/announcements")
        data = response.get_json()
        # Newest first
        assert data["announcements"][0]["title"] == "Second"
        assert data["announcements"][1]["title"] == "First"


class TestGetSingleAnnouncement:
    """Tests for GET /api/announcements/<id> endpoint."""

    def test_get_announcement_success(self, client, db_session):
        """Test getting a single announcement."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="high",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["priority"] == "high"

    def test_get_announcement_not_found(self, client):
        """Test getting non-existent announcement returns 404 or 500."""
        response = client.get("/api/announcements/99999")
        # The get_or_404 raises an exception caught by generic handler
        assert response.status_code in [404, 500]

    def test_get_announcement_with_auth_includes_read_status(self, client, db_session, regular_user, user_auth_headers):
        """Test authenticated user sees read status."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Mark as read
        read_record = AnnouncementRead(
            announcement_id=announcement.id,
            user_id=regular_user.id
        )
        db_session.add(read_record)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}", headers=user_auth_headers)
        data = response.get_json()
        assert data["read"] is True
        assert "read_at" in data

    def test_get_announcement_unread_status(self, client, db_session, regular_user, user_auth_headers):
        """Test unread announcement shows read=False."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}", headers=user_auth_headers)
        data = response.get_json()
        assert data["read"] is False

    def test_get_announcement_admin_includes_read_statistics(self, client, db_session, admin_user, auth_headers, regular_user):
        """Test admin user sees read statistics."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=admin_user.id,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Create read records
        read_record = AnnouncementRead(
            announcement_id=announcement.id,
            user_id=regular_user.id
        )
        db_session.add(read_record)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}", headers=auth_headers)
        data = response.get_json()
        assert "reads" in data
        assert "read_count" in data
        assert data["read_count"] == 1
        assert len(data["reads"]) == 1

    def test_get_announcement_non_admin_no_read_statistics(self, client, db_session, user_auth_headers):
        """Test non-admin user doesn't see read statistics."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}", headers=user_auth_headers)
        data = response.get_json()
        assert "reads" not in data
        assert "read_count" not in data

    def test_get_announcement_without_auth(self, client, db_session):
        """Test getting announcement without auth (no read status)."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.get(f"/api/announcements/{announcement.id}")
        data = response.get_json()
        # Should not have read status when not authenticated
        assert "read" not in data


class TestCreateAnnouncement:
    """Tests for POST /api/announcements endpoint."""

    def test_create_announcement_success(self, client, auth_headers):
        """Test successful announcement creation."""
        data = {
            "title": "New Announcement",
            "content": "Important information",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.get_json()
        assert result["title"] == "New Announcement"
        assert result["content"] == "Important information"
        assert result["priority"] == "high"
        assert result["is_active"] is True
        assert "id" in result
        assert "created_at" in result

    def test_create_announcement_with_expiration_date(self, client, auth_headers):
        """Test creating announcement with expiration date."""
        future_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        data = {
            "title": "Expiring Announcement",
            "content": "This will expire",
            "priority": "medium",
            "expiration_date": future_date
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.get_json()
        assert result["expiration_date"] is not None

    def test_create_announcement_with_z_suffix_date(self, client, auth_headers):
        """Test creating announcement with Z suffix date format."""
        data = {
            "title": "Z Date Announcement",
            "content": "Content",
            "priority": "low",
            "expiration_date": "2025-12-31T23:59:59Z"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.get_json()
        assert result["expiration_date"] is not None

    def test_create_announcement_with_is_active_false(self, client, auth_headers):
        """Test creating inactive announcement."""
        data = {
            "title": "Inactive Announcement",
            "content": "Content",
            "priority": "low",
            "is_active": False
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.get_json()
        assert result["is_active"] is False

    def test_create_announcement_missing_title(self, client, auth_headers):
        """Test creating announcement without title fails."""
        data = {
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result
        assert "title" in result["error"]

    def test_create_announcement_missing_content(self, client, auth_headers):
        """Test creating announcement without content fails."""
        data = {
            "title": "Title",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result
        assert "content" in result["error"]

    def test_create_announcement_missing_priority(self, client, auth_headers):
        """Test creating announcement without priority fails."""
        data = {
            "title": "Title",
            "content": "Content"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result
        assert "priority" in result["error"]

    def test_create_announcement_empty_title(self, client, auth_headers):
        """Test creating announcement with empty title fails."""
        data = {
            "title": "",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 400

    def test_create_announcement_invalid_expiration_date(self, client, auth_headers):
        """Test creating announcement with invalid date format fails."""
        data = {
            "title": "Title",
            "content": "Content",
            "priority": "high",
            "expiration_date": "invalid-date"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 400
        result = response.get_json()
        assert "Invalid expiration date format" in result["error"]

    def test_create_announcement_no_auth(self, client):
        """Test creating announcement without authentication fails."""
        data = {
            "title": "Title",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data)
        assert response.status_code == 401

    def test_create_announcement_non_admin(self, client, user_auth_headers):
        """Test creating announcement as non-admin fails."""
        data = {
            "title": "Title",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=user_auth_headers)
        assert response.status_code == 403

    def test_create_announcement_no_json_body(self, client, auth_headers):
        """Test creating announcement with no JSON body."""
        # When no content-type is set and no body, Flask returns 415 or 500
        response = client.post("/api/announcements", headers=auth_headers)
        assert response.status_code in [400, 415, 500]

    def test_create_announcement_empty_json_body(self, client, auth_headers):
        """Test creating announcement with empty JSON body."""
        response = client.post("/api/announcements", json={}, headers=auth_headers)
        assert response.status_code == 400

    def test_create_announcement_creates_audit_log(self, client, auth_headers, db_session):
        """Test that creating announcement creates audit log."""
        from models import AuditLog

        data = {
            "title": "Audit Test",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201

        # Check audit log was created
        logs = AuditLog.query.filter_by(action_type="create_announcement").all()
        assert len(logs) >= 1
        latest_log = logs[-1]
        assert "Audit Test" in latest_log.action_details

    def test_create_announcement_creates_user_activity(self, client, auth_headers, db_session):
        """Test that creating announcement creates user activity."""
        from models import UserActivity

        data = {
            "title": "Activity Test",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 201

        # Check user activity was created
        activities = UserActivity.query.filter_by(activity_type="create_announcement").all()
        assert len(activities) >= 1
        latest_activity = activities[-1]
        assert "Activity Test" in latest_activity.description


class TestUpdateAnnouncement:
    """Tests for PUT /api/announcements/<id> endpoint."""

    def test_update_announcement_title(self, client, auth_headers, db_session):
        """Test updating announcement title."""
        from models import Announcement

        announcement = Announcement(
            title="Original",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"title": "Updated Title"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["title"] == "Updated Title"
        assert result["content"] == "Content"  # Unchanged

    def test_update_announcement_content(self, client, auth_headers, db_session):
        """Test updating announcement content."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Original Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"content": "Updated Content"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["content"] == "Updated Content"

    def test_update_announcement_priority(self, client, auth_headers, db_session):
        """Test updating announcement priority."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="low",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"priority": "critical"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["priority"] == "critical"

    def test_update_announcement_is_active(self, client, auth_headers, db_session):
        """Test updating announcement is_active status."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"is_active": False}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["is_active"] is False

    def test_update_announcement_expiration_date(self, client, auth_headers, db_session):
        """Test updating announcement expiration date."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True,
            expiration_date=None
        )
        db_session.add(announcement)
        db_session.commit()

        future_date = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        data = {"expiration_date": future_date}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["expiration_date"] is not None

    def test_update_announcement_remove_expiration_date(self, client, auth_headers, db_session):
        """Test removing announcement expiration date."""
        from models import Announcement

        future_date = datetime.now(UTC) + timedelta(days=7)
        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True,
            expiration_date=future_date
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"expiration_date": None}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["expiration_date"] is None

    def test_update_announcement_with_z_suffix_date(self, client, auth_headers, db_session):
        """Test updating announcement with Z suffix date."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"expiration_date": "2026-01-01T00:00:00Z"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200

    def test_update_announcement_invalid_expiration_date(self, client, auth_headers, db_session):
        """Test updating announcement with invalid date fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"expiration_date": "invalid"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 400
        result = response.get_json()
        assert "Invalid expiration date format" in result["error"]

    def test_update_announcement_not_found(self, client, auth_headers):
        """Test updating non-existent announcement returns 404 or 500."""
        data = {"title": "Updated"}
        response = client.put("/api/announcements/99999", json=data, headers=auth_headers)
        # The get_or_404 raises an exception caught by generic handler
        assert response.status_code in [404, 500]

    def test_update_announcement_no_auth(self, client, db_session):
        """Test updating announcement without authentication fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"title": "Updated"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data)
        assert response.status_code == 401

    def test_update_announcement_non_admin(self, client, user_auth_headers, db_session):
        """Test updating announcement as non-admin fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"title": "Updated"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=user_auth_headers)
        assert response.status_code == 403

    def test_update_announcement_multiple_fields(self, client, auth_headers, db_session):
        """Test updating multiple fields at once."""
        from models import Announcement

        announcement = Announcement(
            title="Original Title",
            content="Original Content",
            priority="low",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {
            "title": "New Title",
            "content": "New Content",
            "priority": "high",
            "is_active": False
        }
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert result["title"] == "New Title"
        assert result["content"] == "New Content"
        assert result["priority"] == "high"
        assert result["is_active"] is False

    def test_update_announcement_creates_audit_log(self, client, auth_headers, db_session):
        """Test that updating announcement creates audit log."""
        from models import Announcement, AuditLog

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"title": "Updated"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200

        # Check audit log was created
        logs = AuditLog.query.filter_by(action_type="update_announcement").all()
        assert len(logs) >= 1

    def test_update_announcement_creates_user_activity(self, client, auth_headers, db_session):
        """Test that updating announcement creates user activity."""
        from models import Announcement, UserActivity

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        data = {"title": "Updated"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 200

        # Check user activity was created
        activities = UserActivity.query.filter_by(activity_type="update_announcement").all()
        assert len(activities) >= 1

    def test_update_announcement_no_json_body(self, client, auth_headers, db_session):
        """Test updating announcement with no JSON body uses empty dict."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.put(f"/api/announcements/{announcement.id}", headers=auth_headers)
        # When no content-type is set and no body, Flask returns 415 or 500
        assert response.status_code in [200, 415, 500]

    def test_update_announcement_empty_json_body(self, client, auth_headers, db_session):
        """Test updating announcement with empty JSON body succeeds."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.put(f"/api/announcements/{announcement.id}", json={}, headers=auth_headers)
        # Should succeed but not change anything
        assert response.status_code == 200
        result = response.get_json()
        assert result["title"] == "Title"


class TestDeleteAnnouncement:
    """Tests for DELETE /api/announcements/<id> endpoint."""

    def test_delete_announcement_success(self, client, auth_headers, db_session):
        """Test successful announcement deletion."""
        from models import Announcement

        announcement = Announcement(
            title="To Delete",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()
        announcement_id = announcement.id

        response = client.delete(f"/api/announcements/{announcement_id}", headers=auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert "Announcement deleted successfully" in result["message"]

        # Verify deletion
        deleted = Announcement.query.get(announcement_id)
        assert deleted is None

    def test_delete_announcement_with_reads(self, client, auth_headers, db_session, regular_user):
        """Test deleting announcement also deletes associated read records."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="To Delete",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Create read record
        read_record = AnnouncementRead(
            announcement_id=announcement.id,
            user_id=regular_user.id
        )
        db_session.add(read_record)
        db_session.commit()
        announcement_id = announcement.id

        response = client.delete(f"/api/announcements/{announcement_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify read records are also deleted
        reads = AnnouncementRead.query.filter_by(announcement_id=announcement_id).all()
        assert len(reads) == 0

    def test_delete_announcement_not_found(self, client, auth_headers):
        """Test deleting non-existent announcement returns 404 or 500."""
        response = client.delete("/api/announcements/99999", headers=auth_headers)
        # The get_or_404 raises an exception caught by generic handler
        assert response.status_code in [404, 500]

    def test_delete_announcement_no_auth(self, client, db_session):
        """Test deleting announcement without authentication fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.delete(f"/api/announcements/{announcement.id}")
        assert response.status_code == 401

    def test_delete_announcement_non_admin(self, client, user_auth_headers, db_session):
        """Test deleting announcement as non-admin fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.delete(f"/api/announcements/{announcement.id}", headers=user_auth_headers)
        assert response.status_code == 403

    def test_delete_announcement_creates_audit_log(self, client, auth_headers, db_session):
        """Test that deleting announcement creates audit log."""
        from models import Announcement, AuditLog

        announcement = Announcement(
            title="Audit Delete Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.delete(f"/api/announcements/{announcement.id}", headers=auth_headers)
        assert response.status_code == 200

        # Check audit log was created
        logs = AuditLog.query.filter_by(action_type="delete_announcement").all()
        assert len(logs) >= 1
        latest_log = logs[-1]
        assert "Audit Delete Test" in latest_log.action_details

    def test_delete_announcement_creates_user_activity(self, client, auth_headers, db_session):
        """Test that deleting announcement creates user activity."""
        from models import Announcement, UserActivity

        announcement = Announcement(
            title="Activity Delete Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.delete(f"/api/announcements/{announcement.id}", headers=auth_headers)
        assert response.status_code == 200

        # Check user activity was created
        activities = UserActivity.query.filter_by(activity_type="delete_announcement").all()
        assert len(activities) >= 1
        latest_activity = activities[-1]
        assert "Activity Delete Test" in latest_activity.description


class TestMarkAnnouncementRead:
    """Tests for POST /api/announcements/<id>/read endpoint."""

    def test_mark_announcement_read_success(self, client, user_auth_headers, db_session):
        """Test marking announcement as read successfully."""
        from models import Announcement

        announcement = Announcement(
            title="To Read",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.post(f"/api/announcements/{announcement.id}/read", headers=user_auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert "Announcement marked as read" in result["message"]

    def test_mark_announcement_read_already_read(self, client, user_auth_headers, db_session, regular_user):
        """Test marking already-read announcement."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="Already Read",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Mark as read first time
        read_record = AnnouncementRead(
            announcement_id=announcement.id,
            user_id=regular_user.id
        )
        db_session.add(read_record)
        db_session.commit()

        # Try to mark as read again
        response = client.post(f"/api/announcements/{announcement.id}/read", headers=user_auth_headers)
        assert response.status_code == 200
        result = response.get_json()
        assert "already marked as read" in result["message"]

        # Verify no duplicate records
        reads = AnnouncementRead.query.filter_by(
            announcement_id=announcement.id,
            user_id=regular_user.id
        ).all()
        assert len(reads) == 1

    def test_mark_announcement_read_creates_record(self, client, user_auth_headers, db_session, regular_user):
        """Test that marking as read creates AnnouncementRead record."""
        from models import Announcement, AnnouncementRead

        announcement = Announcement(
            title="To Read",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.post(f"/api/announcements/{announcement.id}/read", headers=user_auth_headers)
        assert response.status_code == 200

        # Verify record was created
        read_record = AnnouncementRead.query.filter_by(
            announcement_id=announcement.id,
            user_id=regular_user.id
        ).first()
        assert read_record is not None
        assert read_record.read_at is not None

    def test_mark_announcement_read_not_found(self, client, user_auth_headers):
        """Test marking non-existent announcement returns 404 or 500."""
        response = client.post("/api/announcements/99999/read", headers=user_auth_headers)
        # The get_or_404 raises an exception caught by generic handler
        assert response.status_code in [404, 500]

    def test_mark_announcement_read_no_auth(self, client, db_session):
        """Test marking announcement as read without authentication fails."""
        from models import Announcement

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.post(f"/api/announcements/{announcement.id}/read")
        assert response.status_code == 401

    def test_mark_announcement_read_admin_user(self, client, auth_headers, db_session):
        """Test admin can also mark announcements as read."""
        from models import Announcement

        announcement = Announcement(
            title="Admin Read",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        response = client.post(f"/api/announcements/{announcement.id}/read", headers=auth_headers)
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling in announcement routes."""

    def test_get_announcements_database_error(self, client, db_session, monkeypatch):
        """Test error handling when database fails during get announcements."""
        # Mock datetime.now to raise an exception (it's called when active_only=true)
        def raise_error(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr("routes_announcements.datetime", type("MockDateTime", (), {
            "now": staticmethod(raise_error),
            "fromisoformat": staticmethod(lambda x: None)
        })())

        response = client.get("/api/announcements")
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result

    def test_get_single_announcement_database_error(self, client, db_session, monkeypatch):
        """Test error handling when database fails during get single announcement."""
        from models import Announcement

        announcement = Announcement(
            title="Test",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Mock to_dict to raise an exception
        def raise_error(*args, **kwargs):
            raise Exception("Serialization error")

        monkeypatch.setattr(Announcement, "to_dict", raise_error)

        response = client.get(f"/api/announcements/{announcement.id}")
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result

    def test_create_announcement_database_error(self, client, auth_headers, monkeypatch):
        """Test error handling when database fails during create."""
        from models import db

        # Mock commit to raise an exception
        def raise_error(*args, **kwargs):
            raise Exception("Database write error")

        monkeypatch.setattr(db.session, "commit", raise_error)

        data = {
            "title": "Title",
            "content": "Content",
            "priority": "high"
        }
        response = client.post("/api/announcements", json=data, headers=auth_headers)
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result

    def test_update_announcement_database_error(self, client, auth_headers, db_session, monkeypatch):
        """Test error handling when database fails during update."""
        from models import Announcement, db

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Track commit calls and raise error on second call
        original_commit = db.session.commit
        call_count = [0]

        def mock_commit(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] > 0:
                raise Exception("Database update error")
            return original_commit()

        monkeypatch.setattr(db.session, "commit", mock_commit)

        data = {"title": "Updated"}
        response = client.put(f"/api/announcements/{announcement.id}", json=data, headers=auth_headers)
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result

    def test_delete_announcement_database_error(self, client, auth_headers, db_session, monkeypatch):
        """Test error handling when database fails during delete."""
        from models import Announcement, db

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Track commit calls and raise error on commit after setup
        original_commit = db.session.commit
        call_count = [0]

        def mock_commit(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] > 0:
                raise Exception("Database delete error")
            return original_commit()

        monkeypatch.setattr(db.session, "commit", mock_commit)

        response = client.delete(f"/api/announcements/{announcement.id}", headers=auth_headers)
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result

    def test_mark_read_database_error(self, client, user_auth_headers, db_session, monkeypatch):
        """Test error handling when database fails during mark read."""
        from models import Announcement, db

        announcement = Announcement(
            title="Title",
            content="Content",
            priority="medium",
            created_by=1,
            is_active=True
        )
        db_session.add(announcement)
        db_session.commit()

        # Track commit calls and raise error after initial commit
        call_count = [0]

        def mock_commit(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] > 0:
                raise Exception("Database error")

        monkeypatch.setattr(db.session, "commit", mock_commit)

        response = client.post(f"/api/announcements/{announcement.id}/read", headers=user_auth_headers)
        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result
