"""
API routes for message search and filtering.
Provides full-text search across all messages with advanced filters.
"""
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import or_, and_, func

from auth import jwt_required
from auth.jwt_manager import JWTManager
from models import db, User
from models_messaging import (
    Channel, ChannelMember, ChannelMessage,
    MessageAttachment
)
from models_kits import KitMessage

logger = logging.getLogger(__name__)

search_bp = Blueprint('message_search', __name__, url_prefix='/api/messages/search')


@search_bp.route('', methods=['GET'])
@jwt_required
def search_messages():
    """
    Full-text search across all messages accessible to the user.

    Query parameters:
    - q: Search query (required)
    - type: Message type filter ('kit', 'channel', 'all') - default: 'all'
    - sender: Filter by sender user ID
    - channel_id: Filter by channel ID
    - kit_id: Filter by kit ID
    - has_attachments: Boolean filter for messages with attachments
    - from_date: Start date (ISO format)
    - to_date: End date (ISO format)
    - limit: Number of results (default 50, max 100)
    - offset: Pagination offset (default 0)
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Get search query
        search_query = request.args.get('q', '').strip()
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400

        # Get filters
        message_type = request.args.get('type', 'all')
        sender_id = request.args.get('sender')
        channel_id = request.args.get('channel_id')
        kit_id = request.args.get('kit_id')
        has_attachments = request.args.get('has_attachments', '').lower() == 'true'
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        results = []

        # Search kit messages
        if message_type in ['kit', 'all']:
            kit_query = KitMessage.query.filter(
                or_(
                    KitMessage.sender_id == current_user_id,
                    KitMessage.recipient_id == current_user_id
                )
            ).filter(
                or_(
                    KitMessage.subject.ilike(f'%{search_query}%'),
                    KitMessage.message.ilike(f'%{search_query}%')
                )
            )

            # Apply filters
            if sender_id:
                kit_query = kit_query.filter(KitMessage.sender_id == sender_id)
            if kit_id:
                kit_query = kit_query.filter(KitMessage.kit_id == kit_id)
            if from_date:
                try:
                    from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                    kit_query = kit_query.filter(KitMessage.sent_date >= from_dt)
                except ValueError:
                    pass
            if to_date:
                try:
                    to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                    kit_query = kit_query.filter(KitMessage.sent_date <= to_dt)
                except ValueError:
                    pass
            if has_attachments:
                kit_query = kit_query.filter(KitMessage.attachments.isnot(None))

            kit_messages = kit_query.order_by(KitMessage.sent_date.desc()).limit(limit).all()

            for msg in kit_messages:
                results.append({
                    'type': 'kit',
                    'id': msg.id,
                    'subject': msg.subject,
                    'message': msg.message,
                    'sender_id': msg.sender_id,
                    'sender_name': msg.sender.name if msg.sender else None,
                    'recipient_id': msg.recipient_id,
                    'recipient_name': msg.recipient.name if msg.recipient else None,
                    'sent_date': msg.sent_date.isoformat() if msg.sent_date else None,
                    'is_read': msg.is_read,
                    'kit_id': msg.kit_id,
                    'kit_name': msg.kit.name if msg.kit else None,
                    'has_attachments': bool(msg.attachments)
                })

        # Search channel messages
        if message_type in ['channel', 'all']:
            # Get channels user is a member of
            member_channel_ids = db.session.query(ChannelMember.channel_id).filter(
                ChannelMember.user_id == current_user_id
            ).all()
            member_channel_ids = [c[0] for c in member_channel_ids]

            if member_channel_ids:
                channel_query = ChannelMessage.query.filter(
                    ChannelMessage.channel_id.in_(member_channel_ids),
                    ChannelMessage.is_deleted == False,
                    ChannelMessage.message.ilike(f'%{search_query}%')
                )

                # Apply filters
                if sender_id:
                    channel_query = channel_query.filter(ChannelMessage.sender_id == sender_id)
                if channel_id:
                    channel_query = channel_query.filter(ChannelMessage.channel_id == channel_id)
                if from_date:
                    try:
                        from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                        channel_query = channel_query.filter(ChannelMessage.sent_date >= from_dt)
                    except ValueError:
                        pass
                if to_date:
                    try:
                        to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                        channel_query = channel_query.filter(ChannelMessage.sent_date <= to_dt)
                    except ValueError:
                        pass
                if has_attachments:
                    # Join with attachments table
                    channel_query = channel_query.join(
                        MessageAttachment,
                        MessageAttachment.channel_message_id == ChannelMessage.id
                    )

                channel_messages = channel_query.order_by(
                    ChannelMessage.sent_date.desc()
                ).limit(limit).all()

                for msg in channel_messages:
                    # Get attachment count
                    attachment_count = MessageAttachment.query.filter_by(
                        channel_message_id=msg.id
                    ).count()

                    results.append({
                        'type': 'channel',
                        'id': msg.id,
                        'message': msg.message,
                        'sender_id': msg.sender_id,
                        'sender_name': msg.sender.name if msg.sender else None,
                        'sent_date': msg.sent_date.isoformat() if msg.sent_date else None,
                        'channel_id': msg.channel_id,
                        'channel_name': msg.channel.name if msg.channel else None,
                        'has_attachments': attachment_count > 0,
                        'attachment_count': attachment_count
                    })

        # Sort all results by date
        results.sort(key=lambda x: x.get('sent_date', ''), reverse=True)

        # Apply pagination
        paginated_results = results[offset:offset + limit]

        return jsonify({
            'results': paginated_results,
            'total': len(results),
            'limit': limit,
            'offset': offset,
            'query': search_query
        }), 200

    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to search messages'}), 500


@search_bp.route('/senders', methods=['GET'])
@jwt_required
def get_message_senders():
    """
    Get list of users who have sent messages to the current user.
    Useful for sender filter dropdown.
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Get kit message senders
        kit_senders = db.session.query(
            User.id, User.name
        ).join(
            KitMessage, KitMessage.sender_id == User.id
        ).filter(
            or_(
                KitMessage.recipient_id == current_user_id,
                KitMessage.sender_id == current_user_id
            )
        ).distinct().all()

        # Get channel message senders from user's channels
        member_channel_ids = db.session.query(ChannelMember.channel_id).filter(
            ChannelMember.user_id == current_user_id
        ).all()
        member_channel_ids = [c[0] for c in member_channel_ids]

        channel_senders = []
        if member_channel_ids:
            channel_senders = db.session.query(
                User.id, User.name
            ).join(
                ChannelMessage, ChannelMessage.sender_id == User.id
            ).filter(
                ChannelMessage.channel_id.in_(member_channel_ids)
            ).distinct().all()

        # Combine and deduplicate
        all_senders = {}
        for user_id, name in kit_senders + channel_senders:
            all_senders[user_id] = name

        senders = [
            {'id': user_id, 'name': name}
            for user_id, name in sorted(all_senders.items(), key=lambda x: x[1])
        ]

        return jsonify({'senders': senders}), 200

    except Exception as e:
        logger.error(f"Error fetching message senders: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch senders'}), 500


@search_bp.route('/stats', methods=['GET'])
@jwt_required
def get_message_stats():
    """
    Get message statistics for the current user.
    Returns counts of total, unread, sent, and received messages.
    """
    try:
        user_payload = JWTManager.get_current_user()
        current_user_id = user_payload['user_id']

        # Kit message stats
        kit_received = KitMessage.query.filter_by(recipient_id=current_user_id).count()
        kit_unread = KitMessage.query.filter_by(
            recipient_id=current_user_id,
            is_read=False
        ).count()
        kit_sent = KitMessage.query.filter_by(sender_id=current_user_id).count()

        # Channel message stats
        member_channel_ids = db.session.query(ChannelMember.channel_id).filter(
            ChannelMember.user_id == current_user_id
        ).all()
        member_channel_ids = [c[0] for c in member_channel_ids]

        channel_total = 0
        channel_unread = 0
        if member_channel_ids:
            channel_total = ChannelMessage.query.filter(
                ChannelMessage.channel_id.in_(member_channel_ids),
                ChannelMessage.is_deleted == False
            ).count()

            # Calculate unread by comparing last_read_message_id
            for channel_id in member_channel_ids:
                membership = ChannelMember.query.filter_by(
                    channel_id=channel_id,
                    user_id=current_user_id
                ).first()

                if membership and membership.last_read_message_id:
                    unread_count = ChannelMessage.query.filter(
                        ChannelMessage.channel_id == channel_id,
                        ChannelMessage.id > membership.last_read_message_id,
                        ChannelMessage.is_deleted == False
                    ).count()
                    channel_unread += unread_count
                else:
                    # All messages unread
                    channel_unread += ChannelMessage.query.filter(
                        ChannelMessage.channel_id == channel_id,
                        ChannelMessage.is_deleted == False
                    ).count()

        return jsonify({
            'kit_messages': {
                'received': kit_received,
                'unread': kit_unread,
                'sent': kit_sent,
                'total': kit_received + kit_sent
            },
            'channel_messages': {
                'total': channel_total,
                'unread': channel_unread
            },
            'totals': {
                'all_messages': kit_received + kit_sent + channel_total,
                'unread': kit_unread + channel_unread
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching message stats: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch message stats'}), 500


def register_message_search_routes(app):
    """
    Register message search routes with the Flask app.
    """
    app.register_blueprint(search_bp)
    logger.info("Message search routes registered")
