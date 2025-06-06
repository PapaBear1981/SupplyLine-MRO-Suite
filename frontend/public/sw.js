/**
 * Service Worker for SupplyLine MRO Suite PWA
 *
 * Provides offline support, caching, and background sync capabilities
 */

const CACHE_NAME = 'supplyline-v3.6.0';
const STATIC_CACHE = 'supplyline-static-v3.6.0';
const DYNAMIC_CACHE = 'supplyline-dynamic-v3.6.0';

// Files to cache immediately (critical app shell)
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192x192.png',
  '/icon-512x512.png',
  '/vite.svg'
];

// Supabase API patterns to cache
const SUPABASE_API_PATTERNS = [
  /^https:\/\/.*\.supabase\.co\/rest\/v1\//,
  /^https:\/\/.*\.supabase\.co\/auth\/v1\//
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker...');

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[SW] Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('[SW] Static files cached successfully');
        return self.skipWaiting(); // Activate immediately
      })
      .catch(err => {
        console.error('[SW] Failed to cache static files:', err);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker...');

  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE &&
                cacheName !== DYNAMIC_CACHE &&
                cacheName !== CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Service worker activated');
        return self.clients.claim(); // Take control immediately
      })
  );
});

// Fetch event - handle requests with caching strategy
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle different types of requests
  if (isStaticFile(request)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  } else if (isSupabaseAPI(request)) {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
  } else if (isNavigationRequest(request)) {
    event.respondWith(handleNavigation(request));
  } else {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
  }
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);

  if (event.tag === 'supabase-sync') {
    event.waitUntil(syncOfflineData());
  }
});

// Helper functions
function isStaticFile(request) {
  const url = new URL(request.url);
  return STATIC_FILES.some(file => url.pathname === file) ||
         url.pathname.includes('/assets/') ||
         url.pathname.includes('/icons/');
}

function isSupabaseAPI(request) {
  return SUPABASE_API_PATTERNS.some(pattern => pattern.test(request.url));
}

function isNavigationRequest(request) {
  return request.mode === 'navigate' ||
         (request.method === 'GET' && request.headers.get('accept').includes('text/html'));
}

// Cache-first strategy (for static files)
async function cacheFirst(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log('[SW] Serving from cache:', request.url);
      return cachedResponse;
    }

    console.log('[SW] Fetching and caching:', request.url);
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache-first failed:', error);
    return new Response('Offline - Resource not available', { status: 503 });
  }
}

// Network-first strategy (for API calls)
async function networkFirst(request, cacheName) {
  try {
    console.log('[SW] Network-first for:', request.url);
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    return new Response('Offline - API not available', {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Offline - API not available' })
    });
  }
}

// Handle navigation requests (SPA routing)
async function handleNavigation(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('[SW] Navigation offline, serving cached index.html');
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match('/index.html');
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

// Sync offline data with Supabase
async function syncOfflineData() {
  console.log('[SW] Syncing offline data...');

  try {
    // This will be implemented when we integrate with the sync service
    // For now, just log that sync was attempted
    console.log('[SW] Offline data sync completed');
  } catch (error) {
    console.error('[SW] Offline data sync failed:', error);
  }
}

// Message handling for communication with main app
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});
