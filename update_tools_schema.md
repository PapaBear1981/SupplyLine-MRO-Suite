# Database Schema Update Script

## Purpose
This script (`update_tools_schema.py`) is used to update the SQLite database schema to ensure compatibility with the latest version of the application. It adds missing columns and tables that are required for the tool service functionality.

## What it does
1. Adds a `category` column to the `tools` table with a default value of 'General'
2. Verifies that the `status` column exists in the `tools` table
3. Verifies that the `status_reason` column exists in the `tools` table
4. Creates the `tool_service_records` table if it doesn't exist

## When to use
Run this script when:
- Upgrading from version 1.0.0 to version 1.1.1
- Experiencing database schema compatibility issues
- Getting errors related to missing columns in the tools table

## How to run
```bash
python update_tools_schema.py
```

## Output
The script will output information about the current state of the database and the changes it makes.
