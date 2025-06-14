/**
 * General test helper functions for E2E tests
 */

/**
 * Wait for loading spinner to disappear
 * @param {import('@playwright/test').Page} page 
 */
export async function waitForLoadingToComplete(page) {
  try {
    // Wait for any loading spinners to appear and then disappear
    await page.waitForSelector('.spinner-border', { timeout: 2000 });
    await page.waitForSelector('.spinner-border', { state: 'detached', timeout: 10000 });
  } catch {
    // No loading spinner found, continue
  }
}

/**
 * Wait for toast notification and optionally verify its content
 * @param {import('@playwright/test').Page} page 
 * @param {string} expectedMessage - Optional expected message
 * @param {'success'|'error'|'warning'|'info'} type - Optional toast type
 */
export async function waitForToast(page, expectedMessage = null, type = null) {
  const toastSelector = '.toast';
  await page.waitForSelector(toastSelector, { timeout: 5000 });
  
  if (expectedMessage) {
    await page.waitForSelector(`${toastSelector}:has-text("${expectedMessage}")`, { timeout: 5000 });
  }
  
  if (type) {
    await page.waitForSelector(`${toastSelector}.toast-${type}`, { timeout: 5000 });
  }
  
  // Wait for toast to disappear
  await page.waitForSelector(toastSelector, { state: 'detached', timeout: 10000 });
}

/**
 * Fill form field by data-testid
 * @param {import('@playwright/test').Page} page 
 * @param {string} testId 
 * @param {string} value 
 */
export async function fillField(page, testId, value) {
  const selector = `[data-testid="${testId}"]`;
  await page.waitForSelector(selector);
  await page.fill(selector, value);
}

/**
 * Click button by data-testid
 * @param {import('@playwright/test').Page} page 
 * @param {string} testId 
 */
export async function clickButton(page, testId) {
  const selector = `[data-testid="${testId}"]`;
  await page.waitForSelector(selector);
  await page.click(selector);
}

/**
 * Select option from dropdown by data-testid
 * @param {import('@playwright/test').Page} page 
 * @param {string} testId 
 * @param {string} value 
 */
export async function selectOption(page, testId, value) {
  const selector = `[data-testid="${testId}"]`;
  await page.waitForSelector(selector);
  await page.selectOption(selector, value);
}

/**
 * Upload file to input by data-testid
 * @param {import('@playwright/test').Page} page 
 * @param {string} testId 
 * @param {string} filePath 
 */
export async function uploadFile(page, testId, filePath) {
  const selector = `[data-testid="${testId}"]`;
  await page.waitForSelector(selector);
  await page.setInputFiles(selector, filePath);
}

/**
 * Wait for table to load and return row count
 * @param {import('@playwright/test').Page} page 
 * @param {string} tableTestId 
 * @returns {Promise<number>}
 */
export async function waitForTableToLoad(page, tableTestId = 'data-table') {
  const tableSelector = `[data-testid="${tableTestId}"]`;
  await page.waitForSelector(tableSelector);
  await waitForLoadingToComplete(page);
  
  const rows = await page.locator(`${tableSelector} tbody tr`).count();
  return rows;
}

/**
 * Search in table or list
 * @param {import('@playwright/test').Page} page 
 * @param {string} searchTerm 
 * @param {string} searchInputTestId 
 */
export async function searchInTable(page, searchTerm, searchInputTestId = 'search-input') {
  await fillField(page, searchInputTestId, searchTerm);
  await page.keyboard.press('Enter');
  await waitForLoadingToComplete(page);
}

/**
 * Navigate to page and wait for it to load
 * @param {import('@playwright/test').Page} page 
 * @param {string} path 
 */
export async function navigateToPage(page, path) {
  await page.goto(path);
  await waitForLoadingToComplete(page);
}

/**
 * Take screenshot with timestamp
 * @param {import('@playwright/test').Page} page 
 * @param {string} name 
 */
export async function takeScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ 
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true 
  });
}
