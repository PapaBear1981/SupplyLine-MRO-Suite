-- Fix Tools Table Schema Migration for SupplyLine MRO Suite
-- Resolves tool_number vs tool_id column inconsistency

-- First, check if we need to rename tool_id to tool_number
DO $$ 
BEGIN
    -- Check if tool_id column exists and tool_number doesn't
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='tool_id') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='tool_number') THEN
        
        -- Rename tool_id to tool_number to match SQLAlchemy model
        ALTER TABLE tools RENAME COLUMN tool_id TO tool_number;
        RAISE NOTICE 'Renamed tool_id column to tool_number';
        
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='tool_number') THEN
        RAISE NOTICE 'tool_number column already exists, no rename needed';
    ELSE
        RAISE NOTICE 'Neither tool_id nor tool_number found, table may need to be created';
    END IF;
END $$;

-- Ensure all required columns exist in tools table
DO $$ 
BEGIN
    -- Add missing columns if they don't exist
    
    -- Add serial_number if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='serial_number') THEN
        ALTER TABLE tools ADD COLUMN serial_number VARCHAR(100);
        RAISE NOTICE 'Added serial_number column';
    END IF;
    
    -- Add condition if missing  
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='condition') THEN
        ALTER TABLE tools ADD COLUMN condition VARCHAR(50);
        RAISE NOTICE 'Added condition column';
    END IF;
    
    -- Add category if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='category') THEN
        ALTER TABLE tools ADD COLUMN category VARCHAR(100) DEFAULT 'General';
        RAISE NOTICE 'Added category column';
    END IF;
    
    -- Add status if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='status') THEN
        ALTER TABLE tools ADD COLUMN status VARCHAR(50) DEFAULT 'available';
        RAISE NOTICE 'Added status column';
    END IF;
    
    -- Add status_reason if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='status_reason') THEN
        ALTER TABLE tools ADD COLUMN status_reason TEXT;
        RAISE NOTICE 'Added status_reason column';
    END IF;
    
    -- Add calibration columns if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='requires_calibration') THEN
        ALTER TABLE tools ADD COLUMN requires_calibration BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added requires_calibration column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='calibration_status') THEN
        ALTER TABLE tools ADD COLUMN calibration_status VARCHAR(50) DEFAULT 'not_applicable';
        RAISE NOTICE 'Added calibration_status column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='last_calibration_date') THEN
        ALTER TABLE tools ADD COLUMN last_calibration_date TIMESTAMP;
        RAISE NOTICE 'Added last_calibration_date column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='next_calibration_date') THEN
        ALTER TABLE tools ADD COLUMN next_calibration_date TIMESTAMP;
        RAISE NOTICE 'Added next_calibration_date column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='calibration_frequency_days') THEN
        ALTER TABLE tools ADD COLUMN calibration_frequency_days INTEGER;
        RAISE NOTICE 'Added calibration_frequency_days column';
    END IF;
    
    -- Add updated_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tools' AND column_name='updated_at') THEN
        ALTER TABLE tools ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column';
    END IF;
    
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tools_tool_number ON tools(tool_number);
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_location ON tools(location);

-- Print success message
DO $$ 
BEGIN
    RAISE NOTICE 'Tools table schema migration completed successfully!';
    RAISE NOTICE 'All column inconsistencies have been resolved.';
    RAISE NOTICE 'The Reports page should now work without database errors.';
END $$;
