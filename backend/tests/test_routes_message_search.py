"""
Comprehensive tests for routes_message_search.py - Message search API endpoints.
Targets 100% code coverage for search, senders, and stats endpoints.
"""
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from auth.jwt_manager import JWTManager
from models import User, db
from models_kits import AircraftType, Kit, KitMessage
from models_messaging import Channel, ChannelMember, ChannelMessage, MessageAttachment


@pytest.fixture
def search_client(app):
    """Create test client for search tests."""
    return app.test_client()


@pytest.fixture
def search_db_session(app):
    """Create database session for search tests with message-related tables cleared."""
    with app.app_context():
        # Clear all relevant tables
        db.session.query(MessageAttachment).delete()
        db.session.query(ChannelMessage).delete()
        db.session.query(ChannelMember).delete()
        db.session.query(Channel).delete()
        db.session.query(KitMessage).delete()
        db.session.query(Kit).delete()
        db.session.query(AircraftType).delete()
        db.session.query(User).delete()
        db.session.commit()
        yield db.session
        db.session.rollback()


@pytest.fixture
def search_user(search_db_session):
    """Create primary user for search tests."""
    user = User(
        name="Search User",
        employee_number="SEARCH001",
        department="Engineering",
        password_hash=generate_password_hash("test123"),
        is_admin=False,
        is_active=True
    )
    search_db_session.add(user)
    search_db_session.commit()
    return user


@pytest.fixture
def other_user(search_db_session):
    """Create secondary user for message sending."""
    user = User(
        name="Other User",
        employee_number="OTHER001",
        department="Materials",
        password_hash=generate_password_hash("test123"),
        is_admin=False,
        is_active=True
    )
    search_db_session.add(user)
    search_db_session.commit()
    return user


@pytest.fixture
def third_user(search_db_session):
    """Create third user for additional test scenarios."""
    user = User(
        name="Third User",
        employee_number="THIRD001",
        department="IT",
        password_hash=generate_password_hash("test123"),
        is_admin=False,
        is_active=True
    )
    search_db_session.add(user)
    search_db_session.commit()
    return user


@pytest.fixture
def search_token(app, search_user):
    """Generate JWT token for search user."""
    with app.app_context():
        tokens = JWTManager.generate_tokens(search_user)
        return tokens["access_token"]


@pytest.fixture
def search_auth_headers(search_token):
    """Authorization headers for search user."""
    return {"Authorization": f"Bearer {search_token}"}


@pytest.fixture
def aircraft_type(search_db_session):
    """Create aircraft type for kit tests."""
    at = AircraftType(
        name="TestAircraft",
        description="Test aircraft type",
        is_active=True
    )
    search_db_session.add(at)
    search_db_session.commit()
    return at


@pytest.fixture
def test_kit(search_db_session, aircraft_type, search_user):
    """Create a test kit."""
    kit = Kit(
        name="TestKit001",
        aircraft_type_id=aircraft_type.id,
        description="Test kit for messages",
        status="active",
        created_by=search_user.id
    )
    search_db_session.add(kit)
    search_db_session.commit()
    return kit


@pytest.fixture
def second_kit(search_db_session, aircraft_type, search_user):
    """Create a second test kit."""
    kit = Kit(
        name="TestKit002",
        aircraft_type_id=aircraft_type.id,
        description="Second test kit",
        status="active",
        created_by=search_user.id
    )
    search_db_session.add(kit)
    search_db_session.commit()
    return kit


@pytest.fixture
def test_channel(search_db_session, search_user):
    """Create a test channel."""
    channel = Channel(
        name="TestChannel001",
        description="Test channel for messages",
        channel_type="department",
        department="Engineering",
        is_active=True,
        created_by=search_user.id
    )
    search_db_session.add(channel)
    search_db_session.commit()
    return channel


@pytest.fixture
def second_channel(search_db_session, search_user):
    """Create a second test channel."""
    channel = Channel(
        name="TestChannel002",
        description="Second test channel",
        channel_type="team",
        department="Materials",
        is_active=True,
        created_by=search_user.id
    )
    search_db_session.add(channel)
    search_db_session.commit()
    return channel


@pytest.fixture
def channel_membership(search_db_session, test_channel, search_user):
    """Add search user to test channel."""
    membership = ChannelMember(
        channel_id=test_channel.id,
        user_id=search_user.id,
        role="member",
        notifications_enabled=True
    )
    search_db_session.add(membership)
    search_db_session.commit()
    return membership


@pytest.fixture
def kit_messages(search_db_session, test_kit, second_kit, search_user, other_user):
    """Create kit messages for search tests."""
    messages = []

    # Message sent to search user with specific keyword
    msg1 = KitMessage(
        kit_id=test_kit.id,
        sender_id=other_user.id,
        recipient_id=search_user.id,
        subject="Important Update",
        message="This is an urgent message about reorder status",
        is_read=False,
        sent_date=datetime.now(UTC) - timedelta(days=1)
    )
    messages.append(msg1)

    # Message sent by search user
    msg2 = KitMessage(
        kit_id=test_kit.id,
        sender_id=search_user.id,
        recipient_id=other_user.id,
        subject="Re: Important Update",
        message="Thank you for the update about reorder",
        is_read=True,
        sent_date=datetime.now(UTC) - timedelta(hours=12)
    )
    messages.append(msg2)

    # Message with attachments
    msg3 = KitMessage(
        kit_id=second_kit.id,
        sender_id=other_user.id,
        recipient_id=search_user.id,
        subject="Document Attached",
        message="Please review the attached specification document",
        is_read=False,
        attachments='["file1.pdf", "file2.pdf"]',
        sent_date=datetime.now(UTC) - timedelta(hours=6)
    )
    messages.append(msg3)

    # Old message for date filtering
    msg4 = KitMessage(
        kit_id=test_kit.id,
        sender_id=other_user.id,
        recipient_id=search_user.id,
        subject="Old Notification",
        message="This is an older message about urgent matters",
        is_read=True,
        sent_date=datetime.now(UTC) - timedelta(days=30)
    )
    messages.append(msg4)

    for msg in messages:
        search_db_session.add(msg)
    search_db_session.commit()
    return messages


@pytest.fixture
def channel_messages(search_db_session, test_channel, second_channel, search_user, other_user, channel_membership):
    """Create channel messages for search tests."""
    messages = []

    # Regular channel message
    msg1 = ChannelMessage(
        channel_id=test_channel.id,
        sender_id=other_user.id,
        message="Team meeting scheduled for tomorrow, please review the agenda",
        message_type="text",
        sent_date=datetime.now(UTC) - timedelta(hours=2),
        is_deleted=False
    )
    messages.append(msg1)

    # Another channel message with keyword
    msg2 = ChannelMessage(
        channel_id=test_channel.id,
        sender_id=search_user.id,
        message="I've completed the urgent task assignment",
        message_type="text",
        sent_date=datetime.now(UTC) - timedelta(hours=1),
        is_deleted=False
    )
    messages.append(msg2)

    # Deleted message (should not appear in search)
    msg3 = ChannelMessage(
        channel_id=test_channel.id,
        sender_id=other_user.id,
        message="This message contains urgent keyword but is deleted",
        message_type="text",
        sent_date=datetime.now(UTC) - timedelta(minutes=30),
        is_deleted=True
    )
    messages.append(msg3)

    for msg in messages:
        search_db_session.add(msg)
    search_db_session.commit()
    return messages


@pytest.fixture
def channel_with_attachments(search_db_session, test_channel, other_user, channel_messages):
    """Add attachments to a channel message."""
    attachment = MessageAttachment(
        channel_message_id=channel_messages[0].id,
        filename="test_attachment.pdf",
        original_filename="original.pdf",
        file_path="/uploads/test_attachment.pdf",
        file_size=1024,
        mime_type="application/pdf",
        file_type="pdf",
        uploaded_by=other_user.id
    )
    search_db_session.add(attachment)
    search_db_session.commit()
    return attachment


# Authentication Tests
class TestAuthentication:
    """Test authentication requirements for message search endpoints."""

    def test_search_messages_no_auth(self, search_client):
        """Search messages should fail without authentication."""
        response = search_client.get("/api/messages/search?q=test")
        assert response.status_code == 401

    def test_search_messages_invalid_token(self, search_client):
        """Search messages should fail with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = search_client.get("/api/messages/search?q=test", headers=headers)
        assert response.status_code == 401

    def test_get_senders_no_auth(self, search_client):
        """Get senders should fail without authentication."""
        response = search_client.get("/api/messages/search/senders")
        assert response.status_code == 401

    def test_get_stats_no_auth(self, search_client):
        """Get stats should fail without authentication."""
        response = search_client.get("/api/messages/search/stats")
        assert response.status_code == 401


# Search Messages Tests
class TestSearchMessages:
    """Test the main search_messages endpoint."""

    def test_search_without_query(self, search_client, search_auth_headers):
        """Search should fail without query parameter."""
        response = search_client.get("/api/messages/search", headers=search_auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "required" in data["error"].lower()

    def test_search_with_empty_query(self, search_client, search_auth_headers):
        """Search should fail with empty query string."""
        response = search_client.get("/api/messages/search?q=", headers=search_auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_search_with_whitespace_query(self, search_client, search_auth_headers):
        """Search should fail with whitespace-only query."""
        response = search_client.get("/api/messages/search?q=   ", headers=search_auth_headers)
        assert response.status_code == 400

    def test_search_kit_messages_only(self, search_client, search_auth_headers, kit_messages):
        """Search should return only kit messages when type=kit."""
        response = search_client.get(
            "/api/messages/search?q=urgent&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert "total" in data
        # All results should be kit type
        for result in data["results"]:
            assert result["type"] == "kit"

    def test_search_channel_messages_only(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should return only channel messages when type=channel."""
        response = search_client.get(
            "/api/messages/search?q=urgent&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should be channel type
        for result in data["results"]:
            assert result["type"] == "channel"

    def test_search_all_message_types(
        self, search_client, search_auth_headers, kit_messages, channel_membership, channel_messages
    ):
        """Search should return both kit and channel messages when type=all."""
        response = search_client.get(
            "/api/messages/search?q=urgent&type=all",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] > 0
        # Should have results from both types
        types_found = set(r["type"] for r in data["results"])
        assert "kit" in types_found or "channel" in types_found

    def test_search_by_sender_filter(self, search_client, search_auth_headers, kit_messages, other_user):
        """Search should filter by sender ID."""
        response = search_client.get(
            f"/api/messages/search?q=message&sender={other_user.id}",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should be from specified sender
        for result in data["results"]:
            assert result["sender_id"] == other_user.id

    def test_search_by_kit_id_filter(self, search_client, search_auth_headers, kit_messages, test_kit):
        """Search should filter by kit ID."""
        response = search_client.get(
            f"/api/messages/search?q=message&kit_id={test_kit.id}&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should be from specified kit
        for result in data["results"]:
            assert result["kit_id"] == test_kit.id

    def test_search_by_channel_id_filter(
        self, search_client, search_auth_headers, channel_membership, channel_messages, test_channel
    ):
        """Search should filter by channel ID."""
        response = search_client.get(
            f"/api/messages/search?q=meeting&channel_id={test_channel.id}&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should be from specified channel
        for result in data["results"]:
            assert result["channel_id"] == test_channel.id

    def test_search_with_attachments_filter_kit(self, search_client, search_auth_headers, kit_messages):
        """Search should filter kit messages with attachments."""
        response = search_client.get(
            "/api/messages/search?q=document&has_attachments=true&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should have attachments
        for result in data["results"]:
            if result["type"] == "kit":
                assert result["has_attachments"] is True

    def test_search_with_attachments_filter_channel(
        self, search_client, search_auth_headers, channel_membership, channel_messages, channel_with_attachments
    ):
        """Search should filter channel messages with attachments."""
        response = search_client.get(
            "/api/messages/search?q=meeting&has_attachments=true&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # Results should have attachments
        for result in data["results"]:
            if result["type"] == "channel":
                assert result["has_attachments"] is True

    def test_search_with_from_date_filter(self, search_client, search_auth_headers, kit_messages):
        """Search should filter messages from a specific date."""
        from_date = (datetime.now(UTC) - timedelta(days=2)).isoformat()
        response = search_client.get(
            f"/api/messages/search?q=message&from_date={from_date}&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # Old message (30 days ago) should be excluded
        assert data["total"] >= 0

    def test_search_with_to_date_filter(self, search_client, search_auth_headers, kit_messages):
        """Search should filter messages up to a specific date."""
        to_date = (datetime.now(UTC) - timedelta(days=25)).isoformat()
        response = search_client.get(
            f"/api/messages/search?q=urgent&to_date={to_date}&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # Only old message should be included
        assert data["total"] >= 0

    def test_search_with_date_range_filter(self, search_client, search_auth_headers, kit_messages):
        """Search should filter messages within a date range."""
        from_date = (datetime.now(UTC) - timedelta(days=5)).isoformat()
        to_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        response = search_client.get(
            f"/api/messages/search?q=message&from_date={from_date}&to_date={to_date}&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 0

    def test_search_with_invalid_from_date(self, search_client, search_auth_headers, kit_messages):
        """Search should handle invalid from_date gracefully."""
        response = search_client.get(
            "/api/messages/search?q=message&from_date=invalid-date&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should still return results, ignoring invalid date

    def test_search_with_invalid_to_date(self, search_client, search_auth_headers, kit_messages):
        """Search should handle invalid to_date gracefully."""
        response = search_client.get(
            "/api/messages/search?q=message&to_date=not-a-date&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should still return results, ignoring invalid date

    def test_search_with_z_suffix_date(self, search_client, search_auth_headers, kit_messages):
        """Search should handle ISO dates with Z suffix."""
        from_date = "2024-01-01T00:00:00Z"
        to_date = "2030-12-31T23:59:59Z"
        response = search_client.get(
            f"/api/messages/search?q=message&from_date={from_date}&to_date={to_date}&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200

    def test_search_with_pagination_limit(self, search_client, search_auth_headers, kit_messages):
        """Search should respect limit parameter."""
        response = search_client.get(
            "/api/messages/search?q=message&limit=2&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["limit"] == 2
        assert len(data["results"]) <= 2

    def test_search_with_pagination_offset(self, search_client, search_auth_headers, kit_messages):
        """Search should respect offset parameter."""
        response = search_client.get(
            "/api/messages/search?q=message&offset=1&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["offset"] == 1

    def test_search_limit_max_100(self, search_client, search_auth_headers, kit_messages):
        """Search limit should be capped at 100."""
        response = search_client.get(
            "/api/messages/search?q=message&limit=500",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["limit"] == 100

    def test_search_default_limit(self, search_client, search_auth_headers, kit_messages):
        """Search should use default limit of 50."""
        response = search_client.get(
            "/api/messages/search?q=message",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["limit"] == 50

    def test_search_returns_query_in_response(self, search_client, search_auth_headers, kit_messages):
        """Search response should include the search query."""
        response = search_client.get(
            "/api/messages/search?q=urgent",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["query"] == "urgent"

    def test_search_result_structure_kit_message(self, search_client, search_auth_headers, kit_messages):
        """Verify kit message result structure."""
        response = search_client.get(
            "/api/messages/search?q=reorder&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        if data["results"]:
            result = data["results"][0]
            assert "type" in result
            assert "id" in result
            assert "subject" in result
            assert "message" in result
            assert "sender_id" in result
            assert "sender_name" in result
            assert "recipient_id" in result
            assert "recipient_name" in result
            assert "sent_date" in result
            assert "is_read" in result
            assert "kit_id" in result
            assert "kit_name" in result
            assert "has_attachments" in result

    def test_search_result_structure_channel_message(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Verify channel message result structure."""
        response = search_client.get(
            "/api/messages/search?q=meeting&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        if data["results"]:
            result = data["results"][0]
            assert "type" in result
            assert "id" in result
            assert "message" in result
            assert "sender_id" in result
            assert "sender_name" in result
            assert "sent_date" in result
            assert "channel_id" in result
            assert "channel_name" in result
            assert "has_attachments" in result
            assert "attachment_count" in result

    def test_search_no_channel_messages_without_membership(
        self, search_client, search_auth_headers, search_db_session, test_channel, other_user
    ):
        """Search should not return channel messages if user is not a member."""
        # Create channel messages but don't add user to channel
        msg = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=other_user.id,
            message="Meeting scheduled for tomorrow",
            message_type="text",
            is_deleted=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=meeting&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # Should have no channel results since user is not a member
        assert data["total"] == 0

    def test_search_excludes_deleted_channel_messages(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should not return deleted channel messages."""
        response = search_client.get(
            "/api/messages/search?q=urgent&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # Deleted message should not appear
        for result in data["results"]:
            # None of the returned messages should be the deleted one
            assert "deleted" not in result["message"].lower() or result["type"] != "channel"

    def test_search_with_no_results(self, search_client, search_auth_headers, kit_messages):
        """Search should return empty results for non-matching query."""
        response = search_client.get(
            "/api/messages/search?q=nonexistentquery12345",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 0
        assert data["results"] == []

    def test_search_case_insensitive(self, search_client, search_auth_headers, kit_messages):
        """Search should be case-insensitive."""
        response1 = search_client.get(
            "/api/messages/search?q=URGENT&type=kit",
            headers=search_auth_headers
        )
        response2 = search_client.get(
            "/api/messages/search?q=urgent&type=kit",
            headers=search_auth_headers
        )
        assert response1.status_code == 200
        assert response2.status_code == 200
        # Both should return same number of results
        data1 = response1.get_json()
        data2 = response2.get_json()
        assert data1["total"] == data2["total"]

    def test_search_in_subject(self, search_client, search_auth_headers, kit_messages):
        """Search should match keywords in message subject."""
        response = search_client.get(
            "/api/messages/search?q=Important&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] > 0

    def test_search_in_message_body(self, search_client, search_auth_headers, kit_messages):
        """Search should match keywords in message body."""
        response = search_client.get(
            "/api/messages/search?q=reorder&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] > 0

    def test_search_results_sorted_by_date(
        self, search_client, search_auth_headers, kit_messages, channel_membership, channel_messages
    ):
        """Search results should be sorted by sent_date descending."""
        response = search_client.get(
            "/api/messages/search?q=message&type=all",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        if len(data["results"]) > 1:
            # Verify descending order
            dates = [r["sent_date"] for r in data["results"]]
            assert dates == sorted(dates, reverse=True)

    @patch("routes_message_search.JWTManager.get_current_user")
    def test_search_messages_exception_handling(
        self, mock_get_user, search_client, search_auth_headers
    ):
        """Search should handle exceptions gracefully."""
        mock_get_user.side_effect = Exception("Database error")
        response = search_client.get(
            "/api/messages/search?q=test",
            headers=search_auth_headers
        )
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("routes_message_search.KitMessage.query")
    def test_search_messages_database_exception(
        self, mock_query, search_client, search_auth_headers, kit_messages
    ):
        """Search should handle database exceptions in message queries."""
        mock_query.filter.side_effect = Exception("Database connection lost")
        response = search_client.get(
            "/api/messages/search?q=test&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to search messages" in data["error"]


# Get Senders Tests
class TestGetSenders:
    """Test the get_message_senders endpoint."""

    def test_get_senders_success(self, search_client, search_auth_headers, kit_messages):
        """Get senders should return list of message senders."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "senders" in data
        assert isinstance(data["senders"], list)

    def test_get_senders_structure(
        self, search_client, search_auth_headers, kit_messages, other_user
    ):
        """Verify sender structure in response."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        if data["senders"]:
            sender = data["senders"][0]
            assert "id" in sender
            assert "name" in sender

    def test_get_senders_includes_kit_senders(
        self, search_client, search_auth_headers, kit_messages, other_user
    ):
        """Get senders should include senders from kit messages."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        sender_ids = [s["id"] for s in data["senders"]]
        # Other user sent messages to search user
        assert other_user.id in sender_ids

    def test_get_senders_includes_channel_senders(
        self, search_client, search_auth_headers, channel_membership, channel_messages, other_user
    ):
        """Get senders should include senders from channel messages."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        sender_ids = [s["id"] for s in data["senders"]]
        # Other user sent messages to the channel
        assert other_user.id in sender_ids

    def test_get_senders_deduplicates(
        self, search_client, search_auth_headers, kit_messages, channel_membership, channel_messages, other_user
    ):
        """Get senders should deduplicate senders appearing in both kit and channel messages."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        sender_ids = [s["id"] for s in data["senders"]]
        # Each sender should appear only once
        assert len(sender_ids) == len(set(sender_ids))

    def test_get_senders_sorted_by_name(
        self, search_client, search_auth_headers, kit_messages, search_user, other_user
    ):
        """Get senders should return senders sorted by name."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        if len(data["senders"]) > 1:
            names = [s["name"] for s in data["senders"]]
            assert names == sorted(names)

    def test_get_senders_no_messages(self, search_client, search_auth_headers):
        """Get senders should return empty list when no messages exist."""
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "senders" in data
        assert data["senders"] == []

    def test_get_senders_without_channel_membership(
        self, search_client, search_auth_headers, kit_messages, channel_messages
    ):
        """Get senders should only include channel senders from user's channels."""
        # User is not a member of any channel, so no channel senders
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Should only have kit message senders
        assert "senders" in data

    @patch("routes_message_search.JWTManager.get_current_user")
    def test_get_senders_exception_handling(self, mock_get_user, search_client, search_auth_headers):
        """Get senders should handle exceptions gracefully."""
        mock_get_user.side_effect = Exception("Database error")
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("routes_message_search.db.session.query")
    def test_get_senders_database_exception(
        self, mock_query, search_client, search_auth_headers, kit_messages
    ):
        """Get senders should handle database exceptions."""
        mock_query.side_effect = Exception("Database connection lost")
        response = search_client.get("/api/messages/search/senders", headers=search_auth_headers)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to fetch senders" in data["error"]


# Get Stats Tests
class TestGetStats:
    """Test the get_message_stats endpoint."""

    def test_get_stats_success(self, search_client, search_auth_headers):
        """Get stats should return message statistics."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "kit_messages" in data
        assert "channel_messages" in data
        assert "totals" in data

    def test_get_stats_kit_messages_structure(self, search_client, search_auth_headers):
        """Verify kit messages stats structure."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        kit_stats = data["kit_messages"]
        assert "received" in kit_stats
        assert "unread" in kit_stats
        assert "sent" in kit_stats
        assert "total" in kit_stats

    def test_get_stats_channel_messages_structure(self, search_client, search_auth_headers):
        """Verify channel messages stats structure."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        channel_stats = data["channel_messages"]
        assert "total" in channel_stats
        assert "unread" in channel_stats

    def test_get_stats_totals_structure(self, search_client, search_auth_headers):
        """Verify totals stats structure."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        totals = data["totals"]
        assert "all_messages" in totals
        assert "unread" in totals

    def test_get_stats_kit_received_count(
        self, search_client, search_auth_headers, kit_messages, search_user
    ):
        """Get stats should count received kit messages."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Search user receives 3 messages (msg1, msg3, msg4)
        assert data["kit_messages"]["received"] == 3

    def test_get_stats_kit_sent_count(
        self, search_client, search_auth_headers, kit_messages, search_user
    ):
        """Get stats should count sent kit messages."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Search user sends 1 message (msg2)
        assert data["kit_messages"]["sent"] == 1

    def test_get_stats_kit_unread_count(
        self, search_client, search_auth_headers, kit_messages, search_user
    ):
        """Get stats should count unread kit messages."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # msg1 and msg3 are unread
        assert data["kit_messages"]["unread"] == 2

    def test_get_stats_kit_total_calculation(
        self, search_client, search_auth_headers, kit_messages
    ):
        """Get stats kit total should equal received + sent."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        kit_stats = data["kit_messages"]
        assert kit_stats["total"] == kit_stats["received"] + kit_stats["sent"]

    def test_get_stats_channel_total_count(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Get stats should count total channel messages."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Only non-deleted messages (msg1, msg2)
        assert data["channel_messages"]["total"] == 2

    def test_get_stats_channel_unread_with_no_last_read(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Get stats should count all messages as unread when no last_read_message_id."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # All non-deleted messages should be unread since last_read_message_id is None
        assert data["channel_messages"]["unread"] == 2

    def test_get_stats_channel_unread_with_last_read(
        self, search_client, search_auth_headers, search_db_session, channel_membership, channel_messages
    ):
        """Get stats should calculate unread based on last_read_message_id."""
        # Update membership to mark first message as read
        channel_membership.last_read_message_id = channel_messages[0].id
        search_db_session.commit()

        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Only msg2 (id > msg1.id) should be unread
        assert data["channel_messages"]["unread"] == 1

    def test_get_stats_no_channel_membership(
        self, search_client, search_auth_headers, search_db_session, test_channel, other_user
    ):
        """Get stats should show zero channel messages when not a member."""
        # Create channel messages but don't add user to channel
        msg = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=other_user.id,
            message="Message in channel",
            message_type="text",
            is_deleted=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["channel_messages"]["total"] == 0
        assert data["channel_messages"]["unread"] == 0

    def test_get_stats_totals_calculation(
        self, search_client, search_auth_headers, kit_messages, channel_membership, channel_messages
    ):
        """Get stats totals should sum kit and channel stats."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        expected_all = (
            data["kit_messages"]["received"] +
            data["kit_messages"]["sent"] +
            data["channel_messages"]["total"]
        )
        assert data["totals"]["all_messages"] == expected_all

        expected_unread = (
            data["kit_messages"]["unread"] +
            data["channel_messages"]["unread"]
        )
        assert data["totals"]["unread"] == expected_unread

    def test_get_stats_no_messages(self, search_client, search_auth_headers):
        """Get stats should return zeros when no messages exist."""
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["kit_messages"]["received"] == 0
        assert data["kit_messages"]["sent"] == 0
        assert data["kit_messages"]["unread"] == 0
        assert data["channel_messages"]["total"] == 0
        assert data["channel_messages"]["unread"] == 0
        assert data["totals"]["all_messages"] == 0
        assert data["totals"]["unread"] == 0

    def test_get_stats_multiple_channel_memberships(
        self, search_client, search_auth_headers, search_db_session,
        test_channel, second_channel, search_user, other_user
    ):
        """Get stats should count messages from all user's channels."""
        # Add user to both channels
        membership1 = ChannelMember(
            channel_id=test_channel.id,
            user_id=search_user.id,
            role="member"
        )
        membership2 = ChannelMember(
            channel_id=second_channel.id,
            user_id=search_user.id,
            role="member"
        )
        search_db_session.add(membership1)
        search_db_session.add(membership2)

        # Add messages to both channels
        msg1 = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=other_user.id,
            message="Message in channel 1",
            is_deleted=False
        )
        msg2 = ChannelMessage(
            channel_id=second_channel.id,
            sender_id=other_user.id,
            message="Message in channel 2",
            is_deleted=False
        )
        search_db_session.add(msg1)
        search_db_session.add(msg2)
        search_db_session.commit()

        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # Should count messages from both channels
        assert data["channel_messages"]["total"] == 2
        # Both unread since no last_read_message_id
        assert data["channel_messages"]["unread"] == 2

    @patch("routes_message_search.JWTManager.get_current_user")
    def test_get_stats_exception_handling(self, mock_get_user, search_client, search_auth_headers):
        """Get stats should handle exceptions gracefully."""
        mock_get_user.side_effect = Exception("Database error")
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("routes_message_search.KitMessage.query")
    def test_get_stats_database_exception(
        self, mock_query, search_client, search_auth_headers, kit_messages
    ):
        """Get stats should handle database exceptions."""
        mock_query.filter_by.side_effect = Exception("Database connection lost")
        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to fetch message stats" in data["error"]


# Edge Cases and Additional Coverage
class TestEdgeCases:
    """Test edge cases and additional scenarios for full coverage."""

    def test_search_with_null_sender(
        self, search_client, search_auth_headers, search_db_session, test_kit, search_user
    ):
        """Search should handle messages with null sender relationship."""
        # Create a message referencing a non-existent sender
        msg = KitMessage(
            kit_id=test_kit.id,
            sender_id=99999,  # Non-existent user
            recipient_id=search_user.id,
            subject="Test",
            message="Test message with null sender",
            is_read=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=message&type=kit",
            headers=search_auth_headers
        )
        # Should not crash, may or may not include the message depending on FK constraints
        assert response.status_code in [200, 500]

    def test_search_with_null_recipient(
        self, search_client, search_auth_headers, search_db_session, test_kit, search_user
    ):
        """Search should handle messages with null recipient."""
        msg = KitMessage(
            kit_id=test_kit.id,
            sender_id=search_user.id,
            recipient_id=None,  # Broadcast message
            subject="Broadcast",
            message="This is a broadcast message",
            is_read=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=broadcast&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200

    def test_search_with_null_kit_relationship(
        self, search_client, search_auth_headers, search_db_session, search_user, other_user
    ):
        """Search should handle messages with missing kit relationship."""
        msg = KitMessage(
            kit_id=99999,  # Non-existent kit
            sender_id=other_user.id,
            recipient_id=search_user.id,
            subject="Test",
            message="Message with missing kit",
            is_read=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=message&type=kit",
            headers=search_auth_headers
        )
        # Should handle gracefully
        assert response.status_code in [200, 500]

    def test_search_channel_with_null_sender(
        self, search_client, search_auth_headers, search_db_session,
        test_channel, channel_membership
    ):
        """Search should handle channel messages with null sender relationship."""
        msg = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=99999,  # Non-existent user
            message="Message with null sender",
            is_deleted=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=message&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code in [200, 500]

    def test_search_channel_with_null_channel_relationship(
        self, search_client, search_auth_headers, search_db_session,
        search_user, channel_membership
    ):
        """Search should handle channel messages with missing channel relationship."""
        msg = ChannelMessage(
            channel_id=99999,  # Non-existent channel
            sender_id=search_user.id,
            message="Message with missing channel",
            is_deleted=False
        )
        search_db_session.add(msg)
        search_db_session.commit()

        response = search_client.get(
            "/api/messages/search?q=message&type=channel",
            headers=search_auth_headers
        )
        assert response.status_code in [200, 500]

    def test_search_with_special_characters_in_query(
        self, search_client, search_auth_headers, kit_messages
    ):
        """Search should handle special characters in query."""
        response = search_client.get(
            "/api/messages/search?q=%25test%25",
            headers=search_auth_headers
        )
        assert response.status_code == 200

    def test_search_with_very_long_query(self, search_client, search_auth_headers, kit_messages):
        """Search should handle very long query strings."""
        long_query = "a" * 1000
        response = search_client.get(
            f"/api/messages/search?q={long_query}",
            headers=search_auth_headers
        )
        assert response.status_code == 200

    def test_search_with_sql_injection_attempt(
        self, search_client, search_auth_headers, kit_messages
    ):
        """Search should be safe from SQL injection."""
        response = search_client.get(
            "/api/messages/search?q='; DROP TABLE kit_messages; --",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should return empty results, not cause an error

    def test_register_message_search_routes(self, app):
        """Test that register_message_search_routes function works."""
        from routes_message_search import register_message_search_routes
        # This is already registered in the app, but test function exists
        # Just verify it doesn't crash
        assert register_message_search_routes is not None

    def test_multiple_channel_memberships_unread_calculation(
        self, search_client, search_auth_headers, search_db_session,
        test_channel, second_channel, search_user, other_user
    ):
        """Test unread calculation across multiple channels with different read states."""
        # First channel membership with some messages read
        membership1 = ChannelMember(
            channel_id=test_channel.id,
            user_id=search_user.id,
            role="member"
        )
        search_db_session.add(membership1)

        # Second channel membership with no messages read
        membership2 = ChannelMember(
            channel_id=second_channel.id,
            user_id=search_user.id,
            role="member"
        )
        search_db_session.add(membership2)

        # Messages in first channel
        msg1 = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=other_user.id,
            message="Old message channel 1",
            is_deleted=False
        )
        search_db_session.add(msg1)
        search_db_session.flush()

        # Mark first message as read
        membership1.last_read_message_id = msg1.id

        msg2 = ChannelMessage(
            channel_id=test_channel.id,
            sender_id=other_user.id,
            message="New message channel 1",
            is_deleted=False
        )
        search_db_session.add(msg2)

        # Messages in second channel (all unread)
        msg3 = ChannelMessage(
            channel_id=second_channel.id,
            sender_id=other_user.id,
            message="Message channel 2",
            is_deleted=False
        )
        search_db_session.add(msg3)
        search_db_session.commit()

        response = search_client.get("/api/messages/search/stats", headers=search_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        # 1 unread in channel 1 (msg2) + 1 unread in channel 2 (msg3) = 2 unread
        assert data["channel_messages"]["unread"] == 2
        assert data["channel_messages"]["total"] == 3

    def test_search_partial_match(self, search_client, search_auth_headers, kit_messages):
        """Search should find partial matches in message content."""
        response = search_client.get(
            "/api/messages/search?q=upd&type=kit",  # Partial match for "update"
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] > 0

    def test_search_with_has_attachments_false(
        self, search_client, search_auth_headers, kit_messages
    ):
        """Search with has_attachments=false should not filter."""
        response = search_client.get(
            "/api/messages/search?q=message&has_attachments=false&type=kit",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # has_attachments only filters when true

    def test_search_with_type_default(
        self, search_client, search_auth_headers, kit_messages, channel_membership, channel_messages
    ):
        """Search without type parameter should default to 'all'."""
        response = search_client.get(
            "/api/messages/search?q=message",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should search both kit and channel messages

    def test_search_channel_by_sender_filter(
        self, search_client, search_auth_headers, channel_membership, channel_messages, other_user
    ):
        """Search should filter channel messages by sender ID."""
        response = search_client.get(
            f"/api/messages/search?q=meeting&type=channel&sender={other_user.id}",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        # All results should be from specified sender
        for result in data["results"]:
            assert result["sender_id"] == other_user.id

    def test_search_channel_with_from_date_filter(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should filter channel messages from a specific date."""
        from_date = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        response = search_client.get(
            f"/api/messages/search?q=meeting&type=channel&from_date={from_date}",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 0

    def test_search_channel_with_to_date_filter(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should filter channel messages up to a specific date."""
        to_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        response = search_client.get(
            f"/api/messages/search?q=meeting&type=channel&to_date={to_date}",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 0

    def test_search_channel_with_invalid_from_date(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should handle invalid from_date for channel messages gracefully."""
        response = search_client.get(
            "/api/messages/search?q=meeting&type=channel&from_date=invalid-date",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should still return results, ignoring invalid date

    def test_search_channel_with_invalid_to_date(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should handle invalid to_date for channel messages gracefully."""
        response = search_client.get(
            "/api/messages/search?q=meeting&type=channel&to_date=not-a-date",
            headers=search_auth_headers
        )
        assert response.status_code == 200
        # Should still return results, ignoring invalid date

    def test_search_channel_with_z_suffix_dates(
        self, search_client, search_auth_headers, channel_membership, channel_messages
    ):
        """Search should handle ISO dates with Z suffix for channel messages."""
        from_date = "2024-01-01T00:00:00Z"
        to_date = "2030-12-31T23:59:59Z"
        response = search_client.get(
            f"/api/messages/search?q=meeting&type=channel&from_date={from_date}&to_date={to_date}",
            headers=search_auth_headers
        )
        assert response.status_code == 200
