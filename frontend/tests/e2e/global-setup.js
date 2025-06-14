/**
 * Global setup for Playwright tests
 * This runs once before all tests
 */

import { chromium } from '@playwright/test';

async function globalSetup(config) {
  console.log('🚀 Starting global setup for E2E tests...');

  // Get URLs from environment or config
  const frontendUrl = process.env.FRONTEND_URL || process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';

  // Create a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for the application to be ready
    console.log('⏳ Waiting for application to be ready...');
    await page.goto(frontendUrl, { waitUntil: 'networkidle' });

    // Check if backend is responding
    const backendResponse = await page.request.get(`${backendUrl}/api/health`);
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

  const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';
  const adminEmployeeNumber = process.env.E2E_ADMIN_EMPLOYEE_NUMBER || 'ADMIN001';
  const adminPassword = process.env.E2E_ADMIN_PASSWORD || 'admin123';

  try {
    // Create admin user for testing if it doesn't exist
    const adminLoginResponse = await page.request.post(`${backendUrl}/api/auth/login`, {
      data: {
        employee_number: adminEmployeeNumber,
        password: adminPassword
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
