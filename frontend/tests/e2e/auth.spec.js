import { test, expect } from '@playwright/test';

// Test data
const TEST_USER = {
  username: 'ADMIN001',
  password: 'admin123'
};

const INVALID_USER = {
  username: 'INVALID001',
  password: 'wrongpassword'
};

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    // Check that login form elements are present
    await expect(page.locator('input[placeholder="Enter employee number"]')).toBeVisible();
    await expect(page.locator('input[placeholder="Password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Check for validation messages
    await expect(page.locator('.invalid-feedback')).toContainText(['Please provide your employee number', 'Please provide a password']);
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[placeholder="Enter employee number"]', INVALID_USER.username);
    await page.fill('input[placeholder="Password"]', INVALID_USER.password);
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for error message
    await expect(page.locator('.alert-danger')).toBeVisible();
    await expect(page.locator('.alert-danger')).toContainText('Invalid credentials');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill in valid credentials
    await page.fill('input[placeholder="Enter employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Password"]', TEST_USER.password);
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard (root path)
    await expect(page).toHaveURL('/');

    // Should see user dashboard elements
    await expect(page.locator('h1')).toContainText('Dashboard');

    // Verify auth token stored
    const token = await page.evaluate(() => localStorage.getItem('supplyline_access_token'));
    expect(token).not.toBeNull();
  });


  test('should logout successfully', async ({ page }) => {
    // First login
    await page.fill('input[placeholder="Enter employee number"]', TEST_USER.username);
    await page.fill('input[placeholder="Password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Wait for dashboard (root path)
    await expect(page).toHaveURL('/');
    
    // Click on user profile button to open profile modal
    await page.click('button.btn-outline-light:has-text("John Engineer")', { timeout: 10000 });

    // Click logout button in the modal
    await page.click('button:has-text("Logout")');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/login');

    // Tokens should be cleared
    const token = await page.evaluate(() => localStorage.getItem('supplyline_access_token'));
    expect(token).toBeNull();
  });


  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Try to access protected route directly
    await page.goto('/tools');
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
  });

  test('should redirect back to intended page after login', async ({ page }) => {
    // Try to access protected route directly
    await page.goto('/tools');

    // Should redirect to login
    await expect(page).toHaveURL('/login');

    // Login
    const [request] = await Promise.all([
      page.waitForRequest(req => req.url().includes('/api/tools') && req.method() === 'GET'),
      page.fill('input[placeholder="Enter employee number"]', TEST_USER.username),
      page.fill('input[placeholder="Password"]', TEST_USER.password),
      page.click('button[type="submit"]'),
    ]);

    // Should redirect back to tools page
    await expect(page).toHaveURL('/tools');

    // Authorization header should be sent
    expect(request.headers()['authorization']).toBeTruthy();
  });
});
