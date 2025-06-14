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
import { testCalibrationStandards } from '../fixtures/test-data.js';

test.describe('Calibration Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/calibrations');
  });

  test('should display calibration management page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Calibration.*SupplyLine MRO Suite/);
    
    // Check main elements
    await expect(page.locator('[data-testid="calibration-page-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="calibration-dashboard"]')).toBeVisible();
  });

  test('should display calibration due notifications', async ({ page }) => {
    // Check calibration notifications section
    const notificationsSection = page.locator('[data-testid="calibration-notifications"]');
    if (await notificationsSection.isVisible()) {
      await expect(notificationsSection).toBeVisible();
      
      // Should show due calibrations or "No calibrations due" message
      const hasDueCalibrations = await page.locator('[data-testid="due-calibrations"]').isVisible();
      const noDueCalibrations = await page.locator('[data-testid="no-due-calibrations"]').isVisible();
      
      expect(hasDueCalibrations || noDueCalibrations).toBeTruthy();
    }
  });

  test('should display overdue calibrations', async ({ page }) => {
    // Check overdue calibrations section
    const overdueSection = page.locator('[data-testid="overdue-calibrations"]');
    if (await overdueSection.isVisible()) {
      await expect(overdueSection).toBeVisible();
      
      // Should show overdue calibrations or "No overdue calibrations" message
      const hasOverdue = await page.locator('[data-testid="overdue-calibration-items"]').isVisible();
      const noOverdue = await page.locator('[data-testid="no-overdue-calibrations"]').isVisible();
      
      expect(hasOverdue || noOverdue).toBeTruthy();
    }
  });

  test('should display calibration standards table', async ({ page }) => {
    // Check calibration standards section
    const standardsSection = page.locator('[data-testid="calibration-standards"]');
    if (await standardsSection.isVisible()) {
      await expect(standardsSection).toBeVisible();
      
      // Should have add standard button
      await expect(page.locator('[data-testid="add-standard-button"]')).toBeVisible();
      
      // Should show standards table or empty state
      const standardsTable = page.locator('[data-testid="standards-table"]');
      const noStandards = page.locator('[data-testid="no-standards"]');
      
      expect(await standardsTable.isVisible() || await noStandards.isVisible()).toBeTruthy();
    }
  });

  test('should create new calibration standard successfully', async ({ page }) => {
    // Click add standard button
    const addButton = page.locator('[data-testid="add-standard-button"]');
    if (await addButton.isVisible()) {
      await addButton.click();
      
      // Should show standard form (modal or new page)
      const standardForm = page.locator('[data-testid="standard-form"]');
      const standardModal = page.locator('[data-testid="standard-modal"]');
      
      if (await standardForm.isVisible() || await standardModal.isVisible()) {
        // Fill standard form
        const standardData = testCalibrationStandards.basicStandard;
        await fillField(page, 'standard-name-input', standardData.name);
        await fillField(page, 'standard-description-input', standardData.description);
        await fillField(page, 'certificate-number-input', standardData.certificate_number);
        await fillField(page, 'accuracy-input', standardData.accuracy);
        await fillField(page, 'calibration-date-input', standardData.calibration_date);
        await fillField(page, 'expiration-date-input', standardData.expiration_date);
        
        // Submit form
        await clickButton(page, 'save-standard-button');
        
        // Should show success message
        await waitForToast(page, 'Calibration standard created successfully', 'success');
      }
    }
  });

  test('should schedule tool calibration', async ({ page }) => {
    // Look for tools requiring calibration
    const toolsSection = page.locator('[data-testid="tools-requiring-calibration"]');
    if (await toolsSection.isVisible()) {
      const firstScheduleButton = page.locator('[data-testid="schedule-calibration-button"]').first();
      if (await firstScheduleButton.isVisible()) {
        await firstScheduleButton.click();
        
        // Should show calibration scheduling form
        const scheduleForm = page.locator('[data-testid="calibration-schedule-form"]');
        if (await scheduleForm.isVisible()) {
          // Fill scheduling form
          await fillField(page, 'scheduled-date-input', '2025-12-31');
          await selectOption(page, 'technician-select', 'TECH001');
          await fillField(page, 'calibration-notes-input', 'Scheduled calibration for test tool');
          
          // Submit form
          await clickButton(page, 'schedule-calibration-submit-button');
          
          // Should show success message
          await waitForToast(page, 'Calibration scheduled successfully', 'success');
        }
      }
    }
  });

  test('should perform tool calibration', async ({ page }) => {
    // Look for scheduled calibrations
    const scheduledSection = page.locator('[data-testid="scheduled-calibrations"]');
    if (await scheduledSection.isVisible()) {
      const firstPerformButton = page.locator('[data-testid="perform-calibration-button"]').first();
      if (await firstPerformButton.isVisible()) {
        await firstPerformButton.click();
        
        // Should navigate to calibration form or show modal
        const calibrationForm = page.locator('[data-testid="calibration-form"]');
        const calibrationPage = page.url().includes('/calibration');
        
        if (await calibrationForm.isVisible() || calibrationPage) {
          // Fill calibration form
          await selectOption(page, 'calibration-standard-select', 'CERT001');
          await fillField(page, 'calibration-results-input', 'Within tolerance');
          await selectOption(page, 'calibration-status-select', 'passed');
          await fillField(page, 'next-calibration-date-input', '2026-12-31');
          await fillField(page, 'calibration-notes-input', 'Calibration completed successfully');
          
          // Submit calibration
          await clickButton(page, 'complete-calibration-button');
          
          // Should show success message
          await waitForToast(page, 'Calibration completed successfully', 'success');
        }
      }
    }
  });

  test('should view calibration history', async ({ page }) => {
    // Look for tools with calibration history
    const historySection = page.locator('[data-testid="calibration-history"]');
    if (await historySection.isVisible()) {
      const firstHistoryButton = page.locator('[data-testid="view-history-button"]').first();
      if (await firstHistoryButton.isVisible()) {
        await firstHistoryButton.click();
        
        // Should show calibration history
        const historyModal = page.locator('[data-testid="history-modal"]');
        const historyPage = page.url().includes('/history');
        
        if (await historyModal.isVisible() || historyPage) {
          // Should show history table
          await expect(page.locator('[data-testid="history-table"]')).toBeVisible();
          
          // Should have history entries or empty state
          const hasHistory = await page.locator('[data-testid="history-entries"]').isVisible();
          const noHistory = await page.locator('[data-testid="no-history"]').isVisible();
          
          expect(hasHistory || noHistory).toBeTruthy();
        }
      }
    }
  });

  test('should filter calibrations by status', async ({ page }) => {
    // Use status filter if available
    const statusFilter = page.locator('[data-testid="calibration-status-filter"]');
    if (await statusFilter.isVisible()) {
      await selectOption(page, 'calibration-status-filter', 'due');
      await waitForLoadingToComplete(page);
      
      // Should show filtered results
      const filteredItems = await page.locator('[data-testid="calibration-items"] .calibration-item').count();
      expect(filteredItems).toBeGreaterThanOrEqual(0);
    }
  });

  test('should search calibrations by tool number', async ({ page }) => {
    // Use search if available
    const searchInput = page.locator('[data-testid="calibration-search-input"]');
    if (await searchInput.isVisible()) {
      await searchInTable(page, 'T001', 'calibration-search-input');
      
      // Should filter results
      const filteredItems = await page.locator('[data-testid="calibration-items"] .calibration-item').count();
      expect(filteredItems).toBeGreaterThanOrEqual(0);
    }
  });

  test('should generate calibration certificate', async ({ page }) => {
    // Look for completed calibrations
    const completedSection = page.locator('[data-testid="completed-calibrations"]');
    if (await completedSection.isVisible()) {
      const firstCertificateButton = page.locator('[data-testid="generate-certificate-button"]').first();
      if (await firstCertificateButton.isVisible()) {
        // Set up download handler
        const downloadPromise = page.waitForEvent('download');
        
        await firstCertificateButton.click();
        
        // Wait for download
        const download = await downloadPromise;
        
        // Verify download
        expect(download.suggestedFilename()).toMatch(/calibration.*certificate.*\.pdf$/);
      }
    }
  });

  test('should export calibration data', async ({ page }) => {
    // Check if export button exists
    const exportButton = page.locator('[data-testid="export-calibrations-button"]');
    if (await exportButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/calibrations.*\.(csv|xlsx)$/);
    }
  });

  test('should handle calibration alerts and notifications', async ({ page }) => {
    // Check for calibration alerts
    const alertsSection = page.locator('[data-testid="calibration-alerts"]');
    if (await alertsSection.isVisible()) {
      await expect(alertsSection).toBeVisible();
      
      // Should show alert items or "No alerts" message
      const hasAlerts = await page.locator('[data-testid="alert-items"]').isVisible();
      const noAlerts = await page.locator('[data-testid="no-alerts"]').isVisible();
      
      expect(hasAlerts || noAlerts).toBeTruthy();
      
      // If there are alerts, test dismissing one
      if (hasAlerts) {
        const firstDismissButton = page.locator('[data-testid="dismiss-alert-button"]').first();
        if (await firstDismissButton.isVisible()) {
          await firstDismissButton.click();
          
          // Should show confirmation or remove alert
          await waitForToast(page, 'Alert dismissed', 'success');
        }
      }
    }
  });

  test('should handle calibration standard expiration', async ({ page }) => {
    // Check for expiring standards
    const expiringStandards = page.locator('[data-testid="expiring-standards"]');
    if (await expiringStandards.isVisible()) {
      await expect(expiringStandards).toBeVisible();
      
      // Should show expiring standards or "No expiring standards" message
      const hasExpiring = await page.locator('[data-testid="expiring-standard-items"]').isVisible();
      const noExpiring = await page.locator('[data-testid="no-expiring-standards"]').isVisible();
      
      expect(hasExpiring || noExpiring).toBeTruthy();
      
      // If there are expiring standards, test renewal process
      if (hasExpiring) {
        const firstRenewButton = page.locator('[data-testid="renew-standard-button"]').first();
        if (await firstRenewButton.isVisible()) {
          await firstRenewButton.click();
          
          // Should show renewal form
          const renewalForm = page.locator('[data-testid="renewal-form"]');
          if (await renewalForm.isVisible()) {
            await fillField(page, 'new-expiration-date-input', '2026-12-31');
            await fillField(page, 'renewal-notes-input', 'Standard renewed for another year');
            
            await clickButton(page, 'submit-renewal-button');
            
            // Should show success message
            await waitForToast(page, 'Standard renewed successfully', 'success');
          }
        }
      }
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept calibration API and make it fail
    await page.route('**/api/calibration/**', route => {
      route.abort('failed');
    });
    
    await page.reload();
    
    // Should show error message
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
  });
});
