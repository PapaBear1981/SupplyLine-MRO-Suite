/**
 * API Throttling Utility
 *
 * This utility provides functions to throttle and debounce API requests
 * to prevent overwhelming the backend with too many requests.
 */

// Cache for storing API responses
const apiCache = new Map();

// Cache for tracking in-flight requests
const pendingRequests = new Map();

/**
 * Throttled API request function
 *
 * @param {Function} apiCall - The API call function to throttle
 * @param {string} cacheKey - A unique key to identify this request in the cache
 * @param {number} cacheDuration - How long to cache the response in milliseconds
 * @returns {Promise} - The API response
 */
export const throttledRequest = async (apiCall, cacheKey, cacheDuration = 60000) => {
  // Check if we have a cached response that's still valid
  const cachedItem = apiCache.get(cacheKey);
  if (cachedItem && Date.now() - cachedItem.timestamp < cacheDuration) {
    console.log(`Using cached response for ${cacheKey}`);
    return cachedItem.data;
  }

  // Check if there's already a pending request for this key
  if (pendingRequests.has(cacheKey)) {
    console.log(`Reusing in-flight request for ${cacheKey}`);
    return pendingRequests.get(cacheKey);
  }

  // Create a new request and store it in the pending map
  const requestPromise = apiCall().then(response => {
    console.log(`Caching response for ${cacheKey}:`, response);

    // Cache the successful response
    apiCache.set(cacheKey, {
      data: response,
      timestamp: Date.now()
    });

    // Remove from pending requests
    pendingRequests.delete(cacheKey);

    return response;
  }).catch(error => {
    console.error(`Error in throttled request for ${cacheKey}:`, error);
    // Remove from pending requests on error
    pendingRequests.delete(cacheKey);
    throw error;
  });

  // Store the pending request
  pendingRequests.set(cacheKey, requestPromise);

  return requestPromise;
};

// Debounce function for API calls
let debounceTimers = {};

/**
 * Debounced API request function
 *
 * @param {Function} apiCall - The API call function to debounce
 * @param {string} key - A unique key to identify this request
 * @param {number} delay - Debounce delay in milliseconds
 * @returns {Promise} - The API response
 */
export const debouncedRequest = (apiCall, key, delay = 300) => {
  return new Promise((resolve, reject) => {
    // Clear existing timer
    if (debounceTimers[key]) {
      clearTimeout(debounceTimers[key]);
    }

    // Set new timer
    debounceTimers[key] = setTimeout(() => {
      apiCall()
        .then(resolve)
        .catch(reject)
        .finally(() => {
          delete debounceTimers[key];
        });
    }, delay);
  });
};

/**
 * Clear the API cache
 *
 * @param {string} cacheKey - Optional specific cache key to clear
 */
export const clearApiCache = (cacheKey = null) => {
  if (cacheKey) {
    apiCache.delete(cacheKey);
  } else {
    apiCache.clear();
  }
};
