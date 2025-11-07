"""
API routes for message attachments - upload, download, and management.
"""
import logging
import os
import secrets
from datetime import datetime, UTC
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from PIL import Image
from werkzeug.utils import secure_filename

from models import db
from models_messaging import MessageAttachment, AttachmentDownload
from models_kits import KitMessage
from utils.file_validation import (
    FileValidationError,
    validate_file_upload,
    get_file_type,
    scan_file_for_malware
)

logger = logging.getLogger(__name__)

attachments_bp = Blueprint('attachments', __name__, url_prefix='/api/attachments')

# Configuration
UPLOAD_FOLDER = os.environ.get('ATTACHMENTS_FOLDER', '/tmp/supplyline_attachments')
THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'},
    'spreadsheets': {'xls', 'xlsx', 'csv', 'ods'},
    'archives': {'zip', 'tar', 'gz', '7z'},
}
THUMBNAIL_SIZE = (300, 300)

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    all_extensions = set()
    for category in ALLOWED_EXTENSIONS.values():
        all_extensions.update(category)
    return ext in all_extensions


def get_file_extension(filename):
    """Get file extension"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent collisions"""
    ext = get_file_extension(original_filename)
    unique_id = secrets.token_urlsafe(16)
    timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}" if ext else f"{timestamp}_{unique_id}"


def create_thumbnail(image_path, thumbnail_path):
    """
    Create a thumbnail for an image.
    Returns True if successful, False otherwise.
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Create thumbnail
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        logger.error(f"Error creating thumbnail: {str(e)}", exc_info=True)
        return False


@attachments_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_attachment():
    """
    Upload a file attachment for a message.
    Required form data:
    - file: The file to upload
    - message_type: 'kit' or 'channel'
    - message_id: ID of the message (optional, for adding to existing message)

    Returns attachment metadata.
    """
    try:
        current_user_id = get_jwt_identity()

        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        message_type = request.form.get('message_type')
        message_id = request.form.get('message_id')

        if message_type not in ['kit', 'channel']:
            return jsonify({'error': 'Invalid message type'}), 400

        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Save file
        file.save(file_path)

        # Validate file content (magic bytes, MIME type)
        try:
            validate_file_upload(file_path, max_size=MAX_FILE_SIZE)
        except FileValidationError as e:
            os.remove(file_path)
            return jsonify({'error': str(e)}), 400

        # Determine file type
        file_type = get_file_type(file_path)

        # Get MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Create thumbnail for images
        thumbnail_path = None
        if file_type == 'image':
            thumbnail_filename = f"thumb_{unique_filename}"
            thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_filename)
            if create_thumbnail(file_path, thumbnail_path):
                thumbnail_path = f"thumbnails/{thumbnail_filename}"
            else:
                thumbnail_path = None

        # Scan file for malware (basic check)
        is_scanned = True
        scan_result = 'clean'
        try:
            scan_file_for_malware(file_path)
        except Exception as e:
            logger.warning(f"File scan failed: {str(e)}")
            scan_result = 'not_scanned'

        # Create attachment record
        attachment = MessageAttachment(
            kit_message_id=int(message_id) if message_type == 'kit' and message_id else None,
            channel_message_id=int(message_id) if message_type == 'channel' and message_id else None,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_type=file_type,
            thumbnail_path=thumbnail_path,
            uploaded_by=current_user_id,
            is_scanned=is_scanned,
            scan_result=scan_result
        )
        db.session.add(attachment)
        db.session.commit()

        logger.info(f"File uploaded successfully", extra={
            "attachment_id": attachment.id,
            "filename": original_filename,
            "file_type": file_type,
            "file_size": file_size,
            "uploaded_by": current_user_id
        })

        return jsonify({
            'message': 'File uploaded successfully',
            'attachment': attachment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to upload file'}), 500


@attachments_bp.route('/<int:attachment_id>/download', methods=['GET'])
@jwt_required()
def download_attachment(attachment_id):
    """
    Download an attachment file.
    Tracks download in the database.
    """
    try:
        current_user_id = get_jwt_identity()

        attachment = MessageAttachment.query.get(attachment_id)
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        # Verify user has access to the message
        has_access = False
        if attachment.kit_message_id:
            message = KitMessage.query.get(attachment.kit_message_id)
            if message and (message.sender_id == current_user_id or message.recipient_id == current_user_id):
                has_access = True
        elif attachment.channel_message_id:
            # Check if user is a member of the channel
            from models_messaging import ChannelMessage, ChannelMember
            message = ChannelMessage.query.get(attachment.channel_message_id)
            if message:
                membership = ChannelMember.query.filter_by(
                    channel_id=message.channel_id,
                    user_id=current_user_id
                ).first()
                if membership:
                    has_access = True

        if not has_access:
            return jsonify({'error': 'Access denied'}), 403

        # Check if file exists
        if not os.path.exists(attachment.file_path):
            logger.error(f"Attachment file not found on disk", extra={
                "attachment_id": attachment_id,
                "file_path": attachment.file_path
            })
            return jsonify({'error': 'File not found on server'}), 404

        # Track download
        download_record = AttachmentDownload(
            attachment_id=attachment_id,
            user_id=current_user_id,
            ip_address=request.remote_addr
        )
        db.session.add(download_record)

        # Increment download count
        attachment.download_count += 1
        db.session.commit()

        logger.info(f"Attachment downloaded", extra={
            "attachment_id": attachment_id,
            "user_id": current_user_id,
            "download_count": attachment.download_count
        })

        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.original_filename,
            mimetype=attachment.mime_type
        )

    except Exception as e:
        logger.error(f"Error downloading attachment: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to download file'}), 500


@attachments_bp.route('/<int:attachment_id>/thumbnail', methods=['GET'])
@jwt_required()
def get_thumbnail(attachment_id):
    """
    Get thumbnail for an image attachment.
    """
    try:
        current_user_id = get_jwt_identity()

        attachment = MessageAttachment.query.get(attachment_id)
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        if attachment.file_type != 'image' or not attachment.thumbnail_path:
            return jsonify({'error': 'Thumbnail not available'}), 404

        # Verify user has access (same logic as download)
        has_access = False
        if attachment.kit_message_id:
            message = KitMessage.query.get(attachment.kit_message_id)
            if message and (message.sender_id == current_user_id or message.recipient_id == current_user_id):
                has_access = True
        elif attachment.channel_message_id:
            from models_messaging import ChannelMessage, ChannelMember
            message = ChannelMessage.query.get(attachment.channel_message_id)
            if message:
                membership = ChannelMember.query.filter_by(
                    channel_id=message.channel_id,
                    user_id=current_user_id
                ).first()
                if membership:
                    has_access = True

        if not has_access:
            return jsonify({'error': 'Access denied'}), 403

        thumbnail_full_path = os.path.join(UPLOAD_FOLDER, attachment.thumbnail_path)
        if not os.path.exists(thumbnail_full_path):
            return jsonify({'error': 'Thumbnail not found'}), 404

        return send_file(thumbnail_full_path, mimetype='image/jpeg')

    except Exception as e:
        logger.error(f"Error getting thumbnail: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get thumbnail'}), 500


@attachments_bp.route('/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(attachment_id):
    """
    Delete an attachment (uploader or message sender only).
    """
    try:
        current_user_id = get_jwt_identity()

        attachment = MessageAttachment.query.get(attachment_id)
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        # Check if user is the uploader or message sender
        is_uploader = (attachment.uploaded_by == current_user_id)
        is_message_sender = False

        if attachment.kit_message_id:
            message = KitMessage.query.get(attachment.kit_message_id)
            if message and message.sender_id == current_user_id:
                is_message_sender = True
        elif attachment.channel_message_id:
            from models_messaging import ChannelMessage
            message = ChannelMessage.query.get(attachment.channel_message_id)
            if message and message.sender_id == current_user_id:
                is_message_sender = True

        if not (is_uploader or is_message_sender):
            return jsonify({'error': 'Permission denied'}), 403

        # Delete files from disk
        try:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
            if attachment.thumbnail_path:
                thumbnail_full_path = os.path.join(UPLOAD_FOLDER, attachment.thumbnail_path)
                if os.path.exists(thumbnail_full_path):
                    os.remove(thumbnail_full_path)
        except Exception as e:
            logger.warning(f"Error deleting files from disk: {str(e)}")

        # Delete database record
        db.session.delete(attachment)
        db.session.commit()

        logger.info(f"Attachment deleted", extra={
            "attachment_id": attachment_id,
            "deleted_by": current_user_id
        })

        return jsonify({'message': 'Attachment deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting attachment: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to delete attachment'}), 500


@attachments_bp.route('/<int:attachment_id>/info', methods=['GET'])
@jwt_required()
def get_attachment_info(attachment_id):
    """
    Get detailed information about an attachment.
    """
    try:
        current_user_id = get_jwt_identity()

        attachment = MessageAttachment.query.get(attachment_id)
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        # Verify access
        has_access = False
        if attachment.kit_message_id:
            message = KitMessage.query.get(attachment.kit_message_id)
            if message and (message.sender_id == current_user_id or message.recipient_id == current_user_id):
                has_access = True
        elif attachment.channel_message_id:
            from models_messaging import ChannelMessage, ChannelMember
            message = ChannelMessage.query.get(attachment.channel_message_id)
            if message:
                membership = ChannelMember.query.filter_by(
                    channel_id=message.channel_id,
                    user_id=current_user_id
                ).first()
                if membership:
                    has_access = True

        if not has_access:
            return jsonify({'error': 'Access denied'}), 403

        return jsonify({
            'attachment': attachment.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error getting attachment info: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get attachment info'}), 500


def register_attachments_routes(app):
    """
    Register attachment routes with the Flask app.
    """
    app.register_blueprint(attachments_bp)
    logger.info("Attachment routes registered")
