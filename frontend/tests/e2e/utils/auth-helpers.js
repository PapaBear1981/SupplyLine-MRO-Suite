/**
 * Authentication helper functions for E2E tests
 */

/**
 * Login as admin user
 * @param {import('@playwright/test').Page} page 
 */
export async function loginAsAdmin(page) {
  await page.goto('/login');
  
  // Fill login form
  await page.fill('[data-testid="employee-number-input"]', 'ADMIN001');
  await page.fill('[data-testid="password-input"]', 'admin123');
  
  // Submit form
  await page.click('[data-testid="login-button"]');
  
  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard', { timeout: 10000 });
  
  // Verify admin is logged in
  // On mobile devices, the admin dashboard link might be in a collapsed menu
  try {
    // First try to find the admin dashboard link directly
    await page.waitForSelector('[data-testid="admin-dashboard-link"]', { timeout: 2000 });
  } catch {
    // If not visible, try expanding the mobile menu first
    const hamburgerMenu = page.locator('[data-testid="hamburger-menu"], .navbar-toggler');
    if (await hamburgerMenu.isVisible()) {
      await hamburgerMenu.click();
      await page.waitForTimeout(500); // Wait for menu animation
    }
    // Now try to find the admin dashboard link
    await page.waitForSelector('[data-testid="admin-dashboard-link"]', { timeout: 5000 });
  }
}

/**
 * Login as regular user
 * @param {import('@playwright/test').Page} page 
 * @param {string} employeeNumber 
 * @param {string} password 
 */
export async function loginAsUser(page, employeeNumber = 'USER001', password = 'user123') {
  await page.goto('/login');
  
  // Fill login form
  await page.fill('[data-testid="employee-number-input"]', employeeNumber);
  await page.fill('[data-testid="password-input"]', password);
  
  // Submit form
  await page.click('[data-testid="login-button"]');
  
  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard', { timeout: 10000 });
  
  // Verify user is logged in
  await page.waitForSelector('[data-testid="user-menu"]', { timeout: 5000 });
}

/**
 * Logout current user
 * @param {import('@playwright/test').Page} page 
 */
export async function logout(page) {
  // Click user menu
  await page.click('[data-testid="user-menu"]');
  
  // Click logout
  await page.click('[data-testid="logout-button"]');
  
  // Wait for redirect to login page
  await page.waitForURL('/login', { timeout: 10000 });
}

/**
 * Check if user is authenticated
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<boolean>}
 */
export async function isAuthenticated(page) {
  try {
    await page.waitForSelector('[data-testid="user-menu"]', { timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if current user is admin
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<boolean>}
 */
export async function isAdmin(page) {
  try {
    await page.waitForSelector('[data-testid="admin-dashboard-link"]', { timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}
