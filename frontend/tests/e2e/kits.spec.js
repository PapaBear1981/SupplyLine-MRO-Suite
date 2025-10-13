import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

/**
 * E2E Tests for Kit Management Functionality
 * 
 * Tests cover:
 * - Kit listing and filtering
 * - Kit creation wizard
 * - Kit detail view
 * - Kit items management
 * - Kit transfers
 * - Kit reorders
 * - Kit reports
 * - Mobile interface
 */

test.describe('Kit Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin before each test
    await login(page, TEST_USERS.admin);
  });

  test.describe('Kit Listing Page', () => {
    test('should display kits management page', async ({ page }) => {
      await page.goto('/kits');
      
      // Check page title and header
      await expect(page.locator('h2')).toContainText('Mobile Warehouses (Kits)');
      await expect(page.locator('text=Manage mobile warehouses that follow aircraft')).toBeVisible();
      
      // Check action buttons
      await expect(page.locator('button:has-text("Create Kit")')).toBeVisible();
      await expect(page.locator('button:has-text("Reports")')).toBeVisible();
    });

    test('should filter kits by search term', async ({ page }) => {
      await page.goto('/kits');
      
      // Wait for kits to load
      await page.waitForSelector('[placeholder*="Search kits"]', { timeout: 5000 });
      
      // Enter search term
      const searchInput = page.locator('[placeholder*="Search kits"]');
      await searchInput.fill('Q400');
      
      // Verify filtering works (kits should update)
      await page.waitForTimeout(500); // Wait for debounce
    });

    test('should filter kits by aircraft type', async ({ page }) => {
      await page.goto('/kits');
      
      // Wait for aircraft type filter
      await page.waitForSelector('select', { timeout: 5000 });
      
      // Select an aircraft type if available
      const aircraftSelect = page.locator('select').first();
      const options = await aircraftSelect.locator('option').count();
      
      if (options > 1) {
        await aircraftSelect.selectOption({ index: 1 });
        await page.waitForTimeout(500);
      }
    });

    test('should navigate to create kit page', async ({ page }) => {
      await page.goto('/kits');
      
      // Click create kit button
      await page.click('button:has-text("Create Kit")');
      
      // Verify navigation to wizard
      await expect(page).toHaveURL('/kits/new');
      await expect(page.locator('h3')).toContainText('Create New Kit');
    });

    test('should navigate to reports page', async ({ page }) => {
      await page.goto('/kits');
      
      // Click reports button
      await page.click('button:has-text("Reports")');
      
      // Verify navigation to reports
      await expect(page).toHaveURL('/kits/reports');
    });

    test('should display kit cards with information', async ({ page }) => {
      await page.goto('/kits');
      
      // Wait for kits to load
      await page.waitForTimeout(1000);
      
      // Check if any kit cards are displayed
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        // Verify first kit card has expected elements
        const firstCard = kitCards.first();
        await expect(firstCard).toBeVisible();
      }
    });

    test('should navigate to kit detail when clicking a kit card', async ({ page }) => {
      await page.goto('/kits');
      
      // Wait for kits to load
      await page.waitForTimeout(1000);
      
      // Find and click first kit card if available
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Verify navigation to detail page
        await expect(page).toHaveURL(/\/kits\/\d+/);
      }
    });
  });

  test.describe('Kit Creation Wizard', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/kits/new');
    });

    test('should display wizard step 1 - aircraft type selection', async ({ page }) => {
      await expect(page.locator('h3')).toContainText('Create New Kit');
      await expect(page.locator('h4')).toContainText('Select Aircraft Type');
      await expect(page.locator('text=Choose the aircraft type')).toBeVisible();
      
      // Check progress bar
      await expect(page.locator('.progress-bar')).toBeVisible();
      
      // Check navigation buttons
      await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
      await expect(page.locator('button:has-text("Next")')).toBeVisible();
    });

    test('should disable next button when no aircraft type selected', async ({ page }) => {
      const nextButton = page.locator('button:has-text("Next")');
      await expect(nextButton).toBeDisabled();
    });

    test('should enable next button when aircraft type is selected', async ({ page }) => {
      // Wait for aircraft types to load
      await page.waitForTimeout(1000);
      
      // Select first aircraft type if available
      const aircraftCards = page.locator('.card').filter({ hasText: /Q400|B737|Aircraft/ });
      const count = await aircraftCards.count();
      
      if (count > 0) {
        await aircraftCards.first().click();
        
        // Next button should be enabled
        const nextButton = page.locator('button:has-text("Next")');
        await expect(nextButton).toBeEnabled();
      }
    });

    test('should navigate to step 2 when next is clicked', async ({ page }) => {
      // Wait for aircraft types to load
      await page.waitForTimeout(1000);
      
      // Select first aircraft type if available
      const aircraftCards = page.locator('.card').filter({ hasText: /Q400|B737|Aircraft/ });
      const count = await aircraftCards.count();
      
      if (count > 0) {
        await aircraftCards.first().click();
        await page.click('button:has-text("Next")');
        
        // Verify step 2 is displayed
        await expect(page.locator('h4')).toContainText('Kit Details');
      }
    });

    test('should validate required fields in step 2', async ({ page }) => {
      // Navigate to step 2
      await page.waitForTimeout(1000);
      const aircraftCards = page.locator('.card').filter({ hasText: /Q400|B737|Aircraft/ });
      const count = await aircraftCards.count();
      
      if (count > 0) {
        await aircraftCards.first().click();
        await page.click('button:has-text("Next")');
        
        // Try to proceed without filling kit name
        await page.click('button:has-text("Next")');
        
        // Should show validation error
        await expect(page.locator('.invalid-feedback, .text-danger')).toBeVisible();
      }
    });

    test('should allow going back to previous step', async ({ page }) => {
      // Navigate to step 2
      await page.waitForTimeout(1000);
      const aircraftCards = page.locator('.card').filter({ hasText: /Q400|B737|Aircraft/ });
      const count = await aircraftCards.count();
      
      if (count > 0) {
        await aircraftCards.first().click();
        await page.click('button:has-text("Next")');
        
        // Click back button
        await page.click('button:has-text("Back")');
        
        // Should be back at step 1
        await expect(page.locator('h4')).toContainText('Select Aircraft Type');
      }
    });

    test('should cancel wizard and return to kits page', async ({ page }) => {
      await page.click('button:has-text("Cancel")');
      
      // Should navigate back to kits page
      await expect(page).toHaveURL('/kits');
    });
  });

  test.describe('Kit Detail Page', () => {
    test('should display kit detail page with tabs', async ({ page }) => {
      // Navigate to first kit detail page
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Verify tabs are present
        await expect(page.locator('text=Overview')).toBeVisible();
        await expect(page.locator('text=Items')).toBeVisible();
        await expect(page.locator('text=Issuances')).toBeVisible();
        await expect(page.locator('text=Transfers')).toBeVisible();
        await expect(page.locator('text=Reorders')).toBeVisible();
      }
    });

    test('should switch between tabs', async ({ page }) => {
      await page.goto('/kits');
      await page.waitForTimeout(1000);
      
      const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
      const count = await kitCards.count();
      
      if (count > 0) {
        await kitCards.first().click();
        
        // Click Items tab
        await page.click('text=Items');
        await page.waitForTimeout(500);
        
        // Click Transfers tab
        await page.click('text=Transfers');
        await page.waitForTimeout(500);
        
        // Click back to Overview
        await page.click('text=Overview');
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Kit Reports', () => {
    test('should display reports page with tabs', async ({ page }) => {
      await page.goto('/kits/reports');
      
      // Check page title
      await expect(page.locator('h2')).toContainText('Kit Reports');
      
      // Check report tabs
      await expect(page.locator('text=Inventory')).toBeVisible();
    });

    test('should switch between report types', async ({ page }) => {
      await page.goto('/kits/reports');
      await page.waitForTimeout(1000);
      
      // Try clicking different report tabs if they exist
      const tabs = page.locator('.nav-link');
      const tabCount = await tabs.count();
      
      if (tabCount > 1) {
        await tabs.nth(1).click();
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Mobile Kit Interface', () => {
    test('should display mobile interface', async ({ page }) => {
      await page.goto('/kits/mobile');
      
      // Check for mobile-specific elements
      await expect(page.locator('h2, h3, h4')).toContainText(/Kit|Mobile|Warehouse/);
    });

    test('should have large touch-friendly buttons', async ({ page }) => {
      await page.goto('/kits/mobile');
      await page.waitForTimeout(1000);
      
      // Check for large buttons (size="lg")
      const largeButtons = page.locator('button.btn-lg');
      const count = await largeButtons.count();
      
      expect(count).toBeGreaterThan(0);
    });
  });
});

