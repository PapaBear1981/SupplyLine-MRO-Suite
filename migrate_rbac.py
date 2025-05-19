"""
Migration script to add RBAC tables and migrate existing users to the new role system
"""
import os
import sys
import sqlite3
from backend.migrations.add_rbac_tables import run_migration

def main():
    print("Starting RBAC migration...")
    
    # Run the migration
    success = run_migration()
    
    if success:
        print("RBAC migration completed successfully!")
        return 0
    else:
        print("RBAC migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
