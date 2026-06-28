const CACHE_NAME = 'mp-predictor-v3';
const STATIC_ASSETS = [
  '/',
  '/predictor',
  '/search',
  '/faq',
  '/how-it-works',
  '/about',
  '/static/style.css',
  '/static/favicon.png',
  '/static/js/dte-export.js',
  '/static/js/share-utils.js',
  '/static/js/whatif-slider.js',
  '/static/js/notifications.js',
  '/static/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET') return;

  // Always bypass caching for API, Admin, and Account routes
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/admin') || url.pathname.startsWith('/account')) {
    return;
  }

  const isStaticAsset = 
    url.pathname.startsWith('/static/') || 
    url.origin !== self.location.origin || 
    url.pathname.endsWith('.css') || 
    url.pathname.endsWith('.js') || 
    url.pathname.endsWith('.png') || 
    url.pathname.endsWith('.jpg') || 
    url.pathname.endsWith('.ico') || 
    url.pathname.endsWith('.json');

  if (isStaticAsset) {
    // Cache-First (Stale-While-Revalidate) for static resources
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const fetchPromise = fetch(event.request)
          .then((response) => {
            if (response && response.status === 200) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
            }
            return response;
          })
          .catch(() => cached);
        return cached || fetchPromise;
      })
    );
  } else {
    // Network-First (with cache fallback) for dynamic HTML pages
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
  }
});

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'DTE MP', body: 'Counselling update' };
  event.waitUntil(
    self.registration.showNotification(data.title || 'MP DTE Predictor', {
      body: data.body || 'Check counselling dates',
      icon: '/static/favicon.png',
    })
  );
});
