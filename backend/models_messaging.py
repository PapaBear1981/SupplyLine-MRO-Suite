"""
Enhanced messaging models for real-time chat features.
Includes channels, message reactions, user presence tracking, and attachment metadata.
"""
from datetime import datetime, UTC

from models import db


def get_current_time():
    """Return current time in UTC"""
    return datetime.now(UTC)


class Channel(db.Model):
    """
    Department-wide or team channels for group messaging.
    """
    __tablename__ = "channels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    channel_type = db.Column(db.String(50), nullable=False, default='department')  # department, team, project
    department = db.Column(db.String(100))  # Department name for department channels
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_date = db.Column(db.DateTime, default=get_current_time, nullable=False)

    # Relationships
    creator = db.relationship("User", back_populates="created_channels")
    members = db.relationship("ChannelMember", back_populates="channel", cascade="all, delete-orphan")
    messages = db.relationship("ChannelMessage", back_populates="channel", cascade="all, delete-orphan")

    def to_dict(self, include_members=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "channel_type": self.channel_type,
            "department": self.department,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "creator_name": self.creator.name if self.creator else None,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "member_count": len(self.members) if hasattr(self, "members") else 0
        }

        if include_members and hasattr(self, "members"):
            data["members"] = [m.to_dict() for m in self.members]

        return data


class ChannelMember(db.Model):
    """
    Tracks channel membership and user roles within channels.
    """
    __tablename__ = "channel_members"

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(50), default='member')  # admin, moderator, member
    joined_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    last_read_message_id = db.Column(db.Integer, db.ForeignKey("channel_messages.id"))
    notifications_enabled = db.Column(db.Boolean, default=True)

    # Relationships
    channel = db.relationship("Channel", back_populates="members")
    user = db.relationship("User", back_populates="channel_memberships")
    last_read_message = db.relationship("ChannelMessage", foreign_keys=[last_read_message_id])

    # Unique constraint to prevent duplicate memberships
    __table_args__ = (
        db.UniqueConstraint('channel_id', 'user_id', name='unique_channel_membership'),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "role": self.role,
            "joined_date": self.joined_date.isoformat() if self.joined_date else None,
            "last_read_message_id": self.last_read_message_id,
            "notifications_enabled": self.notifications_enabled
        }


class ChannelMessage(db.Model):
    """
    Messages sent to channels (group messages).
    """
    __tablename__ = "channel_messages"

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(5000), nullable=False)
    message_type = db.Column(db.String(50), default='text')  # text, system, announcement
    sent_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    edited_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    parent_message_id = db.Column(db.Integer, db.ForeignKey("channel_messages.id"))  # For threading

    # Relationships
    channel = db.relationship("Channel", back_populates="messages")
    sender = db.relationship("User", back_populates="channel_messages")
    parent_message = db.relationship("ChannelMessage", remote_side=[id], backref="replies")
    reactions = db.relationship("MessageReaction", back_populates="channel_message", cascade="all, delete-orphan")
    attachments = db.relationship("MessageAttachment", back_populates="channel_message", cascade="all, delete-orphan")

    def to_dict(self, include_reactions=False, include_attachments=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "channel_id": self.channel_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name if self.sender else None,
            "message": self.message,
            "message_type": self.message_type,
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "edited_date": self.edited_date.isoformat() if self.edited_date else None,
            "is_deleted": self.is_deleted,
            "parent_message_id": self.parent_message_id,
            "reply_count": len(self.replies) if hasattr(self, "replies") else 0
        }

        if include_reactions and hasattr(self, "reactions"):
            data["reactions"] = [r.to_dict() for r in self.reactions]

        if include_attachments and hasattr(self, "attachments"):
            data["attachments"] = [a.to_dict() for a in self.attachments]

        return data


class MessageReaction(db.Model):
    """
    Reactions/acknowledgments for messages (emojis, likes, etc.).
    """
    __tablename__ = "message_reactions"

    id = db.Column(db.Integer, primary_key=True)
    kit_message_id = db.Column(db.Integer, db.ForeignKey("kit_messages.id"))  # For kit messages
    channel_message_id = db.Column(db.Integer, db.ForeignKey("channel_messages.id"))  # For channel messages
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reaction_type = db.Column(db.String(50), nullable=False)  # emoji code or type: thumbs_up, heart, etc.
    created_date = db.Column(db.DateTime, default=get_current_time, nullable=False)

    # Relationships
    kit_message = db.relationship("KitMessage", backref="reactions")
    channel_message = db.relationship("ChannelMessage", back_populates="reactions")
    user = db.relationship("User", back_populates="message_reactions")

    # Unique constraint to prevent duplicate reactions from same user
    __table_args__ = (
        db.CheckConstraint(
            '(kit_message_id IS NOT NULL AND channel_message_id IS NULL) OR '
            '(kit_message_id IS NULL AND channel_message_id IS NOT NULL)',
            name='check_one_message_type'
        ),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "kit_message_id": self.kit_message_id,
            "channel_message_id": self.channel_message_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "reaction_type": self.reaction_type,
            "created_date": self.created_date.isoformat() if self.created_date else None
        }


class MessageAttachment(db.Model):
    """
    Enhanced file attachment metadata for messages.
    Tracks uploads, downloads, and provides file security information.
    """
    __tablename__ = "message_attachments"

    id = db.Column(db.Integer, primary_key=True)
    kit_message_id = db.Column(db.Integer, db.ForeignKey("kit_messages.id"))  # For kit messages
    channel_message_id = db.Column(db.Integer, db.ForeignKey("channel_messages.id"))  # For channel messages
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, pdf, document, spreadsheet, other
    thumbnail_path = db.Column(db.String(500))  # For image thumbnails
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    download_count = db.Column(db.Integer, default=0, nullable=False)
    is_scanned = db.Column(db.Boolean, default=False)  # Security scan status
    scan_result = db.Column(db.String(50))  # clean, suspicious, malicious

    # Relationships
    kit_message = db.relationship("KitMessage", backref="attachment_files")
    channel_message = db.relationship("ChannelMessage", back_populates="attachments")
    uploader = db.relationship("User", back_populates="uploaded_attachments")
    download_history = db.relationship("AttachmentDownload", back_populates="attachment", cascade="all, delete-orphan")

    # Constraint to ensure attachment belongs to one message type
    __table_args__ = (
        db.CheckConstraint(
            '(kit_message_id IS NOT NULL AND channel_message_id IS NULL) OR '
            '(kit_message_id IS NULL AND channel_message_id IS NOT NULL)',
            name='check_attachment_message_type'
        ),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "kit_message_id": self.kit_message_id,
            "channel_message_id": self.channel_message_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_type": self.file_type,
            "thumbnail_path": self.thumbnail_path,
            "uploaded_by": self.uploaded_by,
            "uploader_name": self.uploader.name if self.uploader else None,
            "uploaded_date": self.uploaded_date.isoformat() if self.uploaded_date else None,
            "download_count": self.download_count,
            "is_scanned": self.is_scanned,
            "scan_result": self.scan_result
        }


class AttachmentDownload(db.Model):
    """
    Tracks when attachments are downloaded by users.
    """
    __tablename__ = "attachment_downloads"

    id = db.Column(db.Integer, primary_key=True)
    attachment_id = db.Column(db.Integer, db.ForeignKey("message_attachments.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    download_date = db.Column(db.DateTime, default=get_current_time, nullable=False)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6

    # Relationships
    attachment = db.relationship("MessageAttachment", back_populates="download_history")
    user = db.relationship("User", back_populates="attachment_downloads")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "attachment_id": self.attachment_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "download_date": self.download_date.isoformat() if self.download_date else None,
            "ip_address": self.ip_address
        }


class UserPresence(db.Model):
    """
    Tracks online/offline status and typing indicators for users.
    """
    __tablename__ = "user_presence"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    is_online = db.Column(db.Boolean, default=False, nullable=False)
    last_seen = db.Column(db.DateTime, default=get_current_time, nullable=False)
    last_activity = db.Column(db.DateTime, default=get_current_time, nullable=False)
    status_message = db.Column(db.String(200))  # Custom status message
    socket_id = db.Column(db.String(100))  # Current WebSocket connection ID

    # Relationships
    user = db.relationship("User", back_populates="presence")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "is_online": self.is_online,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "status_message": self.status_message
        }


class TypingIndicator(db.Model):
    """
    Temporary storage for typing indicators (could also be in-memory/Redis in production).
    """
    __tablename__ = "typing_indicators"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"))  # For channel typing
    kit_id = db.Column(db.Integer, db.ForeignKey("kits.id"))  # For kit message typing
    is_typing = db.Column(db.Boolean, default=True, nullable=False)
    started_typing = db.Column(db.DateTime, default=get_current_time, nullable=False)

    # Relationships
    user = db.relationship("User")
    channel = db.relationship("Channel")

    # Constraint to ensure typing is for one context
    __table_args__ = (
        db.CheckConstraint(
            '(channel_id IS NOT NULL AND kit_id IS NULL) OR '
            '(channel_id IS NULL AND kit_id IS NOT NULL)',
            name='check_typing_context'
        ),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "channel_id": self.channel_id,
            "kit_id": self.kit_id,
            "is_typing": self.is_typing,
            "started_typing": self.started_typing.isoformat() if self.started_typing else None
        }
