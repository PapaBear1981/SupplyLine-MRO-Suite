import { test, expect } from '@playwright/test';

test.describe('Debug Tests', () => {
  test('debug page content after login', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Login
    await page.fill('input[placeholder="Employee Number"]', 'USER001');
    await page.fill('input[placeholder="Password"]', 'user123');
    await page.click('button[type="submit"]');
    
    // Wait for redirect
    await expect(page).toHaveURL('/');
    
    // Wait a moment for the page to fully load
    await page.waitForTimeout(2000);
    
    // Take a screenshot
    await page.screenshot({ path: 'debug-after-login.png', fullPage: true });
    
    // Log all buttons on the page
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons on the page:`);
    
    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      const text = await button.textContent();
      const classes = await button.getAttribute('class');
      console.log(`Button ${i}: "${text}" - classes: "${classes}"`);
    }
    
    // Log all elements with user name
    const userElements = await page.locator('*:has-text("John Engineer")').all();
    console.log(`Found ${userElements.length} elements with "John Engineer":`);
    
    for (let i = 0; i < userElements.length; i++) {
      const element = userElements[i];
      const tagName = await element.evaluate(el => el.tagName);
      const text = await element.textContent();
      const classes = await element.getAttribute('class');
      console.log(`Element ${i}: <${tagName}> "${text}" - classes: "${classes}"`);
    }
  });
});
