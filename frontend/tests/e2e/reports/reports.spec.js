import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, navigateToPage } from '../utils/test-helpers.js';

/**
 * E2E tests for the Reports & Analytics page
 */

test.describe('Reports', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/reports');
  });

  test('should display available reports and generate inventory report', async ({ page }) => {
    // Page heading should be visible
    await expect(page.locator('h1')).toHaveText(/Reports & Analytics/);

    // Report type selector should contain Tool Inventory option
    await expect(page.locator('select').first()).toContainText('Tool Inventory');

    // Generate the default report
    await page.locator('button:has-text("Apply Filters")').click();
    await waitForLoadingToComplete(page);

    // Results card should appear
    await expect(page.locator('text=Tool Inventory')).toBeVisible();
  });

  test('should export generated report', async ({ page }) => {
    // Generate report first
    await page.locator('button:has-text("Apply Filters")').click();
    await waitForLoadingToComplete(page);

    const downloadPromise = page.waitForEvent('download');
    await page.locator('button:has-text("Export Excel")').click();

    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/tool-inventory-report-.*\.xlsx$/);
  });
});
