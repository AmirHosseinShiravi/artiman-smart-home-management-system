const cacheName = 'hetra-pwa-cache-1';
const filesToCache = [
  '/b8f6331a-032a-4233-a21d-e8f7caff0b22',
  '/static/jquery-3.5.1.slim.min.js',
  '/static/popper.min.js',
  '/static/bootstrap.min.js',
  '/static/style.css',
  '/static/bootstrap.min.css',
  '/static/files/hetra_logo.png',
  '/service-worker.js'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(cacheName)
      .then(function(cache) {
        return cache.addAll(filesToCache);
      })
  );
});


// Text in the URL that indicates it should not be cached
const doNotCacheText = 'controller'; // For example, exclude URLs containing 'api'

function shouldCache(url) {
  return !url.includes(doNotCacheText);
}



self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // If the resource is in cache, return it
        if (response) {
          return response;
        }

        // Otherwise, fetch the resource from the network
        return fetch(event.request)
          .then(function(networkResponse) {
            // Cache the fetched resource for future use
            if (shouldCache(networkResponse.url)) {
            return caches.open(cacheName)
              .then(function(cache) {
                cache.put(event.request, networkResponse.clone());
                return networkResponse;
              });
            }
            else {
              return networkResponse;
            }
          });
      })
  );
});
