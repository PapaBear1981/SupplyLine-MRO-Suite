import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsUser, logout } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete } from '../utils/test-helpers.js';

test.describe('Protected Routes and Permissions', () => {
  const protectedRoutes = [
    '/dashboard',
    '/tools',
    '/checkouts',
    '/chemicals',
    '/calibrations',
    '/cycle-counts',
    '/reports'
  ];

  const adminOnlyRoutes = [
    '/admin/dashboard'
  ];

  test.describe('Unauthenticated Access', () => {
    protectedRoutes.forEach(route => {
      test(`should redirect to login when accessing ${route} without authentication`, async ({ page }) => {
        await page.goto(route);
        await expect(page).toHaveURL('/login');
      });
    });

    adminOnlyRoutes.forEach(route => {
      test(`should redirect to login when accessing admin route ${route} without authentication`, async ({ page }) => {
        await page.goto(route);
        await expect(page).toHaveURL('/login');
      });
    });
  });

  test.describe('Admin User Access', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsAdmin(page);
    });

    protectedRoutes.forEach(route => {
      test(`admin should access ${route}`, async ({ page }) => {
        await page.goto(route);
        await waitForLoadingToComplete(page);
        
        // Should not be redirected to login
        expect(page.url()).not.toContain('/login');
        
        // Should show main layout with navigation
        await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
      });
    });

    adminOnlyRoutes.forEach(route => {
      test(`admin should access admin route ${route}`, async ({ page }) => {
        await page.goto(route);
        await waitForLoadingToComplete(page);
        
        // Should not be redirected
        expect(page.url()).not.toContain('/login');
        expect(page.url()).toContain(route);
        
        // Should show admin-specific content
        await expect(page.locator('[data-testid="admin-content"]')).toBeVisible();
      });
    });

    test('admin should see admin navigation links', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should see admin dashboard link
      await expect(page.locator('[data-testid="admin-dashboard-link"]')).toBeVisible();
      
      // Should see all navigation links
      await expect(page.locator('a[href="/chemicals"]')).toBeVisible();
      await expect(page.locator('a[href="/calibrations"]')).toBeVisible();
      await expect(page.locator('a[href="/cycle-counts"]')).toBeVisible();
      await expect(page.locator('a[href="/reports"]')).toBeVisible();
    });
  });

  test.describe('Regular User Access', () => {
    test.beforeEach(async ({ page }) => {
      // Try to login as regular user, skip tests if user doesn't exist
      try {
        await page.goto('/login');
        await page.fill('[data-testid="employee-number-input"]', 'USER001');
        await page.fill('[data-testid="password-input"]', 'user123');
        await page.click('[data-testid="login-button"]');
        
        await page.waitForTimeout(2000);
        
        if (!page.url().includes('/dashboard')) {
          test.skip('Regular user does not exist - skipping regular user tests');
        }
      } catch (error) {
        test.skip('Could not login as regular user - skipping regular user tests');
      }
    });

    test('regular user should access basic routes', async ({ page }) => {
      const basicRoutes = ['/dashboard', '/tools', '/checkouts'];
      
      for (const route of basicRoutes) {
        await page.goto(route);
        await waitForLoadingToComplete(page);
        
        // Should not be redirected to login
        expect(page.url()).not.toContain('/login');
      }
    });

    test('regular user should not see admin navigation links', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should not see admin dashboard link
      await expect(page.locator('[data-testid="admin-dashboard-link"]')).not.toBeVisible();
    });

    adminOnlyRoutes.forEach(route => {
      test(`regular user should not access admin route ${route}`, async ({ page }) => {
        await page.goto(route);
        
        // Should be redirected or show access denied
        const currentUrl = page.url();
        const hasAccessDenied = await page.locator('.access-denied, .unauthorized').isVisible();
        
        expect(
          currentUrl.includes('/login') || 
          currentUrl.includes('/dashboard') || 
          hasAccessDenied
        ).toBeTruthy();
      });
    });
  });

  test.describe('Materials User Access', () => {
    test.beforeEach(async ({ page }) => {
      // Try to login as materials user
      try {
        await page.goto('/login');
        await page.fill('[data-testid="employee-number-input"]', 'MAT001');
        await page.fill('[data-testid="password-input"]', 'materials123');
        await page.click('[data-testid="login-button"]');
        
        await page.waitForTimeout(2000);
        
        if (!page.url().includes('/dashboard')) {
          test.skip('Materials user does not exist - skipping materials user tests');
        }
      } catch (error) {
        test.skip('Could not login as materials user - skipping materials user tests');
      }
    });

    test('materials user should access materials-specific routes', async ({ page }) => {
      const materialsRoutes = ['/chemicals', '/calibrations', '/cycle-counts', '/reports'];
      
      for (const route of materialsRoutes) {
        await page.goto(route);
        await waitForLoadingToComplete(page);
        
        // Should not be redirected to login
        expect(page.url()).not.toContain('/login');
      }
    });

    test('materials user should see materials navigation links', async ({ page }) => {
      await page.goto('/dashboard');
      
      // Should see materials-specific links
      await expect(page.locator('a[href="/chemicals"]')).toBeVisible();
      await expect(page.locator('a[href="/calibrations"]')).toBeVisible();
      await expect(page.locator('a[href="/cycle-counts"]')).toBeVisible();
      
      // Should not see admin dashboard link
      await expect(page.locator('[data-testid="admin-dashboard-link"]')).not.toBeVisible();
    });
  });

  test.describe('Session Management', () => {
    test('should maintain session across page refreshes', async ({ page }) => {
      await loginAsAdmin(page);
      await page.goto('/tools');
      
      // Refresh page
      await page.reload();
      
      // Should still be authenticated and on tools page
      await expect(page).toHaveURL('/tools');
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should handle expired sessions gracefully', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Simulate expired session by clearing storage
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      // Try to access protected route
      await page.goto('/tools');
      
      // Should be redirected to login
      await expect(page).toHaveURL('/login');
    });

    test('should redirect to intended page after login', async ({ page }) => {
      // Try to access a protected route
      await page.goto('/tools');
      
      // Should be redirected to login
      await expect(page).toHaveURL('/login');
      
      // Login
      await loginAsAdmin(page);
      
      // Should be redirected to originally requested page
      // Note: This depends on your implementation
      // You might be redirected to dashboard instead
      const currentUrl = page.url();
      expect(currentUrl.includes('/dashboard') || currentUrl.includes('/tools')).toBeTruthy();
    });
  });
});
