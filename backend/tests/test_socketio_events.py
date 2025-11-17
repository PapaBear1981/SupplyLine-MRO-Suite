"""
Comprehensive tests for WebSocket event handlers (socketio_events.py).
Tests cover connection, disconnection, messaging, typing indicators, reactions, and presence.
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch, call
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from models import db, User
from models_kits import KitMessage
from models_messaging import (
    Channel,
    ChannelMember,
    ChannelMessage,
    MessageReaction,
    UserPresence
)
from socketio_events import (
    authenticated_only,
    handle_connect,
    handle_disconnect,
    handle_kit_message,
    handle_mark_kit_message_read,
    handle_channel_message,
    handle_join_channel,
    handle_leave_channel,
    handle_typing_start,
    handle_typing_stop,
    handle_add_reaction,
    handle_remove_reaction,
    handle_update_status,
    handle_ping,
    register_socketio_events,
)


# === Test Fixtures ===

@pytest.fixture
def mock_request():
    """Mock Flask request object"""
    mock_req = MagicMock()
    mock_req.args = {}
    mock_req.sid = "test_socket_id_123"
    with patch("socketio_events.request", mock_req):
        yield mock_req


@pytest.fixture
def mock_emit():
    """Mock socketio emit function"""
    with patch("socketio_events.emit") as mock:
        yield mock


@pytest.fixture
def mock_join_room():
    """Mock socketio join_room function"""
    with patch("socketio_events.join_room") as mock:
        yield mock


@pytest.fixture
def mock_leave_room():
    """Mock socketio leave_room function"""
    with patch("socketio_events.leave_room") as mock:
        yield mock


@pytest.fixture
def mock_decode_token():
    """Mock JWT decode_token function"""
    with patch("socketio_events.decode_token") as mock:
        yield mock


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    user = User(
        name="Second User",
        employee_number="USER002",
        department="Materials",
        is_admin=False,
        is_active=True
    )
    user.set_password("user456")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def channel_with_member(db_session, test_user):
    """Create a channel with test_user as a member"""
    channel = Channel(
        name="Test Channel",
        description="Test channel for unit tests",
        channel_type="department",
        department="Engineering",
        created_by=test_user.id
    )
    db_session.add(channel)
    db_session.flush()

    membership = ChannelMember(
        channel_id=channel.id,
        user_id=test_user.id,
        role="member"
    )
    db_session.add(membership)
    db_session.commit()
    return channel


@pytest.fixture
def kit_message(db_session, test_user, second_user, test_kit):
    """Create a test kit message"""
    message = KitMessage(
        kit_id=test_kit.id,
        sender_id=test_user.id,
        recipient_id=second_user.id,
        subject="Test Subject",
        message="Test message content",
        is_read=False
    )
    db_session.add(message)
    db_session.commit()
    return message


@pytest.fixture
def channel_message(db_session, test_user, channel_with_member):
    """Create a test channel message"""
    message = ChannelMessage(
        channel_id=channel_with_member.id,
        sender_id=test_user.id,
        message="Test channel message"
    )
    db_session.add(message)
    db_session.commit()
    return message


@pytest.fixture
def user_presence(db_session, test_user):
    """Create a user presence record"""
    presence = UserPresence(
        user_id=test_user.id,
        is_online=False,
        status_message=""
    )
    db_session.add(presence)
    db_session.commit()
    return presence


# === Tests for authenticated_only decorator ===

class TestAuthenticatedOnlyDecorator:
    """Test the authenticated_only decorator"""

    def test_no_token(self, app, db_session, mock_request, mock_emit):
        """Test decorator rejects request without token"""
        mock_request.args = {}

        @authenticated_only
        def test_func(user_id, data):
            return "success"

        result = test_func({})

        assert result is None
        mock_emit.assert_called_once_with(
            "error", {"message": "Authentication required"}
        )

    def test_invalid_token(self, app, db_session, mock_request, mock_emit, mock_decode_token):
        """Test decorator rejects invalid token"""
        mock_request.args = {"token": "invalid_token"}
        mock_decode_token.side_effect = InvalidTokenError("Invalid")

        @authenticated_only
        def test_func(user_id, data):
            return "success"

        result = test_func({})

        assert result is None
        mock_emit.assert_called_once_with(
            "error", {"message": "Invalid token"}
        )

    def test_expired_token(self, app, db_session, mock_request, mock_emit, mock_decode_token):
        """Test decorator rejects expired token"""
        mock_request.args = {"token": "expired_token"}
        mock_decode_token.side_effect = ExpiredSignatureError("Expired")

        @authenticated_only
        def test_func(user_id, data):
            return "success"

        result = test_func({})

        assert result is None
        mock_emit.assert_called_once_with(
            "error", {"message": "Token expired"}
        )

    def test_token_without_sub(self, app, db_session, mock_request, mock_emit, mock_decode_token):
        """Test decorator rejects token without user ID"""
        mock_request.args = {"token": "token_no_sub"}
        mock_decode_token.return_value = {"iss": "test"}  # No 'sub' field

        @authenticated_only
        def test_func(user_id, data):
            return "success"

        result = test_func({})

        assert result is None
        mock_emit.assert_called_once_with(
            "error", {"message": "Invalid token"}
        )

    def test_valid_token(self, app, db_session, mock_request, mock_emit, mock_decode_token):
        """Test decorator allows valid token and passes user_id"""
        mock_request.args = {"token": "valid_token"}
        mock_decode_token.return_value = {"sub": 42}

        @authenticated_only
        def test_func(user_id, data):
            return f"user_{user_id}_data_{data.get('key')}"

        result = test_func({"key": "value"})

        assert result == "user_42_data_value"
        mock_emit.assert_not_called()


# === Tests for Connection Management ===

class TestHandleConnect:
    """Test WebSocket connection handler"""

    def test_connect_without_token(self, app, db_session, mock_request):
        """Test connection rejected without token"""
        mock_request.args = {}

        result = handle_connect()

        assert result is False

    def test_connect_with_invalid_token(self, app, db_session, mock_request, mock_decode_token):
        """Test connection rejected with invalid token"""
        mock_request.args = {"token": "invalid"}
        mock_decode_token.side_effect = InvalidTokenError("Invalid")

        result = handle_connect()

        assert result is False

    def test_connect_with_expired_token(self, app, db_session, mock_request, mock_decode_token):
        """Test connection rejected with expired token"""
        mock_request.args = {"token": "expired"}
        mock_decode_token.side_effect = ExpiredSignatureError("Expired")

        result = handle_connect()

        assert result is False

    def test_connect_token_without_user_id(self, app, db_session, mock_request, mock_decode_token):
        """Test connection rejected when token has no user ID"""
        mock_request.args = {"token": "no_sub"}
        mock_decode_token.return_value = {"iss": "test"}

        result = handle_connect()

        assert result is False

    def test_connect_success_new_presence(
        self, app, db_session, test_user, mock_request, mock_decode_token,
        mock_emit, mock_join_room
    ):
        """Test successful connection creates new presence record"""
        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}

        result = handle_connect()

        assert result is True

        # Verify presence was created
        presence = UserPresence.query.filter_by(user_id=test_user.id).first()
        assert presence is not None
        assert presence.is_online is True
        assert presence.socket_id == "test_socket_id_123"

        # Verify user joined their personal room
        mock_join_room.assert_any_call(f"user_{test_user.id}")

        # Verify broadcast was sent
        assert mock_emit.call_count >= 1
        emit_calls = [call for call in mock_emit.call_args_list if call[0][0] == "user_online"]
        assert len(emit_calls) == 1

    def test_connect_success_existing_presence(
        self, app, db_session, test_user, user_presence, mock_request,
        mock_decode_token, mock_emit, mock_join_room
    ):
        """Test successful connection updates existing presence record"""
        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}

        result = handle_connect()

        assert result is True

        # Verify presence was updated
        presence = UserPresence.query.filter_by(user_id=test_user.id).first()
        assert presence.is_online is True
        assert presence.socket_id == "test_socket_id_123"

    def test_connect_joins_channel_rooms(
        self, app, db_session, test_user, channel_with_member, mock_request,
        mock_decode_token, mock_emit, mock_join_room
    ):
        """Test connection joins all channel rooms user is member of"""
        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}

        handle_connect()

        # Verify user joined channel room
        mock_join_room.assert_any_call(f"channel_{channel_with_member.id}")


class TestHandleDisconnect:
    """Test WebSocket disconnection handler"""

    def test_disconnect_without_token(self, app, db_session, mock_request):
        """Test disconnect handler gracefully handles missing token"""
        mock_request.args = {}

        # Should not raise any exception
        handle_disconnect()

    def test_disconnect_success(
        self, app, db_session, test_user, user_presence, mock_request,
        mock_decode_token, mock_emit
    ):
        """Test successful disconnection updates presence"""
        # Set user as online first
        user_presence.is_online = True
        user_presence.socket_id = "test_socket_id"
        db_session.commit()

        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}

        handle_disconnect()

        # Verify presence was updated
        presence = UserPresence.query.filter_by(user_id=test_user.id).first()
        assert presence.is_online is False
        assert presence.socket_id is None

        # Verify broadcast was sent
        emit_calls = [call for call in mock_emit.call_args_list if call[0][0] == "user_offline"]
        assert len(emit_calls) == 1

    def test_disconnect_no_presence_record(
        self, app, db_session, test_user, mock_request, mock_decode_token, mock_emit
    ):
        """Test disconnect when no presence record exists"""
        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}

        # Should not raise any exception
        handle_disconnect()

        # No broadcast should be sent if no presence record
        emit_calls = [call for call in mock_emit.call_args_list if call[0][0] == "user_offline"]
        assert len(emit_calls) == 0

    def test_disconnect_handles_exception(
        self, app, db_session, mock_request, mock_decode_token
    ):
        """Test disconnect handles exceptions gracefully"""
        mock_request.args = {"token": "valid"}
        mock_decode_token.side_effect = Exception("Unexpected error")

        # Should not raise exception
        handle_disconnect()


# === Tests for Kit Messaging ===

class TestHandleKitMessage:
    """Test kit message handler"""

    def test_missing_required_fields(self, app, db_session, mock_emit):
        """Test error when required fields are missing"""
        # Call the unwrapped function directly to bypass decorator
        handle_kit_message.__wrapped__(1, {"kit_id": 1})  # Missing subject and message

        mock_emit.assert_called_with("error", {"message": "Missing required fields"})

    def test_send_message_with_recipient(
        self, app, db_session, test_user, second_user, test_kit, mock_emit
    ):
        """Test sending message to specific recipient"""
        data = {
            "kit_id": test_kit.id,
            "recipient_id": second_user.id,
            "subject": "Test Subject",
            "message": "Test message content"
        }

        handle_kit_message.__wrapped__(test_user.id, data)

        # Verify message was created
        message = KitMessage.query.filter_by(sender_id=test_user.id).first()
        assert message is not None
        assert message.subject == "Test Subject"
        assert message.message == "Test message content"
        assert message.recipient_id == second_user.id

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "kit_message_sent" in event_names
        assert "new_kit_message" in event_names

    def test_send_message_without_recipient(
        self, app, db_session, test_user, test_kit, mock_emit
    ):
        """Test broadcasting message without specific recipient"""
        data = {
            "kit_id": test_kit.id,
            "subject": "Broadcast Subject",
            "message": "Broadcast message"
        }

        handle_kit_message.__wrapped__(test_user.id, data)

        # Verify message was created without recipient
        message = KitMessage.query.filter_by(sender_id=test_user.id).first()
        assert message.recipient_id is None

        # Verify broadcast emission
        emit_calls = [c for c in mock_emit.call_args_list if c[0][0] == "new_kit_message"]
        assert len(emit_calls) == 1
        assert emit_calls[0][1].get("broadcast") is True

    def test_send_message_with_parent(
        self, app, db_session, test_user, test_kit, kit_message, mock_emit
    ):
        """Test sending reply to existing message"""
        data = {
            "kit_id": test_kit.id,
            "subject": "Reply Subject",
            "message": "Reply message",
            "parent_message_id": kit_message.id
        }

        handle_kit_message.__wrapped__(test_user.id, data)

        # Verify parent message ID was set
        reply = KitMessage.query.filter_by(
            sender_id=test_user.id,
            parent_message_id=kit_message.id
        ).first()
        assert reply is not None

    def test_send_message_exception(self, app, db_session, test_user, mock_emit):
        """Test error handling when exception occurs"""
        with patch("socketio_events.KitMessage") as mock_message:
            mock_message.side_effect = Exception("Database error")

            data = {
                "kit_id": 1,
                "subject": "Subject",
                "message": "Message"
            }

            handle_kit_message.__wrapped__(test_user.id, data)

            mock_emit.assert_called_with("error", {"message": "Failed to send message"})


class TestHandleMarkKitMessageRead:
    """Test marking kit message as read"""

    def test_missing_message_id(self, app, db_session, mock_emit, mock_request):
        """Test error when message ID is missing"""
        handle_mark_kit_message_read.__wrapped__(1, {})

        mock_emit.assert_called_with("error", {"message": "Message ID required"})

    def test_message_not_found(self, app, db_session, mock_emit, mock_request):
        """Test error when message does not exist"""
        handle_mark_kit_message_read.__wrapped__(1, {"message_id": 99999})

        mock_emit.assert_called_with("error", {"message": "Message not found"})

    def test_unauthorized_user(
        self, app, db_session, test_user, kit_message, mock_emit, mock_request
    ):
        """Test error when user is not the recipient"""
        # test_user is the sender, not recipient
        handle_mark_kit_message_read.__wrapped__(test_user.id, {"message_id": kit_message.id})

        mock_emit.assert_called_with("error", {"message": "Unauthorized"})

    def test_mark_read_success(
        self, app, db_session, second_user, kit_message, mock_emit, mock_request
    ):
        """Test successfully marking message as read"""
        # second_user is the recipient
        handle_mark_kit_message_read.__wrapped__(second_user.id, {"message_id": kit_message.id})

        # Verify message was marked as read
        db_session.refresh(kit_message)
        assert kit_message.is_read is True
        assert kit_message.read_date is not None

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "kit_message_read" in event_names
        assert "message_marked_read" in event_names

    def test_mark_read_exception(
        self, app, db_session, second_user, kit_message, mock_emit, mock_request
    ):
        """Test error handling when exception occurs"""
        with patch("socketio_events.KitMessage.query") as mock_query:
            mock_query.get.side_effect = Exception("Database error")

            handle_mark_kit_message_read.__wrapped__(second_user.id, {"message_id": kit_message.id})

            mock_emit.assert_called_with("error", {"message": "Failed to mark message as read"})


# === Tests for Channel Messaging ===

class TestHandleChannelMessage:
    """Test channel message handler"""

    def test_missing_required_fields(self, app, db_session, mock_emit, mock_request):
        """Test error when required fields are missing"""
        handle_channel_message.__wrapped__(1, {"channel_id": 1})  # Missing message

        mock_emit.assert_called_with("error", {"message": "Missing required fields"})

    def test_not_channel_member(self, app, db_session, test_user, channel_with_member, mock_emit, mock_request):
        """Test error when user is not a channel member"""
        # Use a different user ID that's not a member
        handle_channel_message.__wrapped__(99999, {
            "channel_id": channel_with_member.id,
            "message": "Test message"
        })

        mock_emit.assert_called_with("error", {"message": "Not a channel member"})

    def test_send_channel_message_success(
        self, app, db_session, test_user, channel_with_member, mock_emit, mock_request
    ):
        """Test successfully sending channel message"""
        data = {
            "channel_id": channel_with_member.id,
            "message": "Hello channel!"
        }

        handle_channel_message.__wrapped__(test_user.id, data)

        # Verify message was created
        message = ChannelMessage.query.filter_by(
            channel_id=channel_with_member.id,
            sender_id=test_user.id
        ).first()
        assert message is not None
        assert message.message == "Hello channel!"

        # Verify broadcast to channel
        emit_calls = [c for c in mock_emit.call_args_list if c[0][0] == "new_channel_message"]
        assert len(emit_calls) == 1

    def test_send_channel_message_with_parent(
        self, app, db_session, test_user, channel_with_member, channel_message, mock_emit, mock_request
    ):
        """Test sending reply in channel"""
        data = {
            "channel_id": channel_with_member.id,
            "message": "Reply to message",
            "parent_message_id": channel_message.id
        }

        handle_channel_message.__wrapped__(test_user.id, data)

        # Verify parent was set
        reply = ChannelMessage.query.filter_by(
            parent_message_id=channel_message.id
        ).first()
        assert reply is not None

    def test_send_channel_message_exception(
        self, app, db_session, test_user, channel_with_member, mock_emit, mock_request
    ):
        """Test error handling when exception occurs"""
        with patch("socketio_events.ChannelMessage") as mock_message:
            mock_message.side_effect = Exception("Database error")

            data = {
                "channel_id": channel_with_member.id,
                "message": "Test message"
            }

            handle_channel_message.__wrapped__(test_user.id, data)

            mock_emit.assert_called_with("error", {"message": "Failed to send message"})


class TestHandleJoinChannel:
    """Test channel join handler"""

    def test_missing_channel_id(self, app, db_session, mock_emit, mock_request):
        """Test error when channel ID is missing"""
        handle_join_channel.__wrapped__(1, {})

        mock_emit.assert_called_with("error", {"message": "Channel ID required"})

    def test_not_channel_member(self, app, db_session, channel_with_member, mock_emit, mock_request):
        """Test error when user is not a member"""
        handle_join_channel.__wrapped__(99999, {"channel_id": channel_with_member.id})

        mock_emit.assert_called_with("error", {"message": "Not a channel member"})

    def test_join_channel_success(
        self, app, db_session, test_user, channel_with_member, mock_emit, mock_join_room, mock_request
    ):
        """Test successfully joining channel"""
        handle_join_channel.__wrapped__(test_user.id, {"channel_id": channel_with_member.id})

        # Verify join_room was called
        mock_join_room.assert_called_once_with(f"channel_{channel_with_member.id}")

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "channel_joined" in event_names
        assert "user_joined_channel" in event_names

    def test_join_channel_exception(
        self, app, db_session, test_user, channel_with_member, mock_emit, mock_join_room, mock_request
    ):
        """Test error handling when exception occurs"""
        mock_join_room.side_effect = Exception("Room error")

        handle_join_channel.__wrapped__(test_user.id, {"channel_id": channel_with_member.id})

        mock_emit.assert_called_with("error", {"message": "Failed to join channel"})


class TestHandleLeaveChannel:
    """Test channel leave handler"""

    def test_missing_channel_id(self, app, db_session, mock_emit, mock_request):
        """Test error when channel ID is missing"""
        handle_leave_channel.__wrapped__(1, {})

        mock_emit.assert_called_with("error", {"message": "Channel ID required"})

    def test_leave_channel_success(
        self, app, db_session, test_user, mock_emit, mock_leave_room, mock_request
    ):
        """Test successfully leaving channel"""
        handle_leave_channel.__wrapped__(test_user.id, {"channel_id": 1})

        # Verify leave_room was called
        mock_leave_room.assert_called_once_with("channel_1")

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "channel_left" in event_names
        assert "user_left_channel" in event_names

    def test_leave_channel_exception(
        self, app, db_session, test_user, mock_emit, mock_leave_room, mock_request
    ):
        """Test error handling when exception occurs"""
        mock_leave_room.side_effect = Exception("Room error")

        handle_leave_channel.__wrapped__(test_user.id, {"channel_id": 1})

        mock_emit.assert_called_with("error", {"message": "Failed to leave channel"})


# === Tests for Typing Indicators ===

class TestHandleTypingStart:
    """Test typing start indicator"""

    def test_typing_start_channel(self, app, db_session, test_user, mock_emit, mock_request):
        """Test typing indicator for channel"""
        handle_typing_start.__wrapped__(test_user.id, {"channel_id": 1})

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args
        assert call_args[0][0] == "user_typing"
        assert call_args[0][1]["channel_id"] == 1
        assert call_args[0][1]["typing"] is True
        assert call_args[1]["room"] == "channel_1"

    def test_typing_start_kit(self, app, db_session, test_user, mock_emit, mock_request):
        """Test typing indicator for kit"""
        handle_typing_start.__wrapped__(test_user.id, {"kit_id": 2})

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args
        assert call_args[0][0] == "user_typing"
        assert call_args[0][1]["kit_id"] == 2
        assert call_args[0][1]["typing"] is True
        assert call_args[1]["room"] == "kit_2"

    def test_typing_start_no_target(self, app, db_session, test_user, mock_emit, mock_request):
        """Test typing indicator without channel or kit ID"""
        handle_typing_start.__wrapped__(test_user.id, {})

        # Should not emit anything
        mock_emit.assert_not_called()

    def test_typing_start_exception(self, app, db_session, test_user, mock_emit, mock_request):
        """Test error handling when exception occurs"""
        mock_emit.side_effect = Exception("Emit error")

        # Should not raise exception
        handle_typing_start.__wrapped__(test_user.id, {"channel_id": 1})


class TestHandleTypingStop:
    """Test typing stop indicator"""

    def test_typing_stop_channel(self, app, db_session, test_user, mock_emit, mock_request):
        """Test stopping typing indicator for channel"""
        handle_typing_stop.__wrapped__(test_user.id, {"channel_id": 1})

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args
        assert call_args[0][0] == "user_typing"
        assert call_args[0][1]["channel_id"] == 1
        assert call_args[0][1]["typing"] is False

    def test_typing_stop_kit(self, app, db_session, test_user, mock_emit, mock_request):
        """Test stopping typing indicator for kit"""
        handle_typing_stop.__wrapped__(test_user.id, {"kit_id": 2})

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args
        assert call_args[0][0] == "user_typing"
        assert call_args[0][1]["kit_id"] == 2
        assert call_args[0][1]["typing"] is False

    def test_typing_stop_no_target(self, app, db_session, test_user, mock_emit, mock_request):
        """Test typing stop without channel or kit ID"""
        handle_typing_stop.__wrapped__(test_user.id, {})

        mock_emit.assert_not_called()

    def test_typing_stop_exception(self, app, db_session, test_user, mock_emit, mock_request):
        """Test error handling when exception occurs"""
        mock_emit.side_effect = Exception("Emit error")

        # Should not raise exception
        handle_typing_stop.__wrapped__(test_user.id, {"channel_id": 1})


# === Tests for Message Reactions ===

class TestHandleAddReaction:
    """Test adding reactions to messages"""

    def test_missing_reaction_type(self, app, db_session, mock_emit, mock_request):
        """Test error when reaction type is missing"""
        handle_add_reaction.__wrapped__(1, {"channel_message_id": 1})

        mock_emit.assert_called_with("error", {"message": "Reaction type required"})

    def test_missing_message_id(self, app, db_session, mock_emit, mock_request):
        """Test error when message ID is missing"""
        handle_add_reaction.__wrapped__(1, {"reaction_type": "thumbs_up"})

        mock_emit.assert_called_with("error", {"message": "Message ID required"})

    def test_reaction_already_exists(
        self, app, db_session, test_user, channel_message, mock_emit, mock_request
    ):
        """Test error when reaction already exists"""
        # Create existing reaction
        existing = MessageReaction(
            user_id=test_user.id,
            channel_message_id=channel_message.id,
            reaction_type="thumbs_up"
        )
        db_session.add(existing)
        db_session.commit()

        handle_add_reaction.__wrapped__(test_user.id, {
            "channel_message_id": channel_message.id,
            "reaction_type": "thumbs_up"
        })

        mock_emit.assert_called_with("error", {"message": "Reaction already exists"})

    def test_add_reaction_to_channel_message(
        self, app, db_session, test_user, channel_message, mock_emit, mock_request
    ):
        """Test adding reaction to channel message"""
        handle_add_reaction.__wrapped__(test_user.id, {
            "channel_message_id": channel_message.id,
            "reaction_type": "heart"
        })

        # Verify reaction was created
        reaction = MessageReaction.query.filter_by(
            user_id=test_user.id,
            channel_message_id=channel_message.id
        ).first()
        assert reaction is not None
        assert reaction.reaction_type == "heart"

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "reaction_added" in event_names
        assert "reaction_added_confirm" in event_names

    def test_add_reaction_to_kit_message_with_recipient(
        self, app, db_session, test_user, kit_message, mock_emit, mock_request
    ):
        """Test adding reaction to kit message with recipient"""
        handle_add_reaction.__wrapped__(test_user.id, {
            "kit_message_id": kit_message.id,
            "reaction_type": "thumbs_up"
        })

        # Verify reaction was created
        reaction = MessageReaction.query.filter_by(
            user_id=test_user.id,
            kit_message_id=kit_message.id
        ).first()
        assert reaction is not None

        # Should notify both sender and recipient
        emit_calls = [c for c in mock_emit.call_args_list if c[0][0] == "reaction_added"]
        assert len(emit_calls) == 2  # One for recipient, one for sender

    def test_add_reaction_to_kit_message_no_recipient(
        self, app, db_session, test_user, test_kit, mock_emit, mock_request
    ):
        """Test adding reaction to kit message without recipient"""
        # Create message without recipient
        message = KitMessage(
            kit_id=test_kit.id,
            sender_id=test_user.id,
            subject="No Recipient",
            message="Broadcast message"
        )
        db_session.add(message)
        db_session.commit()

        handle_add_reaction.__wrapped__(test_user.id, {
            "kit_message_id": message.id,
            "reaction_type": "fire"
        })

        # Should only notify sender
        emit_calls = [c for c in mock_emit.call_args_list if c[0][0] == "reaction_added"]
        assert len(emit_calls) == 1

    def test_add_reaction_exception(self, app, db_session, test_user, mock_emit, mock_request):
        """Test error handling when exception occurs"""
        with patch("socketio_events.MessageReaction.query") as mock_query:
            mock_query.filter_by.return_value.first.side_effect = Exception("DB error")

            handle_add_reaction.__wrapped__(test_user.id, {
                "channel_message_id": 1,
                "reaction_type": "thumbs_up"
            })

            mock_emit.assert_called_with("error", {"message": "Failed to add reaction"})


class TestHandleRemoveReaction:
    """Test removing reactions from messages"""

    def test_missing_reaction_id(self, app, db_session, mock_emit, mock_request):
        """Test error when reaction ID is missing"""
        handle_remove_reaction.__wrapped__(1, {})

        mock_emit.assert_called_with("error", {"message": "Reaction ID required"})

    def test_reaction_not_found(self, app, db_session, mock_emit, mock_request):
        """Test error when reaction does not exist"""
        handle_remove_reaction.__wrapped__(1, {"reaction_id": 99999})

        mock_emit.assert_called_with("error", {"message": "Reaction not found"})

    def test_unauthorized_removal(
        self, app, db_session, test_user, second_user, channel_message, mock_emit, mock_request
    ):
        """Test error when user tries to remove another's reaction"""
        # Create reaction by test_user
        reaction = MessageReaction(
            user_id=test_user.id,
            channel_message_id=channel_message.id,
            reaction_type="thumbs_up"
        )
        db_session.add(reaction)
        db_session.commit()

        # second_user tries to remove it
        handle_remove_reaction.__wrapped__(second_user.id, {"reaction_id": reaction.id})

        mock_emit.assert_called_with("error", {"message": "Unauthorized"})

    def test_remove_channel_reaction_success(
        self, app, db_session, test_user, channel_message, mock_emit, mock_request
    ):
        """Test successfully removing reaction from channel message"""
        # Create reaction
        reaction = MessageReaction(
            user_id=test_user.id,
            channel_message_id=channel_message.id,
            reaction_type="thumbs_up"
        )
        db_session.add(reaction)
        db_session.commit()
        reaction_id = reaction.id

        handle_remove_reaction.__wrapped__(test_user.id, {"reaction_id": reaction_id})

        # Verify reaction was deleted
        assert MessageReaction.query.get(reaction_id) is None

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "reaction_removed" in event_names
        assert "reaction_removed_confirm" in event_names

    def test_remove_non_channel_reaction(
        self, app, db_session, test_user, kit_message, mock_emit, mock_request
    ):
        """Test removing reaction from non-channel message"""
        # Create kit message reaction
        reaction = MessageReaction(
            user_id=test_user.id,
            kit_message_id=kit_message.id,
            reaction_type="heart"
        )
        db_session.add(reaction)
        db_session.commit()
        reaction_id = reaction.id

        handle_remove_reaction.__wrapped__(test_user.id, {"reaction_id": reaction_id})

        # Verify reaction was deleted
        assert MessageReaction.query.get(reaction_id) is None

        # Should still emit confirmation
        emit_calls = [c for c in mock_emit.call_args_list if c[0][0] == "reaction_removed_confirm"]
        assert len(emit_calls) == 1

    def test_remove_reaction_exception(
        self, app, db_session, test_user, mock_emit, mock_request
    ):
        """Test error handling when exception occurs"""
        with patch("socketio_events.MessageReaction.query") as mock_query:
            mock_query.get.side_effect = Exception("Database error")

            handle_remove_reaction.__wrapped__(test_user.id, {"reaction_id": 1})

            mock_emit.assert_called_with("error", {"message": "Failed to remove reaction"})


# === Tests for Presence & Status ===

class TestHandleUpdateStatus:
    """Test status update handler"""

    def test_update_status_new_presence(
        self, app, db_session, test_user, mock_emit, mock_request
    ):
        """Test updating status creates presence if not exists"""
        handle_update_status.__wrapped__(test_user.id, {"status_message": "Working on project"})

        # Verify presence was created
        presence = UserPresence.query.filter_by(user_id=test_user.id).first()
        assert presence is not None
        assert presence.status_message == "Working on project"

        # Verify emissions
        emit_calls = mock_emit.call_args_list
        event_names = [call[0][0] for call in emit_calls]
        assert "status_updated" in event_names
        assert "status_update_confirm" in event_names

    def test_update_status_existing_presence(
        self, app, db_session, test_user, user_presence, mock_emit, mock_request
    ):
        """Test updating status with existing presence"""
        handle_update_status.__wrapped__(test_user.id, {"status_message": "In a meeting"})

        # Verify presence was updated
        db_session.refresh(user_presence)
        assert user_presence.status_message == "In a meeting"

    def test_update_status_empty_message(
        self, app, db_session, test_user, mock_emit, mock_request
    ):
        """Test updating status with empty message"""
        handle_update_status.__wrapped__(test_user.id, {})

        presence = UserPresence.query.filter_by(user_id=test_user.id).first()
        assert presence.status_message == ""

    def test_update_status_exception(
        self, app, db_session, test_user, mock_emit, mock_request
    ):
        """Test error handling when exception occurs"""
        with patch("socketio_events.UserPresence.query") as mock_query:
            mock_query.filter_by.return_value.first.side_effect = Exception("DB error")

            handle_update_status.__wrapped__(test_user.id, {"status_message": "Test"})

            mock_emit.assert_called_with("error", {"message": "Failed to update status"})


class TestHandlePing:
    """Test ping/keep-alive handler"""

    def test_ping_success(self, app, db_session, test_user, user_presence, mock_emit, mock_request):
        """Test successful ping updates last_activity"""
        old_activity = user_presence.last_activity

        handle_ping.__wrapped__(test_user.id, {})

        # Verify activity was updated
        db_session.refresh(user_presence)
        assert user_presence.last_activity >= old_activity

        # Verify pong was sent
        mock_emit.assert_called_once()
        assert mock_emit.call_args[0][0] == "pong"
        assert "timestamp" in mock_emit.call_args[0][1]

    def test_ping_no_presence_record(self, app, db_session, test_user, mock_emit, mock_request):
        """Test ping when no presence record exists"""
        handle_ping.__wrapped__(test_user.id, {})

        # Should still send pong
        mock_emit.assert_called_once()
        assert mock_emit.call_args[0][0] == "pong"

    def test_ping_exception(self, app, db_session, test_user, mock_emit, mock_request):
        """Test error handling when exception occurs"""
        with patch("socketio_events.UserPresence.query") as mock_query:
            mock_query.filter_by.return_value.first.side_effect = Exception("DB error")

            # Should not raise exception
            handle_ping.__wrapped__(test_user.id, {})


# === Test for register_socketio_events ===

class TestRegisterSocketioEvents:
    """Test the registration function"""

    def test_register_socketio_events(self, app, db_session):
        """Test that register_socketio_events returns socketio instance"""
        result = register_socketio_events(app)

        # Verify it returns the socketio instance
        from socketio_config import socketio
        assert result == socketio


# === Integration-style tests ===

class TestEndToEndScenarios:
    """Test complete workflows"""

    def test_complete_message_workflow(
        self, app, db_session, test_user, second_user, test_kit,
        mock_emit, mock_request, mock_decode_token, mock_join_room
    ):
        """Test complete message sending and reading workflow"""
        # Step 1: User connects
        mock_request.args = {"token": "valid"}
        mock_decode_token.return_value = {"sub": test_user.id}
        handle_connect()

        mock_emit.reset_mock()

        # Step 2: Send a message
        message_data = {
            "kit_id": test_kit.id,
            "recipient_id": second_user.id,
            "subject": "Integration Test",
            "message": "Testing complete workflow"
        }
        handle_kit_message.__wrapped__(test_user.id, message_data)

        # Verify message was created
        message = KitMessage.query.filter_by(sender_id=test_user.id).first()
        assert message is not None

        mock_emit.reset_mock()

        # Step 3: Recipient marks message as read
        handle_mark_kit_message_read.__wrapped__(second_user.id, {"message_id": message.id})

        # Verify message was marked as read
        db_session.refresh(message)
        assert message.is_read is True

    def test_channel_message_with_reaction_workflow(
        self, app, db_session, test_user, second_user, channel_with_member, mock_emit, mock_request
    ):
        """Test channel message with reaction workflow"""
        # Add second_user to channel
        membership = ChannelMember(
            channel_id=channel_with_member.id,
            user_id=second_user.id,
            role="member"
        )
        db_session.add(membership)
        db_session.commit()

        # Step 1: Send channel message
        handle_channel_message.__wrapped__(test_user.id, {
            "channel_id": channel_with_member.id,
            "message": "Check this out!"
        })

        message = ChannelMessage.query.filter_by(
            sender_id=test_user.id
        ).first()
        assert message is not None

        mock_emit.reset_mock()

        # Step 2: Second user adds reaction
        handle_add_reaction.__wrapped__(second_user.id, {
            "channel_message_id": message.id,
            "reaction_type": "thumbs_up"
        })

        reaction = MessageReaction.query.filter_by(
            user_id=second_user.id
        ).first()
        assert reaction is not None

        mock_emit.reset_mock()

        # Step 3: Remove reaction
        handle_remove_reaction.__wrapped__(second_user.id, {"reaction_id": reaction.id})

        assert MessageReaction.query.get(reaction.id) is None

    def test_typing_indicators_workflow(
        self, app, db_session, test_user, mock_emit, mock_request
    ):
        """Test typing indicators start and stop"""
        # Start typing
        handle_typing_start.__wrapped__(test_user.id, {"channel_id": 1})

        first_call = mock_emit.call_args
        assert first_call[0][1]["typing"] is True

        mock_emit.reset_mock()

        # Stop typing
        handle_typing_stop.__wrapped__(test_user.id, {"channel_id": 1})

        second_call = mock_emit.call_args
        assert second_call[0][1]["typing"] is False
