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
export async function login(page, user = TEST_USERS.admin) {
  const response = await page.request.post('/api/auth/login', {
    data: {
      employee_number: user.username,
      password: user.password,
    },
  });

  if (!response.ok()) {
    throw new Error(`Login failed with status ${response.status()}`);
  }

  const data = await response.json();

  await page.addInitScript((tokenData) => {
    localStorage.setItem('accessToken', tokenData.access_token);
    localStorage.setItem('refreshToken', tokenData.refresh_token);
    localStorage.setItem('user', JSON.stringify(tokenData.user));
  }, data);

  await page.context().setExtraHTTPHeaders({
    Authorization: `Bearer ${data.access_token}`,
  });

  await page.goto('/dashboard');
}

/**
 * Logout the current user
 * @param {import('@playwright/test').Page} page 
 */
export async function logout(page) {
  await page.context().setExtraHTTPHeaders({});

  await page.evaluate(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  });

  await page.goto('/login');
}

/**
 * Check if user is authenticated by checking current URL
 * @param {import('@playwright/test').Page} page 
 * @returns {boolean}
 */
export async function isAuthenticated(page) {
  const token = await page.evaluate(() => localStorage.getItem('accessToken'));
  return Boolean(token);
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
  await page.context().setExtraHTTPHeaders({});
  await page.evaluate(() => {
    localStorage.clear();
  });
  await page.goto('/login');
}
