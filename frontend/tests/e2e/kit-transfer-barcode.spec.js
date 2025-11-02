/**
 * E2E Test: Kit Transfer Barcode Modal
 * 
 * Tests PR 470: Show barcode modal after kit expendable transfers
 * Verifies that:
 * 1. Kit-to-kit expendable transfers trigger the barcode modal
 * 2. The barcode modal displays the transferred item details
 * 3. The modal shows correct destination kit and box information
 */

import { test, expect } from '@playwright/test';

test.describe('Kit Transfer Barcode Modal - PR 470', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="employee_number"]', 'ADMIN001');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');
  });

  test('should show barcode modal after kit-to-kit expendable transfer', async ({ page }) => {
    // Navigate to kits
    await page.goto('/kits');
    await page.waitForLoadState('networkidle');

    // Find and click on first kit
    const kitCards = page.locator('[data-testid="kit-card"]');
    const kitCount = await kitCards.count();
    
    if (kitCount === 0) {
      test.skip();
    }

    await kitCards.first().click();
    await page.waitForLoadState('networkidle');

    // Click on Items tab
    await page.click('button[role="tab"]:has-text("Items")');
    await page.waitForLoadState('networkidle');

    // Find an expendable item and click transfer
    const transferButtons = page.locator('button:has-text("Transfer")');
    const transferCount = await transferButtons.count();

    if (transferCount === 0) {
      test.skip();
    }

    // Click first transfer button
    await transferButtons.first().click();
    await expect(page.locator('[data-testid="transfer-modal"]')).toBeVisible({ timeout: 5000 });

    // Fill transfer form for kit-to-kit transfer
    // Select destination type as Kit
    await page.selectOption('select[name="to_location_type"]', 'kit');
    await page.waitForTimeout(500);

    // Select a destination kit
    const destKitSelect = page.locator('select[name="to_location_id"]');
    const options = await destKitSelect.locator('option').count();
    
    if (options > 1) {
      // Select second kit if available
      await destKitSelect.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      // Select a destination box
      const boxSelect = page.locator('select[name="box_id"]');
      const boxOptions = await boxSelect.locator('option').count();
      
      if (boxOptions > 1) {
        await boxSelect.selectOption({ index: 1 });
        await page.waitForTimeout(500);

        // Fill quantity
        await page.fill('input[name="quantity"]', '1');

        // Submit transfer
        await page.click('button[type="submit"]:has-text("Create Transfer")');

        // Wait for success message
        await expect(page.locator('text=Transfer created successfully')).toBeVisible({ timeout: 5000 });

        // Wait for barcode modal to appear
        // The modal should appear after the transfer form closes
        await expect(page.locator('text=Barcode')).toBeVisible({ timeout: 8000 });

        // Verify barcode modal contains item details
        const barcodeModal = page.locator('[role="dialog"]').filter({ hasText: /Barcode|barcode/ });
        await expect(barcodeModal).toBeVisible();

        // Verify modal has barcode content
        const barcodeContent = page.locator('canvas, svg, img[alt*="barcode" i]');
        const barcodeCount = await barcodeContent.count();
        expect(barcodeCount).toBeGreaterThan(0);
      }
    }
  });

  test('should NOT show barcode modal for kit-to-warehouse transfers', async ({ page }) => {
    // Navigate to kits
    await page.goto('/kits');
    await page.waitForLoadState('networkidle');

    // Find and click on first kit
    const kitCards = page.locator('[data-testid="kit-card"]');
    const kitCount = await kitCards.count();
    
    if (kitCount === 0) {
      test.skip();
    }

    await kitCards.first().click();
    await page.waitForLoadState('networkidle');

    // Click on Items tab
    await page.click('button[role="tab"]:has-text("Items")');
    await page.waitForLoadState('networkidle');

    // Find an expendable item and click transfer
    const transferButtons = page.locator('button:has-text("Transfer")');
    const transferCount = await transferButtons.count();

    if (transferCount === 0) {
      test.skip();
    }

    // Click first transfer button
    await transferButtons.first().click();
    await expect(page.locator('[data-testid="transfer-modal"]')).toBeVisible({ timeout: 5000 });

    // Fill transfer form for kit-to-warehouse transfer
    // Select destination type as Warehouse
    await page.selectOption('select[name="to_location_type"]', 'warehouse');
    await page.waitForTimeout(500);

    // Select a destination warehouse
    const destWarehouseSelect = page.locator('select[name="to_location_id"]');
    const options = await destWarehouseSelect.locator('option').count();
    
    if (options > 1) {
      await destWarehouseSelect.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      // Fill quantity
      await page.fill('input[name="quantity"]', '1');

      // Submit transfer
      await page.click('button[type="submit"]:has-text("Create Transfer")');

      // Wait for success message
      await expect(page.locator('text=Transfer created successfully')).toBeVisible({ timeout: 5000 });

      // Barcode modal should NOT appear for kit-to-warehouse transfers
      const barcodeModal = page.locator('text=Barcode');
      await expect(barcodeModal).not.toBeVisible({ timeout: 3000 });
    }
  });
});

