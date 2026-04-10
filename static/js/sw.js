const CACHE_NAME = 'election-predictor-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/parties',
  '/about',
  '/static/css/style.css',
  '/static/images/logo.png',
  '/static/js/navigation.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;

  // Network-First Strategy 
  // Always fetch latest from server so users don't have to reload for updates
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Save the successful network response to cache
        return caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, response.clone());
          return response;
        });
      })
      .catch(() => {
        // If network fails (e.g., offline), fallback to the cache
        return caches.match(event.request);
      })
  );
});
