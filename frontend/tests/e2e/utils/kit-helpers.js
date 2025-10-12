/**
 * Kit E2E Test Helper Functions
 * 
 * Reusable utilities for kit-related E2E tests
 */

/**
 * Navigate to the first available kit detail page
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<boolean>} True if navigation successful, false otherwise
 */
export async function navigateToFirstKit(page) {
  await page.goto('/kits');
  await page.waitForTimeout(1000);
  
  const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
  const count = await kitCards.count();
  
  if (count > 0) {
    await kitCards.first().click();
    await page.waitForTimeout(500);
    return true;
  }
  
  return false;
}

/**
 * Create a new kit using the wizard
 * @param {import('@playwright/test').Page} page 
 * @param {Object} kitData - Kit data
 * @param {string} kitData.aircraftType - Aircraft type name
 * @param {string} kitData.name - Kit name
 * @param {string} kitData.description - Kit description (optional)
 * @returns {Promise<boolean>} True if creation successful
 */
export async function createKit(page, kitData) {
  await page.goto('/kits/new');
  await page.waitForTimeout(1000);
  
  // Step 1: Select aircraft type
  const aircraftCards = page.locator('.card').filter({ 
    hasText: kitData.aircraftType || /Q400|B737|Aircraft/ 
  });
  const count = await aircraftCards.count();
  
  if (count === 0) {
    return false;
  }
  
  await aircraftCards.first().click();
  await page.click('button:has-text("Next")');
  await page.waitForTimeout(500);
  
  // Step 2: Enter kit details
  await page.fill('input[placeholder*="Kit"], input[type="text"]', kitData.name);
  
  if (kitData.description) {
    await page.fill('textarea', kitData.description);
  }
  
  await page.click('button:has-text("Next")');
  await page.waitForTimeout(1000);
  
  // Step 3: Box configuration (use defaults)
  await page.click('button:has-text("Next")');
  await page.waitForTimeout(500);
  
  // Step 4: Review and create
  await page.click('button:has-text("Create"), button:has-text("Finish")');
  await page.waitForTimeout(1000);
  
  // Check if we're on the kit detail page
  const url = page.url();
  return url.includes('/kits/') && !url.includes('/new');
}

/**
 * Navigate to a specific tab on the kit detail page
 * @param {import('@playwright/test').Page} page 
 * @param {string} tabName - Tab name (Overview, Items, Issuances, Transfers, Reorders)
 */
export async function navigateToKitTab(page, tabName) {
  await page.click(`text=${tabName}`);
  await page.waitForTimeout(500);
}

/**
 * Search for kits by term
 * @param {import('@playwright/test').Page} page 
 * @param {string} searchTerm - Search term
 */
export async function searchKits(page, searchTerm) {
  const searchInput = page.locator('[placeholder*="Search kits"]');
  await searchInput.fill(searchTerm);
  await page.waitForTimeout(500); // Wait for debounce
}

/**
 * Filter kits by aircraft type
 * @param {import('@playwright/test').Page} page 
 * @param {number} aircraftTypeIndex - Index of aircraft type in dropdown (0 = all)
 */
export async function filterKitsByAircraftType(page, aircraftTypeIndex) {
  const aircraftSelect = page.locator('select').first();
  await aircraftSelect.selectOption({ index: aircraftTypeIndex });
  await page.waitForTimeout(500);
}

/**
 * Get count of displayed kit cards
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<number>} Number of kit cards
 */
export async function getKitCardCount(page) {
  const kitCards = page.locator('.card').filter({ hasText: /Kit|Q400|B737/ });
  return await kitCards.count();
}

/**
 * Issue an item from a kit
 * @param {import('@playwright/test').Page} page 
 * @param {Object} issuanceData - Issuance data
 * @param {number} issuanceData.quantity - Quantity to issue
 * @param {string} issuanceData.purpose - Purpose of issuance
 * @param {string} issuanceData.workOrder - Work order number (optional)
 * @returns {Promise<boolean>} True if issuance successful
 */
export async function issueKitItem(page, issuanceData) {
  // Assume we're already on the Items tab
  const issueButtons = page.locator('button:has-text("Issue")');
  const buttonCount = await issueButtons.count();
  
  if (buttonCount === 0) {
    return false;
  }
  
  await issueButtons.first().click();
  await page.waitForTimeout(500);
  
  // Fill issuance form
  await page.fill('input[type="number"]', issuanceData.quantity.toString());
  await page.fill('input[placeholder*="Purpose"], textarea[placeholder*="Purpose"]', issuanceData.purpose);
  
  if (issuanceData.workOrder) {
    await page.fill('input[placeholder*="Work Order"]', issuanceData.workOrder);
  }
  
  // Submit form
  await page.click('button:has-text("Submit"), button:has-text("Issue")');
  await page.waitForTimeout(1000);
  
  // Check for success message
  const successMessage = page.locator('.alert-success, .toast, text=Success');
  return await successMessage.count() > 0;
}

/**
 * Create a reorder request
 * @param {import('@playwright/test').Page} page 
 * @param {Object} reorderData - Reorder data
 * @param {string} reorderData.partNumber - Part number
 * @param {string} reorderData.description - Description
 * @param {number} reorderData.quantity - Quantity
 * @param {string} reorderData.priority - Priority (urgent, high, medium, low)
 * @returns {Promise<boolean>} True if request successful
 */
export async function createReorderRequest(page, reorderData) {
  // Assume we're already on the Reorders tab
  const reorderButton = page.locator('button:has-text("Request"), button:has-text("Reorder"), button:has-text("Create")');
  const buttonExists = await reorderButton.count();
  
  if (buttonExists === 0) {
    return false;
  }
  
  await reorderButton.first().click();
  await page.waitForTimeout(500);
  
  // Fill reorder form
  await page.fill('input[placeholder*="Part Number"]', reorderData.partNumber);
  await page.fill('input[placeholder*="Description"], textarea[placeholder*="Description"]', reorderData.description);
  await page.fill('input[type="number"]', reorderData.quantity.toString());
  
  if (reorderData.priority) {
    const prioritySelect = page.locator('select').filter({ hasText: /Priority/ });
    const selectExists = await prioritySelect.count();
    if (selectExists > 0) {
      await prioritySelect.selectOption(reorderData.priority);
    }
  }
  
  // Submit form
  await page.click('button:has-text("Submit"), button:has-text("Request")');
  await page.waitForTimeout(1000);
  
  // Check for success message
  const successMessage = page.locator('.alert-success, .toast, text=Success');
  return await successMessage.count() > 0;
}

/**
 * Transfer a kit to a new location
 * @param {import('@playwright/test').Page} page 
 * @param {Object} transferData - Transfer data
 * @param {string} transferData.destination - Destination location
 * @param {string} transferData.notes - Transfer notes (optional)
 * @returns {Promise<boolean>} True if transfer successful
 */
export async function transferKit(page, transferData) {
  const transferButton = page.locator('button:has-text("Transfer")');
  const transferExists = await transferButton.count();
  
  if (transferExists === 0) {
    return false;
  }
  
  await transferButton.first().click();
  await page.waitForTimeout(500);
  
  // Fill transfer form
  await page.fill('input[placeholder*="Destination"], select', transferData.destination);
  
  if (transferData.notes) {
    await page.fill('textarea[placeholder*="Notes"]', transferData.notes);
  }
  
  // Submit form
  await page.click('button:has-text("Submit"), button:has-text("Transfer")');
  await page.waitForTimeout(1000);
  
  // Check for success message
  const successMessage = page.locator('.alert-success, .toast, text=Success');
  return await successMessage.count() > 0;
}

/**
 * Wait for kit data to load
 * @param {import('@playwright/test').Page} page 
 * @param {number} timeout - Timeout in milliseconds (default: 3000)
 */
export async function waitForKitsToLoad(page, timeout = 3000) {
  await page.waitForTimeout(1000);
  
  // Wait for either kit cards or "no kits" message
  await page.waitForSelector('.card, text=No kits found', { timeout });
}

/**
 * Check if a kit exists by name
 * @param {import('@playwright/test').Page} page 
 * @param {string} kitName - Kit name to search for
 * @returns {Promise<boolean>} True if kit exists
 */
export async function kitExists(page, kitName) {
  await page.goto('/kits');
  await waitForKitsToLoad(page);
  
  const kitCard = page.locator('.card').filter({ hasText: kitName });
  return await kitCard.count() > 0;
}

/**
 * Get kit alert count
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<number>} Number of alerts
 */
export async function getKitAlertCount(page) {
  const alerts = page.locator('.alert, .badge').filter({ hasText: /Warning|Critical|Info|Low/ });
  return await alerts.count();
}

/**
 * Navigate to kit reports page
 * @param {import('@playwright/test').Page} page 
 * @param {string} reportType - Report type (inventory, issuance, transfer, reorder, utilization)
 */
export async function navigateToKitReport(page, reportType) {
  await page.goto('/kits/reports');
  await page.waitForTimeout(1000);
  
  if (reportType) {
    const reportTab = page.locator(`.nav-link:has-text("${reportType}")`);
    const tabExists = await reportTab.count();
    if (tabExists > 0) {
      await reportTab.click();
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Apply report filters
 * @param {import('@playwright/test').Page} page 
 * @param {Object} filters - Filter options
 * @param {string} filters.aircraftType - Aircraft type
 * @param {string} filters.kit - Kit name
 * @param {string} filters.startDate - Start date
 * @param {string} filters.endDate - End date
 */
export async function applyReportFilters(page, filters) {
  if (filters.aircraftType) {
    const aircraftSelect = page.locator('select').filter({ hasText: /Aircraft/ });
    const selectExists = await aircraftSelect.count();
    if (selectExists > 0) {
      await aircraftSelect.first().selectOption({ label: filters.aircraftType });
    }
  }
  
  if (filters.kit) {
    const kitSelect = page.locator('select').filter({ hasText: /Kit/ });
    const selectExists = await kitSelect.count();
    if (selectExists > 0) {
      await kitSelect.first().selectOption({ label: filters.kit });
    }
  }
  
  if (filters.startDate) {
    const startDateInput = page.locator('input[type="date"]').first();
    await startDateInput.fill(filters.startDate);
  }
  
  if (filters.endDate) {
    const endDateInput = page.locator('input[type="date"]').last();
    await endDateInput.fill(filters.endDate);
  }
  
  await page.waitForTimeout(500);
}

