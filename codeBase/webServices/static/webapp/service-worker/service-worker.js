const cacheName = 'Artiman-webApp-pwa-cache-v2';
const filesToCache = [
  '/web_app/v1/',
  '/web_app/v1/edit-profile',
  '/static/webapp/css/custom.css',
  '/static/webapp/css/custom2.css',
  '/static/webapp/css/style.css',

  '/static/webapp/curtain/style.css',

  '/static/webapp/edit-profile/css/style.css',

  '/static/webapp/home/css/main.css',
  '/static/webapp/home/js/theme-mode.js',
  '/static/webapp/home/js/zone-menu.js',

  '/static/webapp/images/img.webp',
  '/static/webapp/images/male_avatar.png',
  '/static/webapp/images/undraw_Empty_re_opql.png',
  "/static/webapp/images/logo.png",

  '/static/webapp/js/main.js',

  '/static/webapp/mqttClient/client.js',

  '/static/webapp/mqttEventBus/eventBus.js',

  '/static/webapp/scene/css/scene-page.css',
  '/static/webapp/scene/js/scene_cards_generator.js',
  '/static/webapp/scene/js/scene_wizard.js',
  '/static/webapp/scene/js/scene-page.js',
  '/static/webapp/scene/js/ui_generator.js',
  '/static/webapp/scene/js/variables.js',

  'service-worker.js',

  '/static/webapp/setting-page/css/style.css',

  '/static/webapp/ui-constructors/curtain-controller.js',
  '/static/webapp/ui-constructors/push-buttons.js',
  '/static/webapp/ui-constructors/switch-buttons.js',
  '/static/webapp/ui-constructors/thermostat.js',

  // libs
  '/static/webapp/libs/bootstrap-5.0.2/bootstrap.min.css',
  '/static/webapp/libs/bootstrap-5.0.2/bootstrap.min.js',
  '/static/webapp/libs/jquery-3.5.1/jquery-3.5.1.slim.min.js',
  '/static/webapp/libs/mqttjs-5.10.1/mqtt.min.js',
  '/static/webapp/libs/page.js/page.js',
  '/static/webapp/libs/pickerjs-1.2.1/dist/picker.min.js',
  '/static/webapp/libs/sortable-1.14.0/Sortable.min.js',
  '/static/webapp/libs/tinycolor/tinycolor-min.js',

  '/static/coloris/coloris.min.js',

  "/static/dashboard/static/dist/js/tabler.min.js",

  "/static/font-awesome-6-pro-main/css/all.css",
  "/static/font-awesome-6-pro-main/css/brands.css",
  "/static/font-awesome-6-pro-main/css/duotone.css",
  "/static/font-awesome-6-pro-main/css/fontawesome.css",
  "/static/font-awesome-6-pro-main/css/light.css",
  "/static/font-awesome-6-pro-main/css/regular.css",
  "/static/font-awesome-6-pro-main/css/solid.css",
  "/static/font-awesome-6-pro-main/css/svg-with-js.css",
  "/static/font-awesome-6-pro-main/css/thin.css",
  "/static/font-awesome-6-pro-main/css/v4-shims.css",
  "/static/font-awesome-6-pro-main/webfonts/fa-light-300.woff2",
  "/static/font-awesome-6-pro-main/webfonts/fa-regular-400.woff2",
  "/static/font-awesome-6-pro-main/webfonts/fa-solid-900.woff2",

];

// self.addEventListener('install', function(event) {
//   event.waitUntil(
//     caches.open(cacheName)
//       .then(function(cache) {
//         return cache.addAll(filesToCache);
//       })
//   );
// });


// // Text in the URL that indicates it should not be cached
// const doNotCacheText = 'controller'; // For example, exclude URLs containing 'api'

// function shouldCache(url) {
//   return !url.includes(doNotCacheText);
// }



// self.addEventListener('fetch', function(event) {
//   event.respondWith(
//     caches.match(event.request)
//       .then(function(response) {
//         // If the resource is in cache, return it
//         if (response) {
//           return response;
//         }

//         // Otherwise, fetch the resource from the network
//         return fetch(event.request)
//           .then(function(networkResponse) {
//             // Cache the fetched resource for future use
//             if (shouldCache(networkResponse.url)) {
//             return caches.open(cacheName)
//               .then(function(cache) {
//                 cache.put(event.request, networkResponse.clone());
//                 return networkResponse;
//               });
//             }
//             else {
//               return networkResponse;
//             }
//           });
//       })
//   );
// });



// Install event: Caching assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
      caches.open(cacheName).then(cache => {
          console.log('Service Worker: Caching Files');
          return cache.addAll(filesToCache);
      }).then(() => self.skipWaiting()) // Forces waiting SW to become active
  );
});

// Activate event: Cleanup old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
      caches.keys().then(cacheNames => {
          return Promise.all(
              cacheNames.map(cache => {
                  if (cache !== cacheName) {
                      console.log('Service Worker: Clearing Old Cache');
                      return caches.delete(cache);
                  }
              })
          );
      }).then(() => self.clients.claim()) // Claiming control immediately
  );
});




// Text in the URL that indicates it should not be cached
const doNotCacheTexts = ['web_app', 'login', 'logout', 'edit-profile', 'linkage_rules']; // For example, exclude URLs containing 'api'

function shouldCache(url) {
  return !doNotCacheTexts.some(word=> url.includes(word));
}





// Fetch event: Respond with cached resources or network request
self.addEventListener('fetch', event => {
  console.log('Service Worker: Fetching resource: ', event.request.url);
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
              }).catch(() => {
                // If both fail, serve the offline fallback page (for HTML files)
                if (event.request.headers.get('accept').includes('text/html')) {
                    return caches.match('/web_app/v1/');
                }
            })
  );
});