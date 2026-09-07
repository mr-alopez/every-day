/* Service worker: cache-first with background revalidate.

   Every launch is served from cache instantly, so the app opens with no signal
   at all. A background fetch refreshes the cache at the same time, which means
   a new deploy lands on the *next* launch rather than the current one.

   Responses are re-cached on every successful fetch, so CACHE only needs
   bumping if the caching strategy itself changes.

   Nothing here touches the habit data — that lives in localStorage on the
   device and is never fetched, sent, or cached. */
const CACHE = "every-day-v1";
const ASSETS = ["./", "./index.html", "./manifest.webmanifest",
                "./icon.svg", "./icon-180.png", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  if (new URL(e.request.url).origin !== location.origin) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(e.request, { ignoreSearch: true });
    const network = fetch(e.request).then(res => {
      if (res && res.ok) cache.put(e.request, res.clone());
      return res;
    }).catch(() => null);
    if (cached) return cached;
    const res = await network;
    if (res) return res;
    if (e.request.mode === "navigate") return cache.match("./index.html");
    return Response.error();
  })());
});
