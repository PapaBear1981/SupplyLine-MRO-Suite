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
  // Use the API login endpoint to obtain JWT tokens
  const response = await page.request.post('/api/auth/login', {
    data: {
      employee_number: user.username,
      password: user.password,
      remember_me: rememberMe,
    },
  });

  if (!response.ok()) {
    throw new Error(`Login failed with status ${response.status()}`);
  }

  const result = await response.json();

  const { access_token, refresh_token, user: userData } = result;

  // Navigate to the app so we have the correct origin for localStorage
  await page.goto('/');

  // Store tokens and user data in localStorage
  await page.evaluate(({ access_token, refresh_token, userData }) => {
    localStorage.setItem('supplyline_access_token', access_token);
    localStorage.setItem('supplyline_refresh_token', refresh_token);
    localStorage.setItem('supplyline_user_data', JSON.stringify(userData));
  }, { access_token, refresh_token, userData });

  // Optionally fetch CSRF token if endpoint exists
  try {
    const csrfResp = await page.request.get('/api/auth/csrf-token', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    if (csrfResp.ok()) {
      const { csrf_token } = await csrfResp.json();
      await page.evaluate((token) => {
        localStorage.setItem('supplyline_csrf_token', token);
      }, csrf_token);
    }
  } catch (err) {
    // CSRF token endpoint may not be available in all environments
  }

  // Reload page with authenticated state
  await page.reload();
}

/**
 * Logout the current user
 * @param {import('@playwright/test').Page} page 
 */
export async function logout(page) {
  const token = await page.evaluate(() =>
    localStorage.getItem('supplyline_access_token')
  );

  if (token) {
    try {
      await page.request.post('/api/auth/logout', {
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (e) {
      // ignore logout errors in tests
    }
  }

  await page.evaluate(() => localStorage.clear());
  await page.goto('/login');
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
