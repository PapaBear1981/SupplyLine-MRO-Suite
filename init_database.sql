-- SupplyLine MRO Suite Database Initialization Script
-- This script creates all necessary tables and initial data

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tools table
CREATE TABLE IF NOT EXISTS tools (
    id SERIAL PRIMARY KEY,
    tool_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'available',
    condition_status VARCHAR(20) DEFAULT 'good',
    last_calibration DATE,
    next_calibration DATE,
    calibration_interval INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool checkout/checkin history
CREATE TABLE IF NOT EXISTS tool_transactions (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER REFERENCES tools(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(20) NOT NULL,
    checkout_time TIMESTAMP,
    expected_return TIMESTAMP,
    actual_return TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chemicals table
CREATE TABLE IF NOT EXISTS chemicals (
    id SERIAL PRIMARY KEY,
    chemical_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    cas_number VARCHAR(20),
    manufacturer VARCHAR(100),
    lot_number VARCHAR(50),
    quantity DECIMAL(10,2),
    unit VARCHAR(20),
    location VARCHAR(100),
    expiration_date DATE,
    safety_data_sheet_url VARCHAR(255),
    hazard_class VARCHAR(50),
    storage_requirements TEXT,
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chemical usage tracking
CREATE TABLE IF NOT EXISTS chemical_transactions (
    id SERIAL PRIMARY KEY,
    chemical_id INTEGER REFERENCES chemicals(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(20) NOT NULL,
    quantity_used DECIMAL(10,2),
    remaining_quantity DECIMAL(10,2),
    purpose TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System settings
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_tools_tool_id ON tools(tool_id);
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
CREATE INDEX IF NOT EXISTS idx_chemicals_chemical_id ON chemicals(chemical_id);
CREATE INDEX IF NOT EXISTS idx_chemicals_expiration ON chemicals(expiration_date);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

-- Insert admin user (password: admin123)
INSERT INTO users (username, password_hash, role, first_name, last_name, email, department)
VALUES ('ADMIN001', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin', 'System', 'Administrator', 'admin@supplyline.local', 'IT')
ON CONFLICT (username) DO NOTHING;

-- Insert sample tools
INSERT INTO tools (tool_id, name, description, category, location, status, condition_status)
VALUES 
    ('TOOL001', 'Digital Multimeter', 'Fluke 87V Digital Multimeter', 'Electronics', 'Lab A-1', 'available', 'good'),
    ('TOOL002', 'Oscilloscope', 'Tektronix TDS2024C Oscilloscope', 'Electronics', 'Lab A-2', 'available', 'good'),
    ('TOOL003', 'Torque Wrench', 'Snap-on 3/8" Drive Torque Wrench', 'Mechanical', 'Tool Room B', 'available', 'good'),
    ('TOOL004', 'Soldering Station', 'Weller WES51 Soldering Station', 'Electronics', 'Lab A-3', 'available', 'good'),
    ('TOOL005', 'Micrometer Set', 'Mitutoyo 0-1" Micrometer Set', 'Measurement', 'Tool Room A', 'available', 'good')
ON CONFLICT (tool_id) DO NOTHING;

-- Insert sample chemicals
INSERT INTO chemicals (chemical_id, name, cas_number, manufacturer, lot_number, quantity, unit, location, expiration_date)
VALUES 
    ('CHEM001', 'Isopropyl Alcohol', '67-63-0', 'Fisher Scientific', 'LOT123', 1000.0, 'mL', 'Chemical Storage A', '2025-12-31'),
    ('CHEM002', 'Acetone', '67-64-1', 'Sigma-Aldrich', 'LOT456', 500.0, 'mL', 'Chemical Storage A', '2025-06-30'),
    ('CHEM003', 'Flux Cleaner', '64-17-5', 'MG Chemicals', 'LOT789', 250.0, 'mL', 'Chemical Storage B', '2026-03-15')
ON CONFLICT (chemical_id) DO NOTHING;

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, description)
VALUES 
    ('app_name', 'SupplyLine MRO Suite', 'Application name'),
    ('version', '3.5.0', 'Application version'),
    ('maintenance_mode', 'false', 'Maintenance mode flag'),
    ('max_checkout_days', '30', 'Maximum checkout duration in days'),
    ('notification_email', 'admin@supplyline.local', 'System notification email')
ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    updated_at = CURRENT_TIMESTAMP;

-- Grant permissions to supplyline_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO supplyline_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO supplyline_user;

-- Success message
SELECT 'Database initialization completed successfully!' as status;
