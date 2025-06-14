# SupplyLine MRO Suite - E2E Testing Guide

## Quick Start

### Prerequisites
1. **Node.js** (v18 or higher)
2. **Python** (v3.10 or higher) 
3. **Backend server** running on `http://localhost:5000`
4. **Frontend server** running on `http://localhost:5173` (dev) or `http://localhost:4173` (preview)

### Installation
```bash
cd frontend
npm install
npx playwright install
```

### Environment Configuration

Create a `.env.local` file in the frontend directory (copy from `.env.example`):

```bash
# Application URLs
PLAYWRIGHT_BASE_URL=http://localhost:5173
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:5000

# Test Credentials (use environment-specific values)
E2E_ADMIN_EMPLOYEE_NUMBER=ADMIN001
E2E_ADMIN_PASSWORD=admin123
E2E_USER_EMPLOYEE_NUMBER=USER001
E2E_USER_PASSWORD=user123

# Test Configuration
E2E_TIMEOUT=30000
E2E_RETRY_COUNT=2
E2E_PARALLEL_WORKERS=1
```

### Security Considerations

⚠️ **IMPORTANT SECURITY PRACTICES:**

- **Never commit real credentials** to version control
- Use environment variables for all sensitive data
- Use test-specific user accounts, not production accounts
- Regularly rotate test credentials
- Ensure test databases are isolated from production
- Review `.env.local` files are in `.gitignore`

### Running Tests

#### Basic Commands
```bash
# Run all tests
npm run test:e2e

# Run with UI (interactive mode)
npm run test:e2e:ui

# Run in debug mode
npm run test:e2e:debug

# Run with visible browser
npm run test:e2e:headed
```

#### Specific Test Categories
```bash
# Authentication tests
npm run test:e2e:auth

# Tool management tests
npm run test:e2e:tools

# Chemical management tests
npm run test:e2e:chemicals

# Dashboard tests
npm run test:e2e:dashboard

# Mobile responsiveness tests
npm run test:e2e:mobile

# Performance tests
npm run test:e2e:performance

# Visual regression tests
npm run test:e2e:visual

# Accessibility tests
npm run test:e2e:accessibility
```

#### Browser-Specific Tests
```bash
# Chrome only
npm run test:e2e:chrome

# Firefox only
npm run test:e2e:firefox

# Safari only
npm run test:e2e:safari

# Smoke tests (quick validation)
npm run test:e2e:smoke

# Regression tests (Chrome + Firefox)
npm run test:e2e:regression
```

#### Using the Test Runner Script
```bash
# Run all tests with automatic server setup
./run-e2e-tests.sh

# Run specific browser
./run-e2e-tests.sh --browser chrome

# Run in UI mode
./run-e2e-tests.sh --ui

# Run specific test file
./run-e2e-tests.sh --test auth/login.spec.js
```

## Test Structure

### Test Categories

1. **Authentication (`auth/`)**
   - Login/logout functionality
   - Protected route access
   - Session management
   - Role-based permissions

2. **Dashboard (`dashboard/`)**
   - User dashboard widgets
   - Admin dashboard features
   - Quick actions and navigation
   - Real-time data display

3. **Tool Management (`tools/`)**
   - CRUD operations
   - Search and filtering
   - Checkout/return workflows
   - Tool status management

4. **Chemical Management (`chemicals/`)**
   - Inventory management
   - Issue/return processes
   - Expiration tracking
   - Reorder workflows

5. **Cycle Count (`cycle-count/`)**
   - Schedule creation
   - Batch processing
   - Mobile counting interface
   - Discrepancy resolution

6. **Calibration (`calibration/`)**
   - Tool calibration workflows
   - Calibration scheduling
   - Notification systems

7. **Mobile Responsiveness (`mobile/`)**
   - Cross-device testing
   - Touch interactions
   - Mobile navigation
   - Responsive layouts

8. **Visual Regression (`visual/`)**
   - Screenshot comparison
   - UI consistency checks
   - Layout validation

9. **Performance (`performance/`)**
   - Page load times
   - API response times
   - Memory usage
   - Network efficiency

10. **Accessibility (`accessibility/`)**
    - WCAG compliance
    - Keyboard navigation
    - Screen reader support
    - Color contrast

11. **Integration (`integration/`)**
    - End-to-end workflows
    - Cross-feature testing
    - Error scenarios

### Helper Functions

#### Authentication Helpers (`utils/auth-helpers.js`)
- `loginAsAdmin(page)` - Login as admin user
- `loginAsUser(page, employeeNumber, password)` - Login as specific user
- `logout(page)` - Logout current user
- `isAuthenticated(page)` - Check authentication status

#### Test Helpers (`utils/test-helpers.js`)
- `waitForLoadingToComplete(page)` - Wait for loading spinners
- `waitForToast(page, message, type)` - Wait for notifications
- `fillField(page, testId, value)` - Fill form fields
- `clickButton(page, testId)` - Click buttons
- `waitForTableToLoad(page, testId)` - Wait for data tables

#### Advanced Helpers (`utils/advanced-helpers.js`)
- `mockApiResponse(page, endpoint, data)` - Mock API responses
- `simulateNetworkConditions(page, conditions)` - Network simulation
- `measurePagePerformance(page)` - Performance metrics
- `generateTestData(type)` - Generate test data

### Test Configuration (`test-config.js`)

Contains centralized configuration for:
- Test timeouts and thresholds
- User credentials
- API endpoints
- Test selectors
- Performance benchmarks

## Best Practices

### Writing Tests
1. **Use data-testid attributes** for reliable element selection
2. **Wait for elements** before interacting with them
3. **Handle loading states** with appropriate waits
4. **Use helper functions** for common operations
5. **Clean up test data** in teardown when necessary
6. **Test error scenarios** as well as happy paths
7. **Keep tests independent** - each test should work in isolation

### Test Data Management
- Use unique test data prefixes (E2E_TOOL_, E2E_CHEM_, etc.)
- Generate dynamic test data to avoid conflicts
- Clean up test data after test completion
- Use fixtures for consistent test data

### Performance Considerations
- Set appropriate timeouts for different operations
- Use network idle waits for dynamic content
- Monitor test execution times
- Optimize slow tests

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

## Maintenance

### Regular Tasks
- Update test data when application features change
- Add new helper functions for common operations
- Keep browser versions updated
- Review and update CI/CD configuration
- Monitor test execution times and optimize slow tests

### Adding New Tests
1. Create test file in appropriate directory
2. Import required helpers and fixtures
3. Use descriptive test names and organize with `describe` blocks
4. Add necessary data-testid attributes to frontend components
5. Update this guide if adding new test categories

## Troubleshooting

### Installation Issues
```bash
# Reinstall Playwright browsers
npx playwright install --force

# Clear npm cache
npm cache clean --force
npm install
```

### Test Failures
```bash
# Run specific failing test
npx playwright test auth/login.spec.js --debug

# Run with verbose output
npx playwright test --reporter=list

# Generate trace for debugging
npx playwright test --trace=on
```

### Performance Issues
```bash
# Run performance tests only
npm run test:e2e:performance

# Check network requests
npx playwright test --reporter=json > results.json
```

For additional help, check the [Playwright documentation](https://playwright.dev/docs/intro) or the test implementation files for examples.
