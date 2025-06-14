import { test, expect } from '@playwright/test';
import { loginAsAdmin, logout, isAuthenticated } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete } from '../utils/test-helpers.js';

test.describe('Authentication - Logout', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await loginAsAdmin(page);
  });

  test('should logout successfully from user menu', async ({ page }) => {
    // Verify we're logged in
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Logout using helper function
    await logout(page);
    
    // Verify we're redirected to login page
    await expect(page).toHaveURL('/login');
    
    // Verify login form is visible
    await expect(page.locator('[data-testid="employee-number-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
  });

  test('should clear authentication state after logout', async ({ page }) => {
    await logout(page);
    
    // Try to access protected route
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL('/login');
  });

  test('should clear user data from UI after logout', async ({ page }) => {
    await logout(page);
    
    // Navigate back to a page that would show user info
    await page.goto('/');
    
    // Should be on login page, not showing any user info
    await expect(page).toHaveURL('/login');
    await expect(page.locator('[data-testid="user-menu"]')).not.toBeVisible();
  });

  test('should handle logout when already logged out', async ({ page }) => {
    await logout(page);
    
    // Try to logout again by directly calling the logout endpoint
    const response = await page.request.post('/api/auth/logout');
    
    // Should handle gracefully (either 200 or appropriate error)
    expect([200, 401, 403]).toContain(response.status());
  });

  test('should logout from all tabs/windows', async ({ context, page }) => {
    // Open a new tab
    const newPage = await context.newPage();
    await newPage.goto('/dashboard');
    
    // Verify both tabs are authenticated
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(newPage.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Logout from first tab
    await logout(page);
    
    // Refresh second tab
    await newPage.reload();
    
    // Second tab should also be logged out
    await expect(newPage).toHaveURL('/login');
  });

  test('should handle network errors during logout gracefully', async ({ page }) => {
    // Intercept logout request and make it fail
    await page.route('**/api/auth/logout', route => {
      route.abort('failed');
    });
    
    // Try to logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Even if network fails, should clear local state and redirect
    await expect(page).toHaveURL('/login');
  });

  test('should show logout confirmation if configured', async ({ page }) => {
    // This test assumes there might be a logout confirmation dialog
    // Adjust based on your actual implementation
    
    await page.click('[data-testid="user-menu"]');
    
    // Check if there's a confirmation dialog
    const logoutButton = page.locator('[data-testid="logout-button"]');
    await logoutButton.click();
    
    // If there's a confirmation dialog, handle it
    const confirmDialog = page.locator('.modal, .confirm-dialog');
    if (await confirmDialog.isVisible()) {
      await page.click('[data-testid="confirm-logout"]');
    }
    
    // Should be logged out
    await expect(page).toHaveURL('/login');
  });
});
