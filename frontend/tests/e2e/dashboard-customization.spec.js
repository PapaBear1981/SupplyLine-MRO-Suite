import { test, expect } from '@playwright/test';

// Test data
const TEST_USER = {
  username: 'ADMIN001',
  password: 'admin123'
};

test.describe('Dashboard Customization', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[placeholder="Enter your employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Enter your password"]', TEST_USER.password);

    // Submit form and wait for navigation
    await Promise.all([
      page.waitForURL('/dashboard', { timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    // Wait for dashboard content to be visible
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
  });

  test('should display customize button', async ({ page }) => {
    // Check for customize button
    await expect(page.locator('button:has-text("Customize")')).toBeVisible();
  });

  test('should open customization modal', async ({ page }) => {
    // Click customize button
    await page.click('button:has-text("Customize")');

    // Modal should be visible
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();
    
    // Should show three columns
    await expect(page.locator('h6:has-text("Main Column")')).toBeVisible();
    await expect(page.locator('h6:has-text("Sidebar")')).toBeVisible();
    await expect(page.locator('h6:has-text("Hidden Widgets")')).toBeVisible();
  });

  test('should display widgets in customization modal', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Should show widgets in main column
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    await expect(mainColumn.locator('.list-group-item').first()).toBeVisible();

    // Should show widgets in sidebar
    const sidebarColumn = page.locator('h6:has-text("Sidebar")').locator('..');
    await expect(sidebarColumn.locator('.list-group-item').first()).toBeVisible();
  });

  test('should hide a widget', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Get the first widget in main column
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    const firstWidget = mainColumn.locator('.list-group-item').first();
    const widgetName = await firstWidget.locator('.fw-semibold').textContent();

    // Click hide button
    await firstWidget.locator('button:has-text("Hide")').click();

    // Widget should now be in hidden column
    const hiddenColumn = page.locator('h6:has-text("Hidden Widgets")').locator('..');
    await expect(hiddenColumn.locator(`.fw-semibold:has-text("${widgetName}")`)).toBeVisible();
  });

  test('should restore a hidden widget', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Hide a widget first
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    const firstWidget = mainColumn.locator('.list-group-item').first();
    const widgetName = await firstWidget.locator('.fw-semibold').textContent();
    await firstWidget.locator('button:has-text("Hide")').click();

    // Now restore it
    const hiddenColumn = page.locator('h6:has-text("Hidden Widgets")').locator('..');
    await hiddenColumn.locator('button:has-text("Restore")').first().click();

    // Widget should be back in a visible column
    const restoredInMain = await mainColumn.locator(`.fw-semibold:has-text("${widgetName}")`).isVisible();
    const restoredInSidebar = await page.locator('h6:has-text("Sidebar")').locator('..').locator(`.fw-semibold:has-text("${widgetName}")`).isVisible();
    
    expect(restoredInMain || restoredInSidebar).toBeTruthy();
  });

  test('should move widget between columns', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Get the first widget in main column
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    const firstWidget = mainColumn.locator('.list-group-item').first();
    const widgetName = await firstWidget.locator('.fw-semibold').textContent();

    // Move to sidebar
    await firstWidget.locator('button:has-text("Move to Sidebar")').click();

    // Widget should now be in sidebar
    const sidebarColumn = page.locator('h6:has-text("Sidebar")').locator('..');
    await expect(sidebarColumn.locator(`.fw-semibold:has-text("${widgetName}")`)).toBeVisible();
  });

  test('should reorder widgets within a column', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Get the first two widgets in main column
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    const widgets = mainColumn.locator('.list-group-item');

    // Get name of second widget (will become first after move)
    const secondWidgetName = await widgets.nth(1).locator('.fw-semibold').textContent();

    // Move first widget down
    await widgets.nth(0).locator('button[aria-label="Move down"]').click();

    // Wait a bit for the reorder
    await page.waitForTimeout(500);

    // Check order has changed
    const newFirstWidgetName = await mainColumn.locator('.list-group-item').nth(0).locator('.fw-semibold').textContent();
    expect(newFirstWidgetName).toBe(secondWidgetName);
  });

  test('should reset layout to default', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Hide a widget
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    await mainColumn.locator('.list-group-item').first().locator('button:has-text("Hide")').click();

    // Click reset button
    await page.click('button:has-text("Reset to Default")');

    // Hidden widgets should be empty
    const hiddenColumn = page.locator('h6:has-text("Hidden Widgets")').locator('..');
    await expect(hiddenColumn.locator('text=No hidden widgets.')).toBeVisible();
  });

  test('should persist layout across page refreshes', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Hide a widget
    const mainColumn = page.locator('h6:has-text("Main Column")').locator('..');
    const firstWidget = mainColumn.locator('.list-group-item').first();
    const widgetName = await firstWidget.locator('.fw-semibold').textContent();
    await firstWidget.locator('button:has-text("Hide")').click();

    // Close modal
    await page.click('button:has-text("Done")');

    // Refresh page
    await page.reload();
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();

    // Open customization modal again
    await page.click('button:has-text("Customize")');

    // Widget should still be hidden
    const hiddenColumn = page.locator('h6:has-text("Hidden Widgets")').locator('..');
    await expect(hiddenColumn.locator(`.fw-semibold:has-text("${widgetName}")`)).toBeVisible();
  });

  test('should close customization modal', async ({ page }) => {
    // Open customization modal
    await page.click('button:has-text("Customize")');

    // Modal should be visible
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).toBeVisible();

    // Click done button
    await page.click('button:has-text("Done")');

    // Modal should be closed
    await expect(page.locator('.modal-title:has-text("Customize Dashboard")')).not.toBeVisible();
  });
});

test.describe('Quick Actions Favorites', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[placeholder="Enter your employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Enter your password"]', TEST_USER.password);

    await Promise.all([
      page.waitForURL('/dashboard', { timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
  });

  test('should display quick actions with star icons', async ({ page }) => {
    // Quick actions should be visible
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();

    // Should have star icons on action buttons
    const starIcons = page.locator('[data-testid="quick-actions"] .bi-star, [data-testid="quick-actions"] .bi-star-fill');
    await expect(starIcons.first()).toBeVisible();
  });

  test('should pin a quick action', async ({ page }) => {
    // Find an unpinned action (has bi-star, not bi-star-fill)
    const unpinnedStar = page.locator('[data-testid="quick-actions"] .bi-star').first();
    
    // Click to pin
    await unpinnedStar.click();

    // Should now be filled star
    await expect(page.locator('[data-testid="quick-actions"] .bi-star-fill').first()).toBeVisible();

    // Should show "Pinned Favorites" section
    await expect(page.locator('text=Pinned Favorites')).toBeVisible();
  });

  test('should unpin a quick action', async ({ page }) => {
    // Pin an action first
    const unpinnedStar = page.locator('[data-testid="quick-actions"] .bi-star').first();
    await unpinnedStar.click();

    // Now unpin it
    const pinnedStar = page.locator('[data-testid="quick-actions"] .bi-star-fill').first();
    await pinnedStar.click();

    // Should be back to unfilled star
    await expect(page.locator('[data-testid="quick-actions"] .bi-star').first()).toBeVisible();
  });

  test('should persist pinned actions across page refreshes', async ({ page }) => {
    // Pin an action
    const unpinnedStar = page.locator('[data-testid="quick-actions"] .bi-star').first();
    await unpinnedStar.click();

    // Get the parent button to find the action name
    const actionButton = unpinnedStar.locator('..').locator('..');
    const actionName = await actionButton.locator('span.text-center').textContent();

    // Refresh page
    await page.reload();
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();

    // Should still show pinned favorites section
    await expect(page.locator('text=Pinned Favorites')).toBeVisible();

    // The action should still be pinned
    const pinnedSection = page.locator('text=Pinned Favorites').locator('..');
    await expect(pinnedSection.locator(`text=${actionName}`)).toBeVisible();
  });

  test('should show badge count for pinned favorites', async ({ page }) => {
    // Pin two actions
    const stars = page.locator('[data-testid="quick-actions"] .bi-star');
    await stars.nth(0).click();
    await stars.nth(1).click();

    // Should show badge with count
    await expect(page.locator('.badge:has-text("2")')).toBeVisible();
  });
});

test.describe('Role-Based Dashboard Themes', () => {
  test('should apply admin theme for admin users', async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.fill('input[placeholder="Enter your employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Enter your password"]', TEST_USER.password);

    await Promise.all([
      page.waitForURL('/dashboard', { timeout: 10000 }),
      page.click('button[type="submit"]')
    ]);

    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();

    // Check for admin theme class
    const dashboardRoot = page.locator('.dashboard-root');
    await expect(dashboardRoot).toHaveClass(/dashboard-theme-admin/);
  });
});

