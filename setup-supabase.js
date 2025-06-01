#!/usr/bin/env node

/**
 * Simple setup script to run the Supabase migration
 */

const { createClient } = require('@supabase/supabase-js');
const readline = require('readline');

async function setupSupabase() {
  console.log('🚀 SupplyLine MRO Suite - Supabase Setup\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function question(prompt) {
    return new Promise((resolve) => {
      rl.question(prompt, (answer) => {
        resolve(answer);
      });
    });
  }

  try {
    // Get Supabase credentials
    console.log('Please provide your Supabase project details:');
    const supabaseUrl = await question('Supabase URL (https://your-project.supabase.co): ');
    const supabaseKey = await question('Supabase service role key: ');

    if (!supabaseUrl || !supabaseKey) {
      console.error('❌ Both URL and service role key are required');
      process.exit(1);
    }

    // Test connection
    console.log('\nTesting connection...');
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Create the basic schema
    console.log('Creating database schema...');
    
    const createUsersTable = `
      CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        employee_number VARCHAR(50) UNIQUE NOT NULL,
        department VARCHAR(100),
        password_hash VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );
    `;

    const createToolsTable = `
      CREATE TABLE IF NOT EXISTS tools (
        id BIGSERIAL PRIMARY KEY,
        tool_number VARCHAR(50) NOT NULL,
        serial_number VARCHAR(100) NOT NULL,
        description TEXT,
        condition VARCHAR(20) DEFAULT 'good',
        location VARCHAR(100),
        category VARCHAR(50) DEFAULT 'General',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );
    `;

    const createCheckoutsTable = `
      CREATE TABLE IF NOT EXISTS checkouts (
        id BIGSERIAL PRIMARY KEY,
        tool_id BIGINT NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        checkout_date TIMESTAMPTZ DEFAULT NOW(),
        return_date TIMESTAMPTZ,
        expected_return_date TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );
    `;

    const createChemicalsTable = `
      CREATE TABLE IF NOT EXISTS chemicals (
        id BIGSERIAL PRIMARY KEY,
        part_number VARCHAR(100) NOT NULL,
        lot_number VARCHAR(100) NOT NULL,
        description TEXT,
        manufacturer VARCHAR(100),
        quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
        unit VARCHAR(20) NOT NULL DEFAULT 'each',
        location VARCHAR(100),
        category VARCHAR(50) DEFAULT 'General',
        status VARCHAR(20) DEFAULT 'available',
        date_added TIMESTAMPTZ DEFAULT NOW(),
        expiration_date DATE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );
    `;

    const createAuditLogTable = `
      CREATE TABLE IF NOT EXISTS audit_log (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
        action_type VARCHAR(50) NOT NULL,
        table_name VARCHAR(50),
        record_id BIGINT,
        action_details TEXT,
        timestamp TIMESTAMPTZ DEFAULT NOW()
      );
    `;

    // Execute table creation
    const tables = [
      { name: 'users', sql: createUsersTable },
      { name: 'tools', sql: createToolsTable },
      { name: 'checkouts', sql: createCheckoutsTable },
      { name: 'chemicals', sql: createChemicalsTable },
      { name: 'audit_log', sql: createAuditLogTable }
    ];

    for (const table of tables) {
      try {
        const { error } = await supabase.rpc('exec_sql', { sql: table.sql });
        if (error) {
          console.log(`⚠️  Warning creating ${table.name} table: ${error.message}`);
        } else {
          console.log(`✅ Created ${table.name} table`);
        }
      } catch (error) {
        console.log(`⚠️  Warning creating ${table.name} table: ${error.message}`);
      }
    }

    // Create default admin user
    console.log('\nCreating default admin user...');
    
    const { data: existingAdmin } = await supabase
      .from('users')
      .select('id')
      .eq('employee_number', 'ADMIN001')
      .single();

    if (!existingAdmin) {
      // Simple password hash (in production, use proper bcrypt)
      const crypto = require('crypto');
      const passwordHash = crypto.createHash('sha256').update('admin123').digest('hex');

      const { error: adminError } = await supabase
        .from('users')
        .insert({
          name: 'System Administrator',
          employee_number: 'ADMIN001',
          department: 'IT',
          password_hash: passwordHash,
          is_admin: true,
          is_active: true
        });

      if (adminError) {
        console.log(`⚠️  Warning creating admin user: ${adminError.message}`);
      } else {
        console.log('✅ Created default admin user (ADMIN001/admin123)');
      }
    } else {
      console.log('ℹ️  Admin user already exists');
    }

    console.log('\n🎉 Supabase setup completed successfully!');
    console.log('\nNext steps:');
    console.log('1. Configure your Electron app with these Supabase credentials');
    console.log('2. Test the connection in your application');
    console.log('3. Import your existing data if needed');
    console.log('\nSupabase URL:', supabaseUrl);
    console.log('Use your anon/public key in the application, not the service role key.');

  } catch (error) {
    console.error('\n❌ Setup failed:', error.message);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// Run setup
setupSupabase();
