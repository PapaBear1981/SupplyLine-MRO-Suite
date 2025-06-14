import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../utils/auth-helpers.js';
import { waitForLoadingToComplete, navigateToPage } from '../utils/test-helpers.js';

test.describe('Performance Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('should load dashboard within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await navigateToPage(page, '/dashboard');
    await waitForLoadingToComplete(page);
    
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Dashboard load time: ${loadTime}ms`);
  });

  test('should load tools page within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await navigateToPage(page, '/tools');
    await waitForLoadingToComplete(page);
    
    const loadTime = Date.now() - startTime;
    
    // Tools page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    console.log(`Tools page load time: ${loadTime}ms`);
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    await navigateToPage(page, '/tools');
    
    // Measure time to load table with data
    const startTime = Date.now();
    
    // Wait for table to be populated
    await page.waitForSelector('[data-testid="tools-table"] tbody tr', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // Large dataset should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
    
    // Check if pagination is working efficiently
    const paginationElement = page.locator('[data-testid="pagination"]');
    if (await paginationElement.isVisible()) {
      const nextButton = page.locator('[data-testid="next-page-button"]');
      if (await nextButton.isVisible() && !await nextButton.isDisabled()) {
        const paginationStartTime = Date.now();
        
        await nextButton.click();
        await waitForLoadingToComplete(page);
        
        const paginationTime = Date.now() - paginationStartTime;
        
        // Pagination should be fast
        expect(paginationTime).toBeLessThan(2000);
        
        console.log(`Pagination time: ${paginationTime}ms`);
      }
    }
    
    console.log(`Large dataset load time: ${loadTime}ms`);
  });

  test('should search efficiently', async ({ page }) => {
    await navigateToPage(page, '/tools');
    await waitForLoadingToComplete(page);
    
    const searchInput = page.locator('[data-testid="tools-search-input"]');
    if (await searchInput.isVisible()) {
      const startTime = Date.now();
      
      // Perform search
      await searchInput.fill('T001');
      await page.keyboard.press('Enter');
      await waitForLoadingToComplete(page);
      
      const searchTime = Date.now() - startTime;
      
      // Search should complete within 2 seconds
      expect(searchTime).toBeLessThan(2000);
      
      console.log(`Search time: ${searchTime}ms`);
    }
  });

  test('should handle form submissions efficiently', async ({ page }) => {
    await navigateToPage(page, '/tools/new');
    
    // Fill form
    await page.fill('[data-testid="tool-number-input"]', 'PERF001');
    await page.fill('[data-testid="serial-number-input"]', 'PERF001');
    await page.fill('[data-testid="description-input"]', 'Performance Test Tool');
    
    const startTime = Date.now();
    
    // Submit form
    await page.click('[data-testid="save-tool-button"]');
    
    // Wait for success or error response
    await Promise.race([
      page.waitForSelector('.toast-success', { timeout: 5000 }),
      page.waitForSelector('.toast-error', { timeout: 5000 }),
      page.waitForURL(/\/tools/, { timeout: 5000 })
    ]);
    
    const submitTime = Date.now() - startTime;
    
    // Form submission should complete within 3 seconds
    expect(submitTime).toBeLessThan(3000);
    
    console.log(`Form submission time: ${submitTime}ms`);
  });

  test('should measure API response times', async ({ page }) => {
    const apiTimes = {};
    
    // Monitor API calls
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        const url = new URL(response.url());
        const endpoint = url.pathname;
        const timing = response.timing();
        
        apiTimes[endpoint] = timing.responseEnd - timing.requestStart;
      }
    });
    
    await navigateToPage(page, '/dashboard');
    await waitForLoadingToComplete(page);
    
    // Check API response times
    for (const [endpoint, time] of Object.entries(apiTimes)) {
      console.log(`API ${endpoint}: ${time}ms`);
      
      // API calls should complete within 2 seconds
      expect(time).toBeLessThan(2000);
    }
  });

  test('should handle concurrent operations efficiently', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Simulate concurrent operations
    const operations = [
      () => page.goto('/tools'),
      () => page.goto('/chemicals'),
      () => page.goto('/checkouts'),
      () => page.goto('/dashboard')
    ];
    
    const startTime = Date.now();
    
    // Execute operations in sequence (simulating user navigation)
    for (const operation of operations) {
      await operation();
      await waitForLoadingToComplete(page);
    }
    
    const totalTime = Date.now() - startTime;
    
    // All navigation should complete within 15 seconds
    expect(totalTime).toBeLessThan(15000);
    
    console.log(`Concurrent operations time: ${totalTime}ms`);
  });

  test('should measure memory usage', async ({ page }) => {
    await navigateToPage(page, '/dashboard');
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      return performance.memory ? {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize
      } : null;
    });
    
    if (initialMemory) {
      console.log(`Initial memory usage: ${(initialMemory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
      
      // Navigate through several pages
      const pages = ['/tools', '/chemicals', '/checkouts', '/cycle-counts', '/dashboard'];
      
      for (const pagePath of pages) {
        await navigateToPage(page, pagePath);
        await waitForLoadingToComplete(page);
      }
      
      // Get final memory usage
      const finalMemory = await page.evaluate(() => {
        return performance.memory ? {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize
        } : null;
      });
      
      if (finalMemory) {
        console.log(`Final memory usage: ${(finalMemory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
        
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
        const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
        
        console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)} MB (${memoryIncreasePercent.toFixed(2)}%)`);
        
        // Memory increase should be reasonable (less than 50MB or 100% increase)
        expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // 50MB
        expect(memoryIncreasePercent).toBeLessThan(100); // 100%
      }
    }
  });

  test('should measure network efficiency', async ({ page }) => {
    const networkRequests = [];
    
    // Monitor network requests
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        timestamp: Date.now()
      });
    });
    
    page.on('response', response => {
      const request = networkRequests.find(req => req.url === response.url());
      if (request) {
        request.responseTime = Date.now() - request.timestamp;
        request.status = response.status();
        request.size = response.headers()['content-length'] || 0;
      }
    });
    
    await navigateToPage(page, '/dashboard');
    await waitForLoadingToComplete(page);
    
    // Analyze network requests
    const apiRequests = networkRequests.filter(req => req.url.includes('/api/'));
    const staticRequests = networkRequests.filter(req => 
      req.url.includes('.js') || req.url.includes('.css') || req.url.includes('.png')
    );
    
    console.log(`Total API requests: ${apiRequests.length}`);
    console.log(`Total static requests: ${staticRequests.length}`);
    
    // Check for excessive API calls
    expect(apiRequests.length).toBeLessThan(20); // Reasonable limit for dashboard
    
    // Check API response times
    apiRequests.forEach(req => {
      if (req.responseTime) {
        console.log(`API ${req.url}: ${req.responseTime}ms`);
        expect(req.responseTime).toBeLessThan(3000);
      }
    });
  });

  test('should handle large table rendering efficiently', async ({ page }) => {
    await navigateToPage(page, '/tools');
    
    // Measure table rendering time
    const startTime = Date.now();
    
    await page.waitForSelector('[data-testid="tools-table"]', { timeout: 10000 });
    
    // Wait for all rows to be rendered
    await page.waitForFunction(() => {
      const table = document.querySelector('[data-testid="tools-table"]');
      const rows = table ? table.querySelectorAll('tbody tr') : [];
      return rows.length > 0;
    }, { timeout: 10000 });
    
    const renderTime = Date.now() - startTime;
    
    console.log(`Table rendering time: ${renderTime}ms`);
    
    // Table should render within 5 seconds
    expect(renderTime).toBeLessThan(5000);
    
    // Check scroll performance
    const tableContainer = page.locator('[data-testid="tools-table"]').first();
    
    const scrollStartTime = Date.now();
    
    // Scroll to bottom
    await tableContainer.evaluate(el => {
      el.scrollTop = el.scrollHeight;
    });
    
    // Wait for scroll to complete
    await page.waitForTimeout(100);
    
    const scrollTime = Date.now() - scrollStartTime;
    
    console.log(`Scroll time: ${scrollTime}ms`);
    
    // Scrolling should be smooth (less than 500ms)
    expect(scrollTime).toBeLessThan(500);
  });

  test('should measure bundle size impact', async ({ page }) => {
    // Navigate to different pages and measure resource loading
    const pages = [
      { path: '/dashboard', name: 'Dashboard' },
      { path: '/tools', name: 'Tools' },
      { path: '/chemicals', name: 'Chemicals' },
      { path: '/cycle-counts', name: 'Cycle Counts' }
    ];
    
    for (const pageInfo of pages) {
      const resourceSizes = [];
      
      page.on('response', response => {
        const contentLength = response.headers()['content-length'];
        if (contentLength && (response.url().includes('.js') || response.url().includes('.css'))) {
          resourceSizes.push({
            url: response.url(),
            size: parseInt(contentLength)
          });
        }
      });
      
      await navigateToPage(page, pageInfo.path);
      await waitForLoadingToComplete(page);
      
      const totalSize = resourceSizes.reduce((sum, resource) => sum + resource.size, 0);
      
      console.log(`${pageInfo.name} total resource size: ${(totalSize / 1024).toFixed(2)} KB`);
      
      // Total bundle size should be reasonable (less than 5MB)
      expect(totalSize).toBeLessThan(5 * 1024 * 1024);
    }
  });
});
