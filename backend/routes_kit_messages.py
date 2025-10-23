"""
Routes for Kit Messaging System

This module provides API endpoints for messaging between mechanics and stores personnel.
"""

from flask import request, jsonify
from models import db, AuditLog
from models_kits import Kit, KitMessage
from datetime import datetime
from auth import jwt_required
from utils.error_handler import handle_errors, ValidationError
import logging

logger = logging.getLogger(__name__)


def register_kit_message_routes(app):
    """Register all kit message routes"""

    @app.route('/api/kits/<int:kit_id>/messages', methods=['POST'])
    @jwt_required
    @handle_errors
    def send_kit_message(kit_id):
        """Send a message related to a kit"""
        kit = Kit.query.get_or_404(kit_id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get('subject'):
            raise ValidationError('Subject is required')
        if not data.get('message'):
            raise ValidationError('Message is required')

        # Create message
        message = KitMessage(
            kit_id=kit_id,
            related_request_id=data.get('related_request_id'),
            sender_id=request.current_user['user_id'],
            recipient_id=data.get('recipient_id'),
            subject=data['subject'],
            message=data['message'],
            parent_message_id=data.get('parent_message_id'),
            attachments=data.get('attachments'),
            is_read=False
        )

        db.session.add(message)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_message_sent',
            action_details=f'Message sent for kit {kit.name}: {message.subject}'
        )
        db.session.add(log)
        db.session.commit()

        logger.info(f"Message sent: ID {message.id}")
        return jsonify(message.to_dict()), 201

    @app.route('/api/kits/<int:kit_id>/messages', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_kit_messages(kit_id):
        """Get all messages for a kit"""
        Kit.query.get_or_404(kit_id)

        # Optional filtering
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        related_request_id = request.args.get('related_request_id', type=int)

        query = KitMessage.query.filter_by(kit_id=kit_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        if related_request_id:
            query = query.filter_by(related_request_id=related_request_id)

        # Filter by user - show messages sent by or to the current user
        user_id = request.current_user['user_id']
        query = query.filter(
            db.or_(
                KitMessage.sender_id == user_id,
                KitMessage.recipient_id == user_id,
                KitMessage.recipient_id.is_(None)  # Broadcast messages
            )
        )

        messages = query.order_by(KitMessage.sent_date.desc()).all()

        return jsonify([msg.to_dict() for msg in messages]), 200

    @app.route('/api/messages', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_user_messages():
        """Get all messages for the current user"""
        user_id = request.current_user['user_id']

        # Optional filtering
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        sent = request.args.get('sent', 'false').lower() == 'true'

        if sent:
            # Messages sent by user
            query = KitMessage.query.filter_by(sender_id=user_id)
        else:
            # Messages received by user
            query = KitMessage.query.filter(
                db.or_(
                    KitMessage.recipient_id == user_id,
                    KitMessage.recipient_id.is_(None)  # Broadcast messages
                )
            )

        if unread_only:
            query = query.filter_by(is_read=False)

        messages = query.order_by(KitMessage.sent_date.desc()).all()

        return jsonify([msg.to_dict() for msg in messages]), 200

    @app.route('/api/messages/<int:id>', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_message(id):
        """Get message details"""
        message = KitMessage.query.get_or_404(id)

        # Verify user has access to this message
        user_id = request.current_user['user_id']
        if message.sender_id != user_id and message.recipient_id != user_id and message.recipient_id is not None:
            raise ValidationError('You do not have access to this message')

        return jsonify(message.to_dict(include_replies=True)), 200

    @app.route('/api/messages/<int:id>/read', methods=['PUT'])
    @jwt_required
    @handle_errors
    def mark_message_read(id):
        """Mark a message as read"""
        message = KitMessage.query.get_or_404(id)

        # Verify user is the recipient
        user_id = request.current_user['user_id']
        if message.recipient_id != user_id and message.recipient_id is not None:
            raise ValidationError('You can only mark your own messages as read')

        if not message.is_read:
            message.is_read = True
            message.read_date = datetime.now()
            db.session.commit()

        return jsonify(message.to_dict()), 200

    @app.route('/api/messages/<int:id>/reply', methods=['POST'])
    @jwt_required
    @handle_errors
    def reply_to_message(id):
        """Reply to a message"""
        parent_message = KitMessage.query.get_or_404(id)
        data = request.get_json() or {}

        # Validate required fields
        if not data.get('message'):
            raise ValidationError('Message is required')

        # Determine recipient (reply to sender of parent message)
        recipient_id = parent_message.sender_id
        if recipient_id == request.current_user['user_id']:
            # If replying to own message, send to original recipient
            recipient_id = parent_message.recipient_id

        # Create reply
        reply = KitMessage(
            kit_id=parent_message.kit_id,
            related_request_id=parent_message.related_request_id,
            sender_id=request.current_user['user_id'],
            recipient_id=recipient_id,
            subject=f"Re: {parent_message.subject}",
            message=data['message'],
            parent_message_id=id,
            attachments=data.get('attachments'),
            is_read=False
        )

        db.session.add(reply)
        db.session.commit()

        # Log action
        log = AuditLog(
            action_type='kit_message_reply',
            action_details=f'Reply sent to message ID {id}'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(reply.to_dict()), 201

    @app.route('/api/messages/unread-count', methods=['GET'])
    @jwt_required
    @handle_errors
    def get_unread_count():
        """Get count of unread messages for current user"""
        user_id = request.current_user['user_id']

        count = KitMessage.query.filter(
            db.or_(
                KitMessage.recipient_id == user_id,
                KitMessage.recipient_id.is_(None)
            ),
            KitMessage.is_read.is_(False)
        ).count()

        return jsonify({'unread_count': count}), 200

    @app.route('/api/messages/<int:id>', methods=['DELETE'])
    @jwt_required
    @handle_errors
    def delete_message(id):
        """Delete a message (soft delete by marking as deleted)"""
        message = KitMessage.query.get_or_404(id)

        # Verify user is sender or recipient
        user_id = request.current_user['user_id']
        if message.sender_id != user_id and message.recipient_id != user_id:
            raise ValidationError('You can only delete your own messages')

        # For now, just delete the message
        # In production, you might want to implement soft delete
        db.session.delete(message)
        db.session.commit()

        return jsonify({'message': 'Message deleted successfully'}), 200
