# Kit Component Testing Setup Guide

## Overview

This guide provides instructions for setting up and running component tests for the Kit Management system using Vitest and React Testing Library.

## Prerequisites

The following dependencies need to be installed:

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/ui
```

## Configuration

### 1. Update `package.json`

Add the following test scripts:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### 2. Create `vitest.config.js`

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    css: true,
  },
});
```

### 3. Create Test Setup File

Create `src/tests/setup.js`:

```javascript
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

## Test Structure

Tests are organized in `frontend/tests/kits/` directory:

```
frontend/tests/kits/
├── TESTING_SETUP_GUIDE.md (this file)
├── KitWizard.test.jsx
├── KitItemsList.test.jsx
├── KitIssuanceForm.test.jsx
├── KitTransferForm.test.jsx
├── KitMessaging.test.jsx
├── KitAlerts.test.jsx
└── helpers/
    └── testUtils.jsx
```

## Test Utilities

### Mock Redux Store

Create `frontend/tests/kits/helpers/testUtils.jsx`:

```javascript
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';

// Import your reducers
import kitsReducer from '../../../src/store/kitsSlice';
import authReducer from '../../../src/store/authSlice';

export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    store = configureStore({
      reducer: {
        kits: kitsReducer,
        auth: authReducer,
      },
      preloadedState,
    }),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </Provider>
    );
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

export * from '@testing-library/react';
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test KitWizard.test.jsx
```

## Test Coverage Goals

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **User Interaction Tests**: Test form submissions, button clicks, etc.
- **API Integration**: Mock API calls and test responses
- **Validation**: Test form validation and error handling

## Best Practices

1. **Arrange-Act-Assert Pattern**: Structure tests clearly
2. **User-Centric Testing**: Test from user's perspective
3. **Avoid Implementation Details**: Test behavior, not implementation
4. **Mock External Dependencies**: Mock API calls, Redux store, etc.
5. **Descriptive Test Names**: Use clear, descriptive test names
6. **Test Edge Cases**: Include error states, loading states, empty states

## Example Test Structure

```javascript
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './helpers/testUtils';
import KitWizard from '../../src/components/kits/KitWizard';

describe('KitWizard', () => {
  it('renders the wizard with step 1', () => {
    renderWithProviders(<KitWizard />);
    expect(screen.getByText(/aircraft type/i)).toBeInTheDocument();
  });

  it('advances to step 2 when aircraft type is selected', async () => {
    const user = userEvent.setup();
    renderWithProviders(<KitWizard />);
    
    const selectButton = screen.getByRole('button', { name: /select/i });
    await user.click(selectButton);
    
    await waitFor(() => {
      expect(screen.getByText(/kit details/i)).toBeInTheDocument();
    });
  });
});
```

## Common Testing Scenarios

### 1. Form Validation
- Test required field validation
- Test format validation (e.g., part numbers)
- Test error message display

### 2. User Interactions
- Button clicks
- Form submissions
- Dropdown selections
- Modal open/close

### 3. API Integration
- Mock successful API responses
- Mock error responses
- Test loading states
- Test error handling

### 4. Redux State
- Test component behavior with different state
- Test dispatched actions
- Test state updates

### 5. Conditional Rendering
- Test different user roles (admin vs. regular user)
- Test empty states
- Test loading states
- Test error states

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure all dependencies are installed
2. **Redux store errors**: Verify store configuration in test utils
3. **Router errors**: Wrap components in BrowserRouter
4. **Async test failures**: Use `waitFor` for async operations
5. **CSS import errors**: Configure Vitest to handle CSS

### Debug Tips

```javascript
// Use screen.debug() to see current DOM
screen.debug();

// Use screen.logTestingPlaygroundURL() for query suggestions
screen.logTestingPlaygroundURL();

// Use prettyDOM for specific elements
import { prettyDOM } from '@testing-library/react';
console.log(prettyDOM(element));
```

## Next Steps

1. Install required dependencies
2. Configure Vitest
3. Create test setup file
4. Create test utilities
5. Write component tests
6. Run tests and verify coverage
7. Integrate into CI/CD pipeline

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [User Event API](https://testing-library.com/docs/user-event/intro)

