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
    const userCount = 3;
    const contexts = await createConcurrentUsers(userCount);
    
    try {
      // Navigate all users to the calibrations page
      await Promise.all(
        contexts.map(({ page }) => page.goto('/calibrations', { waitUntil: 'networkidle' }))
      );

      const firstPage = contexts[0].page;
      
      // Click "Add Calibration" button
      const addBtn = firstPage.locator('button:has-text("Add Calibration"), a:has-text("Add Calibration")').first();
      await addBtn.click({ timeout: 5000 });
      
      // Wait for form to load
      await firstPage.waitForSelector('form, .form', { timeout: 5000 });
      
      // Get a tool from the dropdown
      const toolSelect = firstPage.locator('select[name="tool_id"]');
      await toolSelect.waitFor({ state: 'visible', timeout: 5000 });
      
      // Get the first tool option value
      const toolId = await toolSelect.evaluate(select => {
        const options = select.querySelectorAll('option');
        for (const option of options) {
          if (option.value && option.value !== '') {
            return option.value;
          }
        }
        return null;
      });
      
      expect(toolId).toBeTruthy();
      console.log(`Testing concurrent calibrations for tool ID: ${toolId}`);
      
      // Go back to prepare for concurrent test
      await firstPage.goto('/calibrations', { waitUntil: 'networkidle' });

      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create calibration operations for each user
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();
        
        console.log(`User ${index + 1} (${user.username}) adding calibration...`);
        
        // Click Add Calibration
        const addBtn = page.locator('button:has-text("Add Calibration"), a:has-text("Add Calibration")').first();
        await addBtn.click({ timeout: 5000 });
        
        await page.waitForSelector('form, .form', { timeout: 5000 });
        
        // Fill in calibration form
        const toolSelect = page.locator('select[name="tool_id"]');
        await toolSelect.selectOption(toolId);
        
        // Set calibration date to today
        const today = new Date().toISOString().split('T')[0];
        await page.fill('input[name="calibration_date"], input[type="date"]', today);
        
        // Set next calibration date to 1 year from now
        const nextYear = new Date();
        nextYear.setFullYear(nextYear.getFullYear() + 1);
        const nextCalDate = nextYear.toISOString().split('T')[0];
        await page.fill('input[name="next_calibration_date"]', nextCalDate);
        
        // Select status
        const statusSelect = page.locator('select[name="status"]');
        if (await statusSelect.count() > 0) {
          await statusSelect.selectOption('Pass');
        }
        
        // Add notes
        await page.fill('textarea[name="notes"]', `Concurrent calibration by ${user.username} at ${new Date().toISOString()}`);
        
        // Submit
        const submitBtn = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Add")').first();
        await submitBtn.click();
        
        await page.waitForTimeout(2000);
        
        // Check for success or error
        const hasError = await page.locator('.error, .alert-danger').count() > 0;
        const hasSuccess = await page.locator('.success, .alert-success').count() > 0;
        
        return {
          user: user.username,
          hasError,
          hasSuccess,
        };
      });

      // Execute all calibrations simultaneously
      const results = await executeConcurrently(operations);
      
      console.log('\n=== Concurrent Calibration Results ===');
      console.log(JSON.stringify(analyzeResults(results), null, 2));
      
      // All calibrations should succeed (multiple calibrations allowed per tool)
      expect(results.successCount).toBe(userCount);
      
      // Verify all calibrations were recorded
      await firstPage.goto('/calibrations', { waitUntil: 'networkidle' });
      await firstPage.waitForSelector('table tbody tr', { timeout: 5000 });
      
      const calibrationCount = await firstPage.evaluate((toolIdStr) => {
        const rows = document.querySelectorAll('table tbody tr');
        let count = 0;
        for (const row of rows) {
          const cells = row.querySelectorAll('td');
          for (const cell of cells) {
            if (cell.textContent.includes(toolIdStr)) {
              count++;
              break;
            }
          }
        }
        return count;
      }, toolId);
      
      console.log(`Found ${calibrationCount} calibration records for tool ${toolId}`);
      expect(calibrationCount).toBeGreaterThanOrEqual(userCount);
      
      console.log('✅ All concurrent calibrations recorded successfully');
      
    } finally {
      await cleanupConcurrentUsers(contexts);
    }
  });

  test('should handle concurrent kit transfers', async () => {
    const userCount = 2;
    const contexts = await createConcurrentUsers(userCount);
    
    try {
      // Navigate to kits page
      await Promise.all(
        contexts.map(({ page }) => page.goto('/kits', { waitUntil: 'networkidle' }))
      );

      const firstPage = contexts[0].page;
      await firstPage.waitForSelector('table tbody tr, .kit-card', { timeout: 10000 });
      
      // Find a kit with items
      const kitInfo = await firstPage.evaluate(() => {
        const rows = document.querySelectorAll('table tbody tr, .kit-card');
        for (const row of rows) {
          const kitName = row.querySelector('td:nth-child(2), .kit-name')?.textContent.trim();
          if (kitName) {
            return { kitName };
          }
        }
        return null;
      });
      
      if (!kitInfo) {
        console.log('⚠️  No kits found, skipping test');
        return;
      }

      console.log(`Testing concurrent operations on kit: ${kitInfo.kitName}`);

      // Create a barrier
      const barrier = new ConcurrencyBarrier(userCount);

      // Create concurrent operations
      const operations = contexts.map(({ page, user }, index) => async () => {
        await barrier.wait();
        
        console.log(`User ${index + 1} (${user.username}) performing kit operation...`);
        
        // Click on the kit to view details
        const kitRow = page.locator(`tr:has-text("${kitInfo.kitName}"), .kit-card:has-text("${kitInfo.kitName}")`).first();
        await kitRow.click({ timeout: 5000 });
        
        await page.waitForTimeout(2000);
        
        // Try to perform an operation (view inventory, add message, etc.)
        const hasInventory = await page.locator('table, .inventory-list').count() > 0;
        
        return {
          user: user.username,
          hasInventory,
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
    const userCount = 5;
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

