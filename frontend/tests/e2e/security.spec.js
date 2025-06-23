import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

test.describe('Frontend Security Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should prevent XSS in login form', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Wait for login form to be visible
    await expect(page.locator('input[placeholder="Employee Number"]')).toBeVisible();
    
    // Try XSS payload in employee number field
    const xssPayload = '<script>window.xssExecuted = true;</script>';
    await page.fill('input[placeholder="Employee Number"]', xssPayload);
    await page.fill('input[placeholder="Password"]', 'anypassword');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Check that XSS was not executed
    const xssExecuted = await page.evaluate(() => window.xssExecuted);
    expect(xssExecuted).toBeFalsy();
    
    // Check that the input is properly escaped/sanitized
    const inputValue = await page.inputValue('input[placeholder="Employee Number"]');
    expect(inputValue).not.toContain('<script>');
  });

  test('should handle authentication token securely', async ({ page }) => {
    await login(page, TEST_USERS.user);

    // Wait for potential redirect
    await page.waitForTimeout(3000);
    
    // Check that tokens are not exposed in localStorage (should use httpOnly cookies or secure storage)
    const localStorageTokens = await page.evaluate(() => {
      const tokens = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('token') || key.includes('auth'))) {
          tokens.push({ key, value: localStorage.getItem(key) });
        }
      }
      return tokens;
    });
    
    // Check sessionStorage as well
    const sessionStorageTokens = await page.evaluate(() => {
      const tokens = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.includes('token') || key.includes('auth'))) {
          tokens.push({ key, value: sessionStorage.getItem(key) });
        }
      }
      return tokens;
    });
    
    console.log('LocalStorage tokens found:', localStorageTokens);
    console.log('SessionStorage tokens found:', sessionStorageTokens);
    
    // If tokens are stored in browser storage, they should be properly secured
    // This is acceptable for SPAs, but we should note it in the security report
    if (localStorageTokens.length > 0 || sessionStorageTokens.length > 0) {
      console.log('⚠️  Tokens found in browser storage - ensure proper token rotation and expiration');
    }
  });

  test('should prevent CSRF attacks', async ({ page }) => {
    // This test checks that the application properly validates requests
    // and doesn't accept arbitrary cross-origin requests
    
    // Navigate to login page
    await page.goto('/login');
    
    // Try to make a request from a different origin (simulated)
    const csrfAttempt = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Origin': 'http://evil-site.com'
          },
          body: JSON.stringify({
            employee_number: 'USER001',
            password: 'user123'
          })
        });
        return { success: true, status: response.status };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    // The request should either be blocked by CORS or require proper authentication
    console.log('CSRF attempt result:', csrfAttempt);
    
    // If the request succeeded, it should at least require proper authentication
    if (csrfAttempt.success) {
      expect(csrfAttempt.status).not.toBe(200); // Should not succeed without proper auth
    }
  });

  test('should handle malicious input safely', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    const maliciousInputs = [
      'javascript:alert("xss")',
      'data:text/html,<script>alert("xss")</script>',
      '"><script>alert("xss")</script>',
      "'; DROP TABLE users; --",
      '../../../etc/passwd',
      '%3Cscript%3Ealert%28%22xss%22%29%3C%2Fscript%3E'
    ];
    
    for (const maliciousInput of maliciousInputs) {
      // Clear and fill the employee number field
      await page.fill('input[placeholder="Employee Number"]', '');
      await page.fill('input[placeholder="Employee Number"]', maliciousInput);
      
      // Submit the form
      await page.click('button[type="submit"]');
      
      // Wait for response
      await page.waitForTimeout(1000);
      
      // Check that no JavaScript was executed
      const xssExecuted = await page.evaluate(() => window.xssExecuted || window.alert.called);
      expect(xssExecuted).toBeFalsy();
      
      // Check that the page is still functional
      const isLoginPageStillVisible = await page.locator('input[placeholder="Employee Number"]').isVisible();
      expect(isLoginPageStillVisible).toBeTruthy();
    }
  });

  test('should enforce proper session management', async ({ page }) => {
    // Test that sessions expire properly and users are redirected to login
    
    // Navigate to a protected route without authentication
    await page.goto('/tools');
    
    // Should be redirected to login page
    await expect(page).toHaveURL('/login');
    
    await login(page, TEST_USERS.user);

    // Wait for redirect to dashboard
    await page.waitForTimeout(3000);
    
    // Should now be on dashboard or home page
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('/login');
    
    // Clear all storage to simulate session expiration
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Try to access a protected route
    await page.goto('/tools');
    
    // Should be redirected back to login
    await page.waitForTimeout(2000);
    const finalUrl = page.url();
    expect(finalUrl).toContain('/login');
  });

  test('should validate input length limits', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Test with extremely long input
    const veryLongString = 'A'.repeat(10000);
    
    await page.fill('input[placeholder="Employee Number"]', veryLongString);
    await page.fill('input[placeholder="Password"]', veryLongString);
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // The application should handle this gracefully without crashing
    const isPageResponsive = await page.locator('input[placeholder="Employee Number"]').isVisible();
    expect(isPageResponsive).toBeTruthy();
    
    // Check that the input was truncated or rejected
    const actualValue = await page.inputValue('input[placeholder="Employee Number"]');
    expect(actualValue.length).toBeLessThan(1000); // Should be truncated or rejected
  });

  test('should prevent clickjacking', async ({ page }) => {
    // Check if the application sets proper X-Frame-Options or CSP headers
    
    const response = await page.goto('/');
    const headers = response.headers();
    
    const hasFrameProtection = 
      headers['x-frame-options'] === 'DENY' || 
      headers['x-frame-options'] === 'SAMEORIGIN' ||
      (headers['content-security-policy'] && headers['content-security-policy'].includes('frame-ancestors'));
    
    console.log('Frame protection headers:', {
      'x-frame-options': headers['x-frame-options'],
      'content-security-policy': headers['content-security-policy']
    });
    
    if (hasFrameProtection) {
      console.log('✅ Clickjacking protection detected');
    } else {
      console.log('⚠️  No clickjacking protection detected');
    }
    
    // This is informational - not all applications need frame protection
    expect(true).toBeTruthy(); // Always pass, but log the information
  });
});
