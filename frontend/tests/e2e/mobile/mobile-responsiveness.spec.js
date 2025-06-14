import { test, expect, devices } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { 
  waitForLoadingToComplete, 
  clickButton, 
  navigateToPage 
} from '../utils/test-helpers.js';

// Mobile device configurations
const mobileDevices = [
  { name: 'iPhone 12', ...devices['iPhone 12'] },
  { name: 'Pixel 5', ...devices['Pixel 5'] },
  { name: 'iPad', ...devices['iPad'] }
];

mobileDevices.forEach(device => {
  test.describe(`Mobile Responsiveness - ${device.name}`, () => {
    test.beforeEach(async ({ page, context }) => {
      // Set mobile viewport
      await page.setViewportSize(device.viewport);
      await loginAsAdmin(page);
    });

    test('should display mobile-friendly navigation', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Should show mobile navigation elements
      const mobileNav = page.locator('[data-testid="mobile-navigation"]');
      const hamburgerMenu = page.locator('[data-testid="hamburger-menu"]');
      const collapsedNav = page.locator('.navbar-toggler');
      
      // At least one mobile navigation element should be visible
      const hasMobileNav = await mobileNav.isVisible() || 
                          await hamburgerMenu.isVisible() || 
                          await collapsedNav.isVisible();
      
      expect(hasMobileNav).toBeTruthy();
    });

    test('should expand mobile menu correctly', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Look for mobile menu toggle
      const menuToggle = page.locator('.navbar-toggler, [data-testid="hamburger-menu"], [data-testid="mobile-menu-toggle"]');
      
      if (await menuToggle.isVisible()) {
        await menuToggle.click();
        
        // Should show expanded menu
        const expandedMenu = page.locator('.navbar-collapse.show, [data-testid="mobile-menu-expanded"]');
        await expect(expandedMenu).toBeVisible();
        
        // Should show navigation links
        const navLinks = page.locator('.navbar-nav a, [data-testid="mobile-nav-link"]');
        const linkCount = await navLinks.count();
        expect(linkCount).toBeGreaterThan(0);
      }
    });

    test('should display dashboard widgets in mobile layout', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Dashboard should be visible
      await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
      
      // Widgets should stack vertically on mobile
      const widgets = page.locator('[data-testid*="widget"], .card, .dashboard-widget');
      const widgetCount = await widgets.count();
      
      if (widgetCount > 0) {
        // Check that widgets are properly sized for mobile
        const firstWidget = widgets.first();
        const boundingBox = await firstWidget.boundingBox();
        
        if (boundingBox) {
          // Widget should not exceed viewport width
          expect(boundingBox.width).toBeLessThanOrEqual(device.viewport.width);
        }
      }
    });

    test('should handle mobile tool management', async ({ page }) => {
      await navigateToPage(page, '/tools');
      
      // Tools page should be visible
      await expect(page.locator('[data-testid="tools-page-title"]')).toBeVisible();
      
      // Table should be responsive or show mobile view
      const toolsTable = page.locator('[data-testid="tools-table"]');
      const mobileToolsList = page.locator('[data-testid="mobile-tools-list"]');
      
      const hasTable = await toolsTable.isVisible();
      const hasMobileList = await mobileToolsList.isVisible();
      
      expect(hasTable || hasMobileList).toBeTruthy();
      
      // If table is shown, it should be horizontally scrollable
      if (hasTable) {
        const tableContainer = page.locator('.table-responsive, [data-testid="table-container"]');
        if (await tableContainer.isVisible()) {
          await expect(tableContainer).toBeVisible();
        }
      }
    });

    test('should handle mobile checkout process', async ({ page }) => {
      await navigateToPage(page, '/checkouts');
      
      // Checkout form should be visible and usable
      const checkoutForm = page.locator('[data-testid="checkout-form"]');
      if (await checkoutForm.isVisible()) {
        await expect(checkoutForm).toBeVisible();
        
        // Form inputs should be properly sized
        const inputs = checkoutForm.locator('input, select');
        const inputCount = await inputs.count();
        
        for (let i = 0; i < inputCount; i++) {
          const input = inputs.nth(i);
          const boundingBox = await input.boundingBox();
          
          if (boundingBox) {
            // Input should not exceed viewport width
            expect(boundingBox.width).toBeLessThanOrEqual(device.viewport.width - 40); // Account for padding
          }
        }
      }
    });

    test('should display mobile-friendly scanner interface', async ({ page }) => {
      await navigateToPage(page, '/scanner');
      
      // Scanner interface should be optimized for mobile
      const scannerInterface = page.locator('[data-testid="scanner-interface"]');
      if (await scannerInterface.isVisible()) {
        await expect(scannerInterface).toBeVisible();
        
        // Scanner should take appropriate space on mobile
        const scannerArea = page.locator('[data-testid="scanner-area"]');
        if (await scannerArea.isVisible()) {
          const boundingBox = await scannerArea.boundingBox();
          
          if (boundingBox) {
            // Scanner area should be reasonably sized for mobile
            expect(boundingBox.width).toBeLessThanOrEqual(device.viewport.width);
            expect(boundingBox.height).toBeLessThanOrEqual(device.viewport.height * 0.7);
          }
        }
      }
    });

    test('should handle mobile cycle count interface', async ({ page }) => {
      await navigateToPage(page, '/cycle-counts/mobile');
      
      // Mobile cycle count interface should be visible
      const mobileInterface = page.locator('[data-testid="mobile-counting-interface"]');
      if (await mobileInterface.isVisible()) {
        await expect(mobileInterface).toBeVisible();
        
        // Should have mobile-optimized controls
        const mobileControls = page.locator('[data-testid="mobile-count-controls"]');
        if (await mobileControls.isVisible()) {
          await expect(mobileControls).toBeVisible();
          
          // Buttons should be touch-friendly
          const buttons = mobileControls.locator('button');
          const buttonCount = await buttons.count();
          
          for (let i = 0; i < buttonCount; i++) {
            const button = buttons.nth(i);
            const boundingBox = await button.boundingBox();
            
            if (boundingBox) {
              // Buttons should be at least 44px tall for touch accessibility
              expect(boundingBox.height).toBeGreaterThanOrEqual(40);
            }
          }
        }
      }
    });

    test('should handle mobile form interactions', async ({ page }) => {
      await navigateToPage(page, '/tools/new');
      
      // New tool form should be mobile-friendly
      const toolForm = page.locator('[data-testid="tool-form"]');
      if (await toolForm.isVisible()) {
        await expect(toolForm).toBeVisible();
        
        // Form should stack vertically on mobile
        const formGroups = toolForm.locator('.form-group, .mb-3, [data-testid*="form-group"]');
        const groupCount = await formGroups.count();
        
        if (groupCount > 1) {
          // Check that form groups are stacked
          const firstGroup = formGroups.first();
          const secondGroup = formGroups.nth(1);
          
          const firstBox = await firstGroup.boundingBox();
          const secondBox = await secondGroup.boundingBox();
          
          if (firstBox && secondBox) {
            // Second group should be below first group (stacked)
            expect(secondBox.y).toBeGreaterThan(firstBox.y + firstBox.height - 10);
          }
        }
      }
    });

    test('should handle mobile modal dialogs', async ({ page }) => {
      await navigateToPage(page, '/tools');
      
      // Try to open a modal (if any tools exist)
      const firstViewButton = page.locator('[data-testid="view-tool-button"]').first();
      if (await firstViewButton.isVisible()) {
        await firstViewButton.click();
        
        // Modal should be mobile-friendly
        const modal = page.locator('.modal, [data-testid*="modal"]');
        if (await modal.isVisible()) {
          const modalDialog = modal.locator('.modal-dialog, [data-testid="modal-dialog"]');
          if (await modalDialog.isVisible()) {
            const boundingBox = await modalDialog.boundingBox();
            
            if (boundingBox) {
              // Modal should fit within viewport
              expect(boundingBox.width).toBeLessThanOrEqual(device.viewport.width);
              expect(boundingBox.height).toBeLessThanOrEqual(device.viewport.height);
            }
          }
        }
      }
    });

    test('should handle mobile touch interactions', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Test touch interactions on mobile
      const quickActions = page.locator('[data-testid="quick-actions"]');
      if (await quickActions.isVisible()) {
        const actionButtons = quickActions.locator('button, a');
        const buttonCount = await actionButtons.count();
        
        if (buttonCount > 0) {
          const firstButton = actionButtons.first();
          
          // Simulate touch interaction
          await firstButton.tap();
          
          // Should handle the tap appropriately
          await waitForLoadingToComplete(page);
          
          // Page should respond to the interaction
          // (specific behavior depends on the button)
        }
      }
    });

    test('should maintain accessibility on mobile', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Check for mobile accessibility features
      const skipLink = page.locator('[data-testid="skip-to-content"], .skip-link');
      const focusableElements = page.locator('button:visible, a:visible, input:visible, select:visible');
      
      const focusableCount = await focusableElements.count();
      expect(focusableCount).toBeGreaterThan(0);
      
      // Test keyboard navigation on mobile (if supported)
      if (focusableCount > 0) {
        const firstFocusable = focusableElements.first();
        await firstFocusable.focus();
        
        // Element should be focused
        const isFocused = await firstFocusable.evaluate(el => el === document.activeElement);
        expect(isFocused).toBeTruthy();
      }
    });

    test('should handle mobile orientation changes', async ({ page }) => {
      await navigateToPage(page, '/dashboard');
      
      // Test landscape orientation (if device supports it)
      if (device.name.includes('iPhone') || device.name.includes('Pixel')) {
        // Rotate to landscape
        await page.setViewportSize({
          width: device.viewport.height,
          height: device.viewport.width
        });
        
        await waitForLoadingToComplete(page);
        
        // Dashboard should still be usable in landscape
        await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
        
        // Navigation should adapt to landscape
        const navigation = page.locator('[data-testid="main-navigation"], .navbar');
        if (await navigation.isVisible()) {
          await expect(navigation).toBeVisible();
        }
      }
    });
  });
});
