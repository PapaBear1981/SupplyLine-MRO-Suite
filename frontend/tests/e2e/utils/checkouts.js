import { expect } from '@playwright/test';

export const CHECKOUTS_SELECTORS = {
  myCheckoutsHeader: 'h1:has-text("My Checkouts")',
  allCheckoutsHeader: 'h1:has-text("All Active Checkouts")',
  activeCard: '.card:has(h4:has-text("Active Checkouts"))',
  historyCard: '.card:has(h4:has-text("Checkout History"))',
  allActiveCard: '.card:has(h4:has-text("All Active Checkouts"))'
};

export async function waitForMyCheckouts(page) {
  await page.waitForLoadState('networkidle');
  await expect(page.locator(CHECKOUTS_SELECTORS.myCheckoutsHeader)).toBeVisible();
}

export async function waitForAllCheckouts(page) {
  await page.waitForLoadState('networkidle');
  await expect(page.locator(CHECKOUTS_SELECTORS.allCheckoutsHeader)).toBeVisible();
}

export function activeCheckoutRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.activeCard} tbody tr`);
}

export function checkoutHistoryRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.historyCard} tbody tr`);
}

export function allCheckoutRows(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.allActiveCard} tbody tr`);
}

export function allCheckoutReturnButtons(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.allActiveCard} button:has-text("Return Tool")`);
}

export function myCheckoutReturnButtons(page) {
  return page.locator(`${CHECKOUTS_SELECTORS.activeCard} button:has-text("Return Tool")`);
}

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
