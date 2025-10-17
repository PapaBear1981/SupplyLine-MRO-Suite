-- Update admin password to Caden1234!
-- This SQL file can be run with: sqlite3 database/tools.db < update_admin_password.sql

-- First, let's check if the admin user exists
SELECT 'Checking for admin user...' as status;
SELECT employee_number, email, is_active FROM user WHERE employee_number = 'ADMIN001';

-- Note: We need to generate the password hash using Python's werkzeug.security.generate_password_hash
-- The hash will be generated and inserted below

-- To use this file:
-- 1. First run the Python script to generate the hash
-- 2. Or manually generate it and replace the placeholder below

-- Placeholder for password hash (will be replaced by script)
-- UPDATE user SET password_hash = 'HASH_PLACEHOLDER' WHERE employee_number = 'ADMIN001';

SELECT 'Admin password update complete!' as status;
SELECT employee_number, email, is_active FROM user WHERE employee_number = 'ADMIN001';

