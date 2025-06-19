-- Comprehensive Cycle Count Tables Migration for SupplyLine MRO Suite
-- Creates all missing cycle count tables to fix blank Cycle Counts page

-- Create cycle_count_schedules table
CREATE TABLE IF NOT EXISTS cycle_count_schedules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL,  -- daily, weekly, monthly, quarterly, annual
    method TEXT NOT NULL,     -- ABC, random, location, category
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create cycle_count_batches table
CREATE TABLE IF NOT EXISTS cycle_count_batches (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,     -- draft, active, review, completed, archived
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (schedule_id) REFERENCES cycle_count_schedules(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create cycle_count_items table
CREATE TABLE IF NOT EXISTS cycle_count_items (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,  -- tool, chemical
    item_id INTEGER NOT NULL,
    expected_quantity REAL,
    expected_location TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, counted, reviewed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES cycle_count_batches(id)
);

-- Create cycle_count_results table
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
    discrepancy_type TEXT,    -- quantity, location, condition, missing, extra
    discrepancy_notes TEXT,
    FOREIGN KEY (item_id) REFERENCES cycle_count_items(id),
    FOREIGN KEY (counted_by) REFERENCES users(id)
);

-- Create cycle_count_adjustments table
CREATE TABLE IF NOT EXISTS cycle_count_adjustments (
    id SERIAL PRIMARY KEY,
    result_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,  -- tool, chemical
    item_id INTEGER NOT NULL,
    adjustment_type TEXT NOT NULL,  -- quantity, location, condition, status
    old_value TEXT,
    new_value TEXT,
    adjusted_by INTEGER NOT NULL,
    adjusted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (result_id) REFERENCES cycle_count_results(id),
    FOREIGN KEY (adjusted_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cycle_count_schedules_created_by ON cycle_count_schedules(created_by);
CREATE INDEX IF NOT EXISTS idx_cycle_count_schedules_is_active ON cycle_count_schedules(is_active);
CREATE INDEX IF NOT EXISTS idx_cycle_count_schedules_frequency ON cycle_count_schedules(frequency);

CREATE INDEX IF NOT EXISTS idx_cycle_count_batches_schedule_id ON cycle_count_batches(schedule_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_batches_status ON cycle_count_batches(status);
CREATE INDEX IF NOT EXISTS idx_cycle_count_batches_created_by ON cycle_count_batches(created_by);
CREATE INDEX IF NOT EXISTS idx_cycle_count_batches_start_date ON cycle_count_batches(start_date);

CREATE INDEX IF NOT EXISTS idx_cycle_count_items_batch_id ON cycle_count_items(batch_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_items_item_type_id ON cycle_count_items(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_items_status ON cycle_count_items(status);

CREATE INDEX IF NOT EXISTS idx_cycle_count_results_item_id ON cycle_count_results(item_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_results_counted_by ON cycle_count_results(counted_by);
CREATE INDEX IF NOT EXISTS idx_cycle_count_results_has_discrepancy ON cycle_count_results(has_discrepancy);
CREATE INDEX IF NOT EXISTS idx_cycle_count_results_counted_at ON cycle_count_results(counted_at);

CREATE INDEX IF NOT EXISTS idx_cycle_count_adjustments_result_id ON cycle_count_adjustments(result_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_adjustments_item_type_id ON cycle_count_adjustments(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_cycle_count_adjustments_adjusted_by ON cycle_count_adjustments(adjusted_by);

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Cycle count tables migration completed successfully!';
    RAISE NOTICE 'Created tables: cycle_count_schedules, cycle_count_batches, cycle_count_items, cycle_count_results, cycle_count_adjustments';
    RAISE NOTICE 'The Cycle Counts page should now work properly.';
END $$;
