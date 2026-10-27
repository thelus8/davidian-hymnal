// Offline support: the app shell is cached on install; Google Fonts are cached the first time they load.
const VERSION = '__VERSION__';
const SHELL = ['./', 'index.html', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png'];

const FONT_CSS = '__FONT_CSS__';

// Fetch the font stylesheet and every font file it names, so the first visit is enough to work offline.
async function cacheFonts() {
  const c = await caches.open('fonts');
  if (await c.match(FONT_CSS)) return;
  const res = await fetch(FONT_CSS);
  const css = await res.clone().text();
  await c.put(FONT_CSS, res);
  const files = [...css.matchAll(/url\((https:[^)]+)\)/g)].map(m => m[1]);
  await Promise.all(files.map(u => fetch(u).then(r => c.put(u, r))));
}

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL))
    .then(() => cacheFonts().catch(() => {}))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== 'fonts').map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open('fonts').then(async c => {
      const hit = await c.match(e.request);
      if (hit) return hit;
      const res = await fetch(e.request);
      c.put(e.request, res.clone());
      return res;
    }));
    return;
  }
  if (url.origin !== location.origin) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true })
    .then(hit => hit || fetch(e.request))
    .catch(() => caches.match('index.html')));
});
