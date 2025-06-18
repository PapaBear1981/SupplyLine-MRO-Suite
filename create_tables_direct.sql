-- Direct SQL script to create missing database tables for SupplyLine MRO Suite
-- This script creates the missing tables that are causing 500 errors in the API endpoints
-- Run this script directly against the PostgreSQL database to fix issue #339

-- Create checkouts table
CREATE TABLE IF NOT EXISTS checkouts (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    expected_return_date TIMESTAMP,
    return_condition TEXT,
    returned_by TEXT,
    found BOOLEAN DEFAULT FALSE,
    return_notes TEXT,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create user_activity table
CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiration_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create announcement_reads table
CREATE TABLE IF NOT EXISTS announcement_reads (
    id SERIAL PRIMARY KEY,
    announcement_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (announcement_id) REFERENCES announcements(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create audit_log table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    action_type TEXT NOT NULL,
    action_details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tool_calibrations table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS tool_calibrations (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL,
    calibration_date TIMESTAMP NOT NULL,
    next_calibration_date TIMESTAMP,
    performed_by_user_id INTEGER NOT NULL,
    calibration_notes TEXT,
    calibration_status TEXT DEFAULT 'pass',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (performed_by_user_id) REFERENCES users(id)
);

-- Create calibration_standards table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS calibration_standards (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    standard_number TEXT NOT NULL,
    certification_date TIMESTAMP NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tool_calibration_standards table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS tool_calibration_standards (
    id SERIAL PRIMARY KEY,
    calibration_id INTEGER NOT NULL,
    standard_id INTEGER NOT NULL,
    FOREIGN KEY (calibration_id) REFERENCES tool_calibrations(id),
    FOREIGN KEY (standard_id) REFERENCES calibration_standards(id)
);

-- Create chemical_issuances table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS chemical_issuances (
    id SERIAL PRIMARY KEY,
    chemical_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    hangar TEXT NOT NULL,
    purpose TEXT,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chemical_id) REFERENCES chemicals(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create tool_service_records table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS tool_service_records (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add missing columns to existing tables (if they don't exist)

-- Add missing columns to tools table
DO $$ 
BEGIN
    -- Add status column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='status') THEN
        ALTER TABLE tools ADD COLUMN status TEXT DEFAULT 'available';
    END IF;
    
    -- Add calibration columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='requires_calibration') THEN
        ALTER TABLE tools ADD COLUMN requires_calibration BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='calibration_status') THEN
        ALTER TABLE tools ADD COLUMN calibration_status TEXT DEFAULT 'not_applicable';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='last_calibration_date') THEN
        ALTER TABLE tools ADD COLUMN last_calibration_date TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='next_calibration_date') THEN
        ALTER TABLE tools ADD COLUMN next_calibration_date TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='calibration_frequency_days') THEN
        ALTER TABLE tools ADD COLUMN calibration_frequency_days INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='status_reason') THEN
        ALTER TABLE tools ADD COLUMN status_reason TEXT;
    END IF;
END $$;

-- Add missing columns to users table
DO $$ 
BEGIN
    -- Add avatar column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='avatar') THEN
        ALTER TABLE users ADD COLUMN avatar TEXT;
    END IF;
    
    -- Add account lockout columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='failed_login_attempts') THEN
        ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='account_locked_until') THEN
        ALTER TABLE users ADD COLUMN account_locked_until TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='last_failed_login') THEN
        ALTER TABLE users ADD COLUMN last_failed_login TIMESTAMP;
    END IF;
    
    -- Add token columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token') THEN
        ALTER TABLE users ADD COLUMN reset_token TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='reset_token_expiry') THEN
        ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='remember_token') THEN
        ALTER TABLE users ADD COLUMN remember_token TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='remember_token_expiry') THEN
        ALTER TABLE users ADD COLUMN remember_token_expiry TIMESTAMP;
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_return_date ON checkouts(return_date);
CREATE INDEX IF NOT EXISTS idx_checkouts_expected_return_date ON checkouts(expected_return_date);

CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp);

CREATE INDEX IF NOT EXISTS idx_announcements_created_by ON announcements(created_by);
CREATE INDEX IF NOT EXISTS idx_announcements_is_active ON announcements(is_active);
CREATE INDEX IF NOT EXISTS idx_announcements_expiration_date ON announcements(expiration_date);

CREATE INDEX IF NOT EXISTS idx_announcement_reads_announcement_id ON announcement_reads(announcement_id);
CREATE INDEX IF NOT EXISTS idx_announcement_reads_user_id ON announcement_reads(user_id);

-- Print success message
DO $$ 
BEGIN
    RAISE NOTICE 'Database migration completed successfully!';
    RAISE NOTICE 'All missing tables and columns have been created.';
    RAISE NOTICE 'The following API endpoints should now work:';
    RAISE NOTICE '- /api/checkouts/overdue';
    RAISE NOTICE '- /api/checkouts/user';
    RAISE NOTICE '- /api/user/activity';
    RAISE NOTICE '- /api/announcements';
END $$;
