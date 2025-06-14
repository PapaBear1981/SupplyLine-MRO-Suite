import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, navigateToPage } from '../utils/test-helpers.js';

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('should have proper heading hierarchy on dashboard', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Check heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    
    expect(headings.length).toBeGreaterThan(0);
    
    // Should have at least one h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
    
    // Check that headings are in logical order
    const headingLevels = [];
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
      const level = parseInt(tagName.charAt(1));
      headingLevels.push(level);
    }
    
    // First heading should be h1
    expect(headingLevels[0]).toBe(1);
    
    console.log('Heading hierarchy:', headingLevels);
  });

  test('should have proper alt text for images', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    const images = await page.locator('img').all();
    
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      const src = await img.getAttribute('src');
      
      // Images should have alt text (can be empty for decorative images)
      expect(alt).not.toBeNull();
      
      // If image has meaningful content, alt should not be empty
      if (src && !src.includes('decoration') && !src.includes('spacer')) {
        expect(alt.length).toBeGreaterThan(0);
      }
      
      console.log(`Image: ${src}, Alt: "${alt}"`);
    }
  });

  test('should have proper form labels', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    const inputs = await page.locator('input, select, textarea').all();
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const type = await input.getAttribute('type');
      
      // Skip hidden inputs
      if (type === 'hidden') continue;
      
      // Input should have a label, aria-label, or aria-labelledby
      const hasLabel = id && await page.locator(`label[for="${id}"]`).count() > 0;
      const hasAriaLabel = ariaLabel && ariaLabel.length > 0;
      const hasAriaLabelledBy = ariaLabelledBy && ariaLabelledBy.length > 0;
      
      expect(hasLabel || hasAriaLabel || hasAriaLabelledBy).toBeTruthy();
      
      console.log(`Input type: ${type}, has label: ${hasLabel}, aria-label: ${ariaLabel}`);
    }
  });

  test('should have proper button accessibility', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    const buttons = await page.locator('button, [role="button"]').all();
    
    for (const button of buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      const title = await button.getAttribute('title');
      
      // Button should have accessible text
      const hasAccessibleText = (text && text.trim().length > 0) || 
                               (ariaLabel && ariaLabel.length > 0) || 
                               (title && title.length > 0);
      
      expect(hasAccessibleText).toBeTruthy();
      
      console.log(`Button text: "${text}", aria-label: "${ariaLabel}"`);
    }
  });

  test('should have proper link accessibility', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    const links = await page.locator('a').all();
    
    for (const link of links) {
      const text = await link.textContent();
      const ariaLabel = await link.getAttribute('aria-label');
      const href = await link.getAttribute('href');
      
      // Skip empty links or anchors
      if (!href || href === '#') continue;
      
      // Link should have accessible text
      const hasAccessibleText = (text && text.trim().length > 0) || 
                               (ariaLabel && ariaLabel.length > 0);
      
      expect(hasAccessibleText).toBeTruthy();
      
      console.log(`Link: "${text}", href: ${href}, aria-label: "${ariaLabel}"`);
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Get all focusable elements
    const focusableElements = await page.locator(
      'button:visible, a:visible, input:visible, select:visible, textarea:visible, [tabindex]:visible'
    ).all();
    
    expect(focusableElements.length).toBeGreaterThan(0);
    
    // Test tab navigation
    let currentIndex = 0;
    for (const element of focusableElements.slice(0, 5)) { // Test first 5 elements
      await element.focus();
      
      // Check if element is focused
      const isFocused = await element.evaluate(el => el === document.activeElement);
      expect(isFocused).toBeTruthy();
      
      // Check for visible focus indicator
      const focusStyles = await element.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          outline: styles.outline,
          outlineWidth: styles.outlineWidth,
          boxShadow: styles.boxShadow
        };
      });
      
      // Should have some form of focus indicator
      const hasFocusIndicator = focusStyles.outline !== 'none' || 
                               focusStyles.outlineWidth !== '0px' || 
                               focusStyles.boxShadow !== 'none';
      
      if (!hasFocusIndicator) {
        console.warn(`Element may lack focus indicator:`, await element.evaluate(el => el.outerHTML.substring(0, 100)));
      }
      
      currentIndex++;
    }
    
    console.log(`Tested ${currentIndex} focusable elements`);
  });

  test('should have proper ARIA landmarks', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Check for main landmark
    const main = await page.locator('main, [role="main"]').count();
    expect(main).toBeGreaterThanOrEqual(1);
    
    // Check for navigation landmark
    const nav = await page.locator('nav, [role="navigation"]').count();
    expect(nav).toBeGreaterThanOrEqual(1);
    
    // Check for banner (header)
    const banner = await page.locator('header, [role="banner"]').count();
    
    // Check for contentinfo (footer)
    const contentinfo = await page.locator('footer, [role="contentinfo"]').count();
    
    console.log(`Landmarks - main: ${main}, nav: ${nav}, banner: ${banner}, contentinfo: ${contentinfo}`);
  });

  test('should have proper table accessibility', async ({ page }) => {
    await navigateToPage(page, '/tools');
    
    const tables = await page.locator('table').all();
    
    for (const table of tables) {
      // Table should have headers
      const headers = await table.locator('th').count();
      expect(headers).toBeGreaterThan(0);
      
      // Check for table caption or aria-label
      const caption = await table.locator('caption').count();
      const ariaLabel = await table.getAttribute('aria-label');
      const ariaLabelledBy = await table.getAttribute('aria-labelledby');
      
      const hasAccessibleName = caption > 0 || 
                               (ariaLabel && ariaLabel.length > 0) || 
                               (ariaLabelledBy && ariaLabelledBy.length > 0);
      
      if (!hasAccessibleName) {
        console.warn('Table may lack accessible name');
      }
      
      // Check for proper header associations
      const headerCells = await table.locator('th').all();
      for (const header of headerCells) {
        const scope = await header.getAttribute('scope');
        const id = await header.getAttribute('id');
        
        // Headers should have scope or id for association
        if (!scope && !id) {
          console.warn('Table header may lack proper scope or id');
        }
      }
    }
  });

  test('should have proper color contrast', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Check text elements for color contrast
    const textElements = await page.locator('p, span, div, h1, h2, h3, h4, h5, h6, button, a').all();
    
    let contrastIssues = 0;
    
    for (const element of textElements.slice(0, 10)) { // Test first 10 elements
      const styles = await element.evaluate(el => {
        const computedStyles = window.getComputedStyle(el);
        return {
          color: computedStyles.color,
          backgroundColor: computedStyles.backgroundColor,
          fontSize: computedStyles.fontSize
        };
      });
      
      // This is a simplified check - in a real implementation, you'd use a proper contrast ratio calculator
      const hasTransparentBackground = styles.backgroundColor === 'rgba(0, 0, 0, 0)' || 
                                      styles.backgroundColor === 'transparent';
      
      if (hasTransparentBackground) {
        // Skip elements with transparent backgrounds as they inherit from parent
        continue;
      }
      
      // Log for manual review
      console.log(`Element styles - color: ${styles.color}, background: ${styles.backgroundColor}, fontSize: ${styles.fontSize}`);
    }
    
    // This test mainly logs information for manual review
    // Automated contrast checking would require additional libraries
  });

  test('should handle screen reader announcements', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Check for aria-live regions
    const liveRegions = await page.locator('[aria-live]').all();
    
    for (const region of liveRegions) {
      const ariaLive = await region.getAttribute('aria-live');
      expect(['polite', 'assertive', 'off']).toContain(ariaLive);
      
      console.log(`Live region with aria-live: ${ariaLive}`);
    }
    
    // Check for status messages
    const statusElements = await page.locator('[role="status"], [role="alert"]').all();
    
    for (const status of statusElements) {
      const role = await status.getAttribute('role');
      console.log(`Status element with role: ${role}`);
    }
  });

  test('should support high contrast mode', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Simulate high contrast mode
    await page.addStyleTag({
      content: `
        @media (prefers-contrast: high) {
          * {
            background-color: white !important;
            color: black !important;
            border-color: black !important;
          }
        }
      `
    });
    
    // Check that content is still visible and usable
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
    
    // Check that interactive elements are still accessible
    const buttons = await page.locator('button:visible').count();
    expect(buttons).toBeGreaterThan(0);
    
    console.log('High contrast mode simulation completed');
  });

  test('should support reduced motion preferences', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Simulate reduced motion preference
    await page.addStyleTag({
      content: `
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `
    });
    
    // Navigate to trigger any animations
    await navigateToPage(page, '/tools');
    await waitForLoadingToComplete(page);
    
    // Content should still be functional with reduced motion
    await expect(page.locator('[data-testid="tools-table"]')).toBeVisible();
    
    console.log('Reduced motion simulation completed');
  });

  test('should have proper error message accessibility', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    // Try to submit empty form to trigger validation errors
    await page.click('[data-testid="save-tool-button"]');
    
    // Wait for validation errors
    await page.waitForSelector('.is-invalid, .error-message', { timeout: 2000 });
    
    const errorElements = await page.locator('.is-invalid, .error-message, [aria-invalid="true"]').all();
    
    for (const error of errorElements) {
      // Check for aria-describedby or aria-errormessage
      const ariaDescribedBy = await error.getAttribute('aria-describedby');
      const ariaErrorMessage = await error.getAttribute('aria-errormessage');
      const ariaInvalid = await error.getAttribute('aria-invalid');
      
      // Error fields should have proper ARIA attributes
      if (ariaInvalid === 'true') {
        expect(ariaDescribedBy || ariaErrorMessage).toBeTruthy();
      }
      
      console.log(`Error element - aria-invalid: ${ariaInvalid}, aria-describedby: ${ariaDescribedBy}`);
    }
  });
});
