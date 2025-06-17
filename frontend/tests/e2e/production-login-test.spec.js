import { test, expect } from '@playwright/test';

test.describe('Production Login Test', () => {
  const PRODUCTION_URL = 'https://supplyline-frontend-production-454313121816.us-west1.run.app';
  
  test('should login successfully with ADMIN001 credentials on production', async ({ page }) => {
    // Navigate to production login page
    await page.goto(`${PRODUCTION_URL}/login`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check that we're on the login page
    await expect(page).toHaveTitle(/SupplyLine MRO Suite/);
    
    // Verify login form elements are present
    await expect(page.locator('[data-testid="employee-number-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    
    // Fill in the login credentials
    await page.fill('[data-testid="employee-number-input"]', 'ADMIN001');
    await page.fill('[data-testid="password-input"]', 'admin123');
    
    // Submit the login form
    await page.click('[data-testid="login-button"]');
    
    // Wait for navigation after login
    await page.waitForURL(/\/dashboard/, { timeout: 15000 });
    
    // Verify successful login by checking for dashboard elements
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible({ timeout: 10000 });
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'test-results/production-login-success.png', fullPage: true });
    
    console.log('✅ Successfully logged in to production with ADMIN001 credentials');
    console.log(`Current URL: ${page.url()}`);
  });
  
  test('should display login form correctly on production', async ({ page }) => {
    // Navigate to production login page
    await page.goto(`${PRODUCTION_URL}/login`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check page title
    await expect(page).toHaveTitle(/SupplyLine MRO Suite/);
    
    // Check login form elements
    await expect(page.locator('[data-testid="employee-number-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    
    // Check form labels
    await expect(page.locator('label:has-text("Employee Number")')).toBeVisible();
    await expect(page.locator('label:has-text("Password")')).toBeVisible();
    
    // Take a screenshot of the login page
    await page.screenshot({ path: 'test-results/production-login-page.png', fullPage: true });
    
    console.log('✅ Production login page displays correctly');
  });
  
  test('should handle invalid credentials gracefully on production', async ({ page }) => {
    // Navigate to production login page
    await page.goto(`${PRODUCTION_URL}/login`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Fill in invalid credentials
    await page.fill('[data-testid="employee-number-input"]', 'INVALID');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    
    // Submit the login form
    await page.click('[data-testid="login-button"]');
    
    // Wait for error message or stay on login page
    await page.waitForTimeout(3000);
    
    // Should still be on login page or show error
    const currentUrl = page.url();
    expect(currentUrl).toContain('/login');
    
    console.log('✅ Invalid credentials handled correctly on production');
  });
});
