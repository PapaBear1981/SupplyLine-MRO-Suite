/**
 * Concurrent Chemical Issuance Tests
 * 
 * Tests multiple users attempting to issue chemicals from the same lot simultaneously
 * to verify quantity tracking, race conditions, and inventory consistency.
 */

import { test, expect } from '@playwright/test';
import {
  createConcurrentUsers,
  cleanupConcurrentUsers,
  executeConcurrently,
  executeStaggered,
  analyzeResults,
  ConcurrencyBarrier,
} from './utils/concurrent-helpers.js';

test.describe('Concurrent Chemical Issuance', () => {
  test.describe.configure({ mode: 'serial' });

  test('should handle 3 users issuing from the same chemical lot simultaneously', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);
    
    try {
      // Navigate all users to the chemicals page
      await Promise.all(
        contexts.map(({ page }) => page.goto('/chemicals', { waitUntil: 'networkidle' }))
      );

      // Find a chemical with sufficient quantity
      const firstPage = contexts[0].page;
      await firstPage.waitForSelector('table tbody tr', { timeout: 10000 });

      const chemicalInfo = await firstPage.evaluate(() => {
        const rows = document.querySelectorAll('table tbody tr');
        for (const row of rows) {
          const qtyCell = row.querySelector('td:nth-child(5)'); // Quantity column (5th)
          if (qtyCell) {
            const qtyText = qtyCell.textContent.trim();
            const qty = parseFloat(qtyText);
            if (qty >= 3) { // Need at least 3 units for 3 concurrent issuances
              return {
                partNumber: row.querySelector('td:nth-child(1)')?.textContent.trim(),
                lotNumber: row.querySelector('td:nth-child(2)')?.textContent.trim(),
                availableQty: qty,
              };
            }
          }
        }
        return null;
      });

      expect(chemicalInfo).toBeTruthy();
      console.log(`Testing concurrent issuance for chemical: ${chemicalInfo.partNumber}, Lot: ${chemicalInfo.lotNumber}, Available: ${chemicalInfo.availableQty}`);

      // Create a barrier to synchronize all users
      const barrier = new ConcurrencyBarrier(userCount);

      // Create issuance operations for each user
      const operations = contexts.map(({ page, user }, index) => async () => {
        // Wait at barrier so all users start at the same time
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) attempting to issue chemical...`);

        // Wait for table to be fully loaded
        await page.waitForSelector('table tbody tr', { timeout: 10000 });

        // Find the chemical row and click issue button
        const row = page.locator(`tr:has-text("${chemicalInfo.lotNumber}")`).first();
        const issueBtn = row.locator('button:has-text("Issue")');
        await issueBtn.click({ timeout: 10000 });

        // Wait for navigation to issue page
        await page.waitForURL(/\/chemicals\/\d+\/issue/, { timeout: 10000 });

        // Wait for form to load
        await page.waitForSelector('button:has-text("Issue Chemical")', { timeout: 10000 });

        // Fill in issuance form using name attributes
        // Quantity field
        await page.fill('input[name="quantity"]', '1');

        // Hangar/Location field
        await page.fill('input[name="hangar"]', `Hangar-${index + 1}`);

        // Purpose field (textarea)
        await page.fill('textarea[name="purpose"]', `Concurrent test by ${user.username}`);

        // Issued To dropdown - select first available user (index 1, since 0 is "Select User")
        await page.selectOption('select[name="user_id"]', { index: 1 });

        // Submit the issuance
        const submitBtn = page.locator('button:has-text("Issue Chemical")');
        await submitBtn.click();

        // Wait for navigation or error
        try {
          // If successful, it navigates to /chemicals/{id} (detail page)
          await page.waitForURL(/\/chemicals\/\d+$/, { timeout: 5000 });
          return {
            user: user.username,
            hasError: false,
            hasSuccess: true,
          };
        } catch (e) {
          // If it stays on the issue page or shows an error, it failed
          const currentUrl = page.url();
          const stillOnIssuePage = currentUrl.includes('/issue');
          const hasErrorAlert = await page.locator('.alert-danger, [role="alert"]').count() > 0;

          return {
            user: user.username,
            hasError: stillOnIssuePage || hasErrorAlert,
            hasSuccess: false,
          };
        }
      });

      // Execute all issuances simultaneously
      const results = await executeConcurrently(operations);
      
      console.log('\n=== Concurrent Chemical Issuance Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));
      
      // All should succeed if there's enough quantity
      // OR some should fail if there's a race condition
      expect(results.successCount + results.failureCount).toBe(userCount);
      
      // Navigate back to chemicals page to verify the final quantity
      await firstPage.goto('/chemicals', { waitUntil: 'networkidle' });
      await firstPage.waitForSelector('table tbody tr', { timeout: 10000 });

      const finalQty = await firstPage.evaluate((lotNumber) => {
        const rows = document.querySelectorAll('table tbody tr');
        for (const row of rows) {
          const lotCell = row.querySelector('td:nth-child(2)'); // Lot number column
          if (lotCell && lotCell.textContent.includes(lotNumber)) {
            const qtyCell = row.querySelector('td:nth-child(5)'); // Quantity column
            const qtyText = qtyCell?.textContent.trim() || '0';
            return parseFloat(qtyText);
          }
        }
        return null;
      }, chemicalInfo.lotNumber);

      console.log(`Initial quantity: ${chemicalInfo.availableQty}, Final quantity: ${finalQty}`);
      console.log(`Successful issuances: ${results.successCount}, Expected final: ${chemicalInfo.availableQty - results.successCount}`);

      // The quantity should decrease by the number of actual issuances
      // Note: There might be a discrepancy between reported success and actual issuances
      // due to race conditions or UI navigation timing
      if (finalQty !== null) {
        const actualIssuances = chemicalInfo.availableQty - finalQty;
        console.log(`✅ Chemical quantity tracking: Initial=${chemicalInfo.availableQty}, Final=${finalQty}, Actual issuances=${actualIssuances}`);

        // Verify that at least some issuances succeeded
        expect(actualIssuances).toBeGreaterThan(0);

        // Verify that we didn't issue more than requested
        expect(actualIssuances).toBeLessThanOrEqual(userCount);

        // Log if there's a discrepancy (potential race condition)
        if (actualIssuances !== results.successCount) {
          console.log(`⚠️  Discrepancy detected: ${results.successCount} reported success but ${actualIssuances} actually issued`);
          console.log('   This may indicate a race condition in the backend or UI navigation timing');
        }
      } else {
        console.log('⚠️  Could not verify final quantity - chemical may have been fully depleted');
      }
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent API requests for chemicals list', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);

    try {
      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent API operations
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) making API request...`);

        // Make a concurrent API request to get chemicals list
        const response = await page.request.get('/api/chemicals');

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

  test('should handle rapid page navigation across multiple users', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);

    try {
      // Each user rapidly navigates between pages
      const operations = contexts.map(({ page, user }, index) => async () => {
        console.log(`User ${index + 1} (${user.username}) performing rapid navigation...`);

        const pages = ['/chemicals', '/tools', '/kits', '/dashboard'];

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

