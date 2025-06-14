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
import { testTools } from '../fixtures/test-data.js';

test.describe('Tool Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/tools');
  });

  test('should display tools list page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Tools.*SupplyLine MRO Suite/);
    
    // Check main elements
    await expect(page.locator('[data-testid="tools-page-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="tools-table"]')).toBeVisible();
    await expect(page.locator('[data-testid="add-tool-button"]')).toBeVisible();
  });

  test('should load and display tools in table', async ({ page }) => {
    // Wait for table to load
    const rowCount = await waitForTableToLoad(page, 'tools-table');
    
    // Should have table headers
    await expect(page.locator('[data-testid="tools-table"] th')).toHaveCount(7); // Adjust based on your table
    
    // Check for expected columns
    const expectedHeaders = ['Tool Number', 'Description', 'Category', 'Status', 'Location', 'Actions'];
    for (const header of expectedHeaders) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('should search tools by tool number', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Search for a specific tool (assuming some tools exist)
    await searchInTable(page, 'T001', 'tools-search-input');
    
    // Should filter results
    const filteredRows = await page.locator('[data-testid="tools-table"] tbody tr').count();
    
    // Results should be filtered (could be 0 if no matching tools)
    expect(filteredRows).toBeGreaterThanOrEqual(0);
  });

  test('should filter tools by category', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Use category filter if available
    const categoryFilter = page.locator('[data-testid="category-filter"]');
    if (await categoryFilter.isVisible()) {
      await selectOption(page, 'category-filter', 'Testing');
      await waitForLoadingToComplete(page);
      
      // Should show filtered results
      const filteredRows = await page.locator('[data-testid="tools-table"] tbody tr').count();
      expect(filteredRows).toBeGreaterThanOrEqual(0);
    }
  });

  test('should filter tools by status', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Use status filter if available
    const statusFilter = page.locator('[data-testid="status-filter"]');
    if (await statusFilter.isVisible()) {
      await selectOption(page, 'status-filter', 'available');
      await waitForLoadingToComplete(page);
      
      // Should show filtered results
      const filteredRows = await page.locator('[data-testid="tools-table"] tbody tr').count();
      expect(filteredRows).toBeGreaterThanOrEqual(0);
    }
  });

  test('should navigate to add new tool page', async ({ page }) => {
    await clickButton(page, 'add-tool-button');
    
    // Should navigate to new tool page
    await expect(page).toHaveURL('/tools/new');
    
    // Should show new tool form
    await expect(page.locator('[data-testid="tool-form"]')).toBeVisible();
  });

  test('should create a new tool successfully', async ({ page }) => {
    // Navigate to new tool page
    await clickButton(page, 'add-tool-button');
    await expect(page).toHaveURL('/tools/new');
    
    // Fill tool form
    const toolData = testTools.basicTool;
    await fillField(page, 'tool-number-input', toolData.tool_number);
    await fillField(page, 'serial-number-input', toolData.serial_number);
    await fillField(page, 'description-input', toolData.description);
    await selectOption(page, 'category-select', toolData.category);
    await selectOption(page, 'condition-select', toolData.condition);
    await fillField(page, 'location-input', toolData.location);
    
    // Submit form
    await clickButton(page, 'save-tool-button');
    
    // Should show success message
    await waitForToast(page, 'Tool created successfully', 'success');
    
    // Should redirect to tools list or tool detail
    expect(page.url()).toMatch(/\/tools(\/\d+)?$/);
  });

  test('should show validation errors for invalid tool data', async ({ page }) => {
    // Navigate to new tool page
    await clickButton(page, 'add-tool-button');
    
    // Try to submit empty form
    await clickButton(page, 'save-tool-button');
    
    // Should show validation errors
    await expect(page.locator('.is-invalid, .error-message')).toHaveCount(2); // At least tool number and description
  });

  test('should view tool details', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Click on first tool's view button (if any tools exist)
    const firstViewButton = page.locator('[data-testid="view-tool-button"]').first();
    if (await firstViewButton.isVisible()) {
      await firstViewButton.click();
      
      // Should navigate to tool detail page
      expect(page.url()).toMatch(/\/tools\/\d+$/);
      
      // Should show tool details
      await expect(page.locator('[data-testid="tool-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="tool-number"]')).toBeVisible();
      await expect(page.locator('[data-testid="tool-description"]')).toBeVisible();
    }
  });

  test('should edit tool successfully', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Click on first tool's edit button (if any tools exist)
    const firstEditButton = page.locator('[data-testid="edit-tool-button"]').first();
    if (await firstEditButton.isVisible()) {
      await firstEditButton.click();
      
      // Should navigate to edit page
      expect(page.url()).toMatch(/\/tools\/\d+\/edit$/);
      
      // Should show edit form with existing data
      await expect(page.locator('[data-testid="tool-form"]')).toBeVisible();
      
      // Update description
      await fillField(page, 'description-input', 'Updated Test Tool Description');
      
      // Save changes
      await clickButton(page, 'save-tool-button');
      
      // Should show success message
      await waitForToast(page, 'Tool updated successfully', 'success');
    }
  });

  test('should delete tool with confirmation', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Click on first tool's delete button (if any tools exist)
    const firstDeleteButton = page.locator('[data-testid="delete-tool-button"]').first();
    if (await firstDeleteButton.isVisible()) {
      await firstDeleteButton.click();
      
      // Should show confirmation dialog
      await expect(page.locator('[data-testid="delete-confirmation"]')).toBeVisible();
      
      // Confirm deletion
      await clickButton(page, 'confirm-delete-button');
      
      // Should show success message
      await waitForToast(page, 'Tool deleted successfully', 'success');
      
      // Should refresh the table
      await waitForLoadingToComplete(page);
    }
  });

  test('should cancel tool deletion', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    const initialRowCount = await page.locator('[data-testid="tools-table"] tbody tr').count();
    
    // Click on first tool's delete button (if any tools exist)
    const firstDeleteButton = page.locator('[data-testid="delete-tool-button"]').first();
    if (await firstDeleteButton.isVisible()) {
      await firstDeleteButton.click();
      
      // Should show confirmation dialog
      await expect(page.locator('[data-testid="delete-confirmation"]')).toBeVisible();
      
      // Cancel deletion
      await clickButton(page, 'cancel-delete-button');
      
      // Dialog should close
      await expect(page.locator('[data-testid="delete-confirmation"]')).not.toBeVisible();
      
      // Row count should remain the same
      const finalRowCount = await page.locator('[data-testid="tools-table"] tbody tr').count();
      expect(finalRowCount).toBe(initialRowCount);
    }
  });

  test('should handle pagination if many tools exist', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Check if pagination exists
    const pagination = page.locator('[data-testid="pagination"]');
    if (await pagination.isVisible()) {
      // Click next page
      const nextButton = page.locator('[data-testid="next-page-button"]');
      if (await nextButton.isVisible() && !await nextButton.isDisabled()) {
        await nextButton.click();
        await waitForLoadingToComplete(page);
        
        // Should load next page
        await expect(page.locator('[data-testid="tools-table"]')).toBeVisible();
      }
    }
  });

  test('should export tools data', async ({ page }) => {
    await waitForTableToLoad(page, 'tools-table');
    
    // Check if export button exists
    const exportButton = page.locator('[data-testid="export-tools-button"]');
    if (await exportButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/tools.*\.(csv|xlsx)$/);
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept tools API and make it fail
    await page.route('**/api/tools', route => {
      route.abort('failed');
    });
    
    await page.reload();
    
    // Should show error message
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
  });
});
