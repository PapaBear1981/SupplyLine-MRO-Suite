/**
 * Advanced helper functions for E2E tests
 */

/**
 * Mock API responses for testing
 * @param {import('@playwright/test').Page} page 
 * @param {string} endpoint 
 * @param {object} mockData 
 * @param {number} status 
 */
export async function mockApiResponse(page, endpoint, mockData, status = 200) {
  await page.route(`**${endpoint}`, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(mockData)
    });
  });
}

/**
 * Simulate network conditions
 * @param {import('@playwright/test').Page} page 
 * @param {object} conditions 
 */
export async function simulateNetworkConditions(page, conditions = {}) {
  const {
    offline = false,
    downloadThroughput = 1000000, // 1 Mbps
    uploadThroughput = 1000000,   // 1 Mbps
    latency = 100                 // 100ms
  } = conditions;

  await page.context().setOffline(offline);
  
  if (!offline) {
    // Note: This requires CDP (Chrome DevTools Protocol)
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline,
      downloadThroughput,
      uploadThroughput,
      latency
    });
  }
}

/**
 * Wait for network to be idle
 * @param {import('@playwright/test').Page} page 
 * @param {number} timeout 
 */
export async function waitForNetworkIdle(page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Intercept and log all network requests
 * @param {import('@playwright/test').Page} page 
 * @returns {Array} Array to collect request logs
 */
export function interceptNetworkRequests(page) {
  const requests = [];
  
  page.on('request', request => {
    requests.push({
      url: request.url(),
      method: request.method(),
      headers: request.headers(),
      timestamp: Date.now()
    });
  });
  
  page.on('response', response => {
    const request = requests.find(req => req.url === response.url());
    if (request) {
      request.status = response.status();
      request.responseTime = Date.now() - request.timestamp;
    }
  });
  
  return requests;
}

/**
 * Simulate user typing with realistic delays
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 * @param {string} text 
 * @param {number} delay 
 */
export async function typeWithDelay(page, selector, text, delay = 100) {
  const element = page.locator(selector);
  await element.click();
  
  for (const char of text) {
    await element.type(char);
    await page.waitForTimeout(delay);
  }
}

/**
 * Simulate drag and drop operation
 * @param {import('@playwright/test').Page} page 
 * @param {string} sourceSelector 
 * @param {string} targetSelector 
 */
export async function dragAndDrop(page, sourceSelector, targetSelector) {
  const source = page.locator(sourceSelector);
  const target = page.locator(targetSelector);
  
  await source.dragTo(target);
}

/**
 * Wait for element to be stable (not moving)
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 * @param {number} timeout 
 */
export async function waitForElementStable(page, selector, timeout = 5000) {
  const element = page.locator(selector);
  
  await page.waitForFunction(
    (sel) => {
      const el = document.querySelector(sel);
      if (!el) return false;
      
      const rect1 = el.getBoundingClientRect();
      
      return new Promise(resolve => {
        setTimeout(() => {
          const rect2 = el.getBoundingClientRect();
          resolve(rect1.top === rect2.top && rect1.left === rect2.left);
        }, 100);
      });
    },
    selector,
    { timeout }
  );
}

/**
 * Check if element is in viewport
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 * @returns {Promise<boolean>}
 */
export async function isElementInViewport(page, selector) {
  return await page.locator(selector).evaluate(el => {
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  });
}

/**
 * Scroll element into view
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 */
export async function scrollIntoView(page, selector) {
  await page.locator(selector).scrollIntoViewIfNeeded();
}

/**
 * Get element's computed styles
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 * @param {Array<string>} properties 
 * @returns {Promise<object>}
 */
export async function getComputedStyles(page, selector, properties) {
  return await page.locator(selector).evaluate((el, props) => {
    const styles = window.getComputedStyle(el);
    const result = {};
    props.forEach(prop => {
      result[prop] = styles[prop];
    });
    return result;
  }, properties);
}

/**
 * Wait for animation to complete
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 */
export async function waitForAnimationEnd(page, selector) {
  await page.locator(selector).evaluate(el => {
    return Promise.all(
      el.getAnimations().map(animation => animation.finished)
    );
  });
}

/**
 * Simulate keyboard shortcuts
 * @param {import('@playwright/test').Page} page 
 * @param {string} shortcut 
 */
export async function pressKeyboardShortcut(page, shortcut) {
  const keys = shortcut.split('+');
  const modifiers = [];
  let key = '';
  
  for (const k of keys) {
    if (['Ctrl', 'Alt', 'Shift', 'Meta'].includes(k)) {
      modifiers.push(k);
    } else {
      key = k;
    }
  }
  
  await page.keyboard.press(`${modifiers.join('+')}+${key}`);
}

/**
 * Create test data in the database
 * @param {import('@playwright/test').Page} page 
 * @param {string} endpoint 
 * @param {object} data 
 */
export async function createTestData(page, endpoint, data) {
  const response = await page.request.post(endpoint, {
    data: data
  });
  
  if (!response.ok()) {
    throw new Error(`Failed to create test data: ${response.status()}`);
  }
  
  return await response.json();
}

/**
 * Clean up test data
 * @param {import('@playwright/test').Page} page 
 * @param {string} endpoint 
 * @param {string} id 
 */
export async function cleanupTestData(page, endpoint, id) {
  const response = await page.request.delete(`${endpoint}/${id}`);
  
  if (!response.ok() && response.status() !== 404) {
    console.warn(`Failed to cleanup test data: ${response.status()}`);
  }
}

/**
 * Wait for specific console message
 * @param {import('@playwright/test').Page} page 
 * @param {string} message 
 * @param {number} timeout 
 */
export async function waitForConsoleMessage(page, message, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Console message "${message}" not found within ${timeout}ms`));
    }, timeout);
    
    const handler = (msg) => {
      if (msg.text().includes(message)) {
        clearTimeout(timer);
        page.off('console', handler);
        resolve(msg);
      }
    };
    
    page.on('console', handler);
  });
}

/**
 * Measure page load performance
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<object>}
 */
export async function measurePagePerformance(page) {
  return await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    
    return {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
      firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
      firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
      totalLoadTime: navigation.loadEventEnd - navigation.fetchStart
    };
  });
}

/**
 * Take element screenshot with highlighting
 * @param {import('@playwright/test').Page} page 
 * @param {string} selector 
 * @param {string} filename 
 */
export async function takeElementScreenshotWithHighlight(page, selector, filename) {
  // Add highlight styles
  await page.addStyleTag({
    content: `
      .playwright-highlight {
        outline: 3px solid red !important;
        outline-offset: 2px !important;
      }
    `
  });
  
  // Add highlight class
  await page.locator(selector).evaluate(el => {
    el.classList.add('playwright-highlight');
  });
  
  // Take screenshot
  await page.locator(selector).screenshot({ path: filename });
  
  // Remove highlight
  await page.locator(selector).evaluate(el => {
    el.classList.remove('playwright-highlight');
  });
}

/**
 * Generate random test data
 * @param {string} type 
 * @returns {string}
 */
export function generateTestData(type) {
  const timestamp = Date.now();
  
  switch (type) {
    case 'email':
      return `test${timestamp}@example.com`;
    case 'toolNumber':
      return `T${timestamp}`;
    case 'serialNumber':
      return `SN${timestamp}`;
    case 'partNumber':
      return `P${timestamp}`;
    case 'employeeNumber':
      return `EMP${timestamp}`;
    default:
      return `TEST${timestamp}`;
  }
}
