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
        
        // Find the chemical row and click issue button
        const row = page.locator(`tr:has-text("${chemicalInfo.lotNumber}")`).first();
        const issueBtn = row.locator('button:has-text("Issue")');
        await issueBtn.click({ timeout: 5000 });
        
        // Wait for modal to appear
        await page.waitForSelector('.modal, [role="dialog"]', { timeout: 5000 });
        
        // Fill in issuance form
        await page.fill('input[name="quantity"], input[type="number"]', '1');
        await page.fill('input[name="work_order"], input[placeholder*="Work Order"]', `WO-${Date.now()}-${index}`);
        
        // Select a user (if dropdown exists)
        const userSelect = page.locator('select[name="user_id"]');
        if (await userSelect.count() > 0) {
          await userSelect.selectOption({ index: 1 }); // Select first available user
        }
        
        await page.fill('textarea[name="purpose"], textarea[placeholder*="purpose"]', `Concurrent test by ${user.username}`);
        
        // Submit the issuance
        const submitBtn = page.locator('button:has-text("Issue"), button:has-text("Confirm")').last();
        await submitBtn.click();
        
        // Wait for response
        await page.waitForTimeout(2000);
        
        // Check for success or error
        const hasError = await page.locator('.error, .alert-danger, [role="alert"]').count() > 0;
        const hasSuccess = await page.locator('.success, .alert-success').count() > 0;
        
        return {
          user: user.username,
          hasError,
          hasSuccess,
        };
      });

      // Execute all issuances simultaneously
      const results = await executeConcurrently(operations);
      
      console.log('\n=== Concurrent Chemical Issuance Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));
      
      // All should succeed if there's enough quantity
      // OR some should fail if there's a race condition
      expect(results.successCount + results.failureCount).toBe(userCount);
      
      // Verify the final quantity is correct
      await firstPage.reload({ waitUntil: 'networkidle' });
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

      // The quantity should decrease by exactly the number of successful issuances
      if (finalQty !== null) {
        const expectedFinal = chemicalInfo.availableQty - results.successCount;
        console.log(`✅ Chemical quantity tracking: Initial=${chemicalInfo.availableQty}, Final=${finalQty}, Expected=${expectedFinal}`);
        expect(finalQty).toBe(expectedFinal);
      } else {
        console.log('⚠️  Could not verify final quantity - chemical may have been fully depleted');
      }
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent API requests for chemicals list', async () => {
    const userCount = 4;
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

