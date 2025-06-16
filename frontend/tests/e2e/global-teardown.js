/**
 * Global teardown for Playwright tests
 * This runs once after all tests
 */

import { globalCleanupTestData } from './utils/advanced-helpers.js';
import { cleanupTestData, login } from './utils/data-seeding.js';
import { testUsers } from './fixtures/test-data.js';

async function globalTeardown(config) {
  console.log('🧹 Starting global teardown for E2E tests...');

  try {
    // Clean up test data if needed
    await globalCleanupTestData(config);

    // Also clean up our seeded test data
    try {
      const adminToken = await login(testUsers.admin);
      await cleanupTestData(adminToken);
      console.log('✅ Seeded test data cleanup completed');
    } catch (cleanupError) {
      console.warn('⚠️ Test data cleanup had issues:', cleanupError.message);
    }

    console.log('✅ Global teardown completed successfully');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    process.exitCode = 1;   // signal failure while letting Playwright finish flushing reports
  }
}



export default globalTeardown;
