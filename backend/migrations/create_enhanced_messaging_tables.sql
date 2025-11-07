-- Enhanced Messaging System Database Migration
-- Creates tables for channels, message reactions, attachments, and user presence
-- Run this migration to enable the Enhanced Messaging features

-- Channels table (department-wide or team messaging)
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500),
    channel_type VARCHAR(50) NOT NULL DEFAULT 'department',
    department VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX idx_channels_type ON channels(channel_type);
CREATE INDEX idx_channels_department ON channels(department);
CREATE INDEX idx_channels_active ON channels(is_active);

-- Channel members table
CREATE TABLE IF NOT EXISTS channel_members (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    last_read_message_id INTEGER,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    UNIQUE(channel_id, user_id)
);

CREATE INDEX idx_channel_members_channel ON channel_members(channel_id);
CREATE INDEX idx_channel_members_user ON channel_members(user_id);

-- Channel messages table
CREATE TABLE IF NOT EXISTS channel_messages (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    message VARCHAR(5000) NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    sent_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    edited_date TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    parent_message_id INTEGER REFERENCES channel_messages(id)
);

CREATE INDEX idx_channel_messages_channel ON channel_messages(channel_id);
CREATE INDEX idx_channel_messages_sender ON channel_messages(sender_id);
CREATE INDEX idx_channel_messages_date ON channel_messages(sent_date DESC);
CREATE INDEX idx_channel_messages_parent ON channel_messages(parent_message_id);

-- Add foreign key for last_read_message_id after channel_messages table exists
ALTER TABLE channel_members
ADD CONSTRAINT fk_channel_members_last_read
FOREIGN KEY (last_read_message_id) REFERENCES channel_messages(id) ON DELETE SET NULL;

-- Message reactions table (supports both kit and channel messages)
CREATE TABLE IF NOT EXISTS message_reactions (
    id SERIAL PRIMARY KEY,
    kit_message_id INTEGER REFERENCES kit_messages(id) ON DELETE CASCADE,
    channel_message_id INTEGER REFERENCES channel_messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reaction_type VARCHAR(50) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT check_one_message_type CHECK (
        (kit_message_id IS NOT NULL AND channel_message_id IS NULL) OR
        (kit_message_id IS NULL AND channel_message_id IS NOT NULL)
    )
);

CREATE INDEX idx_message_reactions_kit ON message_reactions(kit_message_id);
CREATE INDEX idx_message_reactions_channel ON message_reactions(channel_message_id);
CREATE INDEX idx_message_reactions_user ON message_reactions(user_id);
CREATE INDEX idx_message_reactions_type ON message_reactions(reaction_type);

-- Message attachments table (enhanced file metadata)
CREATE TABLE IF NOT EXISTS message_attachments (
    id SERIAL PRIMARY KEY,
    kit_message_id INTEGER REFERENCES kit_messages(id) ON DELETE CASCADE,
    channel_message_id INTEGER REFERENCES channel_messages(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    thumbnail_path VARCHAR(500),
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    uploaded_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    download_count INTEGER DEFAULT 0,
    is_scanned BOOLEAN DEFAULT FALSE,
    scan_result VARCHAR(50),
    CONSTRAINT check_attachment_message_type CHECK (
        (kit_message_id IS NOT NULL AND channel_message_id IS NULL) OR
        (kit_message_id IS NULL AND channel_message_id IS NOT NULL)
    )
);

CREATE INDEX idx_message_attachments_kit ON message_attachments(kit_message_id);
CREATE INDEX idx_message_attachments_channel ON message_attachments(channel_message_id);
CREATE INDEX idx_message_attachments_uploader ON message_attachments(uploaded_by);
CREATE INDEX idx_message_attachments_type ON message_attachments(file_type);

-- Attachment downloads table (tracking)
CREATE TABLE IF NOT EXISTS attachment_downloads (
    id SERIAL PRIMARY KEY,
    attachment_id INTEGER NOT NULL REFERENCES message_attachments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    download_date TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    ip_address VARCHAR(45)
);

CREATE INDEX idx_attachment_downloads_attachment ON attachment_downloads(attachment_id);
CREATE INDEX idx_attachment_downloads_user ON attachment_downloads(user_id);
CREATE INDEX idx_attachment_downloads_date ON attachment_downloads(download_date DESC);

-- User presence table (online/offline status)
CREATE TABLE IF NOT EXISTS user_presence (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    last_activity TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    status_message VARCHAR(200),
    socket_id VARCHAR(100)
);

CREATE INDEX idx_user_presence_user ON user_presence(user_id);
CREATE INDEX idx_user_presence_online ON user_presence(is_online);

-- Typing indicators table (optional - can use in-memory storage in production)
CREATE TABLE IF NOT EXISTS typing_indicators (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    kit_id INTEGER REFERENCES kits(id) ON DELETE CASCADE,
    is_typing BOOLEAN NOT NULL DEFAULT TRUE,
    started_typing TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT check_typing_context CHECK (
        (channel_id IS NOT NULL AND kit_id IS NULL) OR
        (channel_id IS NULL AND kit_id IS NOT NULL)
    )
);

CREATE INDEX idx_typing_indicators_user ON typing_indicators(user_id);
CREATE INDEX idx_typing_indicators_channel ON typing_indicators(channel_id);
CREATE INDEX idx_typing_indicators_kit ON typing_indicators(kit_id);

-- Add comments for documentation
COMMENT ON TABLE channels IS 'Department-wide or team channels for group messaging';
COMMENT ON TABLE channel_members IS 'Channel membership with user roles (admin, moderator, member)';
COMMENT ON TABLE channel_messages IS 'Messages sent to channels with threading support';
COMMENT ON TABLE message_reactions IS 'Emoji reactions and acknowledgments for messages';
COMMENT ON TABLE message_attachments IS 'Enhanced file attachment metadata with thumbnails';
COMMENT ON TABLE attachment_downloads IS 'Download tracking for compliance and analytics';
COMMENT ON TABLE user_presence IS 'Real-time user online/offline status tracking';
COMMENT ON TABLE typing_indicators IS 'Real-time typing indicator tracking';

-- Migration complete
SELECT 'Enhanced messaging tables created successfully' AS status;
