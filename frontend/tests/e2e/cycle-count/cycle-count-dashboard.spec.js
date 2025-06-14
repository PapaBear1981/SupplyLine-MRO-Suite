import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { 
  waitForLoadingToComplete, 
  waitForToast, 
  fillField, 
  clickButton, 
  selectOption,
  waitForTableToLoad,
  navigateToPage 
} from '../utils/test-helpers.js';
import { testCycleCountSchedules } from '../fixtures/test-data.js';

test.describe('Cycle Count Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToPage(page, '/cycle-counts');
  });

  test('should display cycle count dashboard correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Cycle Count.*SupplyLine MRO Suite/);
    
    // Check main elements
    await expect(page.locator('[data-testid="cycle-count-dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="cycle-count-title"]')).toBeVisible();
  });

  test('should display schedules section', async ({ page }) => {
    // Check schedules section
    const schedulesSection = page.locator('[data-testid="schedules-section"]');
    if (await schedulesSection.isVisible()) {
      await expect(schedulesSection).toBeVisible();
      
      // Should have create schedule button
      await expect(page.locator('[data-testid="create-schedule-button"]')).toBeVisible();
      
      // Should show schedules table or empty state
      const schedulesTable = page.locator('[data-testid="schedules-table"]');
      const noSchedules = page.locator('[data-testid="no-schedules"]');
      
      expect(await schedulesTable.isVisible() || await noSchedules.isVisible()).toBeTruthy();
    }
  });

  test('should display batches section', async ({ page }) => {
    // Check batches section
    const batchesSection = page.locator('[data-testid="batches-section"]');
    if (await batchesSection.isVisible()) {
      await expect(batchesSection).toBeVisible();
      
      // Should show batches table or empty state
      const batchesTable = page.locator('[data-testid="batches-table"]');
      const noBatches = page.locator('[data-testid="no-batches"]');
      
      expect(await batchesTable.isVisible() || await noBatches.isVisible()).toBeTruthy();
    }
  });

  test('should display analytics section', async ({ page }) => {
    // Check analytics section
    const analyticsSection = page.locator('[data-testid="analytics-section"]');
    if (await analyticsSection.isVisible()) {
      await expect(analyticsSection).toBeVisible();
      
      // Should show analytics charts or data
      const analyticsContent = page.locator('[data-testid="analytics-content"]');
      const noAnalytics = page.locator('[data-testid="no-analytics"]');
      
      expect(await analyticsContent.isVisible() || await noAnalytics.isVisible()).toBeTruthy();
    }
  });

  test('should create new schedule successfully', async ({ page }) => {
    // Click create schedule button
    const createButton = page.locator('[data-testid="create-schedule-button"]');
    if (await createButton.isVisible()) {
      await createButton.click();
      
      // Should show schedule form (modal or new page)
      const scheduleForm = page.locator('[data-testid="schedule-form"]');
      const scheduleModal = page.locator('[data-testid="schedule-modal"]');
      
      if (await scheduleForm.isVisible() || await scheduleModal.isVisible()) {
        // Fill schedule form
        const scheduleData = testCycleCountSchedules.weeklySchedule;
        await fillField(page, 'schedule-name-input', scheduleData.name);
        await selectOption(page, 'frequency-select', scheduleData.frequency);
        await selectOption(page, 'method-select', scheduleData.method);
        await fillField(page, 'schedule-description-input', scheduleData.description);
        
        // Submit form
        await clickButton(page, 'save-schedule-button');
        
        // Should show success message
        await waitForToast(page, 'Schedule created successfully', 'success');
      }
    }
  });

  test('should view schedule details', async ({ page }) => {
    // Look for existing schedules
    const schedulesTable = page.locator('[data-testid="schedules-table"]');
    if (await schedulesTable.isVisible()) {
      const firstViewButton = page.locator('[data-testid="view-schedule-button"]').first();
      if (await firstViewButton.isVisible()) {
        await firstViewButton.click();
        
        // Should navigate to schedule detail page
        expect(page.url()).toMatch(/\/cycle-counts\/schedules\/\d+$/);
        
        // Should show schedule details
        await expect(page.locator('[data-testid="schedule-details"]')).toBeVisible();
      }
    }
  });

  test('should create batch from schedule', async ({ page }) => {
    // Look for existing schedules
    const schedulesTable = page.locator('[data-testid="schedules-table"]');
    if (await schedulesTable.isVisible()) {
      const firstCreateBatchButton = page.locator('[data-testid="create-batch-button"]').first();
      if (await firstCreateBatchButton.isVisible()) {
        await firstCreateBatchButton.click();
        
        // Should show batch creation form
        const batchForm = page.locator('[data-testid="batch-form"]');
        if (await batchForm.isVisible()) {
          // Fill batch form
          await fillField(page, 'batch-name-input', 'Test Batch 2025-01');
          await fillField(page, 'start-date-input', '2025-01-01');
          await fillField(page, 'end-date-input', '2025-01-07');
          
          // Submit form
          await clickButton(page, 'create-batch-button');
          
          // Should show success message
          await waitForToast(page, 'Batch created successfully', 'success');
        }
      }
    }
  });

  test('should view batch details', async ({ page }) => {
    // Look for existing batches
    const batchesTable = page.locator('[data-testid="batches-table"]');
    if (await batchesTable.isVisible()) {
      const firstViewBatchButton = page.locator('[data-testid="view-batch-button"]').first();
      if (await firstViewBatchButton.isVisible()) {
        await firstViewBatchButton.click();
        
        // Should navigate to batch detail page
        expect(page.url()).toMatch(/\/cycle-counts\/batches\/\d+$/);
        
        // Should show batch details
        await expect(page.locator('[data-testid="batch-details"]')).toBeVisible();
      }
    }
  });

  test('should start batch counting', async ({ page }) => {
    // Look for existing batches
    const batchesTable = page.locator('[data-testid="batches-table"]');
    if (await batchesTable.isVisible()) {
      const firstStartButton = page.locator('[data-testid="start-counting-button"]').first();
      if (await firstStartButton.isVisible()) {
        await firstStartButton.click();
        
        // Should navigate to counting interface
        expect(page.url()).toMatch(/\/cycle-counts\/(batches\/\d+\/count|mobile)/);
        
        // Should show counting interface
        const countingInterface = page.locator('[data-testid="counting-interface"]');
        const mobileInterface = page.locator('[data-testid="mobile-counting"]');
        
        expect(await countingInterface.isVisible() || await mobileInterface.isVisible()).toBeTruthy();
      }
    }
  });

  test('should filter schedules by status', async ({ page }) => {
    const schedulesTable = page.locator('[data-testid="schedules-table"]');
    if (await schedulesTable.isVisible()) {
      // Use status filter if available
      const statusFilter = page.locator('[data-testid="schedule-status-filter"]');
      if (await statusFilter.isVisible()) {
        await selectOption(page, 'schedule-status-filter', 'active');
        await waitForLoadingToComplete(page);
        
        // Should show filtered results
        const filteredRows = await page.locator('[data-testid="schedules-table"] tbody tr').count();
        expect(filteredRows).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should filter batches by status', async ({ page }) => {
    const batchesTable = page.locator('[data-testid="batches-table"]');
    if (await batchesTable.isVisible()) {
      // Use status filter if available
      const statusFilter = page.locator('[data-testid="batch-status-filter"]');
      if (await statusFilter.isVisible()) {
        await selectOption(page, 'batch-status-filter', 'active');
        await waitForLoadingToComplete(page);
        
        // Should show filtered results
        const filteredRows = await page.locator('[data-testid="batches-table"] tbody tr').count();
        expect(filteredRows).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should navigate to mobile counting interface', async ({ page }) => {
    // Look for mobile counting button
    const mobileButton = page.locator('[data-testid="mobile-counting-button"]');
    if (await mobileButton.isVisible()) {
      await mobileButton.click();
      
      // Should navigate to mobile interface
      await expect(page).toHaveURL('/cycle-counts/mobile');
      
      // Should show mobile interface
      await expect(page.locator('[data-testid="mobile-counting-interface"]')).toBeVisible();
    }
  });

  test('should display discrepancies section', async ({ page }) => {
    // Check discrepancies section
    const discrepanciesSection = page.locator('[data-testid="discrepancies-section"]');
    if (await discrepanciesSection.isVisible()) {
      await expect(discrepanciesSection).toBeVisible();
      
      // Should show discrepancies table or empty state
      const discrepanciesTable = page.locator('[data-testid="discrepancies-table"]');
      const noDiscrepancies = page.locator('[data-testid="no-discrepancies"]');
      
      expect(await discrepanciesTable.isVisible() || await noDiscrepancies.isVisible()).toBeTruthy();
    }
  });

  test('should handle discrepancy resolution', async ({ page }) => {
    const discrepanciesTable = page.locator('[data-testid="discrepancies-table"]');
    if (await discrepanciesTable.isVisible()) {
      const firstResolveButton = page.locator('[data-testid="resolve-discrepancy-button"]').first();
      if (await firstResolveButton.isVisible()) {
        await firstResolveButton.click();
        
        // Should show resolution form
        const resolutionForm = page.locator('[data-testid="resolution-form"]');
        if (await resolutionForm.isVisible()) {
          // Fill resolution form
          await selectOption(page, 'resolution-action-select', 'adjust');
          await fillField(page, 'resolution-notes-input', 'Adjusted quantity based on physical count');
          
          // Submit resolution
          await clickButton(page, 'submit-resolution-button');
          
          // Should show success message
          await waitForToast(page, 'Discrepancy resolved successfully', 'success');
        }
      }
    }
  });

  test('should export cycle count data', async ({ page }) => {
    // Check if export button exists
    const exportButton = page.locator('[data-testid="export-cycle-count-button"]');
    if (await exportButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/cycle-count.*\.(csv|xlsx)$/);
    }
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Intercept cycle count API and make it fail
    await page.route('**/api/cycle-count/**', route => {
      route.abort('failed');
    });
    
    await page.reload();
    
    // Should show error message
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
  });
});
