import { test, expect } from '@playwright/test';

const baseUrl = process.env.E2E_BASE_URL ?? 'http://localhost:4173';
const shouldSkip = !process.env.E2E_BASE_URL;

test.skip(shouldSkip, 'Set E2E_BASE_URL to run smoke tests');

test.describe('Tool custody smoke', () => {
  test('login → search → checkout → return → export', async ({ page }) => {
    await page.goto(baseUrl);

    await test.step('login', async () => {
      await page.fill('[data-testid="login-username"]', process.env.E2E_USER ?? 'tech@example.com');
      await page.fill('[data-testid="login-password"]', process.env.E2E_PASSWORD ?? 'password');
      await page.click('[data-testid="login-submit"]');
      await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    });

    await test.step('search tool', async () => {
      await page.fill('[data-testid="tool-search-input"]', 'TL-100');
      await page.click('[data-testid="tool-search-submit"]');
      await expect(page.locator('[data-testid="tool-row-TL-100"]')).toBeVisible();
    });

    await test.step('checkout tool', async () => {
      await page.click('[data-testid="checkout-button-TL-100"]');
      await page.fill('[data-testid="checkout-work-order"]', 'WO-123');
      await page.click('[data-testid="confirm-checkout"]');
      await expect(page.locator('[data-testid="tool-status"]')).toHaveText(/checked out/i);
    });

    await test.step('return tool', async () => {
      await page.click('[data-testid="return-button-TL-100"]');
      await page.click('[data-testid="confirm-return"]');
      await expect(page.locator('[data-testid="tool-status"]')).toHaveText(/available/i);
    });

    await test.step('export audit', async () => {
      await page.click('[data-testid="export-audit"]');
      const download = await page.waitForEvent('download');
      await expect(download.suggestedFilename()).toMatch(/audit/i);
    });
  });
});
