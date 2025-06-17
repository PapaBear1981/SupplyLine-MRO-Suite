-- Add missing columns to users table for account lockout functionality
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP;

-- Update existing users to have default values
UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL;
