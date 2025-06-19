-- Essential database migration for SupplyLine MRO Suite
-- Creates the missing tables that are causing 500 errors

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

-- Add missing columns to chemicals table if they don't exist
DO $$ 
BEGIN
    -- Add reordering fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chemicals' AND column_name='needs_reorder') THEN
        ALTER TABLE chemicals ADD COLUMN needs_reorder BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chemicals' AND column_name='reorder_status') THEN
        ALTER TABLE chemicals ADD COLUMN reorder_status TEXT DEFAULT 'not_needed';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chemicals' AND column_name='reorder_date') THEN
        ALTER TABLE chemicals ADD COLUMN reorder_date TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chemicals' AND column_name='expected_delivery_date') THEN
        ALTER TABLE chemicals ADD COLUMN expected_delivery_date TIMESTAMP;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='chemicals' AND column_name='minimum_stock_level') THEN
        ALTER TABLE chemicals ADD COLUMN minimum_stock_level DECIMAL(10,2);
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_checkouts_tool_id ON checkouts(tool_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_user_id ON checkouts(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_calibrations_tool_id ON tool_calibrations(tool_id);
CREATE INDEX IF NOT EXISTS idx_calibration_standards_standard_number ON calibration_standards(standard_number);
