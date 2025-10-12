# Kit Component Tests

Comprehensive test suite for the Kit Management system components.

## Overview

This directory contains unit and integration tests for all kit-related React components using Vitest and React Testing Library.

## Test Files

### Component Tests

1. **KitWizard.test.jsx** - Tests for the 4-step kit creation wizard
   - Aircraft type selection
   - Kit details validation
   - Box configuration
   - Wizard navigation and completion

2. **KitItemsList.test.jsx** - Tests for kit items display and filtering
   - Item rendering
   - Box filtering
   - Status filtering
   - Item actions (issue, transfer)

3. **KitIssuanceForm.test.jsx** - Tests for item issuance form
   - Form validation
   - Quantity validation
   - Purpose and work order fields
   - Submission handling

4. **KitTransferForm.test.jsx** - Tests for item transfer form
   - Destination selection (kit/warehouse)
   - Transfer validation
   - Form submission
   - Error handling

5. **KitMessaging.test.jsx** - Tests for kit messaging interface
   - Message display
   - New message creation
   - Message replies
   - Read/unread status
   - Message filtering

6. **KitAlerts.test.jsx** - Tests for kit alerts display
   - Low stock alerts
   - Out of stock alerts
   - Pending reorder alerts
   - Alert severity levels
   - Alert dismissal

### Helper Files

- **helpers/testUtils.jsx** - Shared test utilities
  - Redux store setup
  - Router setup
  - Mock data
  - API mocking helpers

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/ui
```

### 2. Verify Configuration

Ensure the following files exist:
- `frontend/vitest.config.js` - Vitest configuration
- `frontend/src/tests/setup.js` - Test setup file
- `frontend/package.json` - Updated with test scripts

### 3. Update package.json

Add these scripts to `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:run": "vitest run"
  }
}
```

## Running Tests

### Run All Tests

```bash
npm test
```

### Run Tests in Watch Mode

```bash
npm test -- --watch
```

### Run Tests with UI

```bash
npm run test:ui
```

### Run Tests with Coverage

```bash
npm run test:coverage
```

### Run Specific Test File

```bash
npm test KitWizard.test.jsx
```

### Run Tests Matching Pattern

```bash
npm test -- --grep "validation"
```

## Test Coverage

Current test coverage includes:

### KitWizard (26 tests)
- ✅ Step 1: Aircraft type selection
- ✅ Step 2: Kit details validation
- ✅ Step 3: Box configuration
- ✅ Step 4: Kit creation
- ✅ Navigation (next/back)
- ✅ Form validation

### KitItemsList (15 tests)
- ✅ Item rendering
- ✅ Box filtering
- ✅ Status filtering
- ✅ Type filtering
- ✅ Filter clearing
- ✅ Item actions

### KitIssuanceForm (12 tests)
- ✅ Form rendering
- ✅ Quantity validation
- ✅ Purpose validation
- ✅ Available quantity check
- ✅ Form submission
- ✅ Error handling

### KitTransferForm (14 tests)
- ✅ Destination selection
- ✅ Kit-to-kit transfers
- ✅ Kit-to-warehouse transfers
- ✅ Quantity validation
- ✅ Form submission
- ✅ Error handling

### KitMessaging (18 tests)
- ✅ Message display
- ✅ New message creation
- ✅ Message replies
- ✅ Read/unread status
- ✅ Message filtering
- ✅ Unread count

### KitAlerts (16 tests)
- ✅ Alert display
- ✅ Severity levels
- ✅ Alert dismissal
- ✅ Alert filtering
- ✅ Navigation to items
- ✅ Empty states

**Total: 101 tests**

## Writing New Tests

### Test Structure

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockAuthState } from './helpers/testUtils';
import YourComponent from '../../src/components/kits/YourComponent';

describe('YourComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders component', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          // your state
        },
      };

      renderWithProviders(<YourComponent />, { preloadedState });

      expect(screen.getByText(/expected text/i)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('handles button click', async () => {
      const user = userEvent.setup();
      // ... setup

      const button = screen.getByRole('button', { name: /click me/i });
      await user.click(button);

      await waitFor(() => {
        expect(/* assertion */).toBeTruthy();
      });
    });
  });
});
```

### Best Practices

1. **Use Descriptive Test Names**
   ```javascript
   it('validates required quantity field')
   it('submits form with valid data')
   it('displays error when API call fails')
   ```

2. **Test User Behavior, Not Implementation**
   ```javascript
   // Good
   const button = screen.getByRole('button', { name: /submit/i });
   
   // Avoid
   const button = container.querySelector('.submit-btn');
   ```

3. **Use waitFor for Async Operations**
   ```javascript
   await waitFor(() => {
     expect(screen.getByText(/success/i)).toBeInTheDocument();
   });
   ```

4. **Mock External Dependencies**
   ```javascript
   vi.mock('../../src/store/kitsSlice', () => ({
     fetchKits: vi.fn(),
   }));
   ```

5. **Clean Up After Tests**
   ```javascript
   beforeEach(() => {
     vi.clearAllMocks();
   });
   ```

## Common Queries

### Finding Elements

```javascript
// By role (preferred)
screen.getByRole('button', { name: /submit/i })
screen.getByRole('textbox', { name: /email/i })

// By label
screen.getByLabelText(/username/i)

// By text
screen.getByText(/welcome/i)

// By placeholder
screen.getByPlaceholderText(/enter email/i)

// By test ID (last resort)
screen.getByTestId('custom-element')
```

### User Interactions

```javascript
const user = userEvent.setup();

// Click
await user.click(button);

// Type
await user.type(input, 'text to type');

// Select option
await user.selectOptions(select, 'option-value');

// Clear input
await user.clear(input);
```

## Debugging Tests

### View Current DOM

```javascript
screen.debug();
```

### View Specific Element

```javascript
import { prettyDOM } from '@testing-library/react';
console.log(prettyDOM(element));
```

### Get Query Suggestions

```javascript
screen.logTestingPlaygroundURL();
```

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:
- Pull requests
- Commits to main branch
- Pre-deployment

## Troubleshooting

### Tests Failing Locally

1. Clear node_modules and reinstall
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vitest cache
   ```bash
   npm test -- --clearCache
   ```

### Mock Not Working

Ensure mocks are defined before imports:
```javascript
vi.mock('../../src/store/kitsSlice', () => ({
  // mock implementation
}));

import Component from '../../src/components/Component';
```

### Async Test Timeouts

Increase timeout for slow operations:
```javascript
it('slow test', async () => {
  // test code
}, 10000); // 10 second timeout
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [User Event API](https://testing-library.com/docs/user-event/intro)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)

## Contributing

When adding new components:
1. Create corresponding test file
2. Follow existing test patterns
3. Aim for >80% code coverage
4. Test happy paths and error cases
5. Update this README with new test counts

