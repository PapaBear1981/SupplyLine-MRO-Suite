import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { navigateToPage, waitForLoadingToComplete, takeScreenshot } from '../utils/test-helpers.js';

test.describe('Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('should display 404 page for invalid URL', async ({ page }) => {
    await page.goto('/non-existent-page');
    await waitForLoadingToComplete(page);
    await expect(page.locator('body')).toContainText(/404|not found/i);
    await takeScreenshot(page, '404-page');
  });

  test('should show error message when API request fails', async ({ page }) => {
    await page.route('**/api/tools', route => {
      route.abort('failed');
    });

    await navigateToPage(page, '/tools');
    await expect(page.locator('.alert-danger, .error-message')).toBeVisible();
  });
});
