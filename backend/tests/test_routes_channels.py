"""
Tests for enhanced messaging channel routes.
Tests /api/channels endpoints for CRUD operations, members, and messages.
"""
import json

from models import db
from models_messaging import ChannelMember, ChannelMessage


class TestChannelRoutes:
    """Test channel CRUD operations"""

    def test_get_channels_unauthenticated(self, client):
        """Test getting channels without authentication"""
        response = client.get("/api/channels")
        assert response.status_code == 401

    def test_create_channel(self, client, auth_headers):
        """Test creating a new channel"""
        data = {
            "name": "Engineering Team",
            "description": "Engineering department channel",
            "channel_type": "department",
            "department": "Engineering"
        }

        response = client.post(
            "/api/channels",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "channel" in data
        assert data["channel"]["name"] == "Engineering Team"
        assert data["message"] == "Channel created successfully"

    def test_create_channel_missing_name(self, client, auth_headers):
        """Test creating channel without name"""
        data = {"description": "Test"}

        response = client.post(
            "/api/channels",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_create_duplicate_channel(self, client, auth_headers, test_channel):
        """Test creating channel with duplicate name"""
        data = {"name": test_channel.name}

        response = client.post(
            "/api/channels",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 409

    def test_get_user_channels(self, client, auth_headers, test_channel, admin_user):
        """Test getting channels user is a member of"""
        with client.application.app_context():
            # Add admin user as member
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            db.session.add(member)
            db.session.commit()

        response = client.get("/api/channels", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "channels" in data
        assert len(data["channels"]) > 0

    def test_get_channel_by_id(self, client, auth_headers, test_channel, admin_user):
        """Test getting specific channel details"""
        with client.application.app_context():
            # Add admin user as member
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            db.session.add(member)
            db.session.commit()

        response = client.get(
            f"/api/channels/{test_channel.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["channel"]["id"] == test_channel.id
        assert "members" in data["channel"]

    def test_get_channel_not_member(self, client, auth_headers, test_channel):
        """Test getting channel user is not a member of"""
        response = client.get(
            f"/api/channels/{test_channel.id}",
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_update_channel(self, client, auth_headers, test_channel, admin_user):
        """Test updating channel (admin only)"""
        with client.application.app_context():
            # Add admin user as admin
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="admin"
            )
            db.session.add(member)
            db.session.commit()

        data = {"description": "Updated description"}

        response = client.put(
            f"/api/channels/{test_channel.id}",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["channel"]["description"] == "Updated description"

    def test_update_channel_not_admin(self, client, auth_headers, test_channel, admin_user):
        """Test updating channel without admin role"""
        with client.application.app_context():
            # Add admin user as regular member
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="member"
            )
            db.session.add(member)
            db.session.commit()

        data = {"description": "Updated"}

        response = client.put(
            f"/api/channels/{test_channel.id}",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 403

    def test_delete_channel(self, client, auth_headers, test_channel, admin_user):
        """Test deleting channel (admin only)"""
        with client.application.app_context():
            # Add admin user as admin
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="admin"
            )
            db.session.add(member)
            db.session.commit()

        response = client.delete(
            f"/api/channels/{test_channel.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify channel is deleted
        response = client.get(
            f"/api/channels/{test_channel.id}",
            headers=auth_headers
        )
        assert response.status_code == 403  # No longer a member

    def test_delete_channel_not_admin(self, client, auth_headers, test_channel, admin_user):
        """Test deleting channel without admin role"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="member"
            )
            db.session.add(member)
            db.session.commit()

        response = client.delete(
            f"/api/channels/{test_channel.id}",
            headers=auth_headers
        )

        assert response.status_code == 403


class TestChannelMemberRoutes:
    """Test channel member management"""

    def test_get_channel_members(self, client, auth_headers, test_channel, admin_user):
        """Test getting channel members"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            db.session.add(member)
            db.session.commit()

        response = client.get(
            f"/api/channels/{test_channel.id}/members",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "members" in data
        assert len(data["members"]) > 0

    def test_add_channel_member(self, client, auth_headers, test_channel, admin_user, test_user_2):
        """Test adding a member to channel"""
        with client.application.app_context():
            # Add admin user as admin
            admin = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

        data = {"user_id": test_user_2.id, "role": "member"}

        response = client.post(
            f"/api/channels/{test_channel.id}/members",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["member"]["user_id"] == test_user_2.id

    def test_add_member_not_admin(self, client, auth_headers, test_channel, admin_user, test_user_2):
        """Test adding member without admin permission"""
        with client.application.app_context():
            # Add admin user as regular member
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="member"
            )
            db.session.add(member)
            db.session.commit()

        data = {"user_id": test_user_2.id}

        response = client.post(
            f"/api/channels/{test_channel.id}/members",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 403

    def test_add_duplicate_member(self, client, auth_headers, test_channel, admin_user, test_user_2):
        """Test adding member who is already a member"""
        with client.application.app_context():
            admin = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="admin"
            )
            existing = ChannelMember(
                channel_id=test_channel.id,
                user_id=test_user_2.id
            )
            db.session.add_all([admin, existing])
            db.session.commit()

        data = {"user_id": test_user_2.id}

        response = client.post(
            f"/api/channels/{test_channel.id}/members",
            data=json.dumps(data),
            headers=auth_headers,
            content_type="application/json"
        )

        assert response.status_code == 409

    def test_remove_channel_member(self, client, auth_headers, test_channel, admin_user, test_user_2):
        """Test removing a member from channel"""
        with client.application.app_context():
            admin = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id,
                role="admin"
            )
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=test_user_2.id
            )
            db.session.add_all([admin, member])
            db.session.commit()

        response = client.delete(
            f"/api/channels/{test_channel.id}/members/{test_user_2.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_member_self_leave(self, client, auth_headers, test_channel, admin_user):
        """Test member leaving channel (self-removal)"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            db.session.add(member)
            db.session.commit()

        response = client.delete(
            f"/api/channels/{test_channel.id}/members/{admin_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 200


class TestChannelMessageRoutes:
    """Test channel message operations"""

    def test_get_channel_messages(self, client, auth_headers, test_channel, admin_user):
        """Test getting messages from a channel"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            message = ChannelMessage(
                channel_id=test_channel.id,
                sender_id=admin_user.id,
                message="Test message"
            )
            db.session.add_all([member, message])
            db.session.commit()

        response = client.get(
            f"/api/channels/{test_channel.id}/messages",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "messages" in data
        assert len(data["messages"]) > 0

    def test_get_messages_not_member(self, client, auth_headers, test_channel):
        """Test getting messages when not a member"""
        response = client.get(
            f"/api/channels/{test_channel.id}/messages",
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_get_messages_pagination(self, client, auth_headers, test_channel, admin_user):
        """Test message pagination"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            db.session.add(member)

            # Create multiple messages
            for i in range(10):
                message = ChannelMessage(
                    channel_id=test_channel.id,
                    sender_id=admin_user.id,
                    message=f"Message {i}"
                )
                db.session.add(message)

            db.session.commit()

        response = client.get(
            f"/api/channels/{test_channel.id}/messages?limit=5&offset=0",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["messages"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0

    def test_delete_channel_message_sender(self, client, auth_headers, test_channel, admin_user):
        """Test deleting message as sender"""
        with client.application.app_context():
            member = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            message = ChannelMessage(
                channel_id=test_channel.id,
                sender_id=admin_user.id,
                message="To be deleted"
            )
            db.session.add_all([member, message])
            db.session.commit()
            message_id = message.id

        response = client.delete(
            f"/api/channels/{test_channel.id}/messages/{message_id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify message is soft-deleted
        with client.application.app_context():
            message = ChannelMessage.query.get(message_id)
            assert message.is_deleted is True

    def test_delete_message_not_sender(self, client, auth_headers, test_channel, admin_user, test_user_2):
        """Test deleting message not sent by user (should fail)"""
        with client.application.app_context():
            member1 = ChannelMember(
                channel_id=test_channel.id,
                user_id=admin_user.id
            )
            member2 = ChannelMember(
                channel_id=test_channel.id,
                user_id=test_user_2.id
            )
            message = ChannelMessage(
                channel_id=test_channel.id,
                sender_id=test_user_2.id,  # Sent by user_2
                message="Test"
            )
            db.session.add_all([member1, member2, message])
            db.session.commit()
            message_id = message.id

        response = client.delete(
            f"/api/channels/{test_channel.id}/messages/{message_id}",
            headers=auth_headers  # Authenticated as admin_user
        )

        assert response.status_code == 403
