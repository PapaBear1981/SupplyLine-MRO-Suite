import { test, expect } from '@playwright/test';

const baseUrl = process.env.E2E_BASE_URL ?? 'http://localhost:4173';
const shouldSkip = !process.env.E2E_BASE_URL;

test.skip(shouldSkip, 'Set E2E_BASE_URL to run role tests');

test.describe('Role-based permissions', () => {
  test('viewer cannot checkout tools', async ({ page }) => {
    await page.goto(`${baseUrl}/login`);
    await page.fill('[data-testid="login-username"]', process.env.E2E_VIEWER ?? 'viewer@example.com');
    await page.fill('[data-testid="login-password"]', process.env.E2E_PASSWORD ?? 'password');
    await page.click('[data-testid="login-submit"]');

    await page.fill('[data-testid="tool-search-input"]', 'TL-100');
    await expect(page.locator('[data-testid="checkout-button-TL-100"]')).toBeDisabled();
  });

  test('auditor can view exports only', async ({ page }) => {
    await page.goto(`${baseUrl}/login`);
    await page.fill('[data-testid="login-username"]', process.env.E2E_AUDITOR ?? 'auditor@example.com');
    await page.fill('[data-testid="login-password"]', process.env.E2E_PASSWORD ?? 'password');
    await page.click('[data-testid="login-submit"]');

    await expect(page.locator('[data-testid="export-audit"]')).toBeVisible();
    await expect(page.locator('[data-testid="checkout-button-TL-100"]')).toBeHidden();
  });
});
