# E2E Tests for SupplyLine MRO Suite

Comprehensive end-to-end tests using Playwright for the SupplyLine MRO Suite application.

## Overview

This directory contains E2E tests that verify the complete user workflows across the application, including authentication, navigation, kit management, and various operations.

## Test Files

### Core Tests

1. **auth.spec.js** - Authentication and authorization tests
   - Login/logout functionality
   - Session management
   - Password validation
   - Remember me functionality

2. **navigation.spec.js** - Navigation and routing tests
   - Menu navigation
   - Protected routes
   - Breadcrumbs
   - Back/forward navigation

3. **dashboard.spec.js** - Dashboard functionality tests
   - Widget display
   - Data loading
   - Quick actions
   - Statistics

4. **security.spec.js** - Security-related tests
   - XSS protection
   - CSRF protection
   - Input sanitization
   - Authorization checks

5. **tools.spec.js** - Tool management tests
   - Tool listing
   - Tool creation
   - Tool checkout/checkin
   - Tool search and filtering

6. **checkouts.spec.js** - Checkout workflows and access control
   - My vs. all checkouts views
   - Role-based permissions and redirects
   - Return tool modal interactions
   - Tool detail navigation from checkout tables

### Kit Management Tests

7. **kits.spec.js** - Kit management core functionality
   - Kit listing and filtering
   - Kit creation wizard (4 steps)
   - Kit detail view
   - Kit tabs navigation
   - Kit reports
   - Mobile interface

8. **kit-operations.spec.js** - Kit operations and workflows
   - Kit transfers
   - Kit reorder requests
   - Kit item issuance
   - Kit alerts
   - Issuance history

## Test Utilities

### Authentication Utilities (`utils/auth.js`)

```javascript
import { login, logout, TEST_USERS } from './utils/auth.js';

// Login as admin
await login(page, TEST_USERS.admin);

// Login as regular user
await login(page, TEST_USERS.user);

// Login as materials department user
await login(page, TEST_USERS.materials);

// Logout
await logout(page);
```

### Kit Helper Functions (`utils/kit-helpers.js`)

```javascript
import {
  navigateToFirstKit,
  createKit,
  navigateToKitTab,
  searchKits,
  issueKitItem,
  createReorderRequest,
  transferKit
} from './utils/kit-helpers.js';

// Navigate to first available kit
await navigateToFirstKit(page);

// Create a new kit
await createKit(page, {
  aircraftType: 'Q400',
  name: 'Test Kit',
  description: 'Test description'
});

// Navigate to a specific tab
await navigateToKitTab(page, 'Items');

// Search for kits
await searchKits(page, 'Q400');

// Issue an item
await issueKitItem(page, {
  quantity: 1,
  purpose: 'Maintenance',
  workOrder: 'WO-12345'
});

// Create reorder request
await createReorderRequest(page, {
  partNumber: 'PART-001',
  description: 'Test part',
  quantity: 5,
  priority: 'high'
});

// Transfer kit
await transferKit(page, {
  destination: 'Hangar 2',
  notes: 'Transfer for maintenance'
});
```

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Install Playwright browsers:**
   ```bash
   npx playwright install
   ```

3. **Start the development servers:**
   - Backend: `python backend/run.py`
   - Frontend: `npm run dev` (in frontend directory)
   
   Or use the convenience script:
   ```bash
   ./start_dev_servers.sh
   ```

### Run All Tests

```bash
# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug
```

### Run Specific Test Files

```bash
# Run only kit tests
npx playwright test kits.spec.js

# Run only kit operations tests
npx playwright test kit-operations.spec.js

# Run only authentication tests
npx playwright test auth.spec.js
```

### Run Specific Tests

```bash
# Run tests matching a pattern
npx playwright test -g "should display kits management page"

# Run tests in a specific describe block
npx playwright test -g "Kit Creation Wizard"
```

### Run on Specific Browsers

```bash
# Run on Chromium only
npx playwright test --project=chromium

# Run on Firefox only
npx playwright test --project=firefox

# Run on WebKit (Safari) only
npx playwright test --project=webkit

# Run on mobile Chrome
npx playwright test --project="Mobile Chrome"
```

### Generate Test Report

```bash
# Run tests and generate HTML report
npx playwright test --reporter=html

# Show report
npx playwright show-report
```

### Update Snapshots

```bash
# Update all snapshots
npx playwright test --update-snapshots

# Update snapshots for specific test
npx playwright test kits.spec.js --update-snapshots
```

## Test Configuration

The Playwright configuration is in `playwright.config.js`:

- **Base URL**: `http://localhost:5173` (Vite dev server)
- **Timeout**: 30 seconds per test
- **Retries**: 2 on CI, 0 locally
- **Screenshots**: On failure
- **Videos**: On failure
- **Trace**: On first retry

### Environment Variables

You can override settings with environment variables:

```bash
# Run in CI mode (more retries, parallel disabled)
CI=true npx playwright test

# Change base URL
BASE_URL=http://localhost:3000 npx playwright test
```

## Writing New Tests

### Basic Test Structure

```javascript
import { test, expect } from '@playwright/test';
import { login, TEST_USERS } from './utils/auth.js';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup - runs before each test
    await login(page, TEST_USERS.admin);
  });

  test('should do something', async ({ page }) => {
    // Navigate
    await page.goto('/some-page');
    
    // Interact
    await page.click('button:has-text("Click Me")');
    
    // Assert
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

### Best Practices

1. **Use semantic selectors:**
   ```javascript
   // Good
   await page.click('button:has-text("Submit")');
   await page.locator('[aria-label="Close"]').click();
   
   // Avoid
   await page.click('.btn-primary');
   await page.click('#submit-btn');
   ```

2. **Wait for elements properly:**
   ```javascript
   // Wait for element to be visible
   await expect(page.locator('text=Success')).toBeVisible();
   
   // Wait for navigation
   await page.waitForURL('/dashboard');
   
   // Wait for network idle
   await page.waitForLoadState('networkidle');
   ```

3. **Use test data from utilities:**
   ```javascript
   import { TEST_USERS } from './utils/auth.js';
   
   await login(page, TEST_USERS.admin);
   ```

4. **Clean up after tests:**
   ```javascript
   test.afterEach(async ({ page }) => {
    // Cleanup code
     await logout(page);
   });
   ```

5. **Handle dynamic content:**
   ```javascript
   // Wait for data to load
   await page.waitForTimeout(1000);
   
   // Check if elements exist before interacting
   const count = await page.locator('.kit-card').count();
   if (count > 0) {
     await page.locator('.kit-card').first().click();
   }
   ```

## Debugging Tests

### Visual Debugging

```bash
# Run with headed browser
npx playwright test --headed

# Run in debug mode (step through)
npx playwright test --debug

# Run specific test in debug mode
npx playwright test kits.spec.js:42 --debug
```

### Trace Viewer

```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

### Screenshots and Videos

Failed tests automatically capture:
- Screenshots (in `test-results/`)
- Videos (in `test-results/`)
- Traces (on retry)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run tests
        run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Troubleshooting

### Tests Timing Out

- Increase timeout in `playwright.config.js`
- Add explicit waits: `await page.waitForTimeout(1000)`
- Check if backend is running

### Elements Not Found

- Use `await page.pause()` to inspect page
- Check selector with `await page.locator('selector').count()`
- Verify element is visible: `await expect(element).toBeVisible()`

### Flaky Tests

- Add proper waits instead of `waitForTimeout`
- Use `waitForLoadState('networkidle')`
- Increase retries in config
- Check for race conditions

### Authentication Issues

- Verify backend is running
- Check test user credentials in `utils/auth.js`
- Clear browser storage: `await page.context().clearCookies()`

## Coverage

Current test coverage:

- ✅ Authentication (login, logout, session)
- ✅ Kit listing and filtering
- ✅ Kit creation wizard (all 4 steps)
- ✅ Kit detail view (all tabs)
- ✅ Kit transfers
- ✅ Kit reorder requests
- ✅ Kit item issuance
- ✅ Kit reports
- ✅ Mobile interface
- ✅ Navigation
- ✅ Dashboard
- ✅ Security
- ✅ Tools management

## Contributing

When adding new tests:

1. Follow existing patterns
2. Use helper functions from `utils/`
3. Add descriptive test names
4. Include comments for complex logic
5. Update this README if adding new test files
6. Ensure tests pass locally before committing

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)

