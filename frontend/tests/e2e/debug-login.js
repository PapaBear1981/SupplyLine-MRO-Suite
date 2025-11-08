import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--disable-dev-shm-usage',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-web-security',
    ]
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture console messages and errors
  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type()}]:`, msg.text());
  });

  page.on('pageerror', error => {
    console.error('[BROWSER ERROR]:', error.message);
    console.error('[BROWSER ERROR STACK]:', error.stack);
  });

  console.log('Navigating to http://localhost:5173/login...');

  try {
    await page.goto('http://localhost:5173/login', { timeout: 30000, waitUntil: 'domcontentloaded' });
    console.log('✓ Navigation successful');
    console.log('✓ Current URL:', page.url());

    // Get HTML content immediately
    const html = await page.content();
    console.log('✓ Got page HTML (length:', html.length, ')');

    // Get page title
    const title = await page.title();
    console.log('✓ Page title:', title);

    // Wait a bit for JS to execute
    await page.waitForTimeout(1500);
    console.log('✓ Waited for page to render');

    // Try to get body text
    try {
      const bodyText = await page.locator('body').textContent({ timeout: 500 });
      console.log('Body text preview:', bodyText.substring(0, 200));
    } catch (e) {
      console.log('Could not get body text:', e.message);
    }

    // Check for login form elements
    const employeeInput = await page.locator('input[placeholder="Enter your employee number"]').count();
    const passwordInput = await page.locator('input[placeholder="Enter your password"]').count();
    const submitButton = await page.locator('button[type="submit"]').count();

    console.log('Employee input found:', employeeInput);
    console.log('Password input found:', passwordInput);
    console.log('Submit button found:', submitButton);

    // Take a screenshot
    await page.screenshot({ path: '/tmp/login-page.png', fullPage: true });
    console.log('✓ Screenshot saved to /tmp/login-page.png');

  } catch (error) {
    console.error('✗ Error:', error.message);
  } finally {
    await browser.close();
  }
})();
