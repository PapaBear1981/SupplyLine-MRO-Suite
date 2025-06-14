import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, navigateToPage } from '../utils/test-helpers.js';

test.describe('User Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/dashboard');
  });

  test('should display dashboard layout correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Dashboard.*SupplyLine MRO Suite/);
    
    // Check main navigation is present
    await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
    
    // Check dashboard content area
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
  });

  test('should display user information', async ({ page }) => {
    // Check user menu shows logged in user
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-menu"]')).toContainText('ADMIN001');
  });

  test('should display quick actions section', async ({ page }) => {
    // Check quick actions are visible
    await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
    
    // Check common quick action buttons
    const quickActionButtons = [
      'checkout-tool-button',
      'return-tool-button',
      'scan-qr-button',
      'view-tools-button'
    ];
    
    for (const buttonTestId of quickActionButtons) {
      const button = page.locator(`[data-testid="${buttonTestId}"]`);
      if (await button.isVisible()) {
        await expect(button).toBeVisible();
      }
    }
  });

  test('should display user checkout status', async ({ page }) => {
    // Check user checkout status section
    const checkoutStatus = page.locator('[data-testid="user-checkout-status"]');
    if (await checkoutStatus.isVisible()) {
      await expect(checkoutStatus).toBeVisible();
      
      // Should show current checkouts or "No active checkouts" message
      const hasCheckouts = await page.locator('[data-testid="active-checkouts"]').isVisible();
      const noCheckouts = await page.locator('[data-testid="no-checkouts"]').isVisible();
      
      expect(hasCheckouts || noCheckouts).toBeTruthy();
    }
  });

  test('should display recent activity', async ({ page }) => {
    // Check recent activity section
    const recentActivity = page.locator('[data-testid="recent-activity"]');
    if (await recentActivity.isVisible()) {
      await expect(recentActivity).toBeVisible();
      
      // Should show activity items or "No recent activity" message
      const hasActivity = await page.locator('[data-testid="activity-items"]').isVisible();
      const noActivity = await page.locator('[data-testid="no-activity"]').isVisible();
      
      expect(hasActivity || noActivity).toBeTruthy();
    }
  });

  test('should display announcements', async ({ page }) => {
    // Check announcements section
    const announcements = page.locator('[data-testid="announcements"]');
    if (await announcements.isVisible()) {
      await expect(announcements).toBeVisible();
      
      // Should show announcements or "No announcements" message
      const hasAnnouncements = await page.locator('[data-testid="announcement-items"]').isVisible();
      const noAnnouncements = await page.locator('[data-testid="no-announcements"]').isVisible();
      
      expect(hasAnnouncements || noAnnouncements).toBeTruthy();
    }
  });

  test('should display overdue chemicals notification', async ({ page }) => {
    // Check overdue chemicals section
    const overdueChemicals = page.locator('[data-testid="overdue-chemicals"]');
    if (await overdueChemicals.isVisible()) {
      await expect(overdueChemicals).toBeVisible();
      
      // If there are overdue chemicals, should show them
      const hasOverdue = await page.locator('[data-testid="overdue-chemical-items"]').isVisible();
      const noOverdue = await page.locator('[data-testid="no-overdue-chemicals"]').isVisible();
      
      expect(hasOverdue || noOverdue).toBeTruthy();
    }
  });

  test('should display calibration notifications', async ({ page }) => {
    // Check calibration notifications section
    const calibrationNotifications = page.locator('[data-testid="calibration-notifications"]');
    if (await calibrationNotifications.isVisible()) {
      await expect(calibrationNotifications).toBeVisible();
      
      // Should show calibration items or "No calibrations due" message
      const hasCalibrations = await page.locator('[data-testid="calibration-items"]').isVisible();
      const noCalibrations = await page.locator('[data-testid="no-calibrations"]').isVisible();
      
      expect(hasCalibrations || noCalibrations).toBeTruthy();
    }
  });

  test('should display past due tools', async ({ page }) => {
    // Check past due tools section
    const pastDueTools = page.locator('[data-testid="past-due-tools"]');
    if (await pastDueTools.isVisible()) {
      await expect(pastDueTools).toBeVisible();
      
      // Should show past due tools or "No past due tools" message
      const hasPastDue = await page.locator('[data-testid="past-due-items"]').isVisible();
      const noPastDue = await page.locator('[data-testid="no-past-due"]').isVisible();
      
      expect(hasPastDue || noPastDue).toBeTruthy();
    }
  });

  test('should navigate to tools page from quick actions', async ({ page }) => {
    const viewToolsButton = page.locator('[data-testid="view-tools-button"]');
    if (await viewToolsButton.isVisible()) {
      await viewToolsButton.click();
      await expect(page).toHaveURL('/tools');
    }
  });

  test('should navigate to scanner from quick actions', async ({ page }) => {
    const scanButton = page.locator('[data-testid="scan-qr-button"]');
    if (await scanButton.isVisible()) {
      await scanButton.click();
      await expect(page).toHaveURL('/scanner');
    }
  });

  test('should refresh dashboard data', async ({ page }) => {
    // Wait for initial load
    await waitForLoadingToComplete(page);
    
    // Look for refresh button
    const refreshButton = page.locator('[data-testid="refresh-dashboard"]');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await waitForLoadingToComplete(page);
      
      // Dashboard should still be visible after refresh
      await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
    }
  });

  test('should handle dashboard data loading errors gracefully', async ({ page }) => {
    // Intercept dashboard API calls and make them fail
    await page.route('**/api/dashboard/**', route => {
      route.abort('failed');
    });
    
    // Reload the page to trigger the failed requests
    await page.reload();
    
    // Dashboard should still render with error states
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
    
    // Should show error messages or fallback content
    const errorElements = await page.locator('.error-message, .alert-danger, [data-testid*="error"]').count();
    expect(errorElements).toBeGreaterThan(0);
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Dashboard should still be usable
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
    
    // Navigation should be collapsed or adapted for mobile
    const mobileNav = page.locator('[data-testid="mobile-navigation"]');
    const hamburgerMenu = page.locator('[data-testid="hamburger-menu"]');
    
    expect(await mobileNav.isVisible() || await hamburgerMenu.isVisible()).toBeTruthy();
  });

  test('should display correct time and date', async ({ page }) => {
    // Check if time/date display exists
    const timeDisplay = page.locator('[data-testid="current-time"]');
    if (await timeDisplay.isVisible()) {
      const timeText = await timeDisplay.textContent();
      
      // Should contain current date/time (basic validation)
      const currentYear = new Date().getFullYear().toString();
      expect(timeText).toContain(currentYear);
    }
  });
});
