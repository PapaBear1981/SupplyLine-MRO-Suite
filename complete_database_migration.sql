-- COMPLETE DATABASE MIGRATION FOR 100% FUNCTIONALITY
-- This script creates ALL missing tables and fixes schema issues

-- Fix tools table schema (rename tool_id to tool_number if needed)
DO $$
BEGIN
    -- Check if tool_id column exists and tool_number doesn't
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tools' AND column_name = 'tool_id')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tools' AND column_name = 'tool_number') THEN
        ALTER TABLE tools RENAME COLUMN tool_id TO tool_number;
        RAISE NOTICE 'Renamed tools.tool_id to tools.tool_number';
    END IF;
END $$;

-- Ensure tools table has all required columns
ALTER TABLE tools ADD COLUMN IF NOT EXISTS requires_calibration BOOLEAN DEFAULT FALSE;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS calibration_frequency_days INTEGER;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS last_calibration_date TIMESTAMP;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS next_calibration_date TIMESTAMP;
ALTER TABLE tools ADD COLUMN IF NOT EXISTS calibration_status TEXT DEFAULT 'not_required';

-- Create tool_calibrations table
CREATE TABLE IF NOT EXISTS tool_calibrations (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL,
    calibration_date TIMESTAMP NOT NULL,
    next_calibration_date TIMESTAMP,
    performed_by_user_id INTEGER NOT NULL,
    calibration_notes TEXT,
    calibration_status TEXT NOT NULL DEFAULT 'completed',
    calibration_certificate_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (performed_by_user_id) REFERENCES users(id)
);

-- Create calibration_standards table
CREATE TABLE IF NOT EXISTS calibration_standards (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    serial_number TEXT,
    manufacturer TEXT,
    model TEXT,
    calibration_interval_days INTEGER NOT NULL DEFAULT 365,
    last_calibration_date TIMESTAMP,
    next_calibration_date TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tool_calibration_standards table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS tool_calibration_standards (
    id SERIAL PRIMARY KEY,
    tool_calibration_id INTEGER NOT NULL,
    calibration_standard_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_calibration_id) REFERENCES tool_calibrations(id) ON DELETE CASCADE,
    FOREIGN KEY (calibration_standard_id) REFERENCES calibration_standards(id) ON DELETE CASCADE,
    UNIQUE(tool_calibration_id, calibration_standard_id)
);

-- Create cycle count tables (comprehensive)
CREATE TABLE IF NOT EXISTS cycle_count_schedules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL,
    method TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS cycle_count_batches (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (schedule_id) REFERENCES cycle_count_schedules(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS cycle_count_items (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    expected_quantity REAL,
    expected_location TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES cycle_count_batches(id)
);

CREATE TABLE IF NOT EXISTS cycle_count_results (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    counted_by INTEGER NOT NULL,
    counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_quantity REAL,
    actual_location TEXT,
    condition TEXT,
    notes TEXT,
    has_discrepancy BOOLEAN DEFAULT FALSE,
    discrepancy_type TEXT,
    discrepancy_notes TEXT,
    FOREIGN KEY (item_id) REFERENCES cycle_count_items(id),
    FOREIGN KEY (counted_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS cycle_count_adjustments (
    id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    adjustment_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    adjusted_by INTEGER NOT NULL,
    adjusted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (result_id) REFERENCES cycle_count_results(id),
    FOREIGN KEY (adjusted_by) REFERENCES users(id)
);

-- Create missing system tables
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tools_tool_number ON tools(tool_number);
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_requires_calibration ON tools(requires_calibration);
CREATE INDEX IF NOT EXISTS idx_tools_next_calibration_date ON tools(next_calibration_date);

CREATE INDEX IF NOT EXISTS idx_tool_calibrations_tool_id ON tool_calibrations(tool_id);
CREATE INDEX IF NOT EXISTS idx_tool_calibrations_next_date ON tool_calibrations(next_calibration_date);

CREATE INDEX IF NOT EXISTS idx_cycle_count_schedules_active ON cycle_count_schedules(is_active);
CREATE INDEX IF NOT EXISTS idx_cycle_count_batches_status ON cycle_count_batches(status);
CREATE INDEX IF NOT EXISTS idx_cycle_count_items_batch_id ON cycle_count_items(batch_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_items_status ON cycle_count_items(status);

-- Insert default system settings
INSERT INTO system_settings (category, key, value, description) VALUES
('session', 'timeout_minutes', '30', 'Session timeout in minutes'),
('security', 'max_login_attempts', '5', 'Maximum failed login attempts'),
('security', 'lockout_duration_minutes', '15', 'Account lockout duration in minutes'),
('calibration', 'default_frequency_days', '365', 'Default calibration frequency in days'),
('notifications', 'calibration_reminder_days', '30', 'Days before calibration due to send reminder')
ON CONFLICT (category, key) DO NOTHING;

-- Insert sample calibration standards
INSERT INTO calibration_standards (name, description, manufacturer, model, calibration_interval_days) VALUES
('Digital Multimeter Standard', 'Primary standard for electrical measurements', 'Fluke', 'DMM-STD-001', 365),
('Torque Wrench Standard', 'Primary standard for torque measurements', 'Snap-on', 'TRQ-STD-001', 365),
('Pressure Gauge Standard', 'Primary standard for pressure measurements', 'Ashcroft', 'PRS-STD-001', 365)
ON CONFLICT DO NOTHING;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE '=== COMPLETE DATABASE MIGRATION FINISHED ===';
    RAISE NOTICE 'Created/verified all required tables:';
    RAISE NOTICE '✓ tools (with calibration columns)';
    RAISE NOTICE '✓ tool_calibrations';
    RAISE NOTICE '✓ calibration_standards';
    RAISE NOTICE '✓ tool_calibration_standards';
    RAISE NOTICE '✓ cycle_count_schedules';
    RAISE NOTICE '✓ cycle_count_batches';
    RAISE NOTICE '✓ cycle_count_items';
    RAISE NOTICE '✓ cycle_count_results';
    RAISE NOTICE '✓ cycle_count_adjustments';
    RAISE NOTICE '✓ system_settings';
    RAISE NOTICE '✓ All indexes created';
    RAISE NOTICE '✓ Sample data inserted';
    RAISE NOTICE 'Database is now ready for 100% functionality!';
END $$;
