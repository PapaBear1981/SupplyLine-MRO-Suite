/**
 * Vitest Test Setup
 * 
 * Global test configuration and setup for all tests
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock scrollTo
window.scrollTo = vi.fn();

// Suppress console errors in tests (optional)
// Uncomment if you want to suppress expected errors
// const originalError = console.error;
// beforeAll(() => {
//   console.error = (...args) => {
//     if (
//       typeof args[0] === 'string' &&
//       args[0].includes('Warning: ReactDOM.render')
//     ) {
//       return;
//     }
//     originalError.call(console, ...args);
//   };
// });
//
// afterAll(() => {
//   console.error = originalError;
// });

