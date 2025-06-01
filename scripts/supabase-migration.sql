-- SupplyLine MRO Suite Database Migration for Supabase
-- This script creates the database schema matching the current SQLite structure

-- Enable Row Level Security
-- Note: Configure JWT_SECRET via environment variables for security
-- Use: supabase secrets set JWT_SECRET="<YOUR_SECURE_SECRET>"

-- Create custom types (with existence checks for idempotent migrations)
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'admin', 'materials');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE tool_condition AS ENUM ('excellent', 'good', 'fair', 'poor', 'needs_repair');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE chemical_status AS ENUM ('available', 'low_stock', 'out_of_stock', 'expired');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE checkout_status AS ENUM ('active', 'returned', 'overdue');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    reset_token VARCHAR(255),
    reset_token_expiry TIMESTAMPTZ,
    remember_token VARCHAR(255),
    remember_token_expiry TIMESTAMPTZ,
    avatar VARCHAR(255),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    role user_role DEFAULT 'user',
    preferences JSONB DEFAULT '{}'::jsonb
);

-- Tools table
CREATE TABLE IF NOT EXISTS tools (
    id BIGSERIAL PRIMARY KEY,
    tool_number VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    description TEXT,
    condition tool_condition DEFAULT 'good',
    location VARCHAR(100),
    category VARCHAR(50) DEFAULT 'General',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    purchase_date DATE,
    purchase_cost DECIMAL(10,2),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_service_date DATE,
    next_service_date DATE,
    service_interval_days INTEGER,
    barcode VARCHAR(100),
    qr_code VARCHAR(255)
);

-- Checkouts table
CREATE TABLE IF NOT EXISTS checkouts (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    checkout_date TIMESTAMPTZ DEFAULT NOW(),
    return_date TIMESTAMPTZ,
    expected_return_date TIMESTAMPTZ,
    status checkout_status DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chemicals table
CREATE TABLE IF NOT EXISTS chemicals (
    id BIGSERIAL PRIMARY KEY,
    part_number VARCHAR(100) NOT NULL,
    lot_number VARCHAR(100) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100),
    quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL DEFAULT 'each',
    location VARCHAR(100),
    category VARCHAR(50) DEFAULT 'General',
    status chemical_status DEFAULT 'available',
    date_added TIMESTAMPTZ DEFAULT NOW(),
    expiration_date DATE,
    msds_file VARCHAR(255),
    hazard_class VARCHAR(50),
    storage_requirements TEXT,
    minimum_quantity DECIMAL(10,3) DEFAULT 0,
    maximum_quantity DECIMAL(10,3),
    cost_per_unit DECIMAL(10,2),
    supplier VARCHAR(100),
    supplier_part_number VARCHAR(100),
    notes TEXT,
    needs_reorder BOOLEAN DEFAULT FALSE,
    reorder_status VARCHAR(20) DEFAULT 'not_needed',
    reorder_date TIMESTAMPTZ,
    expected_delivery_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chemical issuances table
CREATE TABLE IF NOT EXISTS chemical_issuances (
    id BIGSERIAL PRIMARY KEY,
    chemical_id BIGINT NOT NULL REFERENCES chemicals(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quantity_issued DECIMAL(10,3) NOT NULL,
    issue_date TIMESTAMPTZ DEFAULT NOW(),
    purpose TEXT,
    project_code VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id BIGINT,
    old_values JSONB,
    new_values JSONB,
    action_details TEXT,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- User activity table
CREATE TABLE IF NOT EXISTS user_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Tool service records table
CREATE TABLE IF NOT EXISTS tool_service_records (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    service_date DATE NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    cost DECIMAL(10,2),
    performed_by VARCHAR(100),
    next_service_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool calibration tables
CREATE TABLE IF NOT EXISTS tool_calibrations (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    calibration_date DATE NOT NULL,
    due_date DATE NOT NULL,
    performed_by VARCHAR(100),
    certificate_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'current',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS calibration_standards (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    certificate_number VARCHAR(100),
    calibration_date DATE,
    expiration_date DATE,
    accuracy VARCHAR(50),
    range_min DECIMAL(15,6),
    range_max DECIMAL(15,6),
    units VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tool_calibration_standards (
    id BIGSERIAL PRIMARY KEY,
    calibration_id BIGINT NOT NULL REFERENCES tool_calibrations(id) ON DELETE CASCADE,
    standard_id BIGINT NOT NULL REFERENCES calibration_standards(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Registration requests table
CREATE TABLE IF NOT EXISTS registration_requests (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    processed_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    admin_notes TEXT
);

-- Cycle count tables
CREATE TABLE IF NOT EXISTS cycle_count_schedules (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    frequency VARCHAR(20) NOT NULL,
    method VARCHAR(20) NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cycle_count_batches (
    id BIGSERIAL PRIMARY KEY,
    schedule_id BIGINT REFERENCES cycle_count_schedules(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS cycle_count_items (
    id BIGSERIAL PRIMARY KEY,
    batch_id BIGINT NOT NULL REFERENCES cycle_count_batches(id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL,
    item_id BIGINT NOT NULL,
    expected_quantity DECIMAL(10,3),
    expected_location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cycle_count_results (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES cycle_count_items(id) ON DELETE CASCADE,
    counted_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    counted_at TIMESTAMPTZ DEFAULT NOW(),
    actual_quantity DECIMAL(10,3),
    actual_location VARCHAR(100),
    condition VARCHAR(50),
    notes TEXT,
    has_discrepancy BOOLEAN DEFAULT FALSE,
    discrepancy_type VARCHAR(50),
    discrepancy_notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_employee_number ON users(employee_number);
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department);
CREATE INDEX IF NOT EXISTS idx_tools_tool_number ON tools(tool_number);
CREATE INDEX IF NOT EXISTS idx_tools_location ON tools(location);
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_status ON checkouts(status);
CREATE INDEX IF NOT EXISTS idx_chemicals_part_number ON chemicals(part_number);
CREATE INDEX IF NOT EXISTS idx_chemicals_status ON chemicals(status);
CREATE INDEX IF NOT EXISTS idx_chemicals_expiration_date ON chemicals(expiration_date);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tools_updated_at BEFORE UPDATE ON tools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_checkouts_updated_at BEFORE UPDATE ON checkouts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chemicals_updated_at BEFORE UPDATE ON chemicals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chemical_issuances_updated_at BEFORE UPDATE ON chemical_issuances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_service_records_updated_at BEFORE UPDATE ON tool_service_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_calibrations_updated_at BEFORE UPDATE ON tool_calibrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_calibration_standards_updated_at BEFORE UPDATE ON calibration_standards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_announcements_updated_at BEFORE UPDATE ON announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cycle_count_schedules_updated_at BEFORE UPDATE ON cycle_count_schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cycle_count_batches_updated_at BEFORE UPDATE ON cycle_count_batches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cycle_count_items_updated_at BEFORE UPDATE ON cycle_count_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
