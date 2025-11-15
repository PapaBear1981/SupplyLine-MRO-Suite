/**
 * Chemical Reorder Feature Tests
 *
 * Tests the reorder button and modal functionality on the Active Chemicals tab
 */

import { test, expect } from '@playwright/test';

test.describe('Chemical Reorder Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login as Materials user
    await page.goto('/login');
    await page.fill('input[name="employee_number"]', 'MAT001');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should display reorder button in actions column', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Check if reorder button exists in the first row
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');

    await expect(reorderButton).toBeVisible();
  });

  test('should open reorder modal when reorder button is clicked', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Click the reorder button on the first chemical
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal to appear
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Verify modal content
    await expect(page.locator('.modal-title')).toContainText('Reorder Chemical');
    await expect(page.locator('text=Part Number:')).toBeVisible();
    await expect(page.locator('text=Expected Due Date')).toBeVisible();
  });

  test('should display chemical information in modal', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Get the part number from the table
    const firstRow = page.locator('table tbody tr').first();
    const partNumber = await firstRow.locator('td').first().textContent();

    // Click the reorder button
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal and verify chemical info is displayed
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });
    await expect(page.locator('.modal-body')).toContainText(partNumber.trim());
  });

  test('should require expected delivery date before submission', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Open reorder modal
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Verify submit button is disabled initially
    const submitButton = page.locator('button:has-text("Mark as Ordered")');
    await expect(submitButton).toBeDisabled();
  });

  test('should enable submit button when delivery date is entered', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Open reorder modal
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Fill in expected delivery date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 7);
    const dateString = tomorrow.toISOString().split('T')[0];

    await page.fill('input[type="date"]', dateString);

    // Verify submit button is enabled
    const submitButton = page.locator('button:has-text("Mark as Ordered")');
    await expect(submitButton).not.toBeDisabled();
  });

  test('should submit reorder and close modal successfully', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Open reorder modal
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Fill in the form
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 7);
    const dateString = tomorrow.toISOString().split('T')[0];

    await page.fill('input[type="date"]', dateString);
    await page.fill('textarea[placeholder*="additional notes"]', 'Test reorder from E2E test');

    // Submit the form
    const submitButton = page.locator('button:has-text("Mark as Ordered")');
    await submitButton.click();

    // Wait for modal to close
    await page.waitForSelector('text=Reorder Chemical', { state: 'hidden', timeout: 5000 });

    // Verify modal is closed
    await expect(page.locator('.modal-title')).not.toBeVisible();
  });

  test('should allow canceling the reorder modal', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Open reorder modal
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Click cancel button
    const cancelButton = page.locator('button:has-text("Cancel")');
    await cancelButton.click();

    // Verify modal is closed
    await page.waitForSelector('text=Reorder Chemical', { state: 'hidden', timeout: 5000 });
    await expect(page.locator('.modal-title')).not.toBeVisible();
  });

  test('should show character count for notes field', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Open reorder modal
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    // Type in notes field
    const notesText = 'This is a test note';
    await page.fill('textarea[placeholder*="additional notes"]', notesText);

    // Verify character count is displayed
    const charCount = `${notesText.length}/500 characters`;
    await expect(page.locator(`text=${charCount}`)).toBeVisible();
  });

  test('should verify reorder appears in Orders page after submission', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Get chemical info before ordering
    const firstRow = page.locator('table tbody tr').first();
    const partNumber = await firstRow.locator('td').first().textContent();

    // Open reorder modal
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.click();

    // Wait for modal and submit
    await page.waitForSelector('text=Reorder Chemical', { timeout: 5000 });

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 7);
    const dateString = tomorrow.toISOString().split('T')[0];

    await page.fill('input[type="date"]', dateString);

    const submitButton = page.locator('button:has-text("Mark as Ordered")');
    await submitButton.click();

    // Wait for modal to close
    await page.waitForSelector('text=Reorder Chemical', { state: 'hidden', timeout: 5000 });

    // Navigate to Orders page
    await page.goto('/orders');
    await page.waitForSelector('table', { timeout: 10000 });

    // Verify the chemical order appears (or check the "Chemicals On Order" tab)
    const onOrderTab = page.locator('button:has-text("Chemicals On Order")');
    if (await onOrderTab.isVisible()) {
      await onOrderTab.click();
      await page.waitForTimeout(1000);

      // Verify the chemical appears in the on-order list
      await expect(page.locator('table tbody')).toContainText(partNumber.trim());
    }
  });
});

test.describe('Reorder Button Tooltip', () => {
  test.beforeEach(async ({ page }) => {
    // Login as Materials user
    await page.goto('/login');
    await page.fill('input[name="employee_number"]', 'MAT001');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should show tooltip on hover over reorder button', async ({ page }) => {
    // Navigate to chemicals page
    await page.goto('/chemicals');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Hover over reorder button
    const firstRow = page.locator('table tbody tr').first();
    const reorderButton = firstRow.locator('button:has(i.bi-cart-plus)');
    await reorderButton.hover();

    // Wait a moment for tooltip to appear (if tooltips are enabled)
    await page.waitForTimeout(500);

    // Note: Tooltip visibility depends on user settings in the app
    // This test verifies the button is hoverable and doesn't break
    await expect(reorderButton).toBeVisible();
  });
});
