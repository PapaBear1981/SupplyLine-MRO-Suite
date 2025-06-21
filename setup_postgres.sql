-- PostgreSQL Setup Script for SupplyLine MRO Suite
-- Run this script as a PostgreSQL superuser to set up the database

-- Create database user
CREATE USER supplyline_user WITH PASSWORD 'supplyline_pass';

-- Create database
CREATE DATABASE supplyline_mro OWNER supplyline_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE supplyline_mro TO supplyline_user;

-- Connect to the database
\c supplyline_mro;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO supplyline_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO supplyline_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO supplyline_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO supplyline_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO supplyline_user;
