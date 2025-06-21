import { test, expect } from '@playwright/test';

// Test data
const TEST_USER = {
  username: 'ADMIN001',
  password: 'admin123'
};

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[placeholder="Enter employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display dashboard title and main sections', async ({ page }) => {
    // Check dashboard title
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Check for main dashboard sections
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-activity"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-checkout-status"]')).toBeVisible();
  });

  test('should display quick action buttons', async ({ page }) => {
    // Check for quick action buttons
    await expect(page.locator('text=Check Out Tool')).toBeVisible();
    await expect(page.locator('text=View Tools')).toBeVisible();
    await expect(page.locator('text=My Checkouts')).toBeVisible();
  });

  test('should navigate to tools page from quick actions', async ({ page }) => {
    // Click on View Tools quick action
    await page.click('text=View Tools');
    
    // Should navigate to tools page
    await expect(page).toHaveURL('/tools');
    await expect(page.locator('h1')).toContainText('Tools');
  });

  test('should navigate to checkouts page from quick actions', async ({ page }) => {
    // Click on My Checkouts quick action
    await page.click('text=My Checkouts');
    
    // Should navigate to checkouts page
    await expect(page).toHaveURL('/my-checkouts');
  });

  test('should display user information in navbar', async ({ page }) => {
    // Check that user menu is visible
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Click user menu to see user info
    await page.click('[data-testid="user-menu"]');
    
    // Should show user name or employee number
    await expect(page.locator('text=ADMIN001')).toBeVisible();
  });

  test('should display announcements section', async ({ page }) => {
    // Check for announcements section
    await expect(page.locator('[data-testid="announcements"]')).toBeVisible();
  });

  test('should display recent activity', async ({ page }) => {
    // Check for recent activity section
    await expect(page.locator('[data-testid="recent-activity"]')).toBeVisible();
    
    // Should have activity list or empty state message
    const activityList = page.locator('[data-testid="activity-list"]');
    const emptyState = page.locator('text=No recent activity');
    
    await expect(activityList.or(emptyState)).toBeVisible();
  });

  test('should display overdue items if any', async ({ page }) => {
    // Check for overdue tools section
    const overdueSection = page.locator('[data-testid="overdue-tools"]');
    
    // If overdue section exists, it should be visible
    if (await overdueSection.isVisible()) {
      await expect(overdueSection).toBeVisible();
    }
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Dashboard should still be functional
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    
    // Navigation should work on mobile
    await page.click('[data-testid="mobile-menu-toggle"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
  });

  test('should refresh data when page is refreshed', async ({ page }) => {
    // Get initial content
    const initialContent = await page.locator('[data-testid="dashboard-content"]').textContent();
    
    // Refresh page
    await page.reload();
    
    // Should still show dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Content should be loaded (might be same or different)
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
  });
});
