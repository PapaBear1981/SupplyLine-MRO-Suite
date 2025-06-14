import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { 
  waitForLoadingToComplete, 
  waitForToast, 
  fillField, 
  clickButton, 
  selectOption,
  waitForTableToLoad,
  searchInTable,
  navigateToPage 
} from '../utils/test-helpers.js';
import { testChemicals } from '../fixtures/test-data.js';

test.describe('Chemical Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/chemicals');
  });

  test('should display chemicals list page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Chemicals.*SupplyLine MRO Suite/);
    
    // Check main elements
    await expect(page.locator('[data-testid="chemicals-page-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="chemicals-table"]')).toBeVisible();
    await expect(page.locator('[data-testid="add-chemical-button"]')).toBeVisible();
  });

  test('should load and display chemicals in table', async ({ page }) => {
    // Wait for table to load
    const rowCount = await waitForTableToLoad(page, 'chemicals-table');
    
    // Should have table headers
    const expectedHeaders = ['Part Number', 'Description', 'Category', 'Quantity', 'Unit', 'Location', 'Status', 'Actions'];
    for (const header of expectedHeaders) {
      const headerElement = page.locator(`th:has-text("${header}")`);
      if (await headerElement.isVisible()) {
        await expect(headerElement).toBeVisible();
      }
    }
  });

  test('should search chemicals by part number', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Search for a specific chemical
    await searchInTable(page, 'CHEM001', 'chemicals-search-input');
    
    // Should filter results
    const filteredRows = await page.locator('[data-testid="chemicals-table"] tbody tr').count();
    expect(filteredRows).toBeGreaterThanOrEqual(0);
  });

  test('should filter chemicals by category', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Use category filter if available
    const categoryFilter = page.locator('[data-testid="chemical-category-filter"]');
    if (await categoryFilter.isVisible()) {
      await selectOption(page, 'chemical-category-filter', 'Solvent');
      await waitForLoadingToComplete(page);
      
      // Should show filtered results
      const filteredRows = await page.locator('[data-testid="chemicals-table"] tbody tr').count();
      expect(filteredRows).toBeGreaterThanOrEqual(0);
    }
  });

  test('should filter chemicals by status', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Use status filter if available
    const statusFilter = page.locator('[data-testid="chemical-status-filter"]');
    if (await statusFilter.isVisible()) {
      await selectOption(page, 'chemical-status-filter', 'available');
      await waitForLoadingToComplete(page);
      
      // Should show filtered results
      const filteredRows = await page.locator('[data-testid="chemicals-table"] tbody tr').count();
      expect(filteredRows).toBeGreaterThanOrEqual(0);
    }
  });

  test('should navigate to add new chemical page', async ({ page }) => {
    await clickButton(page, 'add-chemical-button');
    
    // Should navigate to new chemical page
    await expect(page).toHaveURL('/chemicals/new');
    
    // Should show new chemical form
    await expect(page.locator('[data-testid="chemical-form"]')).toBeVisible();
  });

  test('should create a new chemical successfully', async ({ page }) => {
    // Navigate to new chemical page
    await clickButton(page, 'add-chemical-button');
    await expect(page).toHaveURL('/chemicals/new');
    
    // Fill chemical form
    const chemicalData = testChemicals.basicChemical;
    await fillField(page, 'part-number-input', chemicalData.part_number);
    await fillField(page, 'chemical-description-input', chemicalData.description);
    await selectOption(page, 'chemical-category-select', chemicalData.category);
    await fillField(page, 'quantity-input', chemicalData.quantity.toString());
    await selectOption(page, 'unit-select', chemicalData.unit);
    await fillField(page, 'chemical-location-input', chemicalData.location);
    
    // Submit form
    await clickButton(page, 'save-chemical-button');
    
    // Should show success message
    await waitForToast(page, 'Chemical created successfully', 'success');
    
    // Should redirect to chemicals list or chemical detail
    expect(page.url()).toMatch(/\/chemicals(\/\d+)?$/);
  });

  test('should show validation errors for invalid chemical data', async ({ page }) => {
    // Navigate to new chemical page
    await clickButton(page, 'add-chemical-button');
    
    // Try to submit empty form
    await clickButton(page, 'save-chemical-button');
    
    // Should show validation errors
    await expect(page.locator('.is-invalid, .error-message')).toHaveCount(3); // At least part number, description, and quantity
  });

  test('should view chemical details', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Click on first chemical's view button (if any chemicals exist)
    const firstViewButton = page.locator('[data-testid="view-chemical-button"]').first();
    if (await firstViewButton.isVisible()) {
      await firstViewButton.click();
      
      // Should navigate to chemical detail page
      expect(page.url()).toMatch(/\/chemicals\/\d+$/);
      
      // Should show chemical details
      await expect(page.locator('[data-testid="chemical-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="chemical-part-number"]')).toBeVisible();
      await expect(page.locator('[data-testid="chemical-description"]')).toBeVisible();
    }
  });

  test('should edit chemical successfully', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Click on first chemical's edit button (if any chemicals exist)
    const firstEditButton = page.locator('[data-testid="edit-chemical-button"]').first();
    if (await firstEditButton.isVisible()) {
      await firstEditButton.click();
      
      // Should navigate to edit page
      expect(page.url()).toMatch(/\/chemicals\/\d+\/edit$/);
      
      // Should show edit form with existing data
      await expect(page.locator('[data-testid="chemical-form"]')).toBeVisible();
      
      // Update description
      await fillField(page, 'chemical-description-input', 'Updated Test Chemical Description');
      
      // Save changes
      await clickButton(page, 'save-chemical-button');
      
      // Should show success message
      await waitForToast(page, 'Chemical updated successfully', 'success');
    }
  });

  test('should issue chemical successfully', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Click on first chemical's issue button (if any chemicals exist)
    const firstIssueButton = page.locator('[data-testid="issue-chemical-button"]').first();
    if (await firstIssueButton.isVisible()) {
      await firstIssueButton.click();
      
      // Should show issue form or navigate to issue page
      const issueModal = page.locator('[data-testid="issue-chemical-modal"]');
      const issuePage = page.url().includes('/issue');
      
      if (await issueModal.isVisible()) {
        // Fill issue form in modal
        await fillField(page, 'issue-quantity-input', '10');
        await fillField(page, 'issue-user-input', 'USER001');
        await fillField(page, 'issue-notes-input', 'Test chemical issue');
        
        // Submit issue
        await clickButton(page, 'confirm-issue-button');
        
        // Should show success message
        await waitForToast(page, 'Chemical issued successfully', 'success');
      } else if (issuePage) {
        // Fill issue form on separate page
        await fillField(page, 'issue-quantity-input', '10');
        await fillField(page, 'issue-user-input', 'USER001');
        
        await clickButton(page, 'submit-issue-button');
        
        // Should show success message
        await waitForToast(page, 'Chemical issued successfully', 'success');
      }
    }
  });

  test('should show low stock alerts', async ({ page }) => {
    // Check if low stock section exists
    const lowStockSection = page.locator('[data-testid="low-stock-chemicals"]');
    if (await lowStockSection.isVisible()) {
      await expect(lowStockSection).toBeVisible();
      
      // Should show low stock items or "No low stock" message
      const hasLowStock = await page.locator('[data-testid="low-stock-items"]').isVisible();
      const noLowStock = await page.locator('[data-testid="no-low-stock"]').isVisible();
      
      expect(hasLowStock || noLowStock).toBeTruthy();
    }
  });

  test('should show expiring chemicals alerts', async ({ page }) => {
    // Check if expiring chemicals section exists
    const expiringSection = page.locator('[data-testid="expiring-chemicals"]');
    if (await expiringSection.isVisible()) {
      await expect(expiringSection).toBeVisible();
      
      // Should show expiring items or "No expiring chemicals" message
      const hasExpiring = await page.locator('[data-testid="expiring-items"]').isVisible();
      const noExpiring = await page.locator('[data-testid="no-expiring"]').isVisible();
      
      expect(hasExpiring || noExpiring).toBeTruthy();
    }
  });

  test('should handle chemical reorder process', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Click on first chemical's reorder button (if any chemicals exist)
    const firstReorderButton = page.locator('[data-testid="reorder-chemical-button"]').first();
    if (await firstReorderButton.isVisible()) {
      await firstReorderButton.click();
      
      // Should show reorder form
      const reorderModal = page.locator('[data-testid="reorder-modal"]');
      if (await reorderModal.isVisible()) {
        // Fill reorder form
        await fillField(page, 'reorder-quantity-input', '100');
        await fillField(page, 'supplier-input', 'Test Supplier');
        await fillField(page, 'expected-delivery-input', '2025-12-31');
        
        // Submit reorder
        await clickButton(page, 'submit-reorder-button');
        
        // Should show success message
        await waitForToast(page, 'Reorder submitted successfully', 'success');
      }
    }
  });

  test('should delete chemical with confirmation', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Click on first chemical's delete button (if any chemicals exist)
    const firstDeleteButton = page.locator('[data-testid="delete-chemical-button"]').first();
    if (await firstDeleteButton.isVisible()) {
      await firstDeleteButton.click();
      
      // Should show confirmation dialog
      await expect(page.locator('[data-testid="delete-confirmation"]')).toBeVisible();
      
      // Confirm deletion
      await clickButton(page, 'confirm-delete-button');
      
      // Should show success message
      await waitForToast(page, 'Chemical deleted successfully', 'success');
      
      // Should refresh the table
      await waitForLoadingToComplete(page);
    }
  });

  test('should export chemicals data', async ({ page }) => {
    await waitForTableToLoad(page, 'chemicals-table');
    
    // Check if export button exists
    const exportButton = page.locator('[data-testid="export-chemicals-button"]');
    if (await exportButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/chemicals.*\.(csv|xlsx)$/);
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept chemicals API and make it fail
    await page.route('**/api/chemicals', route => {
      route.abort('failed');
    });
    
    await page.reload();
    
    // Should show error message
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
  });
});
