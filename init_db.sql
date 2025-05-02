-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- tools table
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_number TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    description TEXT,
    condition TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    employee_number TEXT NOT NULL UNIQUE,
    department TEXT,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- checkouts table
CREATE TABLE IF NOT EXISTS checkouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- audit_log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    action_details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);