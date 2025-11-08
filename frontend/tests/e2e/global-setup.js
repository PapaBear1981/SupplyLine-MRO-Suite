/**
 * Playwright Global Setup
 * 
 * This file runs once before all tests to ensure a clean, consistent test environment.
 * It resets and seeds the test database with predictable data.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Run the database seeding script
 */
async function seedDatabase() {
  console.log('🌱 Seeding test database...');
  
  const backendDir = path.resolve(__dirname, '../../../backend');
  const seedScript = path.join(backendDir, 'seed_e2e_test_data.py');
  
  try {
    // Use system Python (just 'python' - will use whatever is in PATH)
    const pythonCmd = 'python';

    // Run the seeding script
    const { stdout, stderr } = await execAsync(`${pythonCmd} "${seedScript}"`, {
      cwd: backendDir,
      timeout: 60000, // 60 second timeout
    });
    
    if (stdout) {
      console.log(stdout);
    }

    // Show all stderr output for debugging
    if (stderr) {
      console.log('Seeding stderr:', stderr);
    }
    
    console.log('✅ Test database seeded successfully');
  } catch (error) {
    console.error('❌ Failed to seed test database:', error.message);
    if (error.stdout) console.log('stdout:', error.stdout);
    if (error.stderr) console.error('stderr:', error.stderr);
    throw error;
  }
}

/**
 * Verify backend is running
 */
async function verifyBackend() {
  console.log('🔍 Verifying backend server...');
  
  const maxRetries = 10;
  const retryDelay = 2000; // 2 seconds
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('http://localhost:5000/api/health', {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      
      if (response.ok) {
        console.log('✅ Backend server is running');
        return;
      }
    } catch {
      if (i < maxRetries - 1) {
        console.log(`⏳ Waiting for backend server... (attempt ${i + 1}/${maxRetries})`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }
  
  console.warn('⚠️  Backend server may not be running. Tests may fail.');
  console.warn('   Please ensure backend is running on http://localhost:5000');
}

/**
 * Global setup function
 */
export default async function globalSetup() {
  console.log('\n🚀 Running Playwright Global Setup...\n');
  
  try {
    // Verify backend is running
    await verifyBackend();
    
    // Seed the database
    await seedDatabase();
    
    console.log('\n✅ Global setup completed successfully\n');
  } catch (error) {
    console.error('\n❌ Global setup failed:', error.message);
    console.error('\nPlease ensure:');
    console.error('  1. Backend server is running (python backend/run.py)');
    console.error('  2. Database is accessible');
    console.error('  3. Python environment is activated\n');
    throw error;
  }
}

