/**
 * Authentication utilities for E2E tests
 */
import { expect } from '@playwright/test';

// Test user credentials
export const TEST_USERS = {
  admin: {
    username: 'ADMIN001',
    password: 'admin123'
  },
  user: {
    username: 'USER001',
    password: 'user123'
  },
  materials: {
    username: 'MAT001',
    password: 'materials123'
  }
};

const EMPLOYEE_NUMBER_SELECTOR = [
  'input[name="employee_number"]',
  'input[name="username"]',
  'input[placeholder*="Employee"]',
  'input[placeholder*="employee"]'
].join(', ');

const PASSWORD_SELECTOR = [
  'input[type="password"]',
  'input[name="password"]',
  'input[placeholder*="Password"]',
  'input[placeholder*="password"]'
].join(', ');

const LOGIN_BUTTON_SELECTOR = 'button[type="submit"], button:has-text("Sign In"), button:has-text("Login")';
const LOGIN_SUCCESS_URL_PATTERN = /\/(?:$|dashboard(?:[\/?#]|$))/;
const LOGIN_ERROR_SELECTOR = [
  '.login-alert.login-alert-danger',
  '.login-alert-danger',
  '.alert-danger',
  '.error-message',
  '[data-testid="login-error"]',
  '[role="alert"]'
].join(', ');

async function getLoginErrorDetails(page) {
  const errorLocator = page.locator(LOGIN_ERROR_SELECTOR).filter({ hasText: /.+/ }).first();
  const isVisible = await errorLocator.isVisible().catch(() => false);

  if (!isVisible) {
    return null;
  }

  const text = await errorLocator.textContent().catch(() => null);
  return text?.trim() || null;
}

async function waitForAuthStatus(page) {
  const statusResponse = await page.request.get('/api/auth/status');
  if (!statusResponse.ok()) {
    throw new Error(`Auth status request failed: ${statusResponse.status()}`);
  }

  const status = await statusResponse.json();
  if (!status.authenticated) {
    throw new Error('Authentication status indicates unauthenticated session');
  }

  return status;
}

async function fetchCurrentUser(page) {
  const meResponse = await page.request.get('/api/auth/me');
  if (!meResponse.ok()) {
    throw new Error(`Failed to fetch current user: ${meResponse.status()}`);
  }

  return meResponse.json();
}

async function ensureOnDashboard(page) {
  if (page.url().includes('/login')) {
    await page.goto('/dashboard');
  }
  await page.waitForLoadState('networkidle').catch(() => {});
}

/**
 * Login with specified user credentials using the UI flow so HttpOnly cookies are issued.
 * Returns the storage state so callers can persist or reuse it.
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, password: string }} user
 * @param {{ storagePath?: string, navigateToDashboard?: boolean }} options
 * @returns {Promise<import('@playwright/test').StorageState>}
 */
export async function login(page, user = TEST_USERS.admin, options = {}) {
  const { storagePath, navigateToDashboard = true } = options;
  const context = page.context();

  await context.clearCookies().catch(() => {});
  await page.goto('/login', { waitUntil: 'load' });

  const employeeInput = page.locator(EMPLOYEE_NUMBER_SELECTOR).first();
  const passwordInput = page.locator(PASSWORD_SELECTOR).first();
  const submitButton = page.locator(LOGIN_BUTTON_SELECTOR).first();

  await expect(employeeInput).toBeVisible({ timeout: 15000 });
  await expect(passwordInput).toBeVisible();

  await employeeInput.fill(user.username, { timeout: 5000 });
  await passwordInput.fill(user.password, { timeout: 5000 });

  // Click submit and wait for navigation - simpler and more reliable across browsers
  await submitButton.click();

  // Wait for navigation to complete (login redirects to dashboard or home)
  try {
    await page.waitForURL(LOGIN_SUCCESS_URL_PATTERN, { timeout: 120000 });
  } catch (error) {
    const loginError = await getLoginErrorDetails(page);
    const details = [
      'Login did not redirect to the dashboard within the allotted time.',
      loginError ? `UI error message: "${loginError}".` : null,
      `Original error: ${error.message}`
    ].filter(Boolean).join(' ');
    throw new Error(details);
  }

  await page.waitForLoadState('networkidle').catch(() => {});

  // Verify authentication succeeded by checking auth status
  try {
    await expect
      .poll(async () => {
        try {
          const status = await waitForAuthStatus(page);
          if (!status?.authenticated) {
            return null;
          }
          await fetchCurrentUser(page);
          return 'authenticated';
        } catch {
          return null;
        }
      }, {
        message: 'Expected to confirm authenticated session via auth endpoints after login.',
        timeout: 60000,
        intervals: [500, 1000, 2000, 4000, 6000]
      })
      .toBe('authenticated');
  } catch (error) {
    const loginError = await getLoginErrorDetails(page);
    const details = [
      'Login navigation completed but authentication APIs did not confirm the session.',
      loginError ? `UI error message: "${loginError}".` : null,
      `Details: ${error.message}`
    ].filter(Boolean).join(' ');
    throw new Error(details);
  }

  if (navigateToDashboard) {
    await ensureOnDashboard(page);
  }

  const storageState = await context.storageState({ path: storagePath });
  return storageState;
}

/**
 * Logout the current user via API and clear browser storage.
 * @param {import('@playwright/test').Page} page
 */
export async function logout(page) {
  await page.request.post('/api/auth/logout').catch(() => {});
  await clearAuthState(page);
}

/**
 * Check authenticated status using the backend status endpoint.
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<boolean>}
 */
export async function isAuthenticated(page) {
  try {
    const status = await waitForAuthStatus(page);
    return Boolean(status?.authenticated);
  } catch {
    return false;
  }
}

/**
 * Setup authentication state for tests that need to start authenticated.
 * Returns storage state to allow reuse in new browser contexts.
 * @param {import('@playwright/test').Page} page
 * @param {{ username: string, password: string }} user
 * @param {{ storagePath?: string, navigateToDashboard?: boolean }} options
 * @returns {Promise<import('@playwright/test').StorageState>}
 */
export async function setupAuthenticatedState(page, user = TEST_USERS.admin, options = {}) {
  return login(page, user, options);
}

/**
 * Clear authentication state (cookies, storage) and ensure login page is loaded.
 * @param {import('@playwright/test').Page} page
 */
export async function clearAuthState(page) {
  const context = page.context();
  await context.clearCookies().catch(() => {});
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.goto('/login', { waitUntil: 'load' });
}
