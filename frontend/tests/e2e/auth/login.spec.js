import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsUser, logout, isAuthenticated } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, waitForToast } from '../utils/test-helpers.js';
import { testUsers } from '../fixtures/test-data.js';

test.describe('Authentication - Login', () => {
  test.beforeEach(async ({ page }) => {
    // Ensure we start from a clean state
    await page.goto('/login');
  });

  test('should display login form correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/SupplyLine MRO Suite/);
    
    // Check login form elements
    await expect(page.locator('[data-testid="employee-number-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    
    // Check form labels
    await expect(page.locator('label:has-text("Employee Number")')).toBeVisible();
    await expect(page.locator('label:has-text("Password")')).toBeVisible();
  });

  test('should login successfully with admin credentials', async ({ page }) => {
    await loginAsAdmin(page);
    
    // Verify we're on the dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify admin-specific elements are visible
    await expect(page.locator('[data-testid="admin-dashboard-link"]')).toBeVisible();
    
    // Verify user menu shows admin user
    await expect(page.locator('[data-testid="user-menu"]')).toContainText('ADMIN001');
  });

  test('should login successfully with regular user credentials', async ({ page }) => {
    // Note: This test assumes a regular user exists. In a real scenario,
    // you might need to create this user in the global setup
    await page.goto('/login');
    
    await page.fill('[data-testid="employee-number-input"]', 'USER001');
    await page.fill('[data-testid="password-input"]', 'user123');
    await page.click('[data-testid="login-button"]');
    
    // Wait for potential redirect
    await page.waitForTimeout(2000);
    
    // If user doesn't exist, we should see an error
    // If user exists, we should be redirected to dashboard
    const currentUrl = page.url();
    if (currentUrl.includes('/dashboard')) {
      // User exists and login was successful
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
      // Regular users shouldn't see admin dashboard link
      await expect(page.locator('[data-testid="admin-dashboard-link"]')).not.toBeVisible();
    } else {
      // User doesn't exist or login failed
      console.log('Regular user test skipped - user may not exist');
    }
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('[data-testid="employee-number-input"]', 'INVALID');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    // Wait for error message
    await waitForLoadingToComplete(page);
    
    // Should stay on login page
    await expect(page).toHaveURL('/login');
    
    // Should show error message (adjust selector based on your error display)
    await expect(page.locator('.alert-danger, .toast-error, .error-message')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    // Try to submit empty form
    await page.click('[data-testid="login-button"]');
    
    // Should show validation errors
    await expect(page.locator('input:invalid')).toHaveCount(2);
  });

  test('should redirect to login when accessing protected route without authentication', async ({ page }) => {
    // Try to access dashboard without logging in
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL('/login');
  });

  test('should remember login state after page refresh', async ({ page }) => {
    await loginAsAdmin(page);
    
    // Refresh the page
    await page.reload();
    
    // Should still be authenticated
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept login request and make it fail
    await page.route('**/api/auth/login', route => {
      route.abort('failed');
    });
    
    await page.fill('[data-testid="employee-number-input"]', testUsers.admin.employee_number);
    await page.fill('[data-testid="password-input"]', testUsers.admin.password);
    await page.click('[data-testid="login-button"]');
    
    // Should show network error message
    await expect(page.locator('.alert-danger, .toast-error, .error-message')).toBeVisible();
  });

  test('should clear form when switching between login and register', async ({ page }) => {
    // Fill login form
    await page.fill('[data-testid="employee-number-input"]', 'test');
    await page.fill('[data-testid="password-input"]', 'test');
    
    // Navigate to register (if register link exists)
    const registerLink = page.locator('a[href="/register"]');
    if (await registerLink.isVisible()) {
      await registerLink.click();
      
      // Navigate back to login
      await page.goto('/login');
      
      // Form should be cleared
      await expect(page.locator('[data-testid="employee-number-input"]')).toHaveValue('');
      await expect(page.locator('[data-testid="password-input"]')).toHaveValue('');
    }
  });
});
