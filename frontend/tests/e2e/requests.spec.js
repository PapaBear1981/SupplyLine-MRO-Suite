/**
 * Requests page E2E tests for supporting documentation upload.
 */

import { test, expect } from '@playwright/test';
import { setupAuthenticatedState, TEST_USERS } from './utils/auth.js';

async function ensureLoggedIn(page) {
  await setupAuthenticatedState(page, TEST_USERS.admin, { navigateToDashboard: true });
}

test.describe('Requests Page - Documentation Upload', () => {
  test('shows supporting documentation upload with guidance text', async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/requests');

    await expect(page.locator('h5:has-text("Submit a Request")')).toBeVisible();
    await expect(page.locator('text=Supporting Documentation')).toBeVisible();
    await expect(page.locator('text=Not required, but highly recommended')).toBeVisible();
  });

  test('allows selecting documentation file and submitting request', async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/requests');

    await expect(page.locator('h5:has-text("Submit a Request")')).toBeVisible();

    const titleInput = page.locator('input[name="title"]');
    await titleInput.fill('E2E Request with documentation');

    const dueDateInput = page.locator('input[name="expected_due_date"]');
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 7);
    const dateString = dueDate.toISOString().split('T')[0];
    await dueDateInput.fill(dateString);

    const fileInput = page.locator('input[type="file"]').first();
    await expect(fileInput).toBeVisible();
    await fileInput.setInputFiles({
      name: 'e2e-supporting.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 E2E test')
    });

    await expect(page.locator('text=Selected file: e2e-supporting.pdf')).toBeVisible();

    await page.click('button:has-text("Submit Request")');

    await expect(page.locator('text=Request submitted successfully')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('.requests-list')).toContainText('E2E Request with documentation');
  });
});

