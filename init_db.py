import os
import sqlite3

# Create database directory if it doesn't exist
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Created database directory: {db_dir}")

# Create database file
db_path = os.path.join(db_dir, 'tools.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    employee_number TEXT UNIQUE NOT NULL,
    department TEXT,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reset_token TEXT,
    reset_token_expiry TIMESTAMP,
    remember_token TEXT,
    remember_token_expiry TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_number TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    description TEXT,
    condition TEXT,
    location TEXT,
    category TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS checkouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    expected_return_date TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Create admin user
from werkzeug.security import generate_password_hash
admin_password_hash = generate_password_hash('admin123')
cursor.execute('''
INSERT INTO users (name, employee_number, department, password_hash, is_admin)
VALUES (?, ?, ?, ?, ?)
''', ('Admin', 'ADMIN001', 'IT', admin_password_hash, 1))

# Create test users
test_users = [
    ('John Doe', 'EMP001', 'Maintenance', generate_password_hash('password123'), 0),
    ('Jane Smith', 'EMP002', 'Maintenance', generate_password_hash('password123'), 0),
    ('Bob Johnson', 'EMP003', 'Materials', generate_password_hash('password123'), 0),
    ('Alice Brown', 'EMP004', 'Engineering', generate_password_hash('password123'), 0)
]

for user in test_users:
    cursor.execute('''
    INSERT INTO users (name, employee_number, department, password_hash, is_admin)
    VALUES (?, ?, ?, ?, ?)
    ''', user)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized successfully with admin user and test users")
