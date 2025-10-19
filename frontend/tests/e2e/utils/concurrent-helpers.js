/**
 * Concurrent Testing Utilities
 * 
 * Helpers for simulating multiple users performing operations simultaneously
 * to test race conditions, collision handling, and concurrent access patterns.
 */

import { chromium } from '@playwright/test';
import { login, TEST_USERS } from './auth.js';

/**
 * Create multiple authenticated browser contexts
 * @param {number} count - Number of contexts to create
 * @param {Array<{username: string, password: string}>} users - Array of user credentials
 * @returns {Promise<Array<{browser: Browser, context: BrowserContext, page: Page, user: Object}>>}
 */
export async function createConcurrentUsers(count, users = null) {
  const contexts = [];

  // If no users provided, create variations of test users
  const userList = users || [
    TEST_USERS.admin,
    TEST_USERS.user,
    TEST_USERS.materials,
    // Add more test users as needed
    { username: 'MAINT001', password: 'user123' },
    { username: 'ENG001', password: 'user123' },
  ];

  // Create users sequentially with delays to avoid overwhelming the server
  for (let i = 0; i < count; i++) {
    console.log(`Creating user ${i + 1}/${count}...`);

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      baseURL: 'http://localhost:5173',
    });
    const page = await context.newPage();

    // Login with the user
    const user = userList[i % userList.length];
    await login(page, user, { navigateToDashboard: true });

    contexts.push({ browser, context, page, user });

    // Add a small delay between creating users to avoid overwhelming the server
    if (i < count - 1) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }

  console.log(`✅ Created ${count} concurrent users successfully`);
  return contexts;
}

/**
 * Clean up all browser contexts
 * @param {Array<{browser: Browser, context: BrowserContext, page: Page}>} contexts
 */
export async function cleanupConcurrentUsers(contexts) {
  for (const { browser, context, page } of contexts) {
    await page.close().catch(() => {});
    await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }
}

/**
 * Execute operations concurrently and collect results
 * @param {Array<Function>} operations - Array of async functions to execute
 * @returns {Promise<Array<{success: boolean, result: any, error: any, duration: number}>>}
 */
export async function executeConcurrently(operations) {
  const startTime = Date.now();
  
  const promises = operations.map(async (operation, index) => {
    const opStartTime = Date.now();
    try {
      const result = await operation();
      return {
        index,
        success: true,
        result,
        error: null,
        duration: Date.now() - opStartTime,
      };
    } catch (error) {
      return {
        index,
        success: false,
        result: null,
        error: error.message,
        duration: Date.now() - opStartTime,
      };
    }
  });
  
  const results = await Promise.all(promises);
  const totalDuration = Date.now() - startTime;
  
  return {
    results,
    totalDuration,
    successCount: results.filter(r => r.success).length,
    failureCount: results.filter(r => !r.success).length,
  };
}

/**
 * Execute operations with a staggered start (to simulate real-world timing)
 * @param {Array<Function>} operations - Array of async functions to execute
 * @param {number} staggerMs - Milliseconds to wait between starting each operation
 * @returns {Promise<Array<{success: boolean, result: any, error: any, duration: number}>>}
 */
export async function executeStaggered(operations, staggerMs = 100) {
  const results = [];
  const startTime = Date.now();
  
  const promises = operations.map(async (operation, index) => {
    // Wait for stagger delay
    await new Promise(resolve => setTimeout(resolve, index * staggerMs));
    
    const opStartTime = Date.now();
    try {
      const result = await operation();
      return {
        index,
        success: true,
        result,
        error: null,
        duration: Date.now() - opStartTime,
        startOffset: index * staggerMs,
      };
    } catch (error) {
      return {
        index,
        success: false,
        result: null,
        error: error.message,
        duration: Date.now() - opStartTime,
        startOffset: index * staggerMs,
      };
    }
  });
  
  const allResults = await Promise.all(promises);
  const totalDuration = Date.now() - startTime;
  
  return {
    results: allResults,
    totalDuration,
    successCount: allResults.filter(r => r.success).length,
    failureCount: allResults.filter(r => !r.success).length,
  };
}

/**
 * Wait for all pages to reach a specific URL pattern
 * @param {Array<Page>} pages - Array of Playwright pages
 * @param {RegExp|string} urlPattern - URL pattern to wait for
 * @param {number} timeout - Timeout in milliseconds
 */
export async function waitForAllPages(pages, urlPattern, timeout = 30000) {
  await Promise.all(
    pages.map(page => page.waitForURL(urlPattern, { timeout }))
  );
}

/**
 * Navigate all pages to the same URL simultaneously
 * @param {Array<Page>} pages - Array of Playwright pages
 * @param {string} url - URL to navigate to
 */
export async function navigateAllPages(pages, url) {
  await Promise.all(
    pages.map(page => page.goto(url, { waitUntil: 'networkidle' }))
  );
}

/**
 * Check if an API response indicates a conflict/collision
 * @param {Response} response - Fetch API response
 * @returns {boolean}
 */
export function isConflictResponse(response) {
  return response.status === 409 || response.status === 423;
}

/**
 * Check if an API response indicates success
 * @param {Response} response - Fetch API response
 * @returns {boolean}
 */
export function isSuccessResponse(response) {
  return response.status >= 200 && response.status < 300;
}

/**
 * Extract error message from response
 * @param {Response} response - Fetch API response
 * @returns {Promise<string>}
 */
export async function getErrorMessage(response) {
  try {
    const data = await response.json();
    return data.error || data.message || `HTTP ${response.status}`;
  } catch {
    return `HTTP ${response.status}`;
  }
}

/**
 * Analyze concurrent operation results for patterns
 * @param {Object} executionResults - Results from executeConcurrently or executeStaggered
 * @returns {Object} Analysis summary
 */
export function analyzeResults(executionResults) {
  const { results, totalDuration, successCount, failureCount } = executionResults;
  
  const errors = results
    .filter(r => !r.success)
    .map(r => r.error);
  
  const uniqueErrors = [...new Set(errors)];
  
  const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
  const maxDuration = Math.max(...results.map(r => r.duration));
  const minDuration = Math.min(...results.map(r => r.duration));
  
  return {
    totalOperations: results.length,
    successCount,
    failureCount,
    successRate: (successCount / results.length * 100).toFixed(2) + '%',
    totalDuration,
    avgDuration: avgDuration.toFixed(2),
    maxDuration,
    minDuration,
    uniqueErrors,
    errorBreakdown: uniqueErrors.map(error => ({
      error,
      count: errors.filter(e => e === error).length,
    })),
  };
}

/**
 * Create a barrier that waits for all participants to reach it
 * Useful for synchronizing concurrent operations
 */
export class ConcurrencyBarrier {
  constructor(participantCount) {
    this.participantCount = participantCount;
    this.arrivedCount = 0;
    this.resolvers = [];
  }

  async wait() {
    this.arrivedCount++;
    
    if (this.arrivedCount === this.participantCount) {
      // All participants have arrived, release them all
      this.resolvers.forEach(resolve => resolve());
      this.resolvers = [];
      this.arrivedCount = 0;
    } else {
      // Wait for other participants
      await new Promise(resolve => {
        this.resolvers.push(resolve);
      });
    }
  }

  reset() {
    this.arrivedCount = 0;
    this.resolvers = [];
  }
}

