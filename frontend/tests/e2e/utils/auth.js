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
 * Store auth tokens in localStorage
 * @param {import('@playwright/test').Page} page
 * @param {string} accessToken
 * @param {string} refreshToken
 */
export async function setAuthTokens(page, accessToken, refreshToken) {
  await page.evaluate(([a, r]) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', r);
  }, [accessToken, refreshToken]);
}

/**
 * Login with specified user credentials
 * @param {import('@playwright/test').Page} page 
 * @param {Object} user - User credentials object
 */
export async function login(page, user = TEST_USERS.admin) {
  const response = await page.request.post('/api/auth/login', {
    data: {
      employee_number: user.username,
      password: user.password
    }
  });

  if (!response.ok()) {
    throw new Error(`Login failed: ${response.status()}`);
  }

  const data = await response.json();
  await setAuthTokens(page, data.access_token, data.refresh_token);

  await page.goto('/dashboard');
}

/**
 * Logout the current user
 * @param {import('@playwright/test').Page} page 
 */
export async function logout(page) {
  const token = await page.evaluate(() => localStorage.getItem('access_token'));

  if (token) {
    await page.request.post('/api/auth/logout', {
      headers: { Authorization: `Bearer ${token}` }
    }).catch(() => {});
  }

  await clearAuthState(page);
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
