"""
WebSocket event handlers for real-time messaging features.
Handles connection, disconnection, messaging, typing indicators, and presence tracking.
"""
import logging
from datetime import datetime, UTC
from functools import wraps

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room, rooms
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from models import db
from models_messaging import (
    Channel, ChannelMember, ChannelMessage,
    MessageReaction, UserPresence, TypingIndicator
)
from models_kits import KitMessage
from socketio_config import socketio

logger = logging.getLogger(__name__)


def authenticated_only(f):
    """
    Decorator to require JWT authentication for WebSocket events.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            logger.warning("WebSocket connection without token")
            emit('error', {'message': 'Authentication required'})
            return None

        try:
            decoded_token = decode_token(token)
            user_id = decoded_token.get('sub')
            if not user_id:
                emit('error', {'message': 'Invalid token'})
                return None

            # Pass user_id to the wrapped function
            return f(user_id, *args, **kwargs)

        except ExpiredSignatureError:
            emit('error', {'message': 'Token expired'})
            return None
        except InvalidTokenError:
            emit('error', {'message': 'Invalid token'})
            return None

    return wrapped


# === Connection Management ===

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection.
    Authenticate user and set them as online.
    """
    token = request.args.get('token')
    if not token:
        logger.warning("WebSocket connection attempt without token")
        return False  # Reject connection

    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get('sub')

        if not user_id:
            logger.warning("WebSocket connection with invalid token")
            return False

        # Update or create user presence
        presence = UserPresence.query.filter_by(user_id=user_id).first()
        if not presence:
            presence = UserPresence(user_id=user_id)
            db.session.add(presence)

        presence.is_online = True
        presence.last_activity = datetime.now(UTC)
        presence.socket_id = request.sid
        db.session.commit()

        # Join user's personal room for direct messages
        join_room(f"user_{user_id}")

        # Join all channels the user is a member of
        memberships = ChannelMember.query.filter_by(user_id=user_id).all()
        for membership in memberships:
            join_room(f"channel_{membership.channel_id}")

        logger.info(f"User {user_id} connected via WebSocket", extra={
            "user_id": user_id,
            "socket_id": request.sid
        })

        # Broadcast presence update to all users
        emit('user_online', {
            'user_id': user_id,
            'timestamp': datetime.now(UTC).isoformat()
        }, broadcast=True)

        return True

    except (ExpiredSignatureError, InvalidTokenError) as e:
        logger.warning(f"WebSocket authentication failed: {str(e)}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    Set user as offline.
    """
    token = request.args.get('token')
    if not token:
        return

    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get('sub')

        if user_id:
            presence = UserPresence.query.filter_by(user_id=user_id).first()
            if presence:
                presence.is_online = False
                presence.last_seen = datetime.now(UTC)
                presence.socket_id = None
                db.session.commit()

                logger.info(f"User {user_id} disconnected from WebSocket", extra={
                    "user_id": user_id
                })

                # Broadcast presence update
                emit('user_offline', {
                    'user_id': user_id,
                    'timestamp': datetime.now(UTC).isoformat()
                }, broadcast=True)

    except Exception as e:
        logger.error(f"Error handling disconnect: {str(e)}")


# === Kit Messaging ===

@socketio.on('send_kit_message')
@authenticated_only
def handle_kit_message(user_id, data):
    """
    Handle sending a new kit message.
    Broadcasts to recipient in real-time.
    """
    try:
        kit_id = data.get('kit_id')
        recipient_id = data.get('recipient_id')
        subject = data.get('subject')
        message = data.get('message')
        parent_message_id = data.get('parent_message_id')

        if not all([kit_id, subject, message]):
            emit('error', {'message': 'Missing required fields'})
            return

        # Create new message
        new_message = KitMessage(
            kit_id=kit_id,
            sender_id=user_id,
            recipient_id=recipient_id,
            subject=subject,
            message=message,
            parent_message_id=parent_message_id
        )
        db.session.add(new_message)
        db.session.commit()

        message_data = new_message.to_dict()

        # Emit to sender
        emit('kit_message_sent', message_data, room=f"user_{user_id}")

        # Emit to recipient if specified
        if recipient_id:
            emit('new_kit_message', message_data, room=f"user_{recipient_id}")
        else:
            # Broadcast to all if no recipient (public message)
            emit('new_kit_message', message_data, broadcast=True)

        logger.info(f"Kit message sent", extra={
            "sender_id": user_id,
            "recipient_id": recipient_id,
            "kit_id": kit_id,
            "message_id": new_message.id
        })

    except Exception as e:
        logger.error(f"Error sending kit message: {str(e)}", exc_info=True)
        emit('error', {'message': 'Failed to send message'})


@socketio.on('mark_kit_message_read')
@authenticated_only
def handle_mark_kit_message_read(user_id, data):
    """
    Mark a kit message as read.
    """
    try:
        message_id = data.get('message_id')
        if not message_id:
            emit('error', {'message': 'Message ID required'})
            return

        message = KitMessage.query.get(message_id)
        if not message:
            emit('error', {'message': 'Message not found'})
            return

        # Only recipient can mark as read
        if message.recipient_id != user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        message.is_read = True
        message.read_date = datetime.now(UTC)
        db.session.commit()

        # Notify sender that message was read
        emit('kit_message_read', {
            'message_id': message_id,
            'read_by': user_id,
            'read_date': message.read_date.isoformat()
        }, room=f"user_{message.sender_id}")

        emit('message_marked_read', {'message_id': message_id})

    except Exception as e:
        logger.error(f"Error marking message as read: {str(e)}")
        emit('error', {'message': 'Failed to mark message as read'})


# === Channel Messaging ===

@socketio.on('send_channel_message')
@authenticated_only
def handle_channel_message(user_id, data):
    """
    Handle sending a message to a channel.
    Broadcasts to all channel members.
    """
    try:
        channel_id = data.get('channel_id')
        message = data.get('message')
        parent_message_id = data.get('parent_message_id')

        if not all([channel_id, message]):
            emit('error', {'message': 'Missing required fields'})
            return

        # Verify user is a member of the channel
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=user_id
        ).first()

        if not membership:
            emit('error', {'message': 'Not a channel member'})
            return

        # Create new channel message
        new_message = ChannelMessage(
            channel_id=channel_id,
            sender_id=user_id,
            message=message,
            parent_message_id=parent_message_id
        )
        db.session.add(new_message)
        db.session.commit()

        message_data = new_message.to_dict(include_reactions=True, include_attachments=True)

        # Broadcast to all channel members
        emit('new_channel_message', message_data, room=f"channel_{channel_id}")

        logger.info(f"Channel message sent", extra={
            "sender_id": user_id,
            "channel_id": channel_id,
            "message_id": new_message.id
        })

    except Exception as e:
        logger.error(f"Error sending channel message: {str(e)}", exc_info=True)
        emit('error', {'message': 'Failed to send message'})


@socketio.on('join_channel')
@authenticated_only
def handle_join_channel(user_id, data):
    """
    Join a channel room for real-time updates.
    """
    try:
        channel_id = data.get('channel_id')
        if not channel_id:
            emit('error', {'message': 'Channel ID required'})
            return

        # Verify user is a member
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=user_id
        ).first()

        if not membership:
            emit('error', {'message': 'Not a channel member'})
            return

        join_room(f"channel_{channel_id}")
        emit('channel_joined', {'channel_id': channel_id})

        # Notify other members
        emit('user_joined_channel', {
            'user_id': user_id,
            'channel_id': channel_id
        }, room=f"channel_{channel_id}", include_self=False)

    except Exception as e:
        logger.error(f"Error joining channel: {str(e)}")
        emit('error', {'message': 'Failed to join channel'})


@socketio.on('leave_channel')
@authenticated_only
def handle_leave_channel(user_id, data):
    """
    Leave a channel room.
    """
    try:
        channel_id = data.get('channel_id')
        if not channel_id:
            emit('error', {'message': 'Channel ID required'})
            return

        leave_room(f"channel_{channel_id}")
        emit('channel_left', {'channel_id': channel_id})

        # Notify other members
        emit('user_left_channel', {
            'user_id': user_id,
            'channel_id': channel_id
        }, room=f"channel_{channel_id}")

    except Exception as e:
        logger.error(f"Error leaving channel: {str(e)}")
        emit('error', {'message': 'Failed to leave channel'})


# === Typing Indicators ===

@socketio.on('typing_start')
@authenticated_only
def handle_typing_start(user_id, data):
    """
    User started typing in a channel or kit message.
    """
    try:
        channel_id = data.get('channel_id')
        kit_id = data.get('kit_id')

        if channel_id:
            # Broadcast typing to channel members
            emit('user_typing', {
                'user_id': user_id,
                'channel_id': channel_id,
                'typing': True
            }, room=f"channel_{channel_id}", include_self=False)

        elif kit_id:
            # Broadcast typing to kit message recipients
            emit('user_typing', {
                'user_id': user_id,
                'kit_id': kit_id,
                'typing': True
            }, room=f"kit_{kit_id}", include_self=False)

    except Exception as e:
        logger.error(f"Error handling typing start: {str(e)}")


@socketio.on('typing_stop')
@authenticated_only
def handle_typing_stop(user_id, data):
    """
    User stopped typing.
    """
    try:
        channel_id = data.get('channel_id')
        kit_id = data.get('kit_id')

        if channel_id:
            emit('user_typing', {
                'user_id': user_id,
                'channel_id': channel_id,
                'typing': False
            }, room=f"channel_{channel_id}", include_self=False)

        elif kit_id:
            emit('user_typing', {
                'user_id': user_id,
                'kit_id': kit_id,
                'typing': False
            }, room=f"kit_{kit_id}", include_self=False)

    except Exception as e:
        logger.error(f"Error handling typing stop: {str(e)}")


# === Message Reactions ===

@socketio.on('add_reaction')
@authenticated_only
def handle_add_reaction(user_id, data):
    """
    Add a reaction to a message.
    """
    try:
        kit_message_id = data.get('kit_message_id')
        channel_message_id = data.get('channel_message_id')
        reaction_type = data.get('reaction_type')

        if not reaction_type:
            emit('error', {'message': 'Reaction type required'})
            return

        if not kit_message_id and not channel_message_id:
            emit('error', {'message': 'Message ID required'})
            return

        # Check if reaction already exists
        existing = MessageReaction.query.filter_by(
            user_id=user_id,
            kit_message_id=kit_message_id,
            channel_message_id=channel_message_id,
            reaction_type=reaction_type
        ).first()

        if existing:
            emit('error', {'message': 'Reaction already exists'})
            return

        # Create reaction
        reaction = MessageReaction(
            user_id=user_id,
            kit_message_id=kit_message_id,
            channel_message_id=channel_message_id,
            reaction_type=reaction_type
        )
        db.session.add(reaction)
        db.session.commit()

        reaction_data = reaction.to_dict()

        # Broadcast to appropriate room
        if channel_message_id:
            message = ChannelMessage.query.get(channel_message_id)
            if message:
                emit('reaction_added', reaction_data, room=f"channel_{message.channel_id}")
        elif kit_message_id:
            message = KitMessage.query.get(kit_message_id)
            if message:
                # Notify sender and recipient
                if message.recipient_id:
                    emit('reaction_added', reaction_data, room=f"user_{message.recipient_id}")
                emit('reaction_added', reaction_data, room=f"user_{message.sender_id}")

        emit('reaction_added_confirm', reaction_data)

    except Exception as e:
        logger.error(f"Error adding reaction: {str(e)}", exc_info=True)
        emit('error', {'message': 'Failed to add reaction'})


@socketio.on('remove_reaction')
@authenticated_only
def handle_remove_reaction(user_id, data):
    """
    Remove a reaction from a message.
    """
    try:
        reaction_id = data.get('reaction_id')
        if not reaction_id:
            emit('error', {'message': 'Reaction ID required'})
            return

        reaction = MessageReaction.query.get(reaction_id)
        if not reaction:
            emit('error', {'message': 'Reaction not found'})
            return

        # Only the user who added the reaction can remove it
        if reaction.user_id != user_id:
            emit('error', {'message': 'Unauthorized'})
            return

        channel_id = None
        if reaction.channel_message_id:
            message = ChannelMessage.query.get(reaction.channel_message_id)
            if message:
                channel_id = message.channel_id

        db.session.delete(reaction)
        db.session.commit()

        # Broadcast removal
        if channel_id:
            emit('reaction_removed', {'reaction_id': reaction_id}, room=f"channel_{channel_id}")

        emit('reaction_removed_confirm', {'reaction_id': reaction_id})

    except Exception as e:
        logger.error(f"Error removing reaction: {str(e)}")
        emit('error', {'message': 'Failed to remove reaction'})


# === Presence & Status ===

@socketio.on('update_status')
@authenticated_only
def handle_update_status(user_id, data):
    """
    Update user's custom status message.
    """
    try:
        status_message = data.get('status_message', '')

        presence = UserPresence.query.filter_by(user_id=user_id).first()
        if not presence:
            presence = UserPresence(user_id=user_id)
            db.session.add(presence)

        presence.status_message = status_message
        presence.last_activity = datetime.now(UTC)
        db.session.commit()

        # Broadcast status update
        emit('status_updated', {
            'user_id': user_id,
            'status_message': status_message
        }, broadcast=True)

        emit('status_update_confirm', {'status_message': status_message})

    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        emit('error', {'message': 'Failed to update status'})


@socketio.on('ping')
@authenticated_only
def handle_ping(user_id, data):
    """
    Keep-alive ping to update user activity.
    """
    try:
        presence = UserPresence.query.filter_by(user_id=user_id).first()
        if presence:
            presence.last_activity = datetime.now(UTC)
            db.session.commit()

        emit('pong', {'timestamp': datetime.now(UTC).isoformat()})

    except Exception as e:
        logger.error(f"Error handling ping: {str(e)}")


def register_socketio_events(app):
    """
    Register all WebSocket event handlers with the app.
    This should be called after socketio.init_app() in app.py
    """
    logger.info("WebSocket event handlers registered")
    return socketio
