/**
 * Authentication utilities for E2E tests
 */

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

/**
 * Login with specified user credentials
 * @param {import('@playwright/test').Page} page 
 * @param {Object} user - User credentials object
 * @param {boolean} rememberMe - Whether to check remember me option
 */
export async function login(page, user = TEST_USERS.admin, rememberMe = false) {
  await page.goto('/login');
  
  // Fill in credentials
  await page.fill('input[placeholder="Enter employee number"]', user.username);
  await page.fill('input[placeholder="Password"]', user.password);
  
  // Check remember me if requested
  if (rememberMe) {
    await page.check('input[type="checkbox"]');
  }
  
  // Submit form
  await page.click('button[type="submit"]');
  
  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard');
}

/**
 * Logout the current user
 * @param {import('@playwright/test').Page} page 
 */
export async function logout(page) {
  // Click user menu
  await page.click('[data-testid="user-menu"]');
  
  // Click logout
  await page.click('text=Logout');
  
  // Wait for redirect to login
  await page.waitForURL('/login');
}

/**
 * Check if user is authenticated by checking current URL
 * @param {import('@playwright/test').Page} page 
 * @returns {boolean}
 */
export async function isAuthenticated(page) {
  const url = page.url();
  return !url.includes('/login');
}

/**
 * Setup authentication state for tests that need to start authenticated
 * @param {import('@playwright/test').Page} page 
 * @param {Object} user - User credentials object
 */
export async function setupAuthenticatedState(page, user = TEST_USERS.admin) {
  await login(page, user);
}

/**
 * Clear authentication state (logout and clear storage)
 * @param {import('@playwright/test').Page} page 
 */
export async function clearAuthState(page) {
  // Clear localStorage
  await page.evaluate(() => {
    localStorage.clear();
  });
  
  // Navigate to login to ensure clean state
  await page.goto('/login');
}
