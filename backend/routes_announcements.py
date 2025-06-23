from flask import request, jsonify, session
from models import db, Announcement, AnnouncementRead, AuditLog, UserActivity
from datetime import datetime, timezone
from functools import wraps
from utils.error_handler import log_security_event
from auth import admin_required
import logging

logger = logging.getLogger(__name__)


def register_announcement_routes(app):
    # Get all announcements
    @app.route('/api/announcements', methods=['GET'])
    def get_announcements():
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get filter parameters
            priority = request.args.get('priority')
            active_only = request.args.get('active_only', 'true').lower() == 'true'

            # Start with base query
            query = Announcement.query

            # Apply filters if provided
            if priority:
                query = query.filter(Announcement.priority == priority)

            if active_only:
                # Only show active announcements that haven't expired
                now = datetime.now(timezone.utc)
                query = query.filter(Announcement.is_active.is_(True))
                query = query.filter((Announcement.expiration_date.is_(None)) | (Announcement.expiration_date > now))

            # Order by created_at (newest first)
            query = query.order_by(Announcement.created_at.desc())

            # Get total count for pagination
            total = query.count()

            # Apply pagination
            announcements = query.offset(offset).limit(limit).all()

            # Check if user is logged in to determine read status
            user_id = session.get('user_id')

            read_map = {}
            if user_id:
                read_map = {
                    r.announcement_id: r for r in
                    AnnouncementRead.query
                        .filter_by(user_id=user_id)
                        .filter(AnnouncementRead.announcement_id.in_([a.id for a in announcements]))
                        .all()
                }

            result = []
            for announcement in announcements:
                announcement_dict = announcement.to_dict()

                if user_id:
                    read = read_map.get(announcement.id)
                    announcement_dict['read'] = read is not None
                    if read:
                        announcement_dict['read_at'] = read.read_at.isoformat()

                result.append(announcement_dict)

            return jsonify({
                'announcements': result,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit  # Ceiling division
            }), 200

        except Exception as e:
            print(f"Error getting announcements: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get a specific announcement
    @app.route('/api/announcements/<int:id>', methods=['GET'])
    def get_announcement(id):
        try:
            announcement = Announcement.query.get_or_404(id)

            # Get the announcement data
            announcement_dict = announcement.to_dict()

            # Check if user is logged in
            user_id = session.get('user_id')
            if user_id:
                # Check if user has read this announcement
                read = AnnouncementRead.query.filter_by(
                    announcement_id=announcement.id,
                    user_id=user_id
                ).first()

                announcement_dict['read'] = read is not None
                if read:
                    announcement_dict['read_at'] = read.read_at.isoformat()

            # If admin, include read statistics
            if session.get('is_admin', False):
                announcement_dict['reads'] = [read.to_dict() for read in announcement.reads.all()]
                announcement_dict['read_count'] = announcement.reads.count()

            return jsonify(announcement_dict), 200

        except Exception as e:
            print(f"Error getting announcement: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Create a new announcement (admin only)
    @app.route('/api/announcements', methods=['POST'])
    @admin_required
    def create_announcement():
        try:
            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['title', 'content', 'priority']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Parse expiration date if provided
            expiration_date = None
            if data.get('expiration_date'):
                try:
                    expiration_date = datetime.fromisoformat(data.get('expiration_date').replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'}), 400

            # Create announcement
            announcement = Announcement(
                title=data.get('title'),
                content=data.get('content'),
                priority=data.get('priority'),
                created_by=session['user_id'],
                expiration_date=expiration_date,
                is_active=data.get('is_active', True)
            )

            # Save to database
            db.session.add(announcement)
            db.session.commit()

            # Create audit log
            log = AuditLog(
                action_type='create_announcement',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) created announcement "{announcement.title}" (ID: {announcement.id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='create_announcement',
                description=f'Created announcement "{announcement.title}"',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(announcement.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            print(f"Error creating announcement: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Update an announcement (admin only)
    @app.route('/api/announcements/<int:id>', methods=['PUT'])
    @admin_required
    def update_announcement(id):
        try:
            # Get the announcement
            announcement = Announcement.query.get_or_404(id)

            # Get data from request
            data = request.get_json() or {}

            # Update fields if provided
            if 'title' in data:
                announcement.title = data['title']
            if 'content' in data:
                announcement.content = data['content']
            if 'priority' in data:
                announcement.priority = data['priority']
            if 'is_active' in data:
                announcement.is_active = data['is_active']

            # Parse expiration date if provided
            if 'expiration_date' in data:
                if data['expiration_date']:
                    try:
                        announcement.expiration_date = datetime.fromisoformat(data['expiration_date'].replace('Z', '+00:00'))
                    except ValueError:
                        return jsonify({'error': 'Invalid expiration date format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'}), 400
                else:
                    announcement.expiration_date = None

            # Save changes
            db.session.commit()

            # Create audit log
            log = AuditLog(
                action_type='update_announcement',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) updated announcement "{announcement.title}" (ID: {announcement.id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='update_announcement',
                description=f'Updated announcement "{announcement.title}"',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(announcement.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error updating announcement: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Delete an announcement (admin only)
    @app.route('/api/announcements/<int:id>', methods=['DELETE'])
    @admin_required
    def delete_announcement(id):
        try:
            # Get the announcement
            announcement = Announcement.query.get_or_404(id)

            # Store announcement details for audit log
            announcement_title = announcement.title
            announcement_id = announcement.id

            # Delete all reads first (due to foreign key constraint)
            AnnouncementRead.query.filter_by(announcement_id=id).delete()

            # Delete the announcement
            db.session.delete(announcement)

            # Create audit log
            log = AuditLog(
                action_type='delete_announcement',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) deleted announcement "{announcement_title}" (ID: {announcement_id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='delete_announcement',
                description=f'Deleted announcement "{announcement_title}"',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({'message': 'Announcement deleted successfully'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting announcement: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Mark an announcement as read
    @app.route('/api/announcements/<int:id>/read', methods=['POST'])
    def mark_announcement_read(id):
        try:
            # Check if user is logged in
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401

            # Get the announcement
            announcement = Announcement.query.get_or_404(id)

            # Check if already read
            existing_read = AnnouncementRead.query.filter_by(
                announcement_id=id,
                user_id=session['user_id']
            ).first()

            if existing_read:
                # Already marked as read
                return jsonify({'message': 'Announcement already marked as read'}), 200

            # Create new read record
            read = AnnouncementRead(
                announcement_id=id,
                user_id=session['user_id']
            )

            db.session.add(read)
            db.session.commit()

            return jsonify({'message': 'Announcement marked as read'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error marking announcement as read: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
