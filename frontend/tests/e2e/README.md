# E2E Testing with Playwright

This directory contains end-to-end (E2E) tests for the SupplyLine MRO Suite application using Playwright.

## Overview

The E2E tests cover the complete user workflows and interactions across the entire application stack:
- Frontend React application
- Backend Flask API
- Database interactions
- Authentication and authorization
- Cross-browser compatibility

## Test Structure

```
tests/e2e/
├── auth/                    # Authentication tests
│   ├── login.spec.js
│   ├── logout.spec.js
│   └── protected-routes.spec.js
├── dashboard/               # Dashboard tests
│   └── user-dashboard.spec.js
├── tools/                   # Tool management tests
│   ├── tool-management.spec.js
│   └── tool-checkout.spec.js
├── chemicals/               # Chemical management tests
├── cycle-count/             # Cycle count tests
├── calibration/             # Calibration tests
├── fixtures/                # Test data and fixtures
│   └── test-data.js
├── utils/                   # Helper functions
│   ├── auth-helpers.js
│   └── test-helpers.js
├── global-setup.js          # Global test setup
├── global-teardown.js       # Global test cleanup
└── README.md               # This file
```

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (v3.10 or higher)
3. **Backend server** running on `http://localhost:5000`
4. **Frontend server** running on `http://localhost:5173` (dev) or `http://localhost:4173` (preview)

## Installation

1. Install Playwright and dependencies:
```bash
cd frontend
npm install
npx playwright install
```

2. Install browsers (if not already installed):
```bash
npx playwright install --with-deps
```

## Running Tests

### All Tests
```bash
npm run test:e2e
```

### Specific Test File
```bash
npx playwright test auth/login.spec.js
```

### Specific Browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Debug Mode
```bash
npm run test:e2e:debug
```

### Headed Mode (See Browser)
```bash
npm run test:e2e:headed
```

### UI Mode (Interactive)
```bash
npm run test:e2e:ui
```

## Test Configuration

The tests are configured in `playwright.config.js` with:
- Multiple browser support (Chromium, Firefox, WebKit)
- Mobile device testing
- Automatic server startup
- Screenshot and video capture on failure
- Trace collection for debugging

## Environment Variables

- `PLAYWRIGHT_BASE_URL`: Frontend URL (default: http://localhost:5173 for dev, http://localhost:4173 for preview)
- `CI`: Set to true in CI environments
- `RUN_PRODUCTION_TESTS`: Set to `true` to enable production environment tests

## Test Data

Test data is defined in `fixtures/test-data.js` and includes:
- Test users (admin, regular user, materials user)
- Test tools with various configurations
- Test chemicals and inventory items
- Test cycle count schedules
- API endpoints

## Helper Functions

### Authentication Helpers (`utils/auth-helpers.js`)
- `loginAsAdmin(page)`: Login as admin user
- `loginAsUser(page, employeeNumber, password)`: Login as specific user
- `logout(page)`: Logout current user
- `isAuthenticated(page)`: Check authentication status
- `isAdmin(page)`: Check admin status

### Test Helpers (`utils/test-helpers.js`)
- `waitForLoadingToComplete(page)`: Wait for loading spinners
- `waitForToast(page, message, type)`: Wait for toast notifications
- `fillField(page, testId, value)`: Fill form fields
- `clickButton(page, testId)`: Click buttons
- `waitForTableToLoad(page, testId)`: Wait for data tables
- `searchInTable(page, term, inputTestId)`: Search functionality
- `navigateToPage(page, path)`: Navigate and wait for load

## Data Test IDs

The tests rely on `data-testid` attributes in the frontend components. Key test IDs include:

### Authentication
- `employee-number-input`
- `password-input`
- `login-button`
- `logout-button`
- `user-menu`

### Navigation
- `main-navigation`
- `admin-dashboard-link`
- `tools-link`
- `checkouts-link`

### Forms
- `tool-form`
- `save-tool-button`
- `cancel-button`
- `delete-confirmation`

### Tables
- `tools-table`
- `checkouts-table`
- `search-input`
- `filter-select`

## Best Practices

1. **Use data-testid attributes** instead of CSS selectors when possible
2. **Wait for elements** before interacting with them
3. **Handle loading states** with appropriate waits
4. **Use helper functions** for common operations
5. **Clean up test data** in teardown when necessary
6. **Test error scenarios** as well as happy paths
7. **Keep tests independent** - each test should work in isolation

## Debugging Tests

### View Test Reports
```bash
npm run test:e2e:report
```

### Debug Failed Tests
1. Run in debug mode: `npm run test:e2e:debug`
2. Check screenshots in `test-results/`
3. View traces in Playwright trace viewer
4. Check console logs and network requests

### Common Issues

1. **Timing Issues**: Use proper waits instead of fixed timeouts
2. **Element Not Found**: Ensure data-testid attributes are present
3. **Authentication**: Verify test users exist in the database
4. **Server Not Running**: Ensure both frontend and backend are running

## CI/CD Integration

Tests run automatically in GitHub Actions on:
- Push to main/master/develop branches
- Pull requests
- Manual workflow dispatch

The CI workflow:
1. Sets up Node.js and Python environments
2. Installs dependencies
3. Starts backend and frontend servers
4. Runs tests across multiple browsers
5. Uploads test reports and artifacts

## Adding New Tests

1. Create test file in appropriate directory
2. Import required helpers and fixtures
3. Use descriptive test names and organize with `describe` blocks
4. Add necessary data-testid attributes to frontend components
5. Update this README if adding new test categories

## Maintenance

- Update test data when application features change
- Add new helper functions for common operations
- Keep browser versions updated
- Review and update CI/CD configuration as needed
- Monitor test execution times and optimize slow tests
