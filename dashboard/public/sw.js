const CACHE_NAME = 'nsoc-v2.1';
const STATIC_ASSETS = ['/', '/index.html', '/manifest.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then(names => Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  e.respondWith(caches.match(e.request).then(cached => {
    if (cached) { fetch(e.request).then(r => { if (r.ok) caches.open(CACHE_NAME).then(c => c.put(e.request, r)); }).catch(()=>{}); return cached; }
    return fetch(e.request).then(r => { if (r && r.status === 200 && r.type === 'basic') caches.open(CACHE_NAME).then(c => c.put(e.request, r.clone())); return r; }).catch(() => e.request.mode === 'navigate' ? caches.match('/index.html') : new Response('Offline', {status: 503}));
  }));
});
