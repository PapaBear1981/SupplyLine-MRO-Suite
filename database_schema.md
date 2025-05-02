# Database Schema

## Tables

### tools
```sql
CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_number TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    description TEXT,
    condition TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    employee_number TEXT NOT NULL UNIQUE,
    department TEXT,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### checkouts
```sql
CREATE TABLE checkouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### audit_log
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    action_details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This schema will be implemented in the development phase. Would you like me to:
1. Proceed with creating the Flask API structure in a new markdown file
2. Document the API endpoints next
3. Or move on to the frontend SPA design documentation?