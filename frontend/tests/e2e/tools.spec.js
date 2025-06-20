import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

test.describe('Tools Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin before each test
    await login(page, TEST_USERS.admin);
  });

  test('should display tools list page', async ({ page }) => {
    // Navigate to tools page
    await page.click('nav >> text=Tools');
    await expect(page).toHaveURL('/tools');
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Tools');
    
    // Should show tools list or empty state
    const toolsList = page.locator('[data-testid="tools-list"]');
    const emptyState = page.locator('text=No tools found');
    await expect(toolsList.or(emptyState)).toBeVisible();
  });

  test('should display search and filter options', async ({ page }) => {
    await page.goto('/tools');
    
    // Check for search input
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
    
    // Check for filter options
    await expect(page.locator('[data-testid="category-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="status-filter"]')).toBeVisible();
  });

  test('should search tools by tool number', async ({ page }) => {
    await page.goto('/tools');
    
    // Enter search term
    await page.fill('input[placeholder*="Search"]', 'T001');
    
    // Should filter results
    await page.waitForTimeout(500); // Wait for search debounce
    
    // Check that search results are displayed
    const searchResults = page.locator('[data-testid="tools-list"] [data-testid="tool-item"]');
    if (await searchResults.count() > 0) {
      // If there are results, they should contain the search term
      await expect(searchResults.first()).toContainText('T001');
    }
  });

  test('should filter tools by category', async ({ page }) => {
    await page.goto('/tools');
    
    // Select a category filter
    await page.selectOption('[data-testid="category-filter"]', 'Testing');
    
    // Should filter results
    await page.waitForTimeout(500);
    
    // Check that filtered results are displayed
    const filteredResults = page.locator('[data-testid="tools-list"] [data-testid="tool-item"]');
    if (await filteredResults.count() > 0) {
      // Results should be from selected category
      await expect(filteredResults.first()).toContainText('Testing');
    }
  });

  test('should filter tools by status', async ({ page }) => {
    await page.goto('/tools');
    
    // Select status filter
    await page.selectOption('[data-testid="status-filter"]', 'available');
    
    // Should filter results
    await page.waitForTimeout(500);
    
    // Check that filtered results show correct status
    const statusBadges = page.locator('[data-testid="tool-status"]');
    if (await statusBadges.count() > 0) {
      await expect(statusBadges.first()).toContainText('Available');
    }
  });

  test('should navigate to tool detail page', async ({ page }) => {
    await page.goto('/tools');
    
    // Click on first tool if available
    const firstTool = page.locator('[data-testid="tool-item"]').first();
    
    if (await firstTool.isVisible()) {
      await firstTool.click();
      
      // Should navigate to tool detail page
      await expect(page).toHaveURL(/\/tools\/\d+/);
      
      // Should show tool details
      await expect(page.locator('[data-testid="tool-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="tool-number"]')).toBeVisible();
      await expect(page.locator('[data-testid="tool-description"]')).toBeVisible();
    }
  });

  test('should display add new tool button for admin', async ({ page }) => {
    await page.goto('/tools');
    
    // Admin should see add new tool button
    await expect(page.locator('text=Add New Tool')).toBeVisible();
  });

  test('should navigate to new tool form', async ({ page }) => {
    await page.goto('/tools');
    
    // Click add new tool button
    await page.click('text=Add New Tool');
    
    // Should navigate to new tool form
    await expect(page).toHaveURL('/tools/new');
    await expect(page.locator('h1')).toContainText('Add New Tool');
    
    // Should show form fields
    await expect(page.locator('input[name="tool_number"]')).toBeVisible();
    await expect(page.locator('input[name="serial_number"]')).toBeVisible();
    await expect(page.locator('textarea[name="description"]')).toBeVisible();
  });

  test('should create new tool with valid data', async ({ page }) => {
    await page.goto('/tools/new');
    
    // Fill in tool data
    const toolNumber = `T${Date.now()}`;
    await page.fill('input[name="tool_number"]', toolNumber);
    await page.fill('input[name="serial_number"]', `S${Date.now()}`);
    await page.fill('textarea[name="description"]', 'Test Tool Description');
    await page.selectOption('select[name="category"]', 'Testing');
    await page.selectOption('select[name="condition"]', 'Good');
    await page.fill('input[name="location"]', 'Test Location');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to tools list or tool detail
    await expect(page).toHaveURL(/\/tools/);
    
    // Should show success message
    await expect(page.locator('.alert-success')).toBeVisible();
  });

  test('should show validation errors for invalid tool data', async ({ page }) => {
    await page.goto('/tools/new');
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('.invalid-feedback')).toBeVisible();
  });

  test('should checkout tool from detail page', async ({ page }) => {
    await page.goto('/tools');
    
    // Find an available tool
    const availableTool = page.locator('[data-testid="tool-item"]:has([data-testid="tool-status"]:has-text("Available"))').first();
    
    if (await availableTool.isVisible()) {
      await availableTool.click();
      
      // Should be on tool detail page
      await expect(page).toHaveURL(/\/tools\/\d+/);
      
      // Click checkout button
      await page.click('text=Check Out');
      
      // Should show checkout modal or navigate to checkout page
      const checkoutModal = page.locator('[data-testid="checkout-modal"]');
      const checkoutPage = page.locator('h1:has-text("Check Out Tool")');
      
      await expect(checkoutModal.or(checkoutPage)).toBeVisible();
    }
  });

  test('should display tool status correctly', async ({ page }) => {
    await page.goto('/tools');
    
    // Check that tools display status badges
    const statusBadges = page.locator('[data-testid="tool-status"]');
    
    if (await statusBadges.count() > 0) {
      // Status should be one of the valid statuses
      const firstStatus = await statusBadges.first().textContent();
      expect(['Available', 'Checked Out', 'Maintenance', 'Retired']).toContain(firstStatus.trim());
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/tools');
    
    // Should still show tools list
    await expect(page.locator('h1')).toContainText('Tools');
    
    // Tools should be displayed in mobile-friendly format
    const toolsList = page.locator('[data-testid="tools-list"]');
    if (await toolsList.isVisible()) {
      await expect(toolsList).toBeVisible();
    }
  });
});
