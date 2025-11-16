/**
 * E2E tests for dashboard widgets and customization features.
 */

import { test, expect } from '@playwright/test';
import { setupAuthenticatedState, TEST_USERS } from './utils/auth.js';

async function ensureLoggedIn(page, user = TEST_USERS.admin) {
  await setupAuthenticatedState(page, user, { navigateToDashboard: true });
}

test.describe('Dashboard Widgets', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display all expected dashboard widgets for admin', async ({ page }) => {
    // Check that dashboard content is visible
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();

    // Check for key widgets
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-activity"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-checkout-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="announcements"]')).toBeVisible();

    // Check for dashboard title
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should display calibration notifications widget', async ({ page }) => {
    // Check for calibration notifications (always visible)
    const calibrationWidget = page.locator('text=Calibration Notifications, text=Calibrations Due');
    await expect(calibrationWidget.first()).toBeVisible();
  });

  test('should display kit alerts summary widget', async ({ page }) => {
    // Check for kit alerts summary (always visible)
    const kitAlertsWidget = page.locator('text=Kit Alerts');
    await expect(kitAlertsWidget.first()).toBeVisible();
  });

  test('should display user checkout status with correct information', async ({ page }) => {
    const checkoutWidget = page.locator('[data-testid="user-checkout-status"]');
    await expect(checkoutWidget).toBeVisible();

    // Should show header and count badge
    await expect(checkoutWidget.locator('text=My Checked Out Tools')).toBeVisible();

    // Should show either list of checkouts or empty state message
    const hasCheckouts = await checkoutWidget.locator('.list-group-item').count() > 0;
    const hasEmptyMessage = await checkoutWidget.locator('text=no tools checked out, text=don\'t have any tools').first().isVisible().catch(() => false);

    expect(hasCheckouts || hasEmptyMessage).toBeTruthy();
  });

  test('should display quick actions with correct buttons for admin', async ({ page }) => {
    const quickActionsWidget = page.locator('[data-testid="quick-actions"]');
    await expect(quickActionsWidget).toBeVisible();

    // Check for common quick actions
    await expect(quickActionsWidget.locator('text=Checkout Tool')).toBeVisible();
    await expect(quickActionsWidget.locator('text=My Checkouts')).toBeVisible();
    await expect(quickActionsWidget.locator('text=View Kits')).toBeVisible();

    // Check for admin-specific quick actions
    await expect(quickActionsWidget.locator('text=Admin Dashboard')).toBeVisible();
    await expect(quickActionsWidget.locator('text=Add New Tool')).toBeVisible();
  });

  test('should navigate from quick actions', async ({ page }) => {
    const quickActionsWidget = page.locator('[data-testid="quick-actions"]');

    // Click on View Kits quick action
    await quickActionsWidget.locator('text=View Kits').click();
    await page.waitForLoadState('networkidle');

    // Should navigate to kits page
    await expect(page).toHaveURL('/kits');
  });

  test('should display recent activity widget', async ({ page }) => {
    const recentActivityWidget = page.locator('[data-testid="recent-activity"]');
    await expect(recentActivityWidget).toBeVisible();

    // Should show header
    await expect(recentActivityWidget.locator('text=Recent Activity')).toBeVisible();

    // Should show either activity list or empty state
    const activityList = page.locator('[data-testid="activity-list"]');
    const emptyState = recentActivityWidget.locator('text=No recent activity');

    await expect(activityList.or(emptyState)).toBeVisible();
  });

  test('should display announcements widget', async ({ page }) => {
    const announcementsWidget = page.locator('[data-testid="announcements"]');
    await expect(announcementsWidget).toBeVisible();

    // Should show header
    await expect(announcementsWidget.locator('text=Announcements')).toBeVisible();

    // Should show either announcements list or empty state
    const hasList = await announcementsWidget.locator('.list-group-item').count() > 0;
    const hasEmptyMessage = await announcementsWidget.locator('text=No announcements').isVisible().catch(() => false);

    expect(hasList || hasEmptyMessage).toBeTruthy();
  });

  test('should apply role-based theme to dashboard', async ({ page }) => {
    // Admin users should have admin theme class
    const dashboardRoot = page.locator('.dashboard-root');
    await expect(dashboardRoot).toBeVisible();

    // Should have one of the theme classes
    const hasAdminTheme = await dashboardRoot.locator('.dashboard-theme-admin').count() > 0;
    const hasMaterialsTheme = await dashboardRoot.locator('.dashboard-theme-materials').count() > 0;
    const hasStandardTheme = await dashboardRoot.locator('.dashboard-theme-standard').count() > 0;

    // Admin user should have admin theme
    const classAttribute = await dashboardRoot.getAttribute('class');
    expect(classAttribute).toContain('dashboard-theme-admin');
  });
});

test.describe('Dashboard Customization', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should open dashboard customization modal from user menu', async ({ page }) => {
    // Open user menu
    await page.click('[data-testid="user-menu"]');

    // Wait for profile modal to appear
    await expect(page.locator('.modal-title:has-text("User Profile")')).toBeVisible();

    // Click on "Customize Dashboard" button (only visible when on dashboard)
    const customizeButton = page.locator('button:has-text("Customize Dashboard")');
    await expect(customizeButton).toBeVisible();
    await customizeButton.click();

    // Should show customization modal
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();
  });

  test('should display widget columns in customization modal', async ({ page }) => {
    // Open user menu and click customize
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');

    // Wait for customization modal
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // Should show three columns: Main, Sidebar, Hidden
    await expect(page.locator('text=Main Column')).toBeVisible();
    await expect(page.locator('text=Sidebar')).toBeVisible();
    await expect(page.locator('text=Hidden Widgets')).toBeVisible();
  });

  test('should allow hiding widgets', async ({ page }) => {
    // Open customization modal
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // Find a widget and click Hide button
    const hideButton = page.locator('.modal-body button:has-text("Hide")').first();
    if (await hideButton.isVisible()) {
      await hideButton.click();

      // Hidden Widgets section should now have content
      const hiddenSection = page.locator('text=Hidden Widgets').locator('..').locator('..');
      await expect(hiddenSection.locator('.list-group-item')).toBeVisible();
    }
  });

  test('should allow restoring hidden widgets', async ({ page }) => {
    // Open customization modal
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // First hide a widget
    const hideButton = page.locator('.modal-body button:has-text("Hide")').first();
    if (await hideButton.isVisible()) {
      const widgetName = await hideButton.locator('..').locator('..').locator('.fw-semibold').first().textContent();
      await hideButton.click();

      // Find Restore button in Hidden Widgets section
      const restoreButton = page.locator('button:has-text("Restore")').first();
      await expect(restoreButton).toBeVisible();
      await restoreButton.click();

      // Widget should be back in a visible column
      await expect(page.locator(`.modal-body:has-text("${widgetName}")`)).toBeVisible();
    }
  });

  test('should reset layout to default', async ({ page }) => {
    // Open customization modal
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // Click reset to default
    const resetButton = page.locator('button:has-text("Reset to Default")');
    await expect(resetButton).toBeVisible();
    await resetButton.click();

    // Verify that hidden widgets section is empty after reset
    await expect(page.locator('text=No hidden widgets')).toBeVisible();
  });

  test('should close customization modal', async ({ page }) => {
    // Open customization modal
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // Click Done button
    await page.click('.modal-footer button:has-text("Done")');

    // Modal should be closed
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).not.toBeVisible();
  });

  test('should persist widget layout after page refresh', async ({ page }) => {
    // Open customization modal and hide a widget
    await page.click('[data-testid="user-menu"]');
    await page.click('button:has-text("Customize Dashboard")');
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    const hideButton = page.locator('.modal-body button:has-text("Hide")').first();
    if (await hideButton.isVisible()) {
      const widgetLabel = await hideButton.locator('..').locator('..').locator('.fw-semibold').first().textContent();
      await hideButton.click();
      await page.click('.modal-footer button:has-text("Done")');

      // Refresh the page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Open customization modal again
      await page.click('[data-testid="user-menu"]');
      await page.click('button:has-text("Customize Dashboard")');
      await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

      // Widget should still be in hidden section
      const hiddenWidgets = page.locator('text=Hidden Widgets').locator('..').locator('..');
      await expect(hiddenWidgets.locator(`:has-text("${widgetLabel}")`)).toBeVisible();
    }
  });
});

test.describe('Admin Dashboard Widgets', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.admin);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should show pending user requests widget for admin', async ({ page }) => {
    // Pending User Requests widget is only visible to admins
    // It may or may not have pending requests
    const pendingUserRequestsWidget = page.locator('text=Pending User Requests');

    // Widget should be present for admin users
    await expect(pendingUserRequestsWidget).toBeVisible();
  });

  test('should show past due tools widget for admin', async ({ page }) => {
    // Past Due Tools widget is visible to admin and materials users
    const pastDueWidget = page.locator('text=Past Due Tools');
    await expect(pastDueWidget).toBeVisible();
  });
});

test.describe('Materials Manager Dashboard', () => {
  test('should show materials-specific widgets', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.materials);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check dashboard has correct theme for materials manager
    const dashboardRoot = page.locator('.dashboard-root');
    const classAttribute = await dashboardRoot.getAttribute('class');
    expect(classAttribute).toContain('dashboard-theme-materials');

    // Should have access to past due tools widget
    const pastDueWidget = page.locator('text=Past Due Tools');
    await expect(pastDueWidget).toBeVisible();
  });
});

test.describe('Regular User Dashboard', () => {
  test('should show standard user widgets without admin features', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.user);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check dashboard has standard theme
    const dashboardRoot = page.locator('.dashboard-root');
    const classAttribute = await dashboardRoot.getAttribute('class');
    expect(classAttribute).toContain('dashboard-theme-standard');

    // Should have basic widgets
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-checkout-status"]')).toBeVisible();

    // Should NOT have admin-specific widgets like Pending User Requests
    const pendingUserRequests = page.locator('text=Pending User Requests');
    await expect(pendingUserRequests).not.toBeVisible();
  });
});
