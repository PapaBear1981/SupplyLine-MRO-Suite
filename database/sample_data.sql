-- SupplyLine MRO Suite Sample Data
-- This script populates the database with comprehensive sample data for testing

-- Sample Users (various departments and roles)
INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active) VALUES
('John Smith', 'EMP001', 'Materials', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Sarah Johnson', 'EMP002', 'Quality', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Mike Wilson', 'EMP003', 'Maintenance', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Lisa Chen', 'EMP004', 'Engineering', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('David Brown', 'EMP005', 'Materials', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Jennifer Davis', 'EMP006', 'Quality', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Robert Miller', 'EMP007', 'Maintenance', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true),
('Amanda Taylor', 'EMP008', 'Engineering', '$2b$12$LQv3c1yqBwLFaAOjymHa2ue8/dCVo/2aQiAuQ6jn2opVpivQBdWvG', false, true)
ON CONFLICT (employee_number) DO NOTHING;

-- Sample Tools (various categories and statuses)
INSERT INTO tools (tool_number, serial_number, description, condition, location, category, status) VALUES
('T001', 'SN001234', 'Digital Multimeter - Fluke 87V', 'Excellent', 'Lab A-1', 'Electronics', 'available'),
('T002', 'SN002345', 'Oscilloscope - Tektronix TDS2024C', 'Good', 'Lab A-2', 'Electronics', 'available'),
('T003', 'SN003456', 'Torque Wrench - Snap-on 3/8" Drive', 'Good', 'Tool Room B', 'Mechanical', 'available'),
('T004', 'SN004567', 'Soldering Station - Weller WES51', 'Excellent', 'Lab A-3', 'Electronics', 'available'),
('T005', 'SN005678', 'Micrometer Set - Mitutoyo 0-1"', 'Good', 'Tool Room A', 'Measurement', 'available'),
('T006', 'SN006789', 'Power Drill - DeWalt DCD771C2', 'Good', 'Tool Room B', 'Power Tools', 'available'),
('T007', 'SN007890', 'Caliper - Mitutoyo Digital 6"', 'Excellent', 'Tool Room A', 'Measurement', 'available'),
('T008', 'SN008901', 'Function Generator - Agilent 33220A', 'Good', 'Lab A-4', 'Electronics', 'available'),
('T009', 'SN009012', 'Impact Wrench - Snap-on MG725', 'Fair', 'Tool Room B', 'Power Tools', 'maintenance'),
('T010', 'SN010123', 'Spectrum Analyzer - Keysight E4402B', 'Good', 'Lab A-5', 'Electronics', 'available'),
('T011', 'SN011234', 'Angle Grinder - Makita 9557PBX1', 'Good', 'Tool Room C', 'Power Tools', 'available'),
('T012', 'SN012345', 'Pressure Gauge - Ashcroft 1009', 'Excellent', 'Tool Room A', 'Measurement', 'available'),
('T013', 'SN013456', 'Heat Gun - Milwaukee 8988-20', 'Good', 'Tool Room C', 'Power Tools', 'available'),
('T014', 'SN014567', 'Crimping Tool - Molex 63811-1000', 'Good', 'Lab A-6', 'Electronics', 'available'),
('T015', 'SN015678', 'Pneumatic Wrench - Ingersoll Rand 2135TiMAX', 'Fair', 'Tool Room B', 'Power Tools', 'available')
ON CONFLICT (tool_number) DO NOTHING;

-- Sample Chemicals (various categories and statuses)
INSERT INTO chemicals (part_number, lot_number, description, manufacturer, quantity, unit, location, category, status, expiration_date, minimum_stock_level) VALUES
('CHM001', 'LOT2024001', 'Aerospace Sealant - PR-1422', 'PPG Industries', 5.5, 'tubes', 'Chemical Storage A', 'Sealant', 'available', '2025-12-31', 2.0),
('CHM002', 'LOT2024002', 'Primer - Cytec BR-127', 'Solvay', 2.3, 'gallons', 'Chemical Storage A', 'Primer', 'available', '2025-06-30', 1.0),
('CHM003', 'LOT2024003', 'Adhesive - 3M Scotch-Weld 2216', '3M Company', 12.0, 'tubes', 'Chemical Storage B', 'Adhesive', 'available', '2026-03-15', 5.0),
('CHM004', 'LOT2023004', 'Cleaning Solvent - Stoddard Solvent', 'ExxonMobil', 0.5, 'gallons', 'Chemical Storage C', 'Solvent', 'low_stock', '2024-12-31', 2.0),
('CHM005', 'LOT2024005', 'Paint - Akzo Nobel Aerodur 2100', 'Akzo Nobel', 3.2, 'gallons', 'Paint Storage', 'Paint', 'available', '2025-09-30', 1.0),
('CHM006', 'LOT2023006', 'Lubricant - Aeroshell Grease 33', 'Shell', 0.0, 'tubes', 'Chemical Storage A', 'Lubricant', 'out_of_stock', '2024-08-15', 3.0),
('CHM007', 'LOT2024007', 'Corrosion Inhibitor - LPS 3', 'ITW Pro Brands', 8.5, 'cans', 'Chemical Storage B', 'Inhibitor', 'available', '2026-01-31', 4.0),
('CHM008', 'LOT2023008', 'Flux Remover - MG Chemicals 4140', 'MG Chemicals', 1.2, 'bottles', 'Chemical Storage C', 'Cleaner', 'available', '2024-11-30', 2.0),
('CHM009', 'LOT2024009', 'Threadlocker - Loctite 242', 'Henkel', 15.0, 'bottles', 'Chemical Storage A', 'Adhesive', 'available', '2025-07-31', 8.0),
('CHM010', 'LOT2023010', 'Degreaser - Simple Green Pro HD', 'Simple Green', 0.8, 'gallons', 'Chemical Storage C', 'Cleaner', 'low_stock', '2024-10-31', 2.0)
ON CONFLICT (part_number) DO NOTHING;

-- Sample Checkouts (some current, some historical)
INSERT INTO checkouts (tool_id, user_id, checkout_date, return_date, expected_return_date) VALUES
-- Current checkouts
((SELECT id FROM tools WHERE tool_number = 'T002'), (SELECT id FROM users WHERE employee_number = 'EMP001'), NOW() - INTERVAL '2 days', NULL, NOW() + INTERVAL '5 days'),
((SELECT id FROM tools WHERE tool_number = 'T005'), (SELECT id FROM users WHERE employee_number = 'EMP003'), NOW() - INTERVAL '1 day', NULL, NOW() + INTERVAL '3 days'),
((SELECT id FROM tools WHERE tool_number = 'T008'), (SELECT id FROM users WHERE employee_number = 'EMP004'), NOW() - INTERVAL '3 hours', NULL, NOW() + INTERVAL '7 days'),

-- Historical checkouts (returned)
((SELECT id FROM tools WHERE tool_number = 'T001'), (SELECT id FROM users WHERE employee_number = 'EMP002'), NOW() - INTERVAL '10 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '7 days'),
((SELECT id FROM tools WHERE tool_number = 'T003'), (SELECT id FROM users WHERE employee_number = 'EMP001'), NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', NOW() - INTERVAL '10 days'),
((SELECT id FROM tools WHERE tool_number = 'T004'), (SELECT id FROM users WHERE employee_number = 'EMP005'), NOW() - INTERVAL '20 days', NOW() - INTERVAL '18 days', NOW() - INTERVAL '15 days'),
((SELECT id FROM tools WHERE tool_number = 'T006'), (SELECT id FROM users WHERE employee_number = 'EMP003'), NOW() - INTERVAL '25 days', NOW() - INTERVAL '22 days', NOW() - INTERVAL '20 days'),
((SELECT id FROM tools WHERE tool_number = 'T007'), (SELECT id FROM users WHERE employee_number = 'EMP006'), NOW() - INTERVAL '30 days', NOW() - INTERVAL '28 days', NOW() - INTERVAL '25 days')
ON CONFLICT DO NOTHING;

-- Sample Chemical Issuances
INSERT INTO chemical_issuances (chemical_id, user_id, quantity, hangar, purpose, issue_date) VALUES
((SELECT id FROM chemicals WHERE part_number = 'CHM001'), (SELECT id FROM users WHERE employee_number = 'EMP001'), 1.0, 'Hangar A', 'Wing seal repair', NOW() - INTERVAL '5 days'),
((SELECT id FROM chemicals WHERE part_number = 'CHM003'), (SELECT id FROM users WHERE employee_number = 'EMP002'), 2.0, 'Hangar B', 'Panel bonding', NOW() - INTERVAL '3 days'),
((SELECT id FROM chemicals WHERE part_number = 'CHM005'), (SELECT id FROM users WHERE employee_number = 'EMP005'), 0.5, 'Hangar A', 'Touch-up painting', NOW() - INTERVAL '7 days'),
((SELECT id FROM chemicals WHERE part_number = 'CHM007'), (SELECT id FROM users WHERE employee_number = 'EMP003'), 1.0, 'Hangar C', 'Corrosion prevention', NOW() - INTERVAL '2 days'),
((SELECT id FROM chemicals WHERE part_number = 'CHM009'), (SELECT id FROM users WHERE employee_number = 'EMP004'), 3.0, 'Hangar B', 'Fastener securing', NOW() - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Sample Audit Log entries
INSERT INTO audit_log (action_type, action_details) VALUES
('user_login', 'User EMP001 (John Smith) logged in successfully'),
('tool_checkout', 'User EMP001 checked out tool T002 (Oscilloscope - Tektronix TDS2024C)'),
('tool_return', 'User EMP002 returned tool T001 (Digital Multimeter - Fluke 87V)'),
('chemical_issue', 'User EMP001 issued 1.0 tubes of CHM001 (Aerospace Sealant - PR-1422)'),
('user_created', 'New user EMP008 (Amanda Taylor) created by admin'),
('tool_maintenance', 'Tool T009 (Impact Wrench - Snap-on MG725) marked for maintenance'),
('chemical_restock', 'Chemical CHM002 (Primer - Cytec BR-127) restocked with 2.3 gallons'),
('user_logout', 'User EMP003 (Mike Wilson) logged out'),
('tool_calibration', 'Tool T001 (Digital Multimeter - Fluke 87V) calibration completed'),
('system_backup', 'Daily system backup completed successfully')
ON CONFLICT DO NOTHING;

-- Sample User Activities
INSERT INTO user_activities (user_id, activity_type, description, ip_address) VALUES
((SELECT id FROM users WHERE employee_number = 'EMP001'), 'login', 'Successful login', '192.168.1.100'),
((SELECT id FROM users WHERE employee_number = 'EMP001'), 'tool_checkout', 'Checked out Oscilloscope - Tektronix TDS2024C', '192.168.1.100'),
((SELECT id FROM users WHERE employee_number = 'EMP002'), 'login', 'Successful login', '192.168.1.101'),
((SELECT id FROM users WHERE employee_number = 'EMP002'), 'tool_return', 'Returned Digital Multimeter - Fluke 87V', '192.168.1.101'),
((SELECT id FROM users WHERE employee_number = 'EMP003'), 'login', 'Successful login', '192.168.1.102'),
((SELECT id FROM users WHERE employee_number = 'EMP003'), 'tool_checkout', 'Checked out Micrometer Set - Mitutoyo 0-1"', '192.168.1.102'),
((SELECT id FROM users WHERE employee_number = 'EMP004'), 'login', 'Successful login', '192.168.1.103'),
((SELECT id FROM users WHERE employee_number = 'EMP004'), 'chemical_issue', 'Issued Threadlocker - Loctite 242', '192.168.1.103'),
((SELECT id FROM users WHERE employee_number = 'EMP005'), 'login', 'Successful login', '192.168.1.104'),
((SELECT id FROM users WHERE employee_number = 'EMP005'), 'chemical_issue', 'Issued Paint - Akzo Nobel Aerodur 2100', '192.168.1.104')
ON CONFLICT DO NOTHING;

-- Sample Roles
INSERT INTO roles (name, description, is_system_role) VALUES
('Admin', 'Full system access with all permissions', true),
('Lead', 'Lead technician with extended permissions', true),
('User', 'Standard user with basic permissions', true),
('Mechanic', 'Limited access for mechanics', true)
ON CONFLICT (name) DO NOTHING;

-- Sample Permissions
INSERT INTO permissions (name, description, category) VALUES
('view_tools', 'View tools inventory', 'Tools'),
('manage_tools', 'Create, edit, and delete tools', 'Tools'),
('checkout_tools', 'Check out tools', 'Tools'),
('return_tools', 'Return tools', 'Tools'),
('view_chemicals', 'View chemicals inventory', 'Chemicals'),
('manage_chemicals', 'Create, edit, and delete chemicals', 'Chemicals'),
('issue_chemicals', 'Issue chemicals to users', 'Chemicals'),
('view_reports', 'View system reports', 'Reports'),
('manage_reports', 'Create and manage reports', 'Reports'),
('view_users', 'View user information', 'Users'),
('manage_users', 'Create, edit, and delete users', 'Users'),
('view_calibrations', 'View calibration records', 'Calibrations'),
('manage_calibrations', 'Create and manage calibrations', 'Calibrations'),
('view_admin_dashboard', 'Access admin dashboard', 'Admin'),
('manage_system', 'System administration', 'Admin'),
('role.manage', 'Manage roles and permissions', 'Admin')
ON CONFLICT (name) DO NOTHING;

-- Sample Role-Permission assignments
INSERT INTO role_permissions (role_id, permission_id) VALUES
-- Admin role gets all permissions
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_tools')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_tools')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'checkout_tools')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'return_tools')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_chemicals')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_chemicals')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'issue_chemicals')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_reports')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_reports')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_users')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_users')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_calibrations')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_calibrations')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'view_admin_dashboard')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'manage_system')),
((SELECT id FROM roles WHERE name = 'Admin'), (SELECT id FROM permissions WHERE name = 'role.manage')),

-- Lead role gets extended permissions
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'view_tools')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'checkout_tools')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'return_tools')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'view_chemicals')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'issue_chemicals')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'view_reports')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'view_calibrations')),
((SELECT id FROM roles WHERE name = 'Lead'), (SELECT id FROM permissions WHERE name = 'manage_calibrations')),

-- User role gets basic permissions
((SELECT id FROM roles WHERE name = 'User'), (SELECT id FROM permissions WHERE name = 'view_tools')),
((SELECT id FROM roles WHERE name = 'User'), (SELECT id FROM permissions WHERE name = 'checkout_tools')),
((SELECT id FROM roles WHERE name = 'User'), (SELECT id FROM permissions WHERE name = 'return_tools')),
((SELECT id FROM roles WHERE name = 'User'), (SELECT id FROM permissions WHERE name = 'view_chemicals')),

-- Mechanic role gets limited permissions
((SELECT id FROM roles WHERE name = 'Mechanic'), (SELECT id FROM permissions WHERE name = 'view_tools')),
((SELECT id FROM roles WHERE name = 'Mechanic'), (SELECT id FROM permissions WHERE name = 'checkout_tools'))
ON CONFLICT DO NOTHING;

-- Sample User-Role assignments
INSERT INTO user_roles (user_id, role_id) VALUES
((SELECT id FROM users WHERE employee_number = 'EMP001'), (SELECT id FROM roles WHERE name = 'Lead')),
((SELECT id FROM users WHERE employee_number = 'EMP002'), (SELECT id FROM roles WHERE name = 'User')),
((SELECT id FROM users WHERE employee_number = 'EMP003'), (SELECT id FROM roles WHERE name = 'Mechanic')),
((SELECT id FROM users WHERE employee_number = 'EMP004'), (SELECT id FROM roles WHERE name = 'User')),
((SELECT id FROM users WHERE employee_number = 'EMP005'), (SELECT id FROM roles WHERE name = 'Lead')),
((SELECT id FROM users WHERE employee_number = 'EMP006'), (SELECT id FROM roles WHERE name = 'User')),
((SELECT id FROM users WHERE employee_number = 'EMP007'), (SELECT id FROM roles WHERE name = 'Mechanic')),
((SELECT id FROM users WHERE employee_number = 'EMP008'), (SELECT id FROM roles WHERE name = 'User'))
ON CONFLICT DO NOTHING;

-- Sample Calibration Standards
INSERT INTO calibration_standards (name, description, certificate_number, expiration_date, is_active) VALUES
('NIST-001', 'NIST Traceable Voltage Standard', 'CERT-2024-001', '2025-12-31', true),
('NIST-002', 'NIST Traceable Frequency Standard', 'CERT-2024-002', '2025-11-30', true),
('NIST-003', 'NIST Traceable Pressure Standard', 'CERT-2024-003', '2025-10-31', true),
('NIST-004', 'NIST Traceable Temperature Standard', 'CERT-2024-004', '2025-09-30', true)
ON CONFLICT (certificate_number) DO NOTHING;

-- Sample Tool Calibrations
INSERT INTO tool_calibrations (tool_id, calibration_date, next_calibration_date, calibrated_by, certificate_number, status, notes) VALUES
((SELECT id FROM tools WHERE tool_number = 'T001'), NOW() - INTERVAL '30 days', NOW() + INTERVAL '335 days', 'Cal Lab Services', 'CAL-2024-001', 'passed', 'All measurements within tolerance'),
((SELECT id FROM tools WHERE tool_number = 'T002'), NOW() - INTERVAL '45 days', NOW() + INTERVAL '320 days', 'Cal Lab Services', 'CAL-2024-002', 'passed', 'Frequency response verified'),
((SELECT id FROM tools WHERE tool_number = 'T005'), NOW() - INTERVAL '60 days', NOW() + INTERVAL '305 days', 'Internal Cal Team', 'CAL-2024-003', 'passed', 'Dimensional accuracy confirmed'),
((SELECT id FROM tools WHERE tool_number = 'T007'), NOW() - INTERVAL '15 days', NOW() + INTERVAL '350 days', 'Internal Cal Team', 'CAL-2024-004', 'passed', 'Digital readout calibrated'),
((SELECT id FROM tools WHERE tool_number = 'T008'), NOW() - INTERVAL '90 days', NOW() + INTERVAL '275 days', 'Cal Lab Services', 'CAL-2024-005', 'passed', 'Waveform generation verified'),
((SELECT id FROM tools WHERE tool_number = 'T010'), NOW() - INTERVAL '120 days', NOW() + INTERVAL '245 days', 'Cal Lab Services', 'CAL-2024-006', 'passed', 'Frequency sweep accuracy confirmed'),
((SELECT id FROM tools WHERE tool_number = 'T012'), NOW() - INTERVAL '75 days', NOW() + INTERVAL '290 days', 'Internal Cal Team', 'CAL-2024-007', 'passed', 'Pressure readings verified')
ON CONFLICT DO NOTHING;

-- Sample Tool Calibration Standards (linking tools to standards used)
INSERT INTO tool_calibration_standards (tool_calibration_id, calibration_standard_id) VALUES
((SELECT id FROM tool_calibrations WHERE certificate_number = 'CAL-2024-001'), (SELECT id FROM calibration_standards WHERE certificate_number = 'CERT-2024-001')),
((SELECT id FROM tool_calibrations WHERE certificate_number = 'CAL-2024-002'), (SELECT id FROM calibration_standards WHERE certificate_number = 'CERT-2024-002')),
((SELECT id FROM tool_calibrations WHERE certificate_number = 'CAL-2024-005'), (SELECT id FROM calibration_standards WHERE certificate_number = 'CERT-2024-002')),
((SELECT id FROM tool_calibrations WHERE certificate_number = 'CAL-2024-006'), (SELECT id FROM calibration_standards WHERE certificate_number = 'CERT-2024-002')),
((SELECT id FROM tool_calibrations WHERE certificate_number = 'CAL-2024-007'), (SELECT id FROM calibration_standards WHERE certificate_number = 'CERT-2024-003'))
ON CONFLICT DO NOTHING;

-- Sample System Settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('app_name', 'SupplyLine MRO Suite', 'Application name displayed in the UI'),
('company_name', 'Aerospace Manufacturing Corp', 'Company name for reports and headers'),
('default_checkout_days', '7', 'Default number of days for tool checkouts'),
('low_stock_threshold', '5', 'Threshold for low stock chemical alerts'),
('calibration_reminder_days', '30', 'Days before calibration due to send reminders'),
('session_timeout_minutes', '60', 'Session timeout in minutes'),
('max_login_attempts', '5', 'Maximum failed login attempts before lockout'),
('lockout_duration_minutes', '15', 'Account lockout duration in minutes'),
('backup_retention_days', '90', 'Number of days to retain backup files'),
('audit_log_retention_days', '365', 'Number of days to retain audit log entries')
ON CONFLICT (setting_key) DO NOTHING;

-- Sample Tool Service Records
INSERT INTO tool_service_records (tool_id, service_date, service_type, description, performed_by, cost, next_service_date) VALUES
((SELECT id FROM tools WHERE tool_number = 'T009'), NOW() - INTERVAL '5 days', 'repair', 'Replaced worn impact mechanism', 'Maintenance Team', 125.50, NOW() + INTERVAL '180 days'),
((SELECT id FROM tools WHERE tool_number = 'T003'), NOW() - INTERVAL '30 days', 'maintenance', 'Lubricated and calibrated torque settings', 'Maintenance Team', 45.00, NOW() + INTERVAL '90 days'),
((SELECT id FROM tools WHERE tool_number = 'T006'), NOW() - INTERVAL '60 days', 'maintenance', 'Replaced battery and cleaned contacts', 'Maintenance Team', 25.00, NOW() + INTERVAL '120 days'),
((SELECT id FROM tools WHERE tool_number = 'T011'), NOW() - INTERVAL '45 days', 'maintenance', 'Replaced grinding disc and safety guard', 'Maintenance Team', 35.00, NOW() + INTERVAL '90 days')
ON CONFLICT DO NOTHING;

-- Update tool statuses based on service records
UPDATE tools SET status = 'available' WHERE tool_number = 'T009' AND status = 'maintenance';

-- Sample announcements (if table exists)
INSERT INTO announcements (title, content, priority, is_active, created_by, expires_at) VALUES
('System Maintenance Scheduled', 'The SupplyLine system will undergo scheduled maintenance on Saturday from 2:00 AM to 6:00 AM. Please plan accordingly.', 'medium', true, 'ADMIN001', NOW() + INTERVAL '7 days'),
('New Chemical Safety Procedures', 'Please review the updated chemical safety procedures document available in the Quality section. All personnel must acknowledge receipt by end of week.', 'high', true, 'ADMIN001', NOW() + INTERVAL '14 days'),
('Tool Calibration Reminder', 'Several tools are due for calibration this month. Please check the calibration schedule and coordinate with the quality team.', 'low', true, 'ADMIN001', NOW() + INTERVAL '30 days')
ON CONFLICT DO NOTHING;
