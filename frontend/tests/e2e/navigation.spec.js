import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.admin);
  });

  test('should display main navigation menu', async ({ page }) => {
    // Check for main navigation items
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Tools')).toBeVisible();
    await expect(page.locator('text=Checkouts')).toBeVisible();
  });

  test('should navigate to tools page', async ({ page }) => {
    // Click on Tools navigation
    await page.click('nav >> text=Tools');
    
    // Should navigate to tools page
    await expect(page).toHaveURL('/tools');
    await expect(page.locator('h1')).toContainText('Tools');
    
    // Should show tools list or empty state
    const toolsList = page.locator('[data-testid="tools-list"]');
    const emptyState = page.locator('text=No tools found');
    await expect(toolsList.or(emptyState)).toBeVisible();
  });

  test('should navigate to checkouts page', async ({ page }) => {
    // Click on Checkouts navigation
    await page.click('nav >> text=Checkouts');
    
    // Should navigate to checkouts page
    await expect(page).toHaveURL('/checkouts');
    await expect(page.locator('h1')).toContainText('Checkouts');
  });

  test('should navigate to chemicals page (if user has access)', async ({ page }) => {
    // Try to navigate to chemicals (admin should have access)
    const chemicalsLink = page.locator('nav >> text=Chemicals');
    
    if (await chemicalsLink.isVisible()) {
      await chemicalsLink.click();
      await expect(page).toHaveURL('/chemicals');
      await expect(page.locator('h1')).toContainText('Chemicals');
    }
  });

  test('should navigate to reports page', async ({ page }) => {
    // Click on Reports navigation
    const reportsLink = page.locator('nav >> text=Reports');
    
    if (await reportsLink.isVisible()) {
      await reportsLink.click();
      await expect(page).toHaveURL('/reports');
      await expect(page.locator('h1')).toContainText('Reports');
    }
  });

  test('should navigate to admin dashboard (admin only)', async ({ page }) => {
    // Click on Admin navigation (should be visible for admin user)
    const adminLink = page.locator('nav >> text=Admin');
    
    if (await adminLink.isVisible()) {
      await adminLink.click();
      await expect(page).toHaveURL('/admin/dashboard');
      await expect(page.locator('h1')).toContainText('Admin Dashboard');
    }
  });

  test('should highlight active navigation item', async ({ page }) => {
    // Navigate to tools page
    await page.click('nav >> text=Tools');
    await expect(page).toHaveURL('/tools');
    
    // Tools navigation item should be active/highlighted
    const toolsNavItem = page.locator('nav >> text=Tools').locator('..');
    await expect(toolsNavItem).toHaveClass(/active|current/);
  });

  test('should work with browser back/forward buttons', async ({ page }) => {
    // Navigate to tools
    await page.click('nav >> text=Tools');
    await expect(page).toHaveURL('/tools');
    
    // Navigate to checkouts
    await page.click('nav >> text=Checkouts');
    await expect(page).toHaveURL('/checkouts');
    
    // Use browser back button
    await page.goBack();
    await expect(page).toHaveURL('/tools');
    
    // Use browser forward button
    await page.goForward();
    await expect(page).toHaveURL('/checkouts');
  });

  test('should display user menu in navigation', async ({ page }) => {
    // Check for user menu
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Click user menu
    await page.click('[data-testid="user-menu"]');
    
    // Should show dropdown with user options
    await expect(page.locator('text=Profile')).toBeVisible();
    await expect(page.locator('text=Logout')).toBeVisible();
  });

  test('should navigate to profile page from user menu', async ({ page }) => {
    // Click user menu
    await page.click('[data-testid="user-menu"]');
    
    // Click profile
    await page.click('text=Profile');
    
    // Should navigate to profile page
    await expect(page).toHaveURL('/profile');
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Should show mobile menu toggle
    await expect(page.locator('[data-testid="mobile-menu-toggle"]')).toBeVisible();
    
    // Click mobile menu toggle
    await page.click('[data-testid="mobile-menu-toggle"]');
    
    // Should show mobile navigation menu
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    await expect(page.locator('[data-testid="mobile-menu"] >> text=Tools')).toBeVisible();
  });

  test('should close mobile menu when navigation item is clicked', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Open mobile menu
    await page.click('[data-testid="mobile-menu-toggle"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    // Click a navigation item
    await page.click('[data-testid="mobile-menu"] >> text=Tools');
    
    // Should navigate and close menu
    await expect(page).toHaveURL('/tools');
    await expect(page.locator('[data-testid="mobile-menu"]')).not.toBeVisible();
  });

  test('should display breadcrumbs on detail pages', async ({ page }) => {
    // Navigate to tools
    await page.click('nav >> text=Tools');
    await expect(page).toHaveURL('/tools');
    
    // If there are tools, click on one to go to detail page
    const firstTool = page.locator('[data-testid="tool-item"]').first();
    
    if (await firstTool.isVisible()) {
      await firstTool.click();
      
      // Should show breadcrumbs
      await expect(page.locator('[data-testid="breadcrumbs"]')).toBeVisible();
      await expect(page.locator('[data-testid="breadcrumbs"] >> text=Tools')).toBeVisible();
    }
  });
});
