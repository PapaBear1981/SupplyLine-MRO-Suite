"""
Tests for enhanced messaging models.
Tests Channel, ChannelMember, ChannelMessage, MessageReaction,
MessageAttachment, AttachmentDownload, UserPresence, and TypingIndicator models.
"""

import pytest
from models_kits import KitMessage
from models_messaging import (
    AttachmentDownload,
    Channel,
    ChannelMember,
    ChannelMessage,
    MessageAttachment,
    MessageReaction,
    TypingIndicator,
    UserPresence,
)
from sqlalchemy.exc import IntegrityError

from models import db


class TestChannelModel:
    """Test Channel model"""

    def test_create_channel(self, app, test_user):
        """Test creating a channel"""
        with app.app_context():
            channel = Channel(
                name="Engineering",
                description="Engineering team channel",
                channel_type="department",
                department="Engineering",
                created_by=test_user.id
            )
            db.session.add(channel)
            db.session.commit()

            assert channel.id is not None
            assert channel.name == "Engineering"
            assert channel.is_active is True
            assert channel.created_date is not None

    def test_channel_to_dict(self, app, test_user):
        """Test channel to_dict method"""
        with app.app_context():
            channel = Channel(
                name="Test Channel",
                created_by=test_user.id
            )
            db.session.add(channel)
            db.session.commit()

            data = channel.to_dict()
            assert data["id"] == channel.id
            assert data["name"] == "Test Channel"
            assert data["member_count"] == 0
            assert "creator_name" in data

    def test_channel_unique_name(self, app, test_user):
        """Test channel name uniqueness constraint"""
        with app.app_context():
            channel1 = Channel(name="Unique", created_by=test_user.id)
            db.session.add(channel1)
            db.session.commit()

            channel2 = Channel(name="Unique", created_by=test_user.id)
            db.session.add(channel2)

            with pytest.raises(IntegrityError):
                db.session.commit()


class TestChannelMemberModel:
    """Test ChannelMember model"""

    def test_create_member(self, app, test_user):
        """Test creating a channel member"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            member = ChannelMember(
                channel_id=channel.id,
                user_id=test_user.id,
                role="admin"
            )
            db.session.add(member)
            db.session.commit()

            assert member.id is not None
            assert member.role == "admin"
            assert member.notifications_enabled is True

    def test_unique_membership(self, app, test_user):
        """Test unique membership constraint"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            member1 = ChannelMember(channel_id=channel.id, user_id=test_user.id)
            db.session.add(member1)
            db.session.commit()

            member2 = ChannelMember(channel_id=channel.id, user_id=test_user.id)
            db.session.add(member2)

            with pytest.raises(IntegrityError):
                db.session.commit()


class TestChannelMessageModel:
    """Test ChannelMessage model"""

    def test_create_message(self, app, test_user):
        """Test creating a channel message"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Hello, World!"
            )
            db.session.add(message)
            db.session.commit()

            assert message.id is not None
            assert message.message == "Hello, World!"
            assert message.is_deleted is False
            assert message.sent_date is not None

    def test_message_threading(self, app, test_user):
        """Test message threading (replies)"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            parent = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Parent message"
            )
            db.session.add(parent)
            db.session.commit()

            reply = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Reply message",
                parent_message_id=parent.id
            )
            db.session.add(reply)
            db.session.commit()

            assert reply.parent_message_id == parent.id
            assert len(parent.replies) == 1
            assert parent.replies[0].id == reply.id

    def test_message_to_dict(self, app, test_user):
        """Test message to_dict method"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Test"
            )
            db.session.add(message)
            db.session.commit()

            data = message.to_dict()
            assert data["id"] == message.id
            assert data["message"] == "Test"
            assert "sender_name" in data
            assert data["reply_count"] == 0


class TestMessageReactionModel:
    """Test MessageReaction model"""

    def test_create_kit_message_reaction(self, app, test_user, test_kit):
        """Test creating a reaction on a kit message"""
        with app.app_context():
            kit_message = KitMessage(
                kit_id=test_kit.id,
                sender_id=test_user.id,
                subject="Test",
                message="Test"
            )
            db.session.add(kit_message)
            db.session.commit()

            reaction = MessageReaction(
                kit_message_id=kit_message.id,
                user_id=test_user.id,
                reaction_type="thumbs_up"
            )
            db.session.add(reaction)
            db.session.commit()

            assert reaction.id is not None
            assert reaction.reaction_type == "thumbs_up"

    def test_create_channel_message_reaction(self, app, test_user):
        """Test creating a reaction on a channel message"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            channel_message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Test"
            )
            db.session.add(channel_message)
            db.session.commit()

            reaction = MessageReaction(
                channel_message_id=channel_message.id,
                user_id=test_user.id,
                reaction_type="heart"
            )
            db.session.add(reaction)
            db.session.commit()

            assert reaction.id is not None
            assert reaction.channel_message_id == channel_message.id


class TestMessageAttachmentModel:
    """Test MessageAttachment model"""

    def test_create_attachment(self, app, test_user):
        """Test creating a message attachment"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Test"
            )
            db.session.add(message)
            db.session.commit()

            attachment = MessageAttachment(
                channel_message_id=message.id,
                filename="test_file.pdf",
                original_filename="test.pdf",
                file_path="/tmp/test_file.pdf",
                file_size=1024,
                mime_type="application/pdf",
                file_type="document",
                uploaded_by=test_user.id
            )
            db.session.add(attachment)
            db.session.commit()

            assert attachment.id is not None
            assert attachment.filename == "test_file.pdf"
            assert attachment.download_count == 0

    def test_attachment_to_dict(self, app, test_user):
        """Test attachment to_dict method"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Test"
            )
            db.session.add(message)
            db.session.commit()

            attachment = MessageAttachment(
                channel_message_id=message.id,
                filename="test.pdf",
                original_filename="test.pdf",
                file_path="/tmp/test.pdf",
                file_size=1024,
                mime_type="application/pdf",
                file_type="document",
                uploaded_by=test_user.id
            )
            db.session.add(attachment)
            db.session.commit()

            data = attachment.to_dict()
            assert data["id"] == attachment.id
            assert data["file_type"] == "document"
            assert "uploader_name" in data


class TestAttachmentDownloadModel:
    """Test AttachmentDownload model"""

    def test_create_download_record(self, app, test_user):
        """Test creating a download tracking record"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            message = ChannelMessage(
                channel_id=channel.id,
                sender_id=test_user.id,
                message="Test"
            )
            db.session.add(message)
            db.session.commit()

            attachment = MessageAttachment(
                channel_message_id=message.id,
                filename="test.pdf",
                original_filename="test.pdf",
                file_path="/tmp/test.pdf",
                file_size=1024,
                mime_type="application/pdf",
                file_type="document",
                uploaded_by=test_user.id
            )
            db.session.add(attachment)
            db.session.commit()

            download = AttachmentDownload(
                attachment_id=attachment.id,
                user_id=test_user.id,
                ip_address="192.168.1.1"
            )
            db.session.add(download)
            db.session.commit()

            assert download.id is not None
            assert download.ip_address == "192.168.1.1"


class TestUserPresenceModel:
    """Test UserPresence model"""

    def test_create_presence(self, app, test_user):
        """Test creating user presence record"""
        with app.app_context():
            presence = UserPresence(
                user_id=test_user.id,
                is_online=True,
                socket_id="test_socket_123"
            )
            db.session.add(presence)
            db.session.commit()

            assert presence.id is not None
            assert presence.is_online is True
            assert presence.socket_id == "test_socket_123"

    def test_presence_to_dict(self, app, test_user):
        """Test presence to_dict method"""
        with app.app_context():
            presence = UserPresence(
                user_id=test_user.id,
                is_online=True,
                status_message="Working on project"
            )
            db.session.add(presence)
            db.session.commit()

            data = presence.to_dict()
            assert data["user_id"] == test_user.id
            assert data["is_online"] is True
            assert data["status_message"] == "Working on project"

    def test_presence_unique_user(self, app, test_user):
        """Test user can only have one presence record"""
        with app.app_context():
            presence1 = UserPresence(user_id=test_user.id, is_online=True)
            db.session.add(presence1)
            db.session.commit()

            presence2 = UserPresence(user_id=test_user.id, is_online=False)
            db.session.add(presence2)

            with pytest.raises(IntegrityError):
                db.session.commit()


class TestTypingIndicatorModel:
    """Test TypingIndicator model"""

    def test_create_typing_indicator_channel(self, app, test_user):
        """Test creating typing indicator for channel"""
        with app.app_context():
            channel = Channel(name="Test", created_by=test_user.id)
            db.session.add(channel)
            db.session.commit()

            typing = TypingIndicator(
                user_id=test_user.id,
                channel_id=channel.id,
                is_typing=True
            )
            db.session.add(typing)
            db.session.commit()

            assert typing.id is not None
            assert typing.is_typing is True

    def test_create_typing_indicator_kit(self, app, test_user, test_kit):
        """Test creating typing indicator for kit"""
        with app.app_context():
            typing = TypingIndicator(
                user_id=test_user.id,
                kit_id=test_kit.id,
                is_typing=True
            )
            db.session.add(typing)
            db.session.commit()

            assert typing.id is not None
            assert typing.kit_id == test_kit.id
