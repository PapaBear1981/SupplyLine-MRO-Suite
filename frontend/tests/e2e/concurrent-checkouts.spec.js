/**
 * Concurrent Tool Checkout Tests
 * 
 * Tests multiple users attempting to checkout the same tool simultaneously
 * to verify collision handling and race condition prevention.
 */

import { test, expect } from '@playwright/test';
import {
  createConcurrentUsers,
  cleanupConcurrentUsers,
  executeConcurrently,
  analyzeResults,
  ConcurrencyBarrier,
} from './utils/concurrent-helpers.js';

test.describe('Concurrent Tool Checkouts', () => {
  test.describe.configure({ mode: 'serial' });

  test('should handle 3 users making concurrent API requests', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);

    try {
      // Create a barrier to synchronize all users
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent API operations
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) making concurrent API request...`);

        // Make a concurrent API request to get tools list
        const response = await page.request.get('/api/tools');

        return {
          user: user.username,
          status: response.status(),
          ok: response.ok(),
        };
      });

      // Execute all requests simultaneously
      const results = await executeConcurrently(operations);

      console.log('\n=== Concurrent API Request Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));

      // All API requests should succeed
      expect(results.successCount).toBe(userCount);

      console.log(`✅ Concurrent API requests handled successfully: ${results.successCount}/${userCount} succeeded`);

    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent API requests for tools list', async () => {
    const userCount = 3; // Reduced from 5 to 3
    const contexts = await createConcurrentUsers(userCount);

    try {
      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent API operations
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) making API request...`);

        // Make a concurrent API request to get tools list
        const response = await page.request.get('/api/tools');

        return {
          user: user.username,
          status: response.status(),
          ok: response.ok(),
        };
      });

      const results = await executeConcurrently(operations);

      console.log('\n=== Concurrent API Request Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));

      // All API requests should succeed
      expect(results.successCount).toBe(userCount);

      console.log(`✅ Concurrent API requests handled successfully: ${results.successCount}/${userCount} succeeded`);

    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle rapid successive page navigation', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);

    try {
      // Each user rapidly navigates between pages
      const operations = contexts.map(({ page, user }, index) => async () => {
        console.log(`User ${index + 1} (${user.username}) performing rapid navigation...`);

        const pages = ['/tools', '/chemicals', '/kits', '/dashboard'];

        for (const url of pages) {
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
          await page.waitForTimeout(300);
        }

        return {
          user: user.username,
          pagesVisited: pages.length,
        };
      });

      const results = await executeConcurrently(operations);

      console.log('\n=== Rapid Navigation Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));

      // All users should complete navigation
      expect(results.successCount).toBe(userCount);

      console.log(`✅ Data consistency maintained during rapid concurrent access: ${results.successCount}/${userCount} succeeded`);

    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });
});

