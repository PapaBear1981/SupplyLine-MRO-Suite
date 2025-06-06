-- SupplyLine MRO Suite - Complete Supabase Schema Migration
-- This script sets up the complete database schema with all tables, relationships, and security policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Users table (enhanced)
ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS remember_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS remember_token_expiry TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS theme VARCHAR(20) DEFAULT 'light';
ALTER TABLE users ADD COLUMN IF NOT EXISTS help_enabled BOOLEAN DEFAULT true;

-- Add unique constraint on employee_number if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'users_employee_number_key'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_employee_number_key UNIQUE (employee_number);
    END IF;
END $$;

-- Tools table (enhanced)
ALTER TABLE tools ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(255);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS model VARCHAR(255);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS purchase_date DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(10,2);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS warranty_expiry DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS last_service_date DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS next_service_date DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS service_interval_days INTEGER;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS requires_calibration BOOLEAN DEFAULT false;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS calibration_interval_days INTEGER;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS last_calibration_date DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS next_calibration_date DATE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500);

-- Add unique constraint on tool_number if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'tools_tool_number_key'
    ) THEN
        ALTER TABLE tools ADD CONSTRAINT tools_tool_number_key UNIQUE (tool_number);
    END IF;
END $$;

-- Checkouts table (enhanced)
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS checkout_date TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS expected_return_date TIMESTAMPTZ;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS actual_return_date TIMESTAMPTZ;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS returned_by_user_id BIGINT REFERENCES users(id);
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS checkout_notes TEXT;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS return_notes TEXT;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS is_returned BOOLEAN DEFAULT false;

-- Add foreign key constraints if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'checkouts_tool_id_fkey'
    ) THEN
        ALTER TABLE checkouts ADD CONSTRAINT checkouts_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES tools(id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'checkouts_user_id_fkey'
    ) THEN
        ALTER TABLE checkouts ADD CONSTRAINT checkouts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- Chemicals table (enhanced)
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(255);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS supplier VARCHAR(255);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS cas_number VARCHAR(50);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS sds_url VARCHAR(500);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS hazard_class VARCHAR(100);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS storage_requirements TEXT;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS disposal_instructions TEXT;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS purchase_date DATE;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(10,2);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS reorder_point INTEGER DEFAULT 0;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS reorder_quantity INTEGER DEFAULT 0;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500);
ALTER TABLE chemicals ADD COLUMN IF NOT EXISTS alternate_part_number VARCHAR(100);

-- Create additional tables that might be missing

-- User Activity table
CREATE TABLE IF NOT EXISTS user_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool Service Records table
CREATE TABLE IF NOT EXISTS tool_service_records (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT NOT NULL REFERENCES tools(id),
    service_date DATE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    description TEXT,
    cost DECIMAL(10,2),
    performed_by VARCHAR(255),
    next_service_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chemical Issuances table
CREATE TABLE IF NOT EXISTS chemical_issuances (
    id BIGSERIAL PRIMARY KEY,
    chemical_id BIGINT NOT NULL REFERENCES chemicals(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    quantity_issued INTEGER NOT NULL,
    issue_date TIMESTAMPTZ DEFAULT NOW(),
    purpose TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expiration_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

-- Announcement Reads table
CREATE TABLE IF NOT EXISTS announcement_reads (
    id BIGSERIAL PRIMARY KEY,
    announcement_id BIGINT NOT NULL REFERENCES announcements(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    read_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool Calibrations table
CREATE TABLE IF NOT EXISTS tool_calibrations (
    id BIGSERIAL PRIMARY KEY,
    tool_id BIGINT NOT NULL REFERENCES tools(id),
    calibration_date DATE NOT NULL,
    calibrated_by VARCHAR(255),
    calibration_standard VARCHAR(255),
    results TEXT,
    passed BOOLEAN DEFAULT true,
    next_calibration_date DATE,
    certificate_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Calibration Standards table
CREATE TABLE IF NOT EXISTS calibration_standards (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    standard_number VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255),
    calibration_date DATE,
    expiry_date DATE,
    certificate_number VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool Calibration Standards junction table
CREATE TABLE IF NOT EXISTS tool_calibration_standards (
    id BIGSERIAL PRIMARY KEY,
    tool_calibration_id BIGINT NOT NULL REFERENCES tool_calibrations(id),
    calibration_standard_id BIGINT NOT NULL REFERENCES calibration_standards(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create updated_at triggers for all tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name != 'audit_log'
    LOOP
        -- Check if updated_at column exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = t AND column_name = 'updated_at'
        ) THEN
            -- Drop trigger if exists and recreate
            EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', t, t);
            EXECUTE format('CREATE TRIGGER update_%I_updated_at 
                           BEFORE UPDATE ON %I 
                           FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
        END IF;
    END LOOP;
END $$;
