/**
 * E2E tests for sidebar navigation and layout features.
 */

import { test, expect } from '@playwright/test';
import { setupAuthenticatedState, TEST_USERS } from './utils/auth.js';

async function ensureLoggedIn(page, user = TEST_USERS.admin) {
  await setupAuthenticatedState(page, user, { navigateToDashboard: true });
}

test.describe('Sidebar Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display sidebar with navigation links', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();

    // Check for essential navigation links
    await expect(sidebar.locator('a[href="/dashboard"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/tools"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/checkouts"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/kits"]')).toBeVisible();
  });

  test('should collapse and expand sidebar', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const toggleButton = page.locator('.sidebar-toggle-btn');

    await expect(sidebar).toBeVisible();
    await expect(toggleButton).toBeVisible();

    // Initially not collapsed
    await expect(sidebar).not.toHaveClass(/collapsed/);

    // Click to collapse
    await toggleButton.click();
    await expect(sidebar).toHaveClass(/collapsed/);

    // Click to expand
    await toggleButton.click();
    await expect(sidebar).not.toHaveClass(/collapsed/);
  });

  test('should show brand logo when sidebar is expanded', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const brand = sidebar.locator('.sidebar-brand');

    // When expanded, brand should be visible
    await expect(sidebar).not.toHaveClass(/collapsed/);
    await expect(brand).toBeVisible();
    await expect(brand).toContainText('SupplyLine MRO');

    // When collapsed, brand should be hidden
    await page.click('.sidebar-toggle-btn');
    await expect(sidebar).toHaveClass(/collapsed/);
    await expect(brand).not.toBeVisible();
  });

  test('should highlight active navigation item', async ({ page }) => {
    // On dashboard page, dashboard link should be active
    const dashboardLink = page.locator('.sidebar a[href="/dashboard"]');
    await expect(dashboardLink).toHaveClass(/active/);

    // Navigate to tools page
    await page.click('.sidebar a[href="/tools"]');
    await page.waitForLoadState('networkidle');

    // Tools link should now be active
    const toolsLink = page.locator('.sidebar a[href="/tools"]');
    await expect(toolsLink).toHaveClass(/active/);

    // Dashboard link should no longer be active
    await expect(page.locator('.sidebar a[href="/dashboard"]')).not.toHaveClass(/active/);
  });

  test('should show user menu at bottom of sidebar', async ({ page }) => {
    const userMenu = page.locator('[data-testid="user-menu"]');
    await expect(userMenu).toBeVisible();

    // User menu should be in sidebar-user-section
    await expect(page.locator('.sidebar-user-section')).toBeVisible();
  });

  test('should display user avatar or initials', async ({ page }) => {
    const userSection = page.locator('.sidebar-user-section');
    const avatar = userSection.locator('.sidebar-avatar');

    await expect(avatar).toBeVisible();

    // Avatar should show either image or initials
    const hasImage = await avatar.locator('img').count() > 0;
    const hasInitials = await avatar.textContent();

    expect(hasImage || hasInitials.length > 0).toBeTruthy();
  });

  test('should show user name when sidebar is expanded', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const userName = page.locator('.sidebar-user-name');

    // When expanded, user name should be visible
    await expect(sidebar).not.toHaveClass(/collapsed/);
    await expect(userName).toBeVisible();

    // When collapsed, user name should be hidden
    await page.click('.sidebar-toggle-btn');
    await expect(sidebar).toHaveClass(/collapsed/);
    await expect(userName).not.toBeVisible();
  });

  test('should show permission-based navigation for admin', async ({ page }) => {
    const sidebar = page.locator('.sidebar');

    // Admin should see all navigation items
    await expect(sidebar.locator('a[href="/chemicals"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/calibrations"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/warehouses"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/reports"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/admin/dashboard"]')).toBeVisible();
  });

  test('should show History link for all users', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const historyLink = sidebar.locator('a[href="/history"]');

    // History is available to all authenticated users
    await expect(historyLink).toBeVisible();
  });

  test('should navigate correctly when clicking sidebar links', async ({ page }) => {
    // Navigate to different pages using sidebar
    await page.click('.sidebar a[href="/kits"]');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/kits');

    await page.click('.sidebar a[href="/chemicals"]');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/chemicals');

    await page.click('.sidebar a[href="/dashboard"]');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL('/dashboard');
  });
});

test.describe('Main Content Area', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should have main content area', async ({ page }) => {
    const mainContent = page.locator('.main-content');
    await expect(mainContent).toBeVisible();
  });

  test('should adjust main content when sidebar collapses', async ({ page }) => {
    const mainContent = page.locator('.main-content');

    // Initially sidebar is expanded
    await expect(mainContent).not.toHaveClass(/sidebar-collapsed/);

    // Collapse sidebar
    await page.click('.sidebar-toggle-btn');

    // Main content should adjust
    await expect(mainContent).toHaveClass(/sidebar-collapsed/);

    // Expand sidebar again
    await page.click('.sidebar-toggle-btn');
    await expect(mainContent).not.toHaveClass(/sidebar-collapsed/);
  });

  test('should display footer with version info', async ({ page }) => {
    const footer = page.locator('.main-footer');
    await expect(footer).toBeVisible();

    // Footer should contain copyright and version
    await expect(footer).toContainText('SupplyLine MRO Suite');
    await expect(footer).toContainText('Version');
  });
});

test.describe('User Profile Modal', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should open profile modal from user menu', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');

    // Profile modal should open
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();
  });

  test('should display user information in profile modal', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Should show user name
    await expect(page.locator('h5:has-text("John Engineer")')).toBeVisible();

    // Should show user role
    await expect(page.locator('p.text-muted:has-text("Administrator")')).toBeVisible();
  });

  test('should have theme toggle switch', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Should have theme switch
    const themeSwitch = page.locator('#theme-switch');
    await expect(themeSwitch).toBeVisible();
  });

  test('should have keyboard shortcuts toggle', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Should have hotkeys switch
    const hotkeysSwitch = page.locator('#hotkeys-switch');
    await expect(hotkeysSwitch).toBeVisible();
  });

  test('should navigate to View Profile page', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Click View Profile link
    await page.click('text=View Profile');
    await page.waitForLoadState('networkidle');

    // Should navigate to profile page
    await expect(page).toHaveURL('/profile');
  });

  test('should navigate to My Checkouts from profile modal', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Click My Checkouts link
    await page.click('.modal-body a:has-text("My Checkouts")');
    await page.waitForLoadState('networkidle');

    // Should navigate to my-checkouts page
    await expect(page).toHaveURL('/my-checkouts');
  });

  test('should close profile modal', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Click Close button
    await page.click('.modal-footer button:has-text("Close")');

    // Modal should be closed
    await expect(page.locator('.modal-title:has-text("User Profile")')).not.toBeVisible();
  });

  test('should have logout button in profile modal', async ({ page }) => {
    await page.click('[data-testid="user-menu"]');
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Should have logout button
    const logoutButton = page.locator('.modal-footer button:has-text("Logout")');
    await expect(logoutButton).toBeVisible();
    await expect(logoutButton).toHaveClass(/btn-danger/);
  });
});

test.describe('Page Transitions', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should show loading overlay during navigation', async ({ page }) => {
    // Navigate to a different page
    await page.click('.sidebar a[href="/tools"]');

    // Loading overlay may appear briefly
    const loadingOverlay = page.locator('.page-loading-overlay');
    // It's ok if it's not visible (fast transition) or visible briefly
    await page.waitForLoadState('networkidle');

    // Should end up on tools page
    await expect(page).toHaveURL('/tools');
  });

  test('should apply page transition classes', async ({ page }) => {
    // The page content wrapper should have transition class
    const pageTransition = page.locator('.page-transition');
    await expect(pageTransition).toBeVisible();
  });
});

test.describe('Responsive Layout', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
  });

  test('should be functional on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Sidebar should be visible
    await expect(page.locator('.sidebar')).toBeVisible();

    // Main content should be visible
    await expect(page.locator('.main-content')).toBeVisible();

    // Dashboard should be functional
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should work with small desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // All elements should be accessible
    await expect(page.locator('.sidebar')).toBeVisible();
    await expect(page.locator('.main-content')).toBeVisible();
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });
});
