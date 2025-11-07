"""
API routes for channel management (department-wide messaging).
"""
import logging
from datetime import datetime, UTC

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from auth import jwt_required
from auth.jwt_manager import JWTManager
from models import db
from models_messaging import Channel, ChannelMember, ChannelMessage

logger = logging.getLogger(__name__)

channels_bp = Blueprint('channels', __name__, url_prefix='/api/channels')


@channels_bp.route('', methods=['GET'])
@jwt_required
def get_channels():
    """
    Get all channels the current user has access to.
    Query params:
    - type: Filter by channel type (department, team, project)
    - active_only: Boolean to show only active channels (default True)
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']
        channel_type = request.args.get('type')
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        # Get all channels the user is a member of
        query = db.session.query(Channel).join(
            ChannelMember,
            Channel.id == ChannelMember.channel_id
        ).filter(
            ChannelMember.user_id == current_user_id
        )

        if channel_type:
            query = query.filter(Channel.channel_type == channel_type)

        if active_only:
            query = query.filter(Channel.is_active == True)

        channels = query.order_by(Channel.created_date.desc()).all()

        return jsonify({
            'channels': [c.to_dict(include_members=False) for c in channels]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching channels: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch channels'}), 500


@channels_bp.route('/<int:channel_id>', methods=['GET'])
@jwt_required
def get_channel(channel_id):
    """
    Get detailed information about a specific channel.
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Verify user is a member
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id
        ).first()

        if not membership:
            return jsonify({'error': 'Access denied'}), 403

        channel = Channel.query.get(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        return jsonify({
            'channel': channel.to_dict(include_members=True)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching channel {channel_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch channel'}), 500


@channels_bp.route('', methods=['POST'])
@jwt_required
def create_channel():
    """
    Create a new channel.
    Required: name, channel_type
    Optional: description, department
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']
        data = request.get_json()

        name = data.get('name')
        channel_type = data.get('channel_type', 'department')
        description = data.get('description', '')
        department = data.get('department')

        if not name:
            return jsonify({'error': 'Channel name is required'}), 400

        # Check if channel name already exists
        existing = Channel.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': 'Channel name already exists'}), 409

        # Create channel
        new_channel = Channel(
            name=name,
            description=description,
            channel_type=channel_type,
            department=department,
            created_by=current_user_id
        )
        db.session.add(new_channel)
        db.session.flush()  # Get the channel ID

        # Add creator as admin member
        creator_membership = ChannelMember(
            channel_id=new_channel.id,
            user_id=current_user_id,
            role='admin'
        )
        db.session.add(creator_membership)
        db.session.commit()

        logger.info(f"Channel created", extra={
            "channel_id": new_channel.id,
            "channel_name": name,
            "created_by": current_user_id
        })

        return jsonify({
            'message': 'Channel created successfully',
            'channel': new_channel.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating channel: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to create channel'}), 500


@channels_bp.route('/<int:channel_id>', methods=['PUT'])
@jwt_required
def update_channel(channel_id):
    """
    Update channel information (admin only).
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']
        data = request.get_json()

        # Check if user is admin of the channel
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id,
            role='admin'
        ).first()

        if not membership:
            return jsonify({'error': 'Admin access required'}), 403

        channel = Channel.query.get(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        # Update fields
        if 'name' in data and data['name']:
            # Check for duplicate names
            existing = Channel.query.filter(
                Channel.name == data['name'],
                Channel.id != channel_id
            ).first()
            if existing:
                return jsonify({'error': 'Channel name already exists'}), 409
            channel.name = data['name']

        if 'description' in data:
            channel.description = data['description']

        if 'channel_type' in data:
            channel.channel_type = data['channel_type']

        if 'department' in data:
            channel.department = data['department']

        if 'is_active' in data:
            channel.is_active = data['is_active']

        db.session.commit()

        logger.info(f"Channel updated", extra={
            "channel_id": channel_id,
            "updated_by": current_user_id
        })

        return jsonify({
            'message': 'Channel updated successfully',
            'channel': channel.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating channel: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update channel'}), 500


@channels_bp.route('/<int:channel_id>', methods=['DELETE'])
@jwt_required
def delete_channel(channel_id):
    """
    Delete a channel (admin only).
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Check if user is admin of the channel
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id,
            role='admin'
        ).first()

        if not membership:
            return jsonify({'error': 'Admin access required'}), 403

        channel = Channel.query.get(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        db.session.delete(channel)
        db.session.commit()

        logger.info(f"Channel deleted", extra={
            "channel_id": channel_id,
            "deleted_by": current_user_id
        })

        return jsonify({'message': 'Channel deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting channel: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to delete channel'}), 500


# === Channel Members ===

@channels_bp.route('/<int:channel_id>/members', methods=['GET'])
@jwt_required
def get_channel_members(channel_id):
    """
    Get all members of a channel.
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Verify user is a member
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id
        ).first()

        if not membership:
            return jsonify({'error': 'Access denied'}), 403

        members = ChannelMember.query.filter_by(channel_id=channel_id).all()

        return jsonify({
            'members': [m.to_dict() for m in members]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching channel members: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch members'}), 500


@channels_bp.route('/<int:channel_id>/members', methods=['POST'])
@jwt_required
def add_channel_member(channel_id):
    """
    Add a member to a channel (admin/moderator only).
    Required: user_id
    Optional: role (default: member)
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']
        data = request.get_json()

        user_id = data.get('user_id')
        role = data.get('role', 'member')

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Check if current user has permission (admin or moderator)
        permission = ChannelMember.query.filter(
            ChannelMember.channel_id == channel_id,
            ChannelMember.user_id == current_user_id,
            ChannelMember.role.in_(['admin', 'moderator'])
        ).first()

        if not permission:
            return jsonify({'error': 'Permission denied'}), 403

        # Check if user is already a member
        existing = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=user_id
        ).first()

        if existing:
            return jsonify({'error': 'User is already a member'}), 409

        # Add member
        new_member = ChannelMember(
            channel_id=channel_id,
            user_id=user_id,
            role=role
        )
        db.session.add(new_member)
        db.session.commit()

        logger.info(f"Member added to channel", extra={
            "channel_id": channel_id,
            "user_id": user_id,
            "role": role,
            "added_by": current_user_id
        })

        return jsonify({
            'message': 'Member added successfully',
            'member': new_member.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding channel member: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to add member'}), 500


@channels_bp.route('/<int:channel_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required
def remove_channel_member(channel_id, user_id):
    """
    Remove a member from a channel (admin only, or user removing themselves).
    """
    try:
        current_user_payload = JWTManager.get_current_user()
        current_user_id = current_user_payload['user_id']

        # Check permissions
        is_admin = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id,
            role='admin'
        ).first()

        is_self = (current_user_id == user_id)

        if not (is_admin or is_self):
            return jsonify({'error': 'Permission denied'}), 403

        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=user_id
        ).first()

        if not membership:
            return jsonify({'error': 'Member not found'}), 404

        db.session.delete(membership)
        db.session.commit()

        logger.info(f"Member removed from channel", extra={
            "channel_id": channel_id,
            "user_id": user_id,
            "removed_by": current_user_id
        })

        return jsonify({'message': 'Member removed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing channel member: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to remove member'}), 500


# === Channel Messages ===

@channels_bp.route('/<int:channel_id>/messages', methods=['GET'])
@jwt_required
def get_channel_messages(channel_id):
    """
    Get messages from a channel.
    Query params:
    - limit: Number of messages to return (default 50)
    - offset: Pagination offset (default 0)
    - since: ISO timestamp to get messages after this time
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Verify user is a member
        membership = ChannelMember.query.filter_by(
            channel_id=channel_id,
            user_id=current_user_id
        ).first()

        if not membership:
            return jsonify({'error': 'Access denied'}), 403

        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        since = request.args.get('since')

        query = ChannelMessage.query.filter_by(
            channel_id=channel_id,
            is_deleted=False
        )

        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                query = query.filter(ChannelMessage.sent_date > since_dt)
            except ValueError:
                return jsonify({'error': 'Invalid since timestamp'}), 400

        messages = query.order_by(
            ChannelMessage.sent_date.desc()
        ).limit(limit).offset(offset).all()

        # Update last read message for user
        if messages:
            membership.last_read_message_id = messages[0].id
            db.session.commit()

        return jsonify({
            'messages': [m.to_dict(include_reactions=True, include_attachments=True) for m in reversed(messages)],
            'count': len(messages),
            'offset': offset,
            'limit': limit
        }), 200

    except Exception as e:
        logger.error(f"Error fetching channel messages: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch messages'}), 500


@channels_bp.route('/<int:channel_id>/messages/<int:message_id>', methods=['DELETE'])
@jwt_required
def delete_channel_message(channel_id, message_id):
    """
    Delete a channel message (sender, moderator, or admin only).
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        message = ChannelMessage.query.filter_by(
            id=message_id,
            channel_id=channel_id
        ).first()

        if not message:
            return jsonify({'error': 'Message not found'}), 404

        # Check permissions
        is_sender = (message.sender_id == current_user_id)
        is_mod_or_admin = ChannelMember.query.filter(
            ChannelMember.channel_id == channel_id,
            ChannelMember.user_id == current_user_id,
            ChannelMember.role.in_(['admin', 'moderator'])
        ).first()

        if not (is_sender or is_mod_or_admin):
            return jsonify({'error': 'Permission denied'}), 403

        # Mark as deleted instead of actually deleting (soft delete)
        message.is_deleted = True
        message.message = "[Message deleted]"
        db.session.commit()

        logger.info(f"Channel message deleted", extra={
            "message_id": message_id,
            "channel_id": channel_id,
            "deleted_by": current_user_id
        })

        return jsonify({'message': 'Message deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting message: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to delete message'}), 500


def register_channels_routes(app):
    """
    Register channel routes with the Flask app.
    """
    app.register_blueprint(channels_bp)
    logger.info("Channel routes registered")
