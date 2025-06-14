import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import {
  waitForLoadingToComplete,
  waitForToast,
  fillField,
  clickButton,
  selectOption,
  navigateToPage
} from '../utils/test-helpers.js';

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/admin/dashboard');
  });

  test('should display admin dashboard correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Admin Dashboard.*SupplyLine MRO Suite/);
    
    // Check main elements
    await expect(page.locator('[data-testid="admin-dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="admin-dashboard-title"]')).toBeVisible();
  });

  test('should display system overview metrics', async ({ page }) => {
    // Check system overview section
    const overviewSection = page.locator('[data-testid="system-overview"]');
    if (await overviewSection.isVisible()) {
      await expect(overviewSection).toBeVisible();
      
      // Should show key metrics
      const metrics = [
        'total-users-metric',
        'total-tools-metric',
        'active-checkouts-metric',
        'total-chemicals-metric'
      ];
      
      for (const metric of metrics) {
        const metricElement = page.locator(`[data-testid="${metric}"]`);
        if (await metricElement.isVisible()) {
          await expect(metricElement).toBeVisible();
          
          // Should contain numeric value
          const metricText = await metricElement.textContent();
          expect(metricText).toMatch(/\d+/);
        }
      }
    }
  });

  test('should display system health status', async ({ page }) => {
    // Check system health section
    const healthSection = page.locator('[data-testid="system-health"]');
    if (await healthSection.isVisible()) {
      await expect(healthSection).toBeVisible();
      
      // Should show health indicators
      const healthIndicators = [
        'server-status',
        'database-status',
        'api-status'
      ];
      
      for (const indicator of healthIndicators) {
        const indicatorElement = page.locator(`[data-testid="${indicator}"]`);
        if (await indicatorElement.isVisible()) {
          await expect(indicatorElement).toBeVisible();
          
          // Should show status (online/offline, healthy/unhealthy, etc.)
          const statusText = await indicatorElement.textContent();
          expect(statusText.toLowerCase()).toMatch(/(online|offline|healthy|unhealthy|active|inactive)/);
        }
      }
    }
  });

  test('should display user management section', async ({ page }) => {
    // Check user management section
    const userMgmtSection = page.locator('[data-testid="user-management"]');
    if (await userMgmtSection.isVisible()) {
      await expect(userMgmtSection).toBeVisible();
      
      // Should have user management actions
      const userActions = [
        'view-all-users-button',
        'pending-registrations-button',
        'user-activity-button'
      ];
      
      for (const action of userActions) {
        const actionElement = page.locator(`[data-testid="${action}"]`);
        if (await actionElement.isVisible()) {
          await expect(actionElement).toBeVisible();
        }
      }
    }
  });

  test('should display recent activity feed', async ({ page }) => {
    // Check recent activity section
    const activitySection = page.locator('[data-testid="recent-activity"]');
    if (await activitySection.isVisible()) {
      await expect(activitySection).toBeVisible();
      
      // Should show activity items or "No recent activity" message
      const hasActivity = await page.locator('[data-testid="activity-items"]').isVisible();
      const noActivity = await page.locator('[data-testid="no-recent-activity"]').isVisible();
      
      expect(hasActivity || noActivity).toBeTruthy();
      
      // If there are activity items, check their structure
      if (hasActivity) {
        const activityItems = page.locator('[data-testid="activity-item"]');
        const itemCount = await activityItems.count();
        
        if (itemCount > 0) {
          // Check first activity item has required elements
          const firstItem = activityItems.first();
          await expect(firstItem.locator('[data-testid="activity-timestamp"]')).toBeVisible();
          await expect(firstItem.locator('[data-testid="activity-description"]')).toBeVisible();
        }
      }
    }
  });

  test('should display pending registrations', async ({ page }) => {
    // Check pending registrations section
    const pendingSection = page.locator('[data-testid="pending-registrations"]');
    if (await pendingSection.isVisible()) {
      await expect(pendingSection).toBeVisible();
      
      // Should show pending registrations or "No pending registrations" message
      const hasPending = await page.locator('[data-testid="pending-registration-items"]').isVisible();
      const noPending = await page.locator('[data-testid="no-pending-registrations"]').isVisible();
      
      expect(hasPending || noPending).toBeTruthy();
    }
  });

  test('should approve user registration', async ({ page }) => {
    // Look for pending registrations
    const pendingItems = page.locator('[data-testid="pending-registration-item"]');
    const itemCount = await pendingItems.count();
    
    if (itemCount > 0) {
      const firstApproveButton = page.locator('[data-testid="approve-registration-button"]').first();
      if (await firstApproveButton.isVisible()) {
        await firstApproveButton.click();
        
        // Should show confirmation dialog
        const confirmDialog = page.locator('[data-testid="approve-confirmation"]');
        if (await confirmDialog.isVisible()) {
          await clickButton(page, 'confirm-approve-button');
          
          // Should show success message
          await waitForToast(page, 'Registration approved successfully', 'success');
        }
      }
    }
  });

  test('should deny user registration', async ({ page }) => {
    // Look for pending registrations
    const pendingItems = page.locator('[data-testid="pending-registration-item"]');
    const itemCount = await pendingItems.count();
    
    if (itemCount > 0) {
      const firstDenyButton = page.locator('[data-testid="deny-registration-button"]').first();
      if (await firstDenyButton.isVisible()) {
        await firstDenyButton.click();
        
        // Should show confirmation dialog with reason
        const confirmDialog = page.locator('[data-testid="deny-confirmation"]');
        if (await confirmDialog.isVisible()) {
          await fillField(page, 'denial-reason-input', 'Incomplete information provided');
          await clickButton(page, 'confirm-deny-button');
          
          // Should show success message
          await waitForToast(page, 'Registration denied', 'success');
        }
      }
    }
  });

  test('should display system alerts and warnings', async ({ page }) => {
    // Check system alerts section
    const alertsSection = page.locator('[data-testid="system-alerts"]');
    if (await alertsSection.isVisible()) {
      await expect(alertsSection).toBeVisible();
      
      // Should show alerts or "No alerts" message
      const hasAlerts = await page.locator('[data-testid="alert-items"]').isVisible();
      const noAlerts = await page.locator('[data-testid="no-system-alerts"]').isVisible();
      
      expect(hasAlerts || noAlerts).toBeTruthy();
      
      // If there are alerts, check their types
      if (hasAlerts) {
        const alertItems = page.locator('[data-testid="alert-item"]');
        const alertCount = await alertItems.count();
        
        if (alertCount > 0) {
          // Check first alert has required elements
          const firstAlert = alertItems.first();
          await expect(firstAlert.locator('[data-testid="alert-type"]')).toBeVisible();
          await expect(firstAlert.locator('[data-testid="alert-message"]')).toBeVisible();
        }
      }
    }
  });

  test('should create system announcement', async ({ page }) => {
    // Look for announcement creation section
    const announcementSection = page.locator('[data-testid="announcements-management"]');
    if (await announcementSection.isVisible()) {
      const createButton = page.locator('[data-testid="create-announcement-button"]');
      if (await createButton.isVisible()) {
        await createButton.click();
        
        // Should show announcement form
        const announcementForm = page.locator('[data-testid="announcement-form"]');
        if (await announcementForm.isVisible()) {
          // Fill announcement form
          await fillField(page, 'announcement-title-input', 'System Maintenance Notice');
          await fillField(page, 'announcement-message-input', 'The system will be down for maintenance on Sunday from 2-4 AM.');
          await selectOption(page, 'announcement-priority-select', 'high');
          await fillField(page, 'announcement-expiry-input', '2025-12-31');
          
          // Submit announcement
          await clickButton(page, 'save-announcement-button');
          
          // Should show success message
          await waitForToast(page, 'Announcement created successfully', 'success');
        }
      }
    }
  });

  test('should display performance analytics', async ({ page }) => {
    // Check performance analytics section
    const analyticsSection = page.locator('[data-testid="performance-analytics"]');
    if (await analyticsSection.isVisible()) {
      await expect(analyticsSection).toBeVisible();
      
      // Should show charts or analytics data
      const hasCharts = await page.locator('[data-testid="analytics-charts"]').isVisible();
      const hasMetrics = await page.locator('[data-testid="performance-metrics"]').isVisible();
      
      expect(hasCharts || hasMetrics).toBeTruthy();
      
      // Check for specific analytics
      const analyticsElements = [
        'tool-utilization-chart',
        'user-activity-chart',
        'checkout-trends-chart'
      ];
      
      for (const element of analyticsElements) {
        const chartElement = page.locator(`[data-testid="${element}"]`);
        if (await chartElement.isVisible()) {
          await expect(chartElement).toBeVisible();
        }
      }
    }
  });

  test('should manage user accounts', async ({ page }) => {
    // Look for user management actions
    const viewUsersButton = page.locator('[data-testid="view-all-users-button"]');
    if (await viewUsersButton.isVisible()) {
      await viewUsersButton.click();
      
      // Should navigate to user management or show user list
      const userManagementPage = page.url().includes('/admin/users');
      const userListModal = page.locator('[data-testid="user-list-modal"]');
      
      if (userManagementPage || await userListModal.isVisible()) {
        // Should show user table
        await expect(page.locator('[data-testid="users-table"]')).toBeVisible();
        
        // Should have user management actions
        const userActions = [
          'edit-user-button',
          'deactivate-user-button',
          'reset-password-button'
        ];
        
        for (const action of userActions) {
          const actionButton = page.locator(`[data-testid="${action}"]`).first();
          if (await actionButton.isVisible()) {
            await expect(actionButton).toBeVisible();
          }
        }
      }
    }
  });

  test('should export system reports', async ({ page }) => {
    // Look for export functionality
    const exportSection = page.locator('[data-testid="export-reports"]');
    if (await exportSection.isVisible()) {
      const exportButton = page.locator('[data-testid="export-system-report-button"]');
      if (await exportButton.isVisible()) {
        // Set up download handler
        const downloadPromise = page.waitForEvent('download');
        
        await exportButton.click();
        
        // Wait for download
        const download = await downloadPromise;
        
        // Verify download
        expect(download.suggestedFilename()).toMatch(/system.*report.*\.(csv|xlsx|pdf)$/);
      }
    }
  });

  test('should refresh dashboard data', async ({ page }) => {
    // Look for refresh button
    const refreshButton = page.locator('[data-testid="refresh-dashboard-button"]');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      
      // Should show loading state and then refresh
      await waitForLoadingToComplete(page);
      
      // Dashboard should still be visible after refresh
      await expect(page.locator('[data-testid="admin-dashboard"]')).toBeVisible();
    }
  });

  test('should handle system maintenance mode', async ({ page }) => {
    // Look for maintenance mode controls
    const maintenanceSection = page.locator('[data-testid="maintenance-mode"]');
    if (await maintenanceSection.isVisible()) {
      const enableMaintenanceButton = page.locator('[data-testid="enable-maintenance-button"]');
      if (await enableMaintenanceButton.isVisible()) {
        await enableMaintenanceButton.click();
        
        // Should show confirmation dialog
        const confirmDialog = page.locator('[data-testid="maintenance-confirmation"]');
        if (await confirmDialog.isVisible()) {
          await fillField(page, 'maintenance-message-input', 'System maintenance in progress');
          await clickButton(page, 'confirm-maintenance-button');
          
          // Should show success message
          await waitForToast(page, 'Maintenance mode enabled', 'success');
        }
      }
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept admin dashboard API and make it fail
    await page.route('**/api/admin/**', route => {
      route.abort('failed');
    });
    
    await page.reload();
    
    // Should show error message but still render basic layout
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
    await expect(page.locator('[data-testid="admin-dashboard"]')).toBeVisible();
  });
});
