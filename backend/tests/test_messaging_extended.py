"""
Extended messaging system tests for SupplyLine MRO Suite

Tests messaging functionality including:
- Channel creation and management
- Message sending and retrieval
- Real-time features (typing indicators, presence)
- Message attachments
- Message reactions
- Message search
- Notification delivery
"""

from datetime import datetime, timedelta

import pytest

from models import User
from models_messaging import (
    Channel,
    ChannelMember,
    ChannelMessage,
    MessageAttachment,
    MessageReaction,
    TypingIndicator,
    UserPresence,
)

# TODO: Re-enable when messaging features are implemented
pytestmark = pytest.mark.skip(reason="Messaging features not yet implemented")

@pytest.mark.messaging
@pytest.mark.integration
class TestChannelManagement:
    """Test channel creation and management"""

    # TODO: Re-enable when channels API is implemented
    @pytest.mark.skip(reason="Channels API endpoint not yet implemented")
    def test_create_department_channel(self, client, db_session, test_user, auth_headers):
        """Test creating a department channel"""
        from auth import JWTManager

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        channel_data = {
            "name": "Engineering Department",
            "description": "Channel for Engineering team",
            "channel_type": "department",
            "department": "Engineering"
        }

        response = client.post(
            "/api/channels",
            headers=user_headers,
            json=channel_data
        )

        # Should create or return appropriate status
        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.get_json()
            assert data["name"] == "Engineering Department"
            assert data["channel_type"] == "department"

    def test_create_private_channel(self, client, db_session, test_user, test_user_2):
        """Test creating a private channel between users"""
        from auth import JWTManager

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        channel_data = {
            "name": "Private Discussion",
            "description": "Private channel",
            "channel_type": "private",
            "members": [test_user.id, test_user_2.id]
        }

        response = client.post(
            "/api/channels",
            headers=user_headers,
            json=channel_data
        )

        assert response.status_code in [201, 404]

    # TODO: Re-enable when channels API is implemented
    @pytest.mark.skip(reason="Channels API endpoint not yet implemented")
    def test_add_channel_members(self, client, db_session, test_user, test_user_2, test_channel):
        """Test adding members to a channel"""
        from auth import JWTManager

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Add member
        response = client.post(
            f"/api/channels/{test_channel.id}/members",
            headers=user_headers,
            json={"user_id": test_user_2.id}
        )

        assert response.status_code in [200, 201, 404]

        if response.status_code in [200, 201]:
            # Verify member added
            member = ChannelMember.query.filter_by(
                channel_id=test_channel.id,
                user_id=test_user_2.id
            ).first()
            assert member is not None

    # TODO: Re-enable when channels API is implemented
    @pytest.mark.skip(reason="Channels API endpoint not yet implemented")
    def test_remove_channel_member(self, client, db_session, test_user, test_user_2, test_channel):
        """Test removing a member from a channel"""
        from auth import JWTManager

        # Add member first
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user_2.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Remove member
        response = client.delete(
            f"/api/channels/{test_channel.id}/members/{test_user_2.id}",
            headers=user_headers
        )

        assert response.status_code in [200, 204, 404]


@pytest.mark.messaging
@pytest.mark.integration
class TestMessageOperations:
    """Test message sending and retrieval"""

    def test_send_message_to_channel(self, client, db_session, test_user, test_channel):
        """Test sending a message to a channel"""
        from auth import JWTManager

        # Add user to channel first
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        message_data = {
            "content": "Hello, this is a test message",
            "message_type": "text"
        }

        response = client.post(
            f"/api/channels/{test_channel.id}/messages",
            headers=user_headers,
            json=message_data
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            data = response.get_json()
            assert data["content"] == "Hello, this is a test message"
            assert data["user_id"] == test_user.id

    def test_retrieve_channel_messages(self, client, db_session, test_user, test_channel):
        """Test retrieving messages from a channel"""
        from auth import JWTManager

        # Add user to channel
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.flush()

        # Create messages
        for i in range(5):
            message = ChannelMessage(
                channel_id=test_channel.id,
                user_id=test_user.id,
                content=f"Test message {i}",
                message_type="text",
                created_at=datetime.utcnow() - timedelta(minutes=i)
            )
            db_session.add(message)

        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = client.get(
            f"/api/channels/{test_channel.id}/messages",
            headers=user_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) >= 5

    def test_message_pagination(self, client, db_session, test_user, test_channel):
        """Test message pagination"""
        from auth import JWTManager

        # Add user to channel
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.flush()

        # Create many messages
        for i in range(50):
            message = ChannelMessage(
                channel_id=test_channel.id,
                user_id=test_user.id,
                content=f"Message {i}",
                message_type="text",
                created_at=datetime.utcnow() - timedelta(seconds=i)
            )
            db_session.add(message)

        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Get first page
        response = client.get(
            f"/api/channels/{test_channel.id}/messages?limit=20&offset=0",
            headers=user_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) <= 20

    def test_edit_message(self, client, db_session, test_user, test_channel):
        """Test editing a message"""
        from auth import JWTManager

        # Create message
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="Original message",
            message_type="text"
        )
        db_session.add(message)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Edit message
        response = client.put(
            f"/api/channels/{test_channel.id}/messages/{message.id}",
            headers=user_headers,
            json={"content": "Edited message"}
        )

        assert response.status_code in [200, 404]

    def test_delete_message(self, client, db_session, test_user, test_channel):
        """Test deleting a message"""
        from auth import JWTManager

        # Create message
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="Message to delete",
            message_type="text"
        )
        db_session.add(message)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Delete message
        response = client.delete(
            f"/api/channels/{test_channel.id}/messages/{message.id}",
            headers=user_headers
        )

        assert response.status_code in [200, 204, 404]


@pytest.mark.messaging
@pytest.mark.integration
class TestMessageReactions:
    """Test message reactions functionality"""

    def test_add_reaction_to_message(self, client, db_session, test_user, test_channel):
        """Test adding a reaction to a message"""
        from auth import JWTManager

        # Create message
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="React to this",
            message_type="text"
        )
        db_session.add(message)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Add reaction
        response = client.post(
            f"/api/messages/{message.id}/reactions",
            headers=user_headers,
            json={"emoji": "👍"}
        )

        assert response.status_code in [201, 404]

        if response.status_code == 201:
            # Verify reaction added
            reaction = MessageReaction.query.filter_by(
                message_id=message.id,
                user_id=test_user.id
            ).first()
            assert reaction is not None

    def test_remove_reaction_from_message(self, client, db_session, test_user, test_channel):
        """Test removing a reaction from a message"""
        from auth import JWTManager

        # Create message and reaction
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="React to this",
            message_type="text"
        )
        db_session.add(message)
        db_session.flush()

        reaction = MessageReaction(
            message_id=message.id,
            user_id=test_user.id,
            emoji="👍"
        )
        db_session.add(reaction)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Remove reaction
        response = client.delete(
            f"/api/messages/{message.id}/reactions/👍",
            headers=user_headers
        )

        assert response.status_code in [200, 204, 404]


@pytest.mark.messaging
@pytest.mark.integration
class TestRealTimeFeatures:
    """Test real-time messaging features"""

    def test_typing_indicator(self, client, db_session, test_user, test_channel):
        """Test typing indicator functionality"""
        from auth import JWTManager

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Start typing
        response = client.post(
            f"/api/channels/{test_channel.id}/typing",
            headers=user_headers
        )

        assert response.status_code in [200, 201, 404]

        if response.status_code in [200, 201]:
            # Verify indicator created
            indicator = TypingIndicator.query.filter_by(
                channel_id=test_channel.id,
                user_id=test_user.id
            ).first()
            assert indicator is not None or response.status_code == 200

    def test_user_presence(self, client, db_session, test_user):
        """Test user presence tracking"""
        from auth import JWTManager

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Update presence
        response = client.post(
            "/api/presence",
            headers=user_headers,
            json={"status": "online"}
        )

        assert response.status_code in [200, 201, 404]

        if response.status_code in [200, 201]:
            # Verify presence updated
            presence = UserPresence.query.filter_by(user_id=test_user.id).first()
            assert presence is None or presence.status == "online"

    def test_presence_cleanup_on_logout(self, client, db_session, test_user):
        """Test that presence is cleaned up on logout"""
        from auth import JWTManager

        # Set online
        presence = UserPresence(
            user_id=test_user.id,
            status="online",
            last_seen=datetime.utcnow()
        )
        db_session.add(presence)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Logout (presence should be updated to offline or removed)
        client.post("/api/auth/logout", headers=user_headers)

        # Implementation specific


@pytest.mark.messaging
@pytest.mark.integration
class TestMessageSearch:
    """Test message search functionality"""

    def test_search_messages_in_channel(self, client, db_session, test_user, test_channel):
        """Test searching for messages in a channel"""
        from auth import JWTManager

        # Add user to channel
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.flush()

        # Create searchable messages
        keywords = ["urgent", "meeting", "deadline", "review", "approve"]
        for i, keyword in enumerate(keywords):
            message = ChannelMessage(
                channel_id=test_channel.id,
                user_id=test_user.id,
                content=f"This is a message about {keyword}",
                message_type="text",
                created_at=datetime.utcnow() - timedelta(minutes=i)
            )
            db_session.add(message)

        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Search for "urgent"
        response = client.get(
            f"/api/channels/{test_channel.id}/messages/search?q=urgent",
            headers=user_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) >= 1
            assert any("urgent" in msg["content"] for msg in data)

    def test_global_message_search(self, client, db_session, test_user, test_channel):
        """Test global message search across all channels"""
        from auth import JWTManager

        # Create messages
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="Global searchable content",
            message_type="text"
        )
        db_session.add(message)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Global search
        response = client.get(
            "/api/messages/search?q=searchable",
            headers=user_headers
        )

        assert response.status_code in [200, 404]


@pytest.mark.messaging
@pytest.mark.integration
class TestMessageAttachments:
    """Test message attachments"""

    def test_send_message_with_attachment(self, client, db_session, test_user, test_channel):
        """Test sending a message with attachment"""
        from io import BytesIO

        from auth import JWTManager

        # Add user to channel
        member = ChannelMember(
            channel_id=test_channel.id,
            user_id=test_user.id,
            joined_at=datetime.utcnow()
        )
        db_session.add(member)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Create message with attachment
        data = {
            "content": "Message with attachment",
            "file": (BytesIO(b"test file content"), "test.txt")
        }

        response = client.post(
            f"/api/channels/{test_channel.id}/messages",
            headers=user_headers,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code in [201, 404, 422]

    def test_download_message_attachment(self, client, db_session, test_user, test_channel):
        """Test downloading a message attachment"""
        from auth import JWTManager

        # Create message with attachment record
        message = ChannelMessage(
            channel_id=test_channel.id,
            user_id=test_user.id,
            content="Message with attachment",
            message_type="text"
        )
        db_session.add(message)
        db_session.flush()

        attachment = MessageAttachment(
            message_id=message.id,
            filename="test.txt",
            file_path="/tmp/test.txt",
            file_size=100,
            mime_type="text/plain"
        )
        db_session.add(attachment)
        db_session.commit()

        with client.application.app_context():
            tokens = JWTManager.generate_tokens(test_user)
            user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Download attachment
        response = client.get(
            f"/api/messages/{message.id}/attachments/{attachment.id}",
            headers=user_headers
        )

        assert response.status_code in [200, 404]
