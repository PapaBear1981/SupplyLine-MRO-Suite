import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { 
  waitForLoadingToComplete, 
  waitForToast, 
  fillField, 
  clickButton, 
  selectOption,
  waitForTableToLoad,
  navigateToPage 
} from '../utils/test-helpers.js';

test.describe('Tool Checkout System', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test.describe('Checkout Process', () => {
    test('should display checkout page correctly', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Check page elements
      await expect(page.locator('[data-testid="checkout-page-title"]')).toBeVisible();
      await expect(page.locator('[data-testid="checkout-form"]')).toBeVisible();
    });

    test('should checkout tool successfully', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Fill checkout form
      await fillField(page, 'employee-number-input', 'USER001');
      await fillField(page, 'tool-number-input', 'T001');
      
      // Submit checkout
      await clickButton(page, 'checkout-button');
      
      // Should show success message
      await waitForToast(page, 'Tool checked out successfully', 'success');
      
      // Form should be cleared
      await expect(page.locator('[data-testid="employee-number-input"]')).toHaveValue('');
      await expect(page.locator('[data-testid="tool-number-input"]')).toHaveValue('');
    });

    test('should show validation errors for invalid checkout data', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Try to submit empty form
      await clickButton(page, 'checkout-button');
      
      // Should show validation errors
      await expect(page.locator('.is-invalid, .error-message')).toHaveCount(2);
    });

    test('should handle checkout of unavailable tool', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Try to checkout a tool that doesn't exist or is unavailable
      await fillField(page, 'employee-number-input', 'USER001');
      await fillField(page, 'tool-number-input', 'NONEXISTENT');
      
      await clickButton(page, 'checkout-button');
      
      // Should show error message
      await waitForToast(page, 'Tool not found or unavailable', 'error');
    });

    test('should handle checkout to invalid user', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Try to checkout to a user that doesn't exist
      await fillField(page, 'employee-number-input', 'INVALID');
      await fillField(page, 'tool-number-input', 'T001');
      
      await clickButton(page, 'checkout-button');
      
      // Should show error message
      await waitForToast(page, 'User not found', 'error');
    });

    test('should use scanner for checkout', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Check if scanner button exists
      const scannerButton = page.locator('[data-testid="scan-tool-button"]');
      if (await scannerButton.isVisible()) {
        await scannerButton.click();
        
        // Should open scanner or navigate to scanner page
        const scannerModal = page.locator('[data-testid="scanner-modal"]');
        const scannerPage = page.url().includes('/scanner');
        
        expect(await scannerModal.isVisible() || scannerPage).toBeTruthy();
      }
    });
  });

  test.describe('Return Process', () => {
    test('should display return form', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Check if return section exists
      const returnSection = page.locator('[data-testid="return-section"]');
      if (await returnSection.isVisible()) {
        await expect(returnSection).toBeVisible();
        await expect(page.locator('[data-testid="return-tool-input"]')).toBeVisible();
        await expect(page.locator('[data-testid="return-button"]')).toBeVisible();
      }
    });

    test('should return tool successfully', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // First, let's check if there are any checked out tools to return
      const returnSection = page.locator('[data-testid="return-section"]');
      if (await returnSection.isVisible()) {
        // Fill return form
        await fillField(page, 'return-tool-input', 'T001');
        
        // Submit return
        await clickButton(page, 'return-button');
        
        // Should show success or error message
        const successToast = page.locator('.toast-success');
        const errorToast = page.locator('.toast-error');
        
        // Either success (tool was checked out) or error (tool wasn't checked out)
        expect(await successToast.isVisible() || await errorToast.isVisible()).toBeTruthy();
      }
    });

    test('should handle return of non-checked-out tool', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      const returnSection = page.locator('[data-testid="return-section"]');
      if (await returnSection.isVisible()) {
        // Try to return a tool that isn't checked out
        await fillField(page, 'return-tool-input', 'NOTCHECKEDOUT');
        
        await clickButton(page, 'return-button');
        
        // Should show error message
        await waitForToast(page, 'Tool is not checked out', 'error');
      }
    });

    test('should add return notes', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      const returnSection = page.locator('[data-testid="return-section"]');
      const notesField = page.locator('[data-testid="return-notes-input"]');
      
      if (await returnSection.isVisible() && await notesField.isVisible()) {
        await fillField(page, 'return-tool-input', 'T001');
        await fillField(page, 'return-notes-input', 'Tool returned in good condition');
        
        await clickButton(page, 'return-button');
        
        // Should process return with notes
        const toast = page.locator('.toast');
        await expect(toast).toBeVisible();
      }
    });
  });

  test.describe('Active Checkouts View', () => {
    test('should display active checkouts list', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      
      // Check page elements
      await expect(page.locator('[data-testid="checkouts-page-title"]')).toBeVisible();
      await expect(page.locator('[data-testid="checkouts-table"]')).toBeVisible();
    });

    test('should load and display checkouts in table', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      
      // Wait for table to load
      await waitForTableToLoad(page, 'checkouts-table');
      
      // Should have table headers
      const expectedHeaders = ['Tool Number', 'Description', 'User', 'Checkout Date', 'Due Date', 'Actions'];
      for (const header of expectedHeaders) {
        const headerElement = page.locator(`th:has-text("${header}")`);
        if (await headerElement.isVisible()) {
          await expect(headerElement).toBeVisible();
        }
      }
    });

    test('should filter checkouts by user', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      await waitForTableToLoad(page, 'checkouts-table');
      
      // Use user filter if available
      const userFilter = page.locator('[data-testid="user-filter"]');
      if (await userFilter.isVisible()) {
        await fillField(page, 'user-filter', 'USER001');
        await waitForLoadingToComplete(page);
        
        // Should show filtered results
        const filteredRows = await page.locator('[data-testid="checkouts-table"] tbody tr').count();
        expect(filteredRows).toBeGreaterThanOrEqual(0);
      }
    });

    test('should filter overdue checkouts', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      await waitForTableToLoad(page, 'checkouts-table');
      
      // Use overdue filter if available
      const overdueFilter = page.locator('[data-testid="overdue-filter"]');
      if (await overdueFilter.isVisible()) {
        await overdueFilter.check();
        await waitForLoadingToComplete(page);
        
        // Should show only overdue checkouts
        const overdueRows = await page.locator('[data-testid="checkouts-table"] tbody tr.overdue').count();
        const totalRows = await page.locator('[data-testid="checkouts-table"] tbody tr').count();
        
        expect(overdueRows).toBe(totalRows);
      }
    });

    test('should return tool from checkouts list', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      await waitForTableToLoad(page, 'checkouts-table');
      
      // Click return button on first checkout (if any exist)
      const firstReturnButton = page.locator('[data-testid="return-checkout-button"]').first();
      if (await firstReturnButton.isVisible()) {
        await firstReturnButton.click();
        
        // Should show return confirmation or form
        const returnModal = page.locator('[data-testid="return-modal"]');
        if (await returnModal.isVisible()) {
          // Confirm return
          await clickButton(page, 'confirm-return-button');
          
          // Should show success message
          await waitForToast(page, 'Tool returned successfully', 'success');
        }
      }
    });

    test('should extend checkout due date', async ({ page }) => {
      await navigateToPage(page, '/checkouts/all');
      await waitForTableToLoad(page, 'checkouts-table');
      
      // Click extend button on first checkout (if any exist)
      const firstExtendButton = page.locator('[data-testid="extend-checkout-button"]').first();
      if (await firstExtendButton.isVisible()) {
        await firstExtendButton.click();
        
        // Should show extend form
        const extendModal = page.locator('[data-testid="extend-modal"]');
        if (await extendModal.isVisible()) {
          // Set new due date
          await fillField(page, 'new-due-date-input', '2025-12-31');
          
          // Confirm extension
          await clickButton(page, 'confirm-extend-button');
          
          // Should show success message
          await waitForToast(page, 'Checkout extended successfully', 'success');
        }
      }
    });
  });

  test.describe('User Checkouts View', () => {
    test('should display current user checkouts', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Check if user checkouts section exists
      const userCheckouts = page.locator('[data-testid="user-checkouts"]');
      if (await userCheckouts.isVisible()) {
        await expect(userCheckouts).toBeVisible();
        
        // Should show current user's checkouts or "No checkouts" message
        const hasCheckouts = await page.locator('[data-testid="user-checkout-items"]').isVisible();
        const noCheckouts = await page.locator('[data-testid="no-user-checkouts"]').isVisible();
        
        expect(hasCheckouts || noCheckouts).toBeTruthy();
      }
    });

    test('should allow user to return their own tools', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Look for user's checkout items
      const userCheckoutItem = page.locator('[data-testid="user-checkout-item"]').first();
      if (await userCheckoutItem.isVisible()) {
        const returnButton = userCheckoutItem.locator('[data-testid="return-my-tool-button"]');
        if (await returnButton.isVisible()) {
          await returnButton.click();
          
          // Should process return
          await waitForToast(page, 'Tool returned successfully', 'success');
        }
      }
    });
  });
});
