import { test, expect } from '@playwright/test';

test.describe('Configuration Validation', () => {
  test('should validate Playwright configuration', async ({ page }) => {
    // This test validates that Playwright is properly configured
    // without requiring the application servers to be running
    
    // Test basic page functionality
    await page.goto('https://example.com');
    await expect(page).toHaveTitle(/Example Domain/);
    
    // Test that we can interact with elements
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText('Example Domain');
    
    // Test that we can take screenshots
    await page.screenshot({ path: 'test-results/config-validation.png' });
    
    console.log('✅ Playwright configuration is working correctly!');
  });

  test('should validate test helpers import', async ({ page }) => {
    // Test that our helper functions can be imported
    const { waitForLoadingToComplete } = await import('../utils/test-helpers.js');
    const { loginAsAdmin } = await import('../utils/auth-helpers.js');
    const { generateTestData } = await import('../utils/advanced-helpers.js');
    
    // Test helper function execution
    const testData = generateTestData('toolNumber');
    expect(testData).toMatch(/^T\d+$/);
    
    console.log('✅ Test helpers are working correctly!');
  });

  test('should validate test configuration', async ({ page }) => {
    // Test that our test configuration can be imported
    const config = await import('../test-config.js');
    
    expect(config.TEST_CONFIG).toBeDefined();
    expect(config.TEST_SELECTORS).toBeDefined();
    expect(config.TEST_ROUTES).toBeDefined();
    expect(config.API_ENDPOINTS).toBeDefined();
    
    // Validate configuration structure
    expect(config.TEST_CONFIG.timeouts).toBeDefined();
    expect(config.TEST_CONFIG.users).toBeDefined();
    expect(config.TEST_CONFIG.performance).toBeDefined();
    
    console.log('✅ Test configuration is valid!');
  });

  test('should validate browser capabilities', async ({ page, browserName }) => {
    // Test browser-specific capabilities
    await page.goto('https://example.com');
    
    // Test JavaScript execution
    const userAgent = await page.evaluate(() => navigator.userAgent);
    expect(userAgent).toBeTruthy();
    
    // Test viewport manipulation
    await page.setViewportSize({ width: 1280, height: 720 });
    const viewport = page.viewportSize();
    expect(viewport.width).toBe(1280);
    expect(viewport.height).toBe(720);
    
    // Test local storage
    await page.evaluate(() => {
      localStorage.setItem('test', 'playwright');
    });
    
    const stored = await page.evaluate(() => localStorage.getItem('test'));
    expect(stored).toBe('playwright');
    
    console.log(`✅ Browser ${browserName} capabilities validated!`);
  });

  test('should validate network interception', async ({ page }) => {
    // Test network request interception
    const requests = [];
    
    page.on('request', request => {
      requests.push(request.url());
    });
    
    await page.goto('https://example.com');
    
    // Should have captured at least one request
    expect(requests.length).toBeGreaterThan(0);
    expect(requests[0]).toContain('example.com');
    
    console.log('✅ Network interception is working!');
  });
});
