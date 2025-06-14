/**
 * Global teardown for Playwright tests
 * This runs once after all tests
 */

import { globalCleanupTestData } from './utils/advanced-helpers.js';

async function globalTeardown(config) {
  console.log('🧹 Starting global teardown for E2E tests...');

  try {
    // Clean up test data if needed
    await globalCleanupTestData(config);

    console.log('✅ Global teardown completed successfully');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error to avoid failing the test run
  }
}



export default globalTeardown;
