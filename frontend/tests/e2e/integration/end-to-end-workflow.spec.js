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
import { 
  generateTestData,
  measurePagePerformance,
  interceptNetworkRequests 
} from '../utils/advanced-helpers.js';
import { TEST_CONFIG, TEST_SELECTORS } from '../test-config.js';

test.describe('End-to-End Workflow Integration', () => {
  let testToolNumber;
  let testChemicalPartNumber;
  let networkRequests;

  test.beforeEach(async ({ page }) => {
    // Generate unique test data
    testToolNumber = generateTestData('toolNumber');
    testChemicalPartNumber = generateTestData('partNumber');
    
    // Set up network monitoring
    networkRequests = interceptNetworkRequests(page);
    
    await loginAsAdmin(page);
  });

  test('should complete full tool lifecycle workflow', async ({ page }) => {
    // Measure performance throughout the workflow
    const performanceMetrics = {};
    
    // Step 1: Navigate to tools page
    let startTime = Date.now();
    await navigateToPage(page, '/tools');
    performanceMetrics.toolsPageLoad = Date.now() - startTime;
    
    // Step 2: Create a new tool
    startTime = Date.now();
    await clickButton(page, 'add-tool-button');
    await expect(page).toHaveURL('/tools/new');
    
    // Fill tool form with comprehensive data
    await fillField(page, 'tool-number-input', testToolNumber);
    await fillField(page, 'serial-number-input', `SN${testToolNumber}`);
    await fillField(page, 'description-input', 'E2E Test Tool - Complete Workflow');
    await selectOption(page, 'category-select', 'Testing');
    await selectOption(page, 'condition-select', 'Good');
    await fillField(page, 'location-input', 'Test Storage Area');
    
    // Add calibration requirements if available
    const calibrationCheckbox = page.locator('[data-testid="requires-calibration-checkbox"]');
    if (await calibrationCheckbox.isVisible()) {
      await calibrationCheckbox.check();
      await fillField(page, 'calibration-frequency-input', '365');
    }
    
    // Submit tool creation
    await clickButton(page, 'save-tool-button');
    await waitForToast(page, 'Tool created successfully', 'success');
    performanceMetrics.toolCreation = Date.now() - startTime;
    
    // Step 3: Verify tool appears in list
    await navigateToPage(page, '/tools');
    await page.fill(TEST_SELECTORS.tools.searchInput, testToolNumber);
    await page.keyboard.press('Enter');
    await waitForLoadingToComplete(page);
    
    // Should find the created tool
    await expect(page.locator(`text=${testToolNumber}`)).toBeVisible();
    
    // Step 4: Checkout the tool
    startTime = Date.now();
    await navigateToPage(page, '/checkouts');
    
    await fillField(page, 'employee-number-input', 'USER001');
    await fillField(page, 'tool-number-input', testToolNumber);
    await fillField(page, 'checkout-notes-input', 'E2E test checkout');
    
    await clickButton(page, 'checkout-button');
    await waitForToast(page, 'Tool checked out successfully', 'success');
    performanceMetrics.toolCheckout = Date.now() - startTime;
    
    // Step 5: Verify checkout in active checkouts
    await navigateToPage(page, '/checkouts/all');
    await page.fill('[data-testid="search-checkouts-input"]', testToolNumber);
    await page.keyboard.press('Enter');
    await waitForLoadingToComplete(page);
    
    // Should find the checkout
    await expect(page.locator(`text=${testToolNumber}`)).toBeVisible();
    await expect(page.locator('text=USER001')).toBeVisible();
    
    // Step 6: Return the tool
    startTime = Date.now();
    const returnButton = page.locator('[data-testid="return-checkout-button"]').first();
    if (await returnButton.isVisible()) {
      await returnButton.click();
      
      // Fill return form if modal appears
      const returnModal = page.locator('[data-testid="return-modal"]');
      if (await returnModal.isVisible()) {
        await fillField(page, 'return-notes-input', 'E2E test return - tool in good condition');
        await clickButton(page, 'confirm-return-button');
      }
      
      await waitForToast(page, 'Tool returned successfully', 'success');
      performanceMetrics.toolReturn = Date.now() - startTime;
    }
    
    // Step 7: Update tool information
    await navigateToPage(page, '/tools');
    await page.fill(TEST_SELECTORS.tools.searchInput, testToolNumber);
    await page.keyboard.press('Enter');
    await waitForLoadingToComplete(page);
    
    const editButton = page.locator('[data-testid="edit-tool-button"]').first();
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Update description
      await fillField(page, 'description-input', 'E2E Test Tool - Updated Description');
      await clickButton(page, 'save-tool-button');
      await waitForToast(page, 'Tool updated successfully', 'success');
    }
    
    // Step 8: View tool history
    const viewButton = page.locator('[data-testid="view-tool-button"]').first();
    if (await viewButton.isVisible()) {
      await viewButton.click();
      
      // Should show tool details and history
      await expect(page.locator('[data-testid="tool-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="tool-history"]')).toBeVisible();
    }
    
    // Log performance metrics
    console.log('Tool Workflow Performance Metrics:', performanceMetrics);
    
    // Verify performance thresholds
    expect(performanceMetrics.toolsPageLoad).toBeLessThan(TEST_CONFIG.performance.pageLoad);
    expect(performanceMetrics.toolCreation).toBeLessThan(TEST_CONFIG.performance.formSubmission);
    expect(performanceMetrics.toolCheckout).toBeLessThan(TEST_CONFIG.performance.formSubmission);
    expect(performanceMetrics.toolReturn).toBeLessThan(TEST_CONFIG.performance.formSubmission);
  });

  test('should complete full chemical lifecycle workflow', async ({ page }) => {
    // Step 1: Create a new chemical
    await navigateToPage(page, '/chemicals');
    await clickButton(page, 'add-chemical-button');
    await expect(page).toHaveURL('/chemicals/new');
    
    // Fill chemical form
    await fillField(page, 'part-number-input', testChemicalPartNumber);
    await fillField(page, 'chemical-description-input', 'E2E Test Chemical - Complete Workflow');
    await selectOption(page, 'chemical-category-select', 'Solvent');
    await fillField(page, 'quantity-input', '100');
    await selectOption(page, 'unit-select', 'ml');
    await fillField(page, 'chemical-location-input', 'Chemical Storage Room A');
    await fillField(page, 'minimum-quantity-input', '10');
    
    // Set expiration date
    const expirationDate = new Date();
    expirationDate.setFullYear(expirationDate.getFullYear() + 1);
    await fillField(page, 'expiration-date-input', expirationDate.toISOString().split('T')[0]);
    
    await clickButton(page, 'save-chemical-button');
    await waitForToast(page, 'Chemical created successfully', 'success');
    
    // Step 2: Issue chemical
    await navigateToPage(page, '/chemicals');
    await page.fill('[data-testid="chemicals-search-input"]', testChemicalPartNumber);
    await page.keyboard.press('Enter');
    await waitForLoadingToComplete(page);
    
    const issueButton = page.locator('[data-testid="issue-chemical-button"]').first();
    if (await issueButton.isVisible()) {
      await issueButton.click();
      
      // Fill issue form
      const issueModal = page.locator('[data-testid="issue-chemical-modal"]');
      if (await issueModal.isVisible()) {
        await fillField(page, 'issue-quantity-input', '25');
        await fillField(page, 'issue-user-input', 'USER001');
        await fillField(page, 'issue-purpose-input', 'E2E testing purpose');
        await fillField(page, 'issue-notes-input', 'Test chemical issue for E2E workflow');
        
        await clickButton(page, 'confirm-issue-button');
        await waitForToast(page, 'Chemical issued successfully', 'success');
      }
    }
    
    // Step 3: Check chemical inventory levels
    await navigateToPage(page, '/chemicals');
    
    // Should show updated quantity
    await page.fill('[data-testid="chemicals-search-input"]', testChemicalPartNumber);
    await page.keyboard.press('Enter');
    await waitForLoadingToComplete(page);
    
    // Verify quantity was reduced
    await expect(page.locator('text=75')).toBeVisible(); // 100 - 25 = 75
    
    // Step 4: Return unused chemical
    const returnButton = page.locator('[data-testid="return-chemical-button"]').first();
    if (await returnButton.isVisible()) {
      await returnButton.click();
      
      const returnModal = page.locator('[data-testid="return-chemical-modal"]');
      if (await returnModal.isVisible()) {
        await fillField(page, 'return-quantity-input', '5');
        await fillField(page, 'return-notes-input', 'Unused portion returned');
        
        await clickButton(page, 'confirm-return-button');
        await waitForToast(page, 'Chemical returned successfully', 'success');
      }
    }
  });

  test('should complete cycle count workflow', async ({ page }) => {
    // Step 1: Create cycle count schedule
    await navigateToPage(page, '/cycle-counts');
    
    const createScheduleButton = page.locator('[data-testid="create-schedule-button"]');
    if (await createScheduleButton.isVisible()) {
      await createScheduleButton.click();
      
      // Fill schedule form
      await fillField(page, 'schedule-name-input', 'E2E Test Schedule');
      await selectOption(page, 'frequency-select', 'weekly');
      await selectOption(page, 'method-select', 'ABC');
      await fillField(page, 'schedule-description-input', 'E2E testing cycle count schedule');
      
      await clickButton(page, 'save-schedule-button');
      await waitForToast(page, 'Schedule created successfully', 'success');
    }
    
    // Step 2: Create batch from schedule
    const createBatchButton = page.locator('[data-testid="create-batch-button"]').first();
    if (await createBatchButton.isVisible()) {
      await createBatchButton.click();
      
      await fillField(page, 'batch-name-input', 'E2E Test Batch');
      await fillField(page, 'start-date-input', new Date().toISOString().split('T')[0]);
      
      const endDate = new Date();
      endDate.setDate(endDate.getDate() + 7);
      await fillField(page, 'end-date-input', endDate.toISOString().split('T')[0]);
      
      await clickButton(page, 'create-batch-button');
      await waitForToast(page, 'Batch created successfully', 'success');
    }
    
    // Step 3: Start counting process
    const startCountingButton = page.locator('[data-testid="start-counting-button"]').first();
    if (await startCountingButton.isVisible()) {
      await startCountingButton.click();
      
      // Should navigate to counting interface
      const countingInterface = page.locator('[data-testid="counting-interface"]');
      if (await countingInterface.isVisible()) {
        // Simulate counting some items
        const countInput = page.locator('[data-testid="count-input"]').first();
        if (await countInput.isVisible()) {
          await countInput.fill('5');
          await clickButton(page, 'submit-count-button');
        }
      }
    }
  });

  test('should handle error scenarios gracefully', async ({ page }) => {
    // Test network error handling
    await page.route('**/api/tools', route => {
      route.abort('failed');
    });
    
    await navigateToPage(page, '/tools');
    
    // Should show error message
    await expect(page.locator('.error-message, .alert-danger')).toBeVisible();
    
    // Test form validation errors
    await page.unroute('**/api/tools');
    await navigateToPage(page, '/tools/new');
    
    // Try to submit empty form
    await clickButton(page, 'save-tool-button');
    
    // Should show validation errors
    await expect(page.locator('.is-invalid, .error-message')).toHaveCount(2);
    
    // Test duplicate tool number
    await fillField(page, 'tool-number-input', 'DUPLICATE001');
    await fillField(page, 'serial-number-input', 'DUP001');
    await fillField(page, 'description-input', 'Duplicate test');
    
    // Mock duplicate error response
    await page.route('**/api/tools', route => {
      route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Tool number already exists' })
      });
    });
    
    await clickButton(page, 'save-tool-button');
    await waitForToast(page, 'Tool number already exists', 'error');
  });

  test.afterEach(async ({ page }) => {
    // Clean up test data
    try {
      // Delete test tool if it was created
      if (testToolNumber) {
        await page.request.delete(`/api/tools/by-number/${testToolNumber}`);
      }
      
      // Delete test chemical if it was created
      if (testChemicalPartNumber) {
        await page.request.delete(`/api/chemicals/by-part-number/${testChemicalPartNumber}`);
      }
    } catch (error) {
      console.warn('Cleanup failed:', error.message);
    }
    
    // Log network request summary
    const apiRequests = networkRequests.filter(req => req.url.includes('/api/'));
    console.log(`Total API requests: ${apiRequests.length}`);
    
    const slowRequests = apiRequests.filter(req => req.responseTime > 2000);
    if (slowRequests.length > 0) {
      console.warn('Slow API requests detected:', slowRequests);
    }
  });
});
