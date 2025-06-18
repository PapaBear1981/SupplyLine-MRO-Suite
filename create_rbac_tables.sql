-- Create RBAC tables for SupplyLine MRO Suite

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE(user_id, role_id)
);

-- Create role_permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);

-- Insert default roles
INSERT INTO roles (name, description, is_system_role) VALUES 
('Administrator', 'Full system access with all permissions', TRUE),
('Materials Manager', 'Can manage tools, chemicals, and users', TRUE),
('Maintenance User', 'Basic access to view and checkout tools', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Insert default permissions
INSERT INTO permissions (name, description, category) VALUES 
('dashboard.view', 'View dashboard', 'dashboard'),
('tool.view', 'View tools', 'tool'),
('tool.create', 'Create tools', 'tool'),
('tool.edit', 'Edit tools', 'tool'),
('tool.delete', 'Delete tools', 'tool'),
('tool.checkout', 'Checkout tools', 'tool'),
('user.view', 'View users', 'user'),
('user.create', 'Create users', 'user'),
('user.edit', 'Edit users', 'user'),
('user.delete', 'Delete users', 'user'),
('chemical.view', 'View chemicals', 'chemical'),
('chemical.create', 'Create chemicals', 'chemical'),
('chemical.edit', 'Edit chemicals', 'chemical'),
('chemical.delete', 'Delete chemicals', 'chemical'),
('chemical.issue', 'Issue chemicals', 'chemical'),
('checkout.view_all', 'View all checkouts', 'checkout'),
('checkout.manage_own', 'Manage own checkouts', 'checkout'),
('cycle_count.view', 'View cycle counts', 'cycle_count'),
('cycle_count.participate', 'Participate in cycle counts', 'cycle_count')
ON CONFLICT (name) DO NOTHING;

-- Assign Administrator role to admin user (user_id = 1)
INSERT INTO user_roles (user_id, role_id) 
SELECT 1, id FROM roles WHERE name = 'Administrator'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Assign all permissions to Administrator role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'Administrator'
ON CONFLICT (role_id, permission_id) DO NOTHING;
