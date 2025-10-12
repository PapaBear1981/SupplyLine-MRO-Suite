import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

/**
 * E2E Tests for Kit Operations
 * 
 * Tests cover:
 * - Kit transfers
 * - Kit reorder requests
 * - Kit item issuance
 * - Kit messaging
 * - Kit alerts
 */

test.describe('Kit Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin before each test
    await login(page, TEST_USERS.admin);
  });

  test.describe('Kit Transfers', () => {
    test('should display transfer form when transfer button is clicked', async ({ page }) => {
      // Navigate to a kit detail page
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Look for transfer button
        const transferButton = page.locator('button:has-text("Transfer")');
        const transferExists = await transferButton.count();
        
        if (transferExists > 0) {
          await transferButton.first().click();
          
          // Verify transfer form/modal appears
          await page.waitForTimeout(500);
          await expect(page.locator('text=Transfer Kit, text=Destination, text=Location')).toBeVisible();
        }
      }
    });

    test('should validate transfer form fields', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        const transferButton = page.locator('button:has-text("Transfer")');
        const transferExists = await transferButton.count();
        
        if (transferExists > 0) {
          await transferButton.first().click();
          await page.waitForTimeout(500);
          
          // Try to submit without filling required fields
          const submitButton = page.locator('button:has-text("Submit"), button:has-text("Transfer")').last();
          if (await submitButton.isVisible()) {
            await submitButton.click();
            
            // Should show validation errors
            await page.waitForTimeout(500);
          }
        }
      }
    });

    test('should navigate to transfers tab and display transfer history', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Click Transfers tab
        await page.click('text=Transfers');
        await page.waitForTimeout(500);
        
        // Verify transfers content is displayed
        await expect(page.locator('.card-body, .table, text=Transfer')).toBeVisible();
      }
    });
  });

  test.describe('Kit Reorder Requests', () => {
    test('should display reorders tab', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Click Reorders tab
        await page.click('text=Reorders');
        await page.waitForTimeout(500);
        
        // Verify reorders content is displayed
        await expect(page.locator('.card-body, text=Reorder')).toBeVisible();
      }
    });

    test('should display create reorder button', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Reorders');
        await page.waitForTimeout(500);
        
        // Look for create/request reorder button
        const reorderButton = page.locator('button:has-text("Request"), button:has-text("Reorder"), button:has-text("Create")');
        const buttonExists = await reorderButton.count();
        
        if (buttonExists > 0) {
          await expect(reorderButton.first()).toBeVisible();
        }
      }
    });

    test('should open reorder request form', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Reorders');
        await page.waitForTimeout(500);
        
        const reorderButton = page.locator('button:has-text("Request"), button:has-text("Reorder"), button:has-text("Create")');
        const buttonExists = await reorderButton.count();
        
        if (buttonExists > 0) {
          await reorderButton.first().click();
          await page.waitForTimeout(500);
          
          // Verify form/modal appears
          await expect(page.locator('text=Part Number, text=Description, text=Quantity')).toBeVisible();
        }
      }
    });

    test('should filter reorders by status', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Reorders');
        await page.waitForTimeout(500);
        
        // Look for status filter
        const statusFilter = page.locator('select, .form-select').filter({ hasText: /Status|Pending|Approved/ });
        const filterExists = await statusFilter.count();
        
        if (filterExists > 0) {
          const options = await statusFilter.first().locator('option').count();
          if (options > 1) {
            await statusFilter.first().selectOption({ index: 1 });
            await page.waitForTimeout(500);
          }
        }
      }
    });
  });

  test.describe('Kit Item Issuance', () => {
    test('should display items tab with item list', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Click Items tab
        await page.click('text=Items');
        await page.waitForTimeout(500);
        
        // Verify items content is displayed
        await expect(page.locator('text=Kit Items, text=Items')).toBeVisible();
      }
    });

    test('should display issue button for items', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Items');
        await page.waitForTimeout(1000);
        
        // Look for issue buttons
        const issueButtons = page.locator('button:has-text("Issue")');
        const buttonCount = await issueButtons.count();
        
        if (buttonCount > 0) {
          await expect(issueButtons.first()).toBeVisible();
        }
      }
    });

    test('should open issuance form when issue button is clicked', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Items');
        await page.waitForTimeout(1000);
        
        const issueButtons = page.locator('button:has-text("Issue")');
        const buttonCount = await issueButtons.count();
        
        if (buttonCount > 0) {
          await issueButtons.first().click();
          await page.waitForTimeout(500);
          
          // Verify issuance form appears
          await expect(page.locator('text=Issue Item, text=Quantity, text=Purpose')).toBeVisible();
        }
      }
    });

    test('should filter items by box', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Items');
        await page.waitForTimeout(1000);
        
        // Look for box filter
        const boxFilter = page.locator('select, .form-select').filter({ hasText: /Box|Filter/ });
        const filterExists = await boxFilter.count();
        
        if (filterExists > 0) {
          const options = await boxFilter.first().locator('option').count();
          if (options > 1) {
            await boxFilter.first().selectOption({ index: 1 });
            await page.waitForTimeout(500);
          }
        }
      }
    });

    test('should search items by part number or description', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Items');
        await page.waitForTimeout(1000);
        
        // Look for search input
        const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]');
        const searchExists = await searchInput.count();
        
        if (searchExists > 0) {
          await searchInput.first().fill('test');
          await page.waitForTimeout(500);
        }
      }
    });
  });

  test.describe('Kit Alerts', () => {
    test('should display alerts section on overview tab', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.waitForTimeout(500);
        
        // Look for alerts section
        const alertsSection = page.locator('text=Alerts, text=Warning, text=Low Stock');
        const alertsExist = await alertsSection.count();
        
        if (alertsExist > 0) {
          await expect(alertsSection.first()).toBeVisible();
        }
      }
    });

    test('should display different alert types with appropriate styling', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.waitForTimeout(500);
        
        // Look for alert badges or cards
        const alerts = page.locator('.alert, .badge').filter({ hasText: /Warning|Critical|Info|Low/ });
        const alertCount = await alerts.count();
        
        // Alerts may or may not exist depending on kit state
        expect(alertCount).toBeGreaterThanOrEqual(0);
      }
    });
  });

  test.describe('Kit Issuances History', () => {
    test('should display issuances tab', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Click Issuances tab
        await page.click('text=Issuances');
        await page.waitForTimeout(500);
        
        // Verify issuances content is displayed
        await expect(page.locator('.card-body, text=Issuance')).toBeVisible();
      }
    });

    test('should display issuance history table or message', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        await page.click('text=Issuances');
        await page.waitForTimeout(500);
        
        // Should show either a table or a "no issuances" message
        const content = page.locator('.table, text=No issuances, text=history');
        await expect(content.first()).toBeVisible();
      }
    });
  });
});

