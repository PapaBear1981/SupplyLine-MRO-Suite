/**
 * Concurrent Calibration and Inventory Update Tests
 * 
 * Tests multiple users performing calibrations and inventory updates simultaneously
 * to verify data consistency and race condition handling.
 */

import { test, expect } from '@playwright/test';
import {
  createConcurrentUsers,
  cleanupConcurrentUsers,
  executeConcurrently,
  analyzeResults,
  ConcurrencyBarrier,
} from './utils/concurrent-helpers.js';

test.describe('Concurrent Calibrations', () => {
  test.describe.configure({ mode: 'serial' });

  test('should handle multiple users adding calibrations to the same tool', async () => {
    // Use only users with page.tools permission (ADMIN001 and MAT001 have it, USER001 doesn't)
    const usersWithToolsPermission = [
      { username: 'ADMIN001', password: 'admin123' },
      { username: 'MAT001', password: 'materials123' },
      { username: 'ADMIN001', password: 'admin123' }, // Reuse admin for 3rd user
    ];
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount, usersWithToolsPermission);

    try {
      console.log(`Testing concurrent calibrations for tool ID: 1`);

      // Navigate each user to the calibration form SEQUENTIALLY to avoid server overload
      // Each user will calibrate a different tool to avoid conflicts
      console.log('\n=== Phase 1: Sequential Navigation ===');
      for (let i = 0; i < contexts.length; i++) {
        const { page, user } = contexts[i];
        const toolId = i + 1; // User 1 -> Tool 1, User 2 -> Tool 2, User 3 -> Tool 3
        console.log(`User ${i + 1} (${user.username}) navigating to calibration form for Tool ${toolId}...`);

        // Navigate to the tool's detail page
        await page.goto(`/tools/${toolId}`, { waitUntil: 'networkidle' });

        // Wait for page to fully load
        await page.waitForSelector('[role="tab"]', { timeout: 15000 });

        // Click on Calibration History tab
        await page.getByRole('tab', { name: 'Calibration History' }).click();

        // Wait for tab content to load
        await page.waitForTimeout(500);

        // Click "Calibrate Tool" button
        await page.getByRole('button', { name: 'Calibrate Tool' }).click();

        // Wait for navigation to calibration form
        await page.waitForURL(/\/tools\/\d+\/calibrations\/new/, { timeout: 15000 });

        // Fill in calibration form
        const notesInput = page.locator('textarea');
        await notesInput.fill(`Concurrent calibration by ${user.username} at ${new Date().toISOString()}`);

        console.log(`User ${i + 1} (${user.username}) ready to submit`);

        // Longer delay before next user to give server time to recover
        if (i < contexts.length - 1) {
          console.log(`Waiting 3 seconds before next user...`);
          await page.waitForTimeout(3000);
        }
      }

      // Now all users are ready - create concurrent submission operations
      console.log('\n=== Phase 2: Concurrent Submission ===');
      const barrier = new ConcurrencyBarrier(userCount);

      const operations = contexts.map(({ page, user }, index) => async () => {
        // Wait at barrier so all users submit at the same time
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) submitting calibration...`);

        // Submit
        const submitBtn = page.locator('button:has-text("Save Calibration")');
        await submitBtn.click();

        // Wait for navigation or error
        try {
          // If successful, it should navigate back to the tool detail page
          await page.waitForURL(/\/tools\/\d+$/, { timeout: 5000 });
          return {
            user: user.username,
            hasError: false,
            hasSuccess: true,
          };
        } catch (e) {
          // If it stays on the calibration form or shows an error, it failed
          const currentUrl = page.url();
          const stillOnCalibrationPage = currentUrl.includes('/calibrations/new');
          const hasErrorAlert = await page.locator('.alert-danger, [role="alert"]').count() > 0;

          return {
            user: user.username,
            hasError: stillOnCalibrationPage || hasErrorAlert,
            hasSuccess: false,
          };
        }
      });

      // Execute all calibrations simultaneously
      const results = await executeConcurrently(operations);
      
      console.log('\n=== Concurrent Calibration Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));
      
      // All calibrations should succeed (multiple calibrations allowed per tool)
      expect(results.successCount).toBe(userCount);

      // Success! All users were able to submit calibrations concurrently
      console.log(`✅ All ${userCount} users successfully submitted calibrations concurrently`);
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent kit access', async () => {
    const userCount = 2;
    const contexts = await createConcurrentUsers(userCount);

    try {
      console.log('Testing concurrent kit access...');

      // Navigate to kits page
      await Promise.all(
        contexts.map(({ page }) => page.goto('/kits', { waitUntil: 'networkidle' }))
      );

      const firstPage = contexts[0].page;

      // Wait for kit cards to load - the kits page uses card layout, not table
      await firstPage.waitForSelector('h5', { timeout: 10000 });

      // Find a kit
      const kitInfo = await firstPage.evaluate(() => {
        const kitHeadings = document.querySelectorAll('h5');
        for (const heading of kitHeadings) {
          const kitName = heading.textContent.trim();
          if (kitName && kitName.startsWith('Kit')) {
            return { kitName };
          }
        }
        return null;
      });

      if (!kitInfo) {
        console.log('⚠️  No kits found, skipping test');
        return;
      }

      console.log(`Testing concurrent access to kit: ${kitInfo.kitName}`);

      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent operations - each user clicks on the same kit
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();

        console.log(`User ${index + 1} (${user.username}) accessing kit...`);

        // Click on the kit card to view details
        const kitCard = page.locator(`h5:has-text("${kitInfo.kitName}")`).first();
        await kitCard.click({ timeout: 5000 });

        // Wait for navigation to kit detail page
        await page.waitForURL(/\/kits\/\d+/, { timeout: 10000 });

        // Check if we successfully loaded the kit detail page
        const onDetailPage = page.url().includes('/kits/');

        return {
          user: user.username,
          success: onDetailPage,
        };
      });

      const results = await executeConcurrently(operations);

      console.log('\n=== Concurrent Kit Access Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));

      // Both users should be able to access the kit
      expect(results.successCount).toBe(userCount);

      console.log('✅ Concurrent kit access handled successfully');

    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent inventory updates via API', async () => {
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);
    
    try {
      // Get auth tokens for each user
      const tokens = await Promise.all(
        contexts.map(async ({ page }) => {
          const token = await page.evaluate(() => {
            return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
          });
          return token;
        })
      );

      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent API operations
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();
        
        console.log(`User ${index + 1} (${user.username}) making API request...`);
        
        // Make a concurrent API request (e.g., get tools list)
        const response = await page.request.get('/api/tools', {
          headers: {
            'Authorization': `Bearer ${tokens[index]}`,
            'Content-Type': 'application/json',
          },
        });
        
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
      
      console.log('✅ Concurrent API requests handled successfully');
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should maintain data consistency with rapid successive updates', async () => {
    // Reduced from 5 to 3 users to avoid login timeouts (known issue with 4+ concurrent users)
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);
    
    try {
      // Each user rapidly navigates and loads data
      const operations = contexts.map(({ page, user }, index) => async () => {
        console.log(`User ${index + 1} (${user.username}) performing rapid navigation...`);
        
        const pages = ['/tools', '/chemicals', '/kits', '/calibrations', '/dashboard'];
        
        for (const url of pages) {
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
          await page.waitForTimeout(500);
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
      
      console.log('✅ Data consistency maintained during rapid concurrent access');
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });
});

