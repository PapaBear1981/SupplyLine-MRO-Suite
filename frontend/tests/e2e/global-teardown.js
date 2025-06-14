/**
 * Global teardown for Playwright tests
 * This runs once after all tests
 */

async function globalTeardown() {
  console.log('🧹 Starting global teardown for E2E tests...');
  
  try {
    // Clean up test data if needed
    await cleanupTestData();
    
    console.log('✅ Global teardown completed successfully');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error to avoid failing the test run
  }
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...');
  
  // Add any cleanup logic here
  // For example, removing test users, tools, etc.
  
  console.log('✅ Test data cleanup completed');
}

export default globalTeardown;
