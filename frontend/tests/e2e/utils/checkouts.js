/**
 * Utility functions and selectors for checkout workflow E2E tests.
 *
 * This module provides reusable selectors, page navigation helpers, and
 * element locators for testing checkout-related functionality in the
 * SupplyLine MRO Suite application.
 *
 * @module checkouts
 */

import { expect } from '@playwright/test';

/**
 * Selectors for checkout page elements.
 * @constant {Object}
 * @property {string} myCheckoutsHeader - Selector for "My Checkouts" page header
 * @property {string} allCheckoutsHeader - Selector for "All Active Checkouts" page header
 * @property {string} activeCard - Selector for active checkouts card
 * @property {string} historyCard - Selector for checkout history card
 * @property {string} allActiveCard - Selector for all active checkouts card
 */
export const CHECKOUTS_SELECTORS = {
  myCheckoutsHeader: 'h1:has-text("My Checkouts")',
  allCheckoutsHeader: 'h1:has-text("All Active Checkouts")',
  activeCard: '.card:has(h4:has-text("Active Checkouts"))',
  historyCard: '.card:has(h4:has-text("Checkout History"))',
  allActiveCard: '.card:has(h4:has-text("All Active Checkouts"))'
};

/**
 * Wait for the "My Checkouts" page to load completely.
 *
 * @async
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {Promise<void>}
 */
export async function waitForMyCheckouts(page) {
  await page.waitForLoadState('networkidle');
  await expect(page.locator(CHECKOUTS_SELECTORS.myCheckoutsHeader)).toBeVisible();
}

/**
 * Wait for the "All Active Checkouts" page to load completely.
 *
 * @async
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {Promise<void>}
 */
export async function waitForAllCheckouts(page) {
  await page.waitForLoadState('networkidle');
  await expect(page.locator(CHECKOUTS_SELECTORS.allCheckoutsHeader)).toBeVisible();
}

/**
 * Get locator for active checkout table rows on "My Checkouts" page.
 *
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {import('@playwright/test').Locator} Locator for active checkout rows
 */
export function activeCheckoutRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.activeCard} tbody tr`);
}

/**
 * Get locator for checkout history table rows on "My Checkouts" page.
 *
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {import('@playwright/test').Locator} Locator for checkout history rows
 */
export function checkoutHistoryRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.historyCard} tbody tr`);
}

/**
 * Get locator for all checkout table rows on "All Active Checkouts" page.
 *
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {import('@playwright/test').Locator} Locator for all checkout rows
 */
export function allCheckoutRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.allActiveCard} tbody tr`);
}

/**
 * Get locator for "Return Tool" buttons on "All Active Checkouts" page.
 *
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {import('@playwright/test').Locator} Locator for return buttons
 */
export function allCheckoutReturnButtons(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.allActiveCard} button:has-text("Return Tool")`);
}

/**
 * Get locator for "Return Tool" buttons on "My Checkouts" page.
 *
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {import('@playwright/test').Locator} Locator for return buttons
 */
export function myCheckoutReturnButtons(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.activeCard} button:has-text("Return Tool")`);
}

/**
 * Check if the checkout table has visible data rows (excluding empty state messages).
 *
 * This function iterates through all rows and checks if any contain actual checkout data
 * rather than empty state messages like "no active checkouts" or "you have no past checkouts".
 *
 * @async
 * @param {import('@playwright/test').Locator} rowLocator - Locator for table rows
 * @returns {Promise<boolean>} True if there are visible data rows, false otherwise
 */
export async function hasVisibleRows(rowLocator) {
  const rowCount = await rowLocator.count();
  if (rowCount === 0) {
    return false;
  }

  for (let index = 0; index < rowCount; index++) {
    const row = rowLocator.nth(index);
    const textContent = (await row.textContent())?.trim() ?? '';
    if (textContent && !/no active checkouts|you have no past checkouts|there are no active checkouts/i.test(textContent)) {
      return true;
    }
  }

  return false;
}
