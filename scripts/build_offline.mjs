// Cache only local application assets. Never cache API, trace or trial responses.
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../apps/web/dist/', import.meta.url));
const files = [];
function walk(directory) {
  for (const item of readdirSync(directory, { withFileTypes: true })) {
    const full = path.join(directory, item.name);
    if (item.isDirectory()) walk(full);
    else if (item.name !== 'sw.js') files.push(full);
  }
}
walk(root);
files.sort();
const hash = createHash('sha256');
for (const file of files) { hash.update(path.relative(root, file)); hash.update(readFileSync(file)); }
const version = hash.digest('hex').slice(0, 16);
const assets = files.map(file => '/' + path.relative(root, file).split(path.sep).join('/'));
writeFileSync(path.join(root, 'sw.js'), `
const CACHE = 'rewind-assets-${version}';
const ASSETS = ${JSON.stringify(assets)};
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('rewind-assets-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
  if (event.request.mode === 'navigate') event.respondWith(fetch(event.request).catch(() => caches.match('/index.html')));
  else if (ASSETS.includes(url.pathname)) event.respondWith(caches.open(CACHE).then(async cache => (await cache.match(url.pathname)) || fetch(event.request)));
});
`);
console.log(`Local offline shell: ${assets.length} bundled assets, ${version}. API responses are excluded.`);
