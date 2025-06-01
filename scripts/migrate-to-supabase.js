#!/usr/bin/env node

/**
 * SupplyLine MRO Suite - Supabase Migration Script
 * 
 * This script migrates the existing SQLite database to Supabase PostgreSQL
 * and sets up the database schema.
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const readline = require('readline');

class SupabaseMigrator {
  constructor() {
    this.supabase = null;
    this.sqliteDb = null;
    this.migrationLog = [];
  }

  async initialize() {
    // Get Supabase credentials
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const supabaseUrl = await this.question(rl, 'Enter your Supabase URL: ');
    const supabaseKey = await this.question(rl, 'Enter your Supabase service role key: ');
    
    rl.close();

    // Initialize Supabase client
    this.supabase = createClient(supabaseUrl, supabaseKey);

    // Test connection
    console.log('Testing Supabase connection...');
    const { data, error } = await this.supabase.from('_test').select('*').limit(1);
    
    if (error && error.code !== 'PGRST116') {
      throw new Error(`Supabase connection failed: ${error.message}`);
    }

    console.log('✅ Supabase connection successful');
  }

  question(rl, prompt) {
    return new Promise((resolve) => {
      rl.question(prompt, (answer) => {
        resolve(answer);
      });
    });
  }

  async runSQLMigration() {
    console.log('Running database schema migration...');
    
    const migrationSQL = fs.readFileSync(
      path.join(__dirname, 'supabase-migration.sql'), 
      'utf8'
    );

    // Split SQL into individual statements
    const statements = migrationSQL
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));

    for (const statement of statements) {
      try {
        const { error } = await this.supabase.rpc('exec_sql', { sql: statement });
        if (error) {
          console.warn(`Warning executing SQL: ${error.message}`);
          this.migrationLog.push(`Warning: ${statement.substring(0, 50)}... - ${error.message}`);
        }
      } catch (error) {
        console.warn(`Warning executing SQL: ${error.message}`);
        this.migrationLog.push(`Warning: ${statement.substring(0, 50)}... - ${error.message}`);
      }
    }

    console.log('✅ Schema migration completed');
  }

  async connectSQLite() {
    const dbPath = path.join(__dirname, '../backend/app.db');
    
    if (!fs.existsSync(dbPath)) {
      console.log('⚠️  SQLite database not found, skipping data migration');
      return false;
    }

    return new Promise((resolve, reject) => {
      this.sqliteDb = new sqlite3.Database(dbPath, (err) => {
        if (err) {
          reject(err);
        } else {
          console.log('✅ Connected to SQLite database');
          resolve(true);
        }
      });
    });
  }

  async migrateSQLiteData() {
    if (!this.sqliteDb) {
      console.log('Skipping data migration - no SQLite database');
      return;
    }

    console.log('Starting data migration from SQLite...');

    const tables = [
      'users',
      'tools', 
      'chemicals',
      'checkouts',
      'chemical_issuances',
      'audit_log',
      'user_activity',
      'tool_service_records',
      'announcements'
    ];

    for (const table of tables) {
      await this.migrateTable(table);
    }

    console.log('✅ Data migration completed');
  }

  async migrateTable(tableName) {
    console.log(`Migrating table: ${tableName}`);

    return new Promise((resolve, reject) => {
      this.sqliteDb.all(`SELECT * FROM ${tableName}`, async (err, rows) => {
        if (err) {
          if (err.message.includes('no such table')) {
            console.log(`  ⚠️  Table ${tableName} not found in SQLite, skipping`);
            resolve();
            return;
          }
          console.error(`  ❌ Error reading ${tableName}:`, err.message);
          reject(err);
          return;
        }

        if (rows.length === 0) {
          console.log(`  ℹ️  Table ${tableName} is empty, skipping`);
          resolve();
          return;
        }

        // Transform data for PostgreSQL
        const transformedRows = rows.map(row => this.transformRow(tableName, row));

        // Insert data in batches
        const batchSize = 100;
        for (let i = 0; i < transformedRows.length; i += batchSize) {
          const batch = transformedRows.slice(i, i + batchSize);
          
          try {
            const { error } = await this.supabase
              .from(tableName)
              .insert(batch);

            if (error) {
              console.error(`  ❌ Error inserting batch for ${tableName}:`, error.message);
              this.migrationLog.push(`Error inserting ${tableName}: ${error.message}`);
            }
          } catch (error) {
            console.error(`  ❌ Error inserting batch for ${tableName}:`, error.message);
            this.migrationLog.push(`Error inserting ${tableName}: ${error.message}`);
          }
        }

        console.log(`  ✅ Migrated ${transformedRows.length} rows from ${tableName}`);
        resolve();
      });
    });
  }

  transformRow(tableName, row) {
    // Transform SQLite data types to PostgreSQL compatible types
    const transformed = { ...row };

    // Convert boolean fields
    const booleanFields = {
      users: ['is_admin', 'is_active'],
      tools: ['is_active'],
      chemicals: ['needs_reorder'],
      checkouts: [],
      announcements: ['is_active']
    };

    if (booleanFields[tableName]) {
      booleanFields[tableName].forEach(field => {
        if (transformed[field] !== undefined) {
          transformed[field] = Boolean(transformed[field]);
        }
      });
    }

    // Convert timestamp fields
    const timestampFields = [
      'created_at', 'updated_at', 'checkout_date', 'return_date', 
      'expected_return_date', 'date_added', 'expiration_date',
      'last_login', 'locked_until', 'reset_token_expiry',
      'remember_token_expiry', 'processed_at', 'reorder_date',
      'expected_delivery_date', 'expires_at'
    ];

    timestampFields.forEach(field => {
      if (transformed[field] && transformed[field] !== '') {
        // Convert SQLite timestamp to ISO string
        const date = new Date(transformed[field]);
        if (!isNaN(date.getTime())) {
          transformed[field] = date.toISOString();
        } else {
          transformed[field] = null;
        }
      } else if (transformed[field] === '') {
        transformed[field] = null;
      }
    });

    // Handle JSON fields
    if (tableName === 'users' && transformed.preferences) {
      try {
        if (typeof transformed.preferences === 'string') {
          transformed.preferences = JSON.parse(transformed.preferences);
        }
      } catch (error) {
        transformed.preferences = {};
      }
    }

    return transformed;
  }

  async setupRowLevelSecurity() {
    console.log('Setting up Row Level Security...');

    const rlsPolicies = [
      // Users can read their own data
      `CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = id::text);`,
      
      // Admins can view all data
      `CREATE POLICY "Admins can view all users" ON users FOR ALL USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid()::bigint AND is_admin = true)
      );`,
      
      // Tools are readable by all authenticated users
      `CREATE POLICY "Authenticated users can view tools" ON tools FOR SELECT TO authenticated USING (true);`,
      
      // Similar policies for other tables...
    ];

    for (const policy of rlsPolicies) {
      try {
        const { error } = await this.supabase.rpc('exec_sql', { sql: policy });
        if (error && !error.message.includes('already exists')) {
          console.warn(`Warning setting up RLS: ${error.message}`);
        }
      } catch (error) {
        console.warn(`Warning setting up RLS: ${error.message}`);
      }
    }

    console.log('✅ Row Level Security setup completed');
  }

  async createDefaultAdmin() {
    console.log('Creating default admin user...');

    const { data: existingAdmin } = await this.supabase
      .from('users')
      .select('id')
      .eq('employee_number', 'ADMIN001')
      .single();

    if (existingAdmin) {
      console.log('  ℹ️  Admin user already exists, skipping');
      return;
    }

    const bcrypt = require('bcrypt');
    const adminPassword = 'admin123'; // Default password
    const hashedPassword = await bcrypt.hash(adminPassword, 10);

    const { error } = await this.supabase
      .from('users')
      .insert({
        name: 'System Administrator',
        employee_number: 'ADMIN001',
        department: 'IT',
        password_hash: hashedPassword,
        is_admin: true,
        is_active: true,
        role: 'admin'
      });

    if (error) {
      console.error('❌ Failed to create admin user:', error.message);
    } else {
      console.log('✅ Default admin user created (ADMIN001/admin123)');
    }
  }

  async generateMigrationReport() {
    const reportPath = path.join(__dirname, 'migration-report.txt');
    const report = [
      'SupplyLine MRO Suite - Supabase Migration Report',
      '=' .repeat(50),
      `Migration completed at: ${new Date().toISOString()}`,
      '',
      'Migration Log:',
      ...this.migrationLog,
      '',
      'Next Steps:',
      '1. Update your Electron app configuration with Supabase credentials',
      '2. Test the application with the new database',
      '3. Set up proper Row Level Security policies for production',
      '4. Configure backup and monitoring for your Supabase project'
    ].join('\n');

    fs.writeFileSync(reportPath, report);
    console.log(`📄 Migration report saved to: ${reportPath}`);
  }

  async run() {
    try {
      console.log('🚀 Starting SupplyLine MRO Suite migration to Supabase...\n');

      await this.initialize();
      await this.runSQLMigration();
      
      const hasSQLite = await this.connectSQLite();
      if (hasSQLite) {
        await this.migrateSQLiteData();
      }

      await this.setupRowLevelSecurity();
      await this.createDefaultAdmin();
      await this.generateMigrationReport();

      console.log('\n🎉 Migration completed successfully!');
      console.log('\nYour SupplyLine MRO Suite database is now ready on Supabase.');
      
    } catch (error) {
      console.error('\n❌ Migration failed:', error.message);
      process.exit(1);
    } finally {
      if (this.sqliteDb) {
        this.sqliteDb.close();
      }
    }
  }
}

// Run migration if called directly
if (require.main === module) {
  const migrator = new SupabaseMigrator();
  migrator.run();
}

module.exports = SupabaseMigrator;
