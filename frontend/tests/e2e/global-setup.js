/**
 * Global setup for Playwright tests
 * This runs once before all tests
 */

import { chromium } from '@playwright/test';

async function globalSetup() {
  console.log('🚀 Starting global setup for E2E tests...');
  
  // Create a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for the application to be ready
    console.log('⏳ Waiting for application to be ready...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    
    // Check if backend is responding
    const backendResponse = await page.request.get('http://localhost:5000/api/health');
    if (!backendResponse.ok()) {
      throw new Error('Backend is not responding');
    }
    
    console.log('✅ Application is ready for testing');
    
    // Create test data if needed
    await setupTestData(page);
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function setupTestData(page) {
  console.log('📊 Setting up test data...');
  
  try {
    // Create admin user for testing if it doesn't exist
    const adminLoginResponse = await page.request.post('http://localhost:5000/api/auth/login', {
      data: {
        employee_number: 'ADMIN001',
        password: 'admin123'
      }
    });
    
    if (adminLoginResponse.ok()) {
      console.log('✅ Admin user exists and is accessible');
    } else {
      console.log('⚠️ Admin user may need to be created manually');
    }
    
    // Add any other test data setup here
    
  } catch (error) {
    console.warn('⚠️ Test data setup encountered issues:', error.message);
    // Don't fail the entire setup for test data issues
  }
}

export default globalSetup;
