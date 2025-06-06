-- SupplyLine MRO Suite - Row Level Security (RLS) Policies
-- This script sets up comprehensive security policies for all tables

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE chemicals ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_service_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE chemical_issuances ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcement_reads ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_calibrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE calibration_standards ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_calibration_standards ENABLE ROW LEVEL SECURITY;

-- Create helper function to get current user from JWT
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS BIGINT AS $$
BEGIN
    RETURN (auth.jwt() ->> 'user_id')::BIGINT;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users 
        WHERE id = get_current_user_id() 
        AND is_admin = true 
        AND is_active = true
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create helper function to check if user is active
CREATE OR REPLACE FUNCTION is_active_user()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users 
        WHERE id = get_current_user_id() 
        AND is_active = true
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Users table policies
DROP POLICY IF EXISTS "Users can view all active users" ON users;
CREATE POLICY "Users can view all active users" ON users
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Users can update their own profile" ON users;
CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (id = get_current_user_id());

DROP POLICY IF EXISTS "Admins can manage all users" ON users;
CREATE POLICY "Admins can manage all users" ON users
    FOR ALL USING (is_admin());

-- Tools table policies
DROP POLICY IF EXISTS "Users can view all tools" ON tools;
CREATE POLICY "Users can view all tools" ON tools
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage tools" ON tools;
CREATE POLICY "Admins can manage tools" ON tools
    FOR ALL USING (is_admin());

-- Checkouts table policies
DROP POLICY IF EXISTS "Users can view all checkouts" ON checkouts;
CREATE POLICY "Users can view all checkouts" ON checkouts
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Users can create checkouts" ON checkouts;
CREATE POLICY "Users can create checkouts" ON checkouts
    FOR INSERT WITH CHECK (is_active_user());

DROP POLICY IF EXISTS "Users can return their own checkouts" ON checkouts;
CREATE POLICY "Users can return their own checkouts" ON checkouts
    FOR UPDATE USING (
        user_id = get_current_user_id() OR 
        is_admin()
    );

DROP POLICY IF EXISTS "Admins can manage all checkouts" ON checkouts;
CREATE POLICY "Admins can manage all checkouts" ON checkouts
    FOR ALL USING (is_admin());

-- Chemicals table policies
DROP POLICY IF EXISTS "Users can view all chemicals" ON chemicals;
CREATE POLICY "Users can view all chemicals" ON chemicals
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage chemicals" ON chemicals;
CREATE POLICY "Admins can manage chemicals" ON chemicals
    FOR ALL USING (is_admin());

-- Audit log policies
DROP POLICY IF EXISTS "Admins can view audit logs" ON audit_log;
CREATE POLICY "Admins can view audit logs" ON audit_log
    FOR SELECT USING (is_admin());

DROP POLICY IF EXISTS "System can insert audit logs" ON audit_log;
CREATE POLICY "System can insert audit logs" ON audit_log
    FOR INSERT WITH CHECK (true);

-- User activity policies
DROP POLICY IF EXISTS "Users can view their own activity" ON user_activity;
CREATE POLICY "Users can view their own activity" ON user_activity
    FOR SELECT USING (
        user_id = get_current_user_id() OR 
        is_admin()
    );

DROP POLICY IF EXISTS "System can insert user activity" ON user_activity;
CREATE POLICY "System can insert user activity" ON user_activity
    FOR INSERT WITH CHECK (is_active_user());

-- Tool service records policies
DROP POLICY IF EXISTS "Users can view tool service records" ON tool_service_records;
CREATE POLICY "Users can view tool service records" ON tool_service_records
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage tool service records" ON tool_service_records;
CREATE POLICY "Admins can manage tool service records" ON tool_service_records
    FOR ALL USING (is_admin());

-- Chemical issuances policies
DROP POLICY IF EXISTS "Users can view chemical issuances" ON chemical_issuances;
CREATE POLICY "Users can view chemical issuances" ON chemical_issuances
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Users can create chemical issuances" ON chemical_issuances;
CREATE POLICY "Users can create chemical issuances" ON chemical_issuances
    FOR INSERT WITH CHECK (is_active_user());

DROP POLICY IF EXISTS "Admins can manage chemical issuances" ON chemical_issuances;
CREATE POLICY "Admins can manage chemical issuances" ON chemical_issuances
    FOR ALL USING (is_admin());

-- Announcements policies
DROP POLICY IF EXISTS "Users can view active announcements" ON announcements;
CREATE POLICY "Users can view active announcements" ON announcements
    FOR SELECT USING (is_active_user() AND is_active = true);

DROP POLICY IF EXISTS "Admins can manage announcements" ON announcements;
CREATE POLICY "Admins can manage announcements" ON announcements
    FOR ALL USING (is_admin());

-- Announcement reads policies
DROP POLICY IF EXISTS "Users can view their own announcement reads" ON announcement_reads;
CREATE POLICY "Users can view their own announcement reads" ON announcement_reads
    FOR SELECT USING (
        user_id = get_current_user_id() OR 
        is_admin()
    );

DROP POLICY IF EXISTS "Users can mark announcements as read" ON announcement_reads;
CREATE POLICY "Users can mark announcements as read" ON announcement_reads
    FOR INSERT WITH CHECK (
        user_id = get_current_user_id() AND 
        is_active_user()
    );

-- Tool calibrations policies
DROP POLICY IF EXISTS "Users can view tool calibrations" ON tool_calibrations;
CREATE POLICY "Users can view tool calibrations" ON tool_calibrations
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage tool calibrations" ON tool_calibrations;
CREATE POLICY "Admins can manage tool calibrations" ON tool_calibrations
    FOR ALL USING (is_admin());

-- Calibration standards policies
DROP POLICY IF EXISTS "Users can view calibration standards" ON calibration_standards;
CREATE POLICY "Users can view calibration standards" ON calibration_standards
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage calibration standards" ON calibration_standards;
CREATE POLICY "Admins can manage calibration standards" ON calibration_standards
    FOR ALL USING (is_admin());

-- Tool calibration standards policies
DROP POLICY IF EXISTS "Users can view tool calibration standards" ON tool_calibration_standards;
CREATE POLICY "Users can view tool calibration standards" ON tool_calibration_standards
    FOR SELECT USING (is_active_user());

DROP POLICY IF EXISTS "Admins can manage tool calibration standards" ON tool_calibration_standards;
CREATE POLICY "Admins can manage tool calibration standards" ON tool_calibration_standards
    FOR ALL USING (is_admin());

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_employee_number ON users(employee_number);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_tools_tool_number ON tools(tool_number);
CREATE INDEX IF NOT EXISTS idx_tools_is_active ON tools(is_active);
CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_is_returned ON checkouts(is_returned);
CREATE INDEX IF NOT EXISTS idx_chemicals_is_active ON chemicals(is_active);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at);
CREATE INDEX IF NOT EXISTS idx_tool_service_records_tool_id ON tool_service_records(tool_id);
CREATE INDEX IF NOT EXISTS idx_chemical_issuances_chemical_id ON chemical_issuances(chemical_id);
CREATE INDEX IF NOT EXISTS idx_chemical_issuances_user_id ON chemical_issuances(user_id);
CREATE INDEX IF NOT EXISTS idx_announcements_is_active ON announcements(is_active);
CREATE INDEX IF NOT EXISTS idx_announcement_reads_user_id ON announcement_reads(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_calibrations_tool_id ON tool_calibrations(tool_id);

-- Create a view for dashboard statistics (accessible to all users)
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM tools WHERE is_active = true) as total_tools,
    (SELECT COUNT(*) FROM checkouts WHERE is_returned = false) as active_checkouts,
    (SELECT COUNT(*) FROM chemicals WHERE is_active = true) as total_chemicals,
    (SELECT COUNT(*) FROM users WHERE is_active = true) as total_users,
    (SELECT COUNT(*) FROM tools WHERE next_calibration_date < CURRENT_DATE AND requires_calibration = true) as overdue_calibrations,
    (SELECT COUNT(*) FROM chemicals WHERE quantity <= reorder_point AND is_active = true) as low_stock_chemicals;

-- Grant access to the view
GRANT SELECT ON dashboard_stats TO authenticated;
