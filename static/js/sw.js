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
  // Only cache GET requests with http/https schemes
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith('http://') && !event.request.url.startsWith('https://')) return;

  // Network-First Strategy
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Save valid 200 responses to cache safely
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            try {
              cache.put(event.request, responseToCache);
            } catch (err) {
              /* ignore cache write errors for non-cacheable items */
            }
          }).catch(() => {});
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache if network fails (e.g. offline)
        return caches.match(event.request);
      })
  );
});
