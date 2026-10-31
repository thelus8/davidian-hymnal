// Offline support: the page is loaded fresh when online and from the cache when offline;
// icons and Google Fonts are cached on install.
const VERSION = 'hymnal-25c0149e65';
const SHELL = ['./', 'index.html', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png'];

const FONT_CSS = 'https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap';

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
  // cache: 'reload' skips the browser's HTTP cache, so a new version never stores an older copy of the page
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' }))))
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
  if (e.request.mode === 'navigate') {
    // Newest page when online; the saved copy when offline or when the network is too slow to wait for
    const fromNet = fetch(e.request, { cache: 'no-cache' }).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put('index.html', copy)); }
      return res;
    });
    const slow = new Promise(r => setTimeout(r, 3500)).then(() => caches.match('index.html'));
    e.respondWith(Promise.race([
      fromNet.catch(() => caches.match('index.html')),
      slow.then(saved => saved || fromNet),
    ]));
    return;
  }
  e.respondWith(caches.match(e.request, { ignoreSearch: true })
    .then(hit => hit || fetch(e.request))
    .catch(() => caches.match('index.html')));
});
