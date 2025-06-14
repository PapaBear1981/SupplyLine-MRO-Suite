import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, navigateToPage } from '../utils/test-helpers.js';

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('should match login page visual appearance', async ({ page }) => {
    await page.goto('/login');
    await waitForLoadingToComplete(page);
    
    // Hide dynamic elements that might cause flaky tests
    await page.addStyleTag({
      content: `
        [data-testid="current-time"],
        .timestamp,
        .loading-spinner {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot and compare
    await expect(page).toHaveScreenshot('login-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match dashboard visual appearance', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Hide dynamic content
    await page.addStyleTag({
      content: `
        [data-testid="current-time"],
        .timestamp,
        .loading-spinner,
        .chart-container canvas {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('dashboard-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match tools management page visual appearance', async ({ page }) => {
    await navigateToPage(page, '/tools');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        [data-testid="last-updated"] {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('tools-management-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match tool form visual appearance', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    // Take screenshot of the form
    await expect(page.locator('[data-testid="tool-form"]')).toHaveScreenshot('tool-form.png', {
      animations: 'disabled'
    });
  });

  test('should match chemicals management page visual appearance', async ({ page }) => {
    await navigateToPage(page, '/chemicals');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        [data-testid="last-updated"] {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('chemicals-management-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match checkout page visual appearance', async ({ page }) => {
    await navigateToPage(page, '/checkouts');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('checkout-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match cycle count dashboard visual appearance', async ({ page }) => {
    await navigateToPage(page, '/cycle-counts');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        .chart-container canvas {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('cycle-count-dashboard.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match admin dashboard visual appearance', async ({ page }) => {
    await navigateToPage(page, '/admin/dashboard');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        .chart-container canvas,
        [data-testid*="metric"] .value {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('admin-dashboard.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match calibration management page visual appearance', async ({ page }) => {
    await navigateToPage(page, '/calibrations');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('calibration-management-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match navigation menu visual appearance', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Take screenshot of navigation
    await expect(page.locator('[data-testid="main-navigation"], .navbar')).toHaveScreenshot('navigation-menu.png', {
      animations: 'disabled'
    });
  });

  test('should match modal dialog visual appearance', async ({ page }) => {
    await navigateToPage(page, '/tools');
    
    // Try to open a modal
    const viewButton = page.locator('[data-testid="view-tool-button"]').first();
    if (await viewButton.isVisible()) {
      await viewButton.click();
      
      // Wait for modal to appear
      const modal = page.locator('.modal, [data-testid*="modal"]');
      if (await modal.isVisible()) {
        // Take screenshot of modal
        await expect(modal).toHaveScreenshot('modal-dialog.png', {
          animations: 'disabled'
        });
      }
    }
  });

  test('should match error state visual appearance', async ({ page }) => {
    // Intercept API calls to simulate error
    await page.route('**/api/tools', route => {
      route.abort('failed');
    });
    
    await navigateToPage(page, '/tools');
    
    // Wait for error state
    await page.waitForSelector('.error-message, .alert-danger', { timeout: 5000 });
    
    // Take screenshot of error state
    await expect(page).toHaveScreenshot('error-state.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match loading state visual appearance', async ({ page }) => {
    // Intercept API calls to delay response
    await page.route('**/api/tools', route => {
      setTimeout(() => route.continue(), 2000);
    });
    
    // Navigate and capture loading state
    await page.goto('/tools');
    
    // Wait for loading spinner
    await page.waitForSelector('.loading-spinner, .spinner-border', { timeout: 1000 });
    
    // Take screenshot of loading state
    await expect(page).toHaveScreenshot('loading-state.png', {
      animations: 'disabled'
    });
  });

  test('should match mobile dashboard visual appearance', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await navigateToPage(page, '/dashboard');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        .chart-container canvas {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('mobile-dashboard.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match tablet layout visual appearance', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    await navigateToPage(page, '/tools');
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('tablet-tools-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match dark theme visual appearance', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Try to enable dark theme if available
    const themeToggle = page.locator('[data-testid="theme-toggle"], [data-testid="dark-mode-toggle"]');
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      await waitForLoadingToComplete(page);
    } else {
      // Manually apply dark theme styles for testing
      await page.addStyleTag({
        content: `
          body {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
          }
          .card, .table {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
          }
        `
      });
    }
    
    // Hide dynamic elements
    await page.addStyleTag({
      content: `
        .timestamp,
        .loading-spinner,
        .chart-container canvas {
          visibility: hidden !important;
        }
      `
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('dark-theme-dashboard.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should match form validation visual appearance', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    // Try to submit empty form to trigger validation
    await page.click('[data-testid="save-tool-button"]');
    
    // Wait for validation errors
    await page.waitForSelector('.is-invalid, .error-message', { timeout: 2000 });
    
    // Take screenshot of validation state
    await expect(page.locator('[data-testid="tool-form"]')).toHaveScreenshot('form-validation-errors.png', {
      animations: 'disabled'
    });
  });

  test('should match success notification visual appearance', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    // Fill form with valid data
    await page.fill('[data-testid="tool-number-input"]', 'VISUAL001');
    await page.fill('[data-testid="serial-number-input"]', 'VISUAL001');
    await page.fill('[data-testid="description-input"]', 'Visual Test Tool');
    
    // Submit form
    await page.click('[data-testid="save-tool-button"]');
    
    // Wait for success notification
    const toast = page.locator('.toast, .alert-success');
    if (await toast.isVisible()) {
      // Take screenshot of success notification
      await expect(toast).toHaveScreenshot('success-notification.png', {
        animations: 'disabled'
      });
    }
  });
});
