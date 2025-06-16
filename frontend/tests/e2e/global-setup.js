/**
 * Global setup for Playwright tests
 * This runs once before all tests
 */

import { chromium } from '@playwright/test';
import { setupTestData } from './utils/data-seeding.js';

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
    console.log('📊 Setting up test data...');
    const setupResult = await setupTestData();
    if (!setupResult.success) {
      throw new Error(`Test data setup failed: ${setupResult.error}`);
    }
    console.log('✅ Test data setup completed');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}



export default globalSetup;
