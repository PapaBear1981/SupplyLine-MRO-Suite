# E2E Test Setup Guide

This guide explains how to set up and run E2E tests for the SupplyLine MRO Suite.

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (v3.9 or higher)
3. **Playwright** browsers installed
4. **Backend server** running on `http://localhost:5000`
5. **Frontend dev server** running on `http://localhost:5173`

## Initial Setup

### 1. Install Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install Playwright browsers
npx playwright install
```

### 2. Seed Test Data

Before running E2E tests, you need to seed the database with test data:

```bash
# From the project root
cd backend
python seed_e2e_test_data.py
```

This script creates:
- **Test Users**:
  - `ADMIN001` / `admin123` (Admin user)
  - `USER001` / `user123` (Regular user)
  - `MAT001` / `materials123` (Materials department user)
  - `MAINT001` / `password123` (Maintenance user)
  - `ENG001` / `password123` (Engineering user)
- **Test Tools**: 5 tools with various statuses
- **Test Chemicals**: 2 chemicals
- **Test Kits**: 2 kits for different aircraft types
- **Test Checkouts**: 1 active checkout

### 3. Verify Backend Endpoints

Verify that all required API endpoints are responding:

```bash
# From the backend directory
python verify_e2e_endpoints.py
```

This script tests:
- Authentication endpoints (`/api/auth/login`, `/api/auth/me`, `/api/auth/logout`)
- Tools endpoints (`/api/tools`, `/api/tools/new`)
- Checkouts endpoints (`/api/checkouts`, `/api/checkouts/user`)
- Kits endpoints (`/api/kits`, `/api/kits/aircraft-types`)
- Dashboard endpoints (`/api/user/activity`)
- Admin endpoints (`/api/admin/dashboard/stats`)

## Running E2E Tests

### Run All Tests

```bash
# From the frontend directory
npx playwright test
```

### Run Tests in UI Mode (Recommended for Development)

```bash
npx playwright test --ui
```

### Run Specific Test File

```bash
npx playwright test tests/e2e/auth.spec.js
npx playwright test tests/e2e/dashboard.spec.js
npx playwright test tests/e2e/tools.spec.js
```

### Run Tests in Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Run Tests in Headed Mode (See Browser)

```bash
npx playwright test --headed
```

### Debug Tests

```bash
npx playwright test --debug
```

## Test Configuration

### Playwright Configuration

The Playwright configuration is in `frontend/playwright.config.js`:

- **Timeout**: 90 seconds per test
- **Action Timeout**: 60 seconds for actions
- **Navigation Timeout**: 60 seconds for page loads
- **Expect Timeout**: 10 seconds for assertions
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Retries**: 2 retries on CI, 0 locally
- **Parallel Execution**: Enabled (except on CI)

### Environment Variables

Test environment variables are in `frontend/.env.test`:

- `VITE_API_URL`: Backend API URL
- `VITE_TEST_MODE`: Enable test mode
- `VITE_ENABLE_CORS`: Enable CORS for test requests
- `VITE_LOG_LEVEL`: Logging level for tests

## Test Structure

### Test Files

- `auth.spec.js`: Authentication tests (login, logout, session management)
- `dashboard.spec.js`: Dashboard tests (quick actions, recent activity, user checkouts)
- `navigation.spec.js`: Navigation tests (menu, breadcrumbs, mobile menu)
- `tools.spec.js`: Tools tests (list, search, filter, checkout)
- `kits.spec.js`: Kits tests (list, create, edit, transfer)
- `kit-operations.spec.js`: Kit operations tests (issuance, transfer, reorder)
- `security.spec.js`: Security tests (CSRF, XSS, authentication)
- `debug.spec.js`: Debug tests (temporary tests for debugging)

### Test Utilities

- `tests/e2e/utils/auth.js`: Authentication helpers
  - `login(page, userType)`: Login as a specific user type
  - `logout(page)`: Logout current user
  - `setupAuthenticatedState(page, userType)`: Setup authenticated state
  - `clearAuthState(page)`: Clear authentication state

### Test Users

```javascript
export const TEST_USERS = {
  admin: { username: 'ADMIN001', password: 'admin123' },
  user: { username: 'USER001', password: 'user123' },
  materials: { username: 'MAT001', password: 'materials123' }
};
```

**Note**: The admin password was updated from `password123` to `admin123` to match the seeding script.

## Data-TestID Attributes

All components have `data-testid` attributes for reliable test selectors:

### Dashboard Components
- `data-testid="dashboard-content"`: Main dashboard container
- `data-testid="quick-actions"`: Quick actions card
- `data-testid="recent-activity"`: Recent activity card
- `data-testid="user-checkout-status"`: User checkout status card
- `data-testid="announcements"`: Announcements card

### Navigation Components
- `data-testid="user-menu"`: User menu button
- `data-testid="mobile-menu-toggle"`: Mobile menu toggle button
- `data-testid="mobile-menu"`: Mobile menu container

### Tools Components
- `data-testid="tools-list"`: Tools list container
- `data-testid="tool-item"`: Individual tool row
- `data-testid="status-filter"`: Status filter dropdown
- `data-testid="category-filter"`: Category filter dropdown

## Troubleshooting

### Tests Failing Due to Timeout

If tests are failing due to timeout:
1. Increase timeout in `playwright.config.js`
2. Check if backend is running and responding
3. Check if frontend dev server is running
4. Use `page.waitForLoadState('networkidle')` instead of `page.waitForTimeout()`

### Tests Failing Due to Authentication

If tests are failing due to authentication:
1. Verify test data is seeded: `python backend/seed_e2e_test_data.py`
2. Check test user credentials in `tests/e2e/utils/auth.js`
3. Verify backend authentication endpoints are working
4. Clear browser storage: `await context.clearCookies()`

### Tests Failing Due to Missing Elements

If tests are failing due to missing elements:
1. Verify `data-testid` attributes are present in components
2. Use Playwright Inspector to debug: `npx playwright test --debug`
3. Check if element is visible: `await expect(element).toBeVisible()`
4. Wait for element to appear: `await page.waitForSelector('[data-testid="element"]')`

### Database State Issues

If tests are failing due to database state:
1. Reset database: `python backend/seed_e2e_test_data.py`
2. Ensure tests are isolated and don't depend on each other
3. Use `beforeEach` hooks to reset state
4. Avoid hardcoding IDs or timestamps

## Best Practices

1. **Use data-testid attributes** instead of CSS selectors or text content
2. **Wait for network idle** instead of arbitrary timeouts
3. **Isolate tests** - each test should be independent
4. **Reset database** before test runs to ensure clean state
5. **Use meaningful test names** that describe what is being tested
6. **Group related tests** using `describe` blocks
7. **Use page objects** for complex pages to reduce duplication
8. **Take screenshots** on failure for debugging
9. **Use Playwright Inspector** for debugging failing tests
10. **Run tests in UI mode** during development for better visibility

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
npm ci
npx playwright install --with-deps

# Seed test data
python backend/seed_e2e_test_data.py

# Run tests
npx playwright test --reporter=html,json,junit

# Upload test results
# (configure based on your CI platform)
```

## Reporting

Test reports are generated in:
- **HTML Report**: `playwright-report/index.html`
- **JSON Report**: `test-results/results.json`
- **JUnit Report**: `test-results/results.xml`

View HTML report:
```bash
npx playwright show-report
```

## Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Playwright Test Fixtures](https://playwright.dev/docs/test-fixtures)

