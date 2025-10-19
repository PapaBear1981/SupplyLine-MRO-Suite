import { test, expect } from '@playwright/test';
import { setupAuthenticatedState, TEST_USERS } from './utils/auth.js';
import {
  waitForMyCheckouts,
  waitForAllCheckouts,
  activeCheckoutRows,
  checkoutHistoryRows,
  allCheckoutRows,
  allCheckoutReturnButtons,
  myCheckoutReturnButtons,
  hasVisibleRows,
  CHECKOUTS_SELECTORS
} from './utils/checkouts.js';

const TOOL_LINK_SELECTOR = `${CHECKOUTS_SELECTORS.allActiveCard} tbody tr td a[href^="/tools/"]`;

async function ensureLoggedIn(page, user) {
  await setupAuthenticatedState(page, user, { navigateToDashboard: true });
}

test.describe('Checkout Workflows', () => {
  test('admin can view all checkouts and interact with return modal', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.admin);
    await page.goto('/checkouts/all');
    await waitForAllCheckouts(page);

    const returnButtons = allCheckoutReturnButtons(page);
    const hasReturnableRows = await hasVisibleRows(allCheckoutRows(page));

    if (hasReturnableRows && await returnButtons.count() > 0) {
      await returnButtons.first().click();
      await expect(page.locator('.modal-title:has-text("Return Tool")')).toBeVisible();
      await expect(page.locator('.modal-body')).toContainText('Tool:');
      await expect(page.locator('.modal-body')).toContainText('Description:');
      await page.click('.modal-footer button:has-text("Cancel")');
      await expect(page.locator('.modal.show')).toHaveCount(0, { timeout: 5000 });
    } else {
      await expect(page.locator('text=There are no active checkouts.')).toBeVisible();
    }
  });

  test('standard users are redirected away from all checkouts view', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.user);
    await page.goto('/checkouts');
    await waitForMyCheckouts(page);

    await expect(page.locator('button:has-text("View All Active Checkouts")')).toHaveCount(0);

    await page.goto('/checkouts/all');
    await waitForMyCheckouts(page);
    await expect(page).toHaveURL('/checkouts');
  });

  test('materials personnel retain return capabilities on personal checkouts', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.materials);
    await page.goto('/checkouts');
    await waitForMyCheckouts(page);

    const returnButtons = myCheckoutReturnButtons(page);
    const hasActionableRows = await hasVisibleRows(activeCheckoutRows(page));

    if (hasActionableRows && await returnButtons.count() > 0) {
      await expect(returnButtons.first()).toBeVisible();
    } else {
      await expect(page.locator('.alert-info')).toHaveCount(0);
    }
  });

  test('tool links from all checkouts navigate to tool detail pages', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.admin);
    await page.goto('/checkouts/all');
    await waitForAllCheckouts(page);

    const toolLink = page.locator(TOOL_LINK_SELECTOR).first();

    if (await toolLink.count() > 0) {
      const href = await toolLink.getAttribute('href');
      await toolLink.click();
      await page.waitForLoadState('networkidle');

      if (href) {
        const escapedHref = href.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
        await expect(page).toHaveURL(new RegExp(`${escapedHref}$`));
      } else {
        await expect(page).toHaveURL(/\/tools\/\d+$/);
      }

      await expect(
        page.locator('[data-testid="tool-details"], h1:has-text("Tool Detail"), h1:has-text("Tool Inventory")')
      ).toBeVisible();
    } else {
      await expect(page.locator('text=There are no active checkouts.')).toBeVisible();
    }
  });

  test('checkout history is available on personal checkouts page', async ({ page }) => {
    await ensureLoggedIn(page, TEST_USERS.admin);
    await page.goto('/checkouts');
    await waitForMyCheckouts(page);

    const historyRows = checkoutHistoryRows(page);
    const hasHistory = await hasVisibleRows(historyRows);

    if (hasHistory) {
      await expect(historyRows.first()).toBeVisible();
    } else {
      await expect(page.locator('text=You have no past checkouts.')).toBeVisible();
    }
  });
});
