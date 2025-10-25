/**
 * AWS Cost Optimizer - Service Worker
 * Handles push notifications and offline functionality
 */

const CACHE_NAME = 'aws-cost-optimizer-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Install event
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker installation failed:', error);
      })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated successfully');
      return self.clients.claim();
    })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
      .catch((error) => {
        console.error('Fetch failed:', error);
        // Return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});

// Push event
self.addEventListener('push', (event) => {
  console.log('Push message received:', event);
  
  let notificationData = {
    title: 'AWS Cost Optimizer',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'cost-optimizer-notification',
    requireInteraction: false,
    silent: false,
    vibrate: [200, 100, 200],
    actions: [
      {
        action: 'view',
        title: 'View Details',
        icon: '/icons/view-24x24.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/icons/dismiss-24x24.png'
      }
    ],
    data: {
      url: '/dashboard',
      timestamp: Date.now()
    }
  };

  // Parse push data if available
  if (event.data) {
    try {
      const pushData = event.data.json();
      notificationData = { ...notificationData, ...pushData };
    } catch (error) {
      console.error('Error parsing push data:', error);
    }
  }

  const notificationOptions = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    tag: notificationData.tag,
    requireInteraction: notificationData.requireInteraction,
    silent: notificationData.silent,
    vibrate: notificationData.vibrate,
    actions: notificationData.actions,
    data: notificationData.data
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationOptions)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();

  const action = event.action;
  const data = event.notification.data;

  if (action === 'view') {
    // Open the app and navigate to relevant page
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            if (data.url) {
              client.navigate(data.url);
            }
            return;
          }
        }
        
        // Open new window if app is not open
        if (clients.openWindow) {
          const url = data.url || '/dashboard';
          return clients.openWindow(url);
        }
      })
    );
  } else if (action === 'dismiss') {
    // Just close the notification
    console.log('Notification dismissed');
  } else {
    // Default click behavior
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            if (data.url) {
              client.navigate(data.url);
            }
            return;
          }
        }
        
        // Open new window if app is not open
        if (clients.openWindow) {
          const url = data.url || '/dashboard';
          return clients.openWindow(url);
        }
      })
    );
  }
});

// Background sync event
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'cost-data-sync') {
    event.waitUntil(syncCostData());
  } else if (event.tag === 'notification-sync') {
    event.waitUntil(syncNotifications());
  }
});

// Message event
self.addEventListener('message', (event) => {
  console.log('Service Worker received message:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// Helper functions
async function syncCostData() {
  try {
    console.log('Syncing cost data...');
    
    // Get pending cost data from IndexedDB
    const pendingData = await getPendingCostData();
    
    if (pendingData.length > 0) {
      // Send to server
      const response = await fetch('/api/cost-data/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAuthToken()}`
        },
        body: JSON.stringify({ data: pendingData })
      });
      
      if (response.ok) {
        // Clear pending data
        await clearPendingCostData();
        console.log('Cost data synced successfully');
      }
    }
  } catch (error) {
    console.error('Error syncing cost data:', error);
  }
}

async function syncNotifications() {
  try {
    console.log('Syncing notifications...');
    
    // Get pending notifications from IndexedDB
    const pendingNotifications = await getPendingNotifications();
    
    if (pendingNotifications.length > 0) {
      // Send to server
      const response = await fetch('/api/notifications/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAuthToken()}`
        },
        body: JSON.stringify({ notifications: pendingNotifications })
      });
      
      if (response.ok) {
        // Clear pending notifications
        await clearPendingNotifications();
        console.log('Notifications synced successfully');
      }
    }
  } catch (error) {
    console.error('Error syncing notifications:', error);
  }
}

async function getAuthToken() {
  // Get auth token from IndexedDB or localStorage
  return new Promise((resolve) => {
    const request = indexedDB.open('aws-cost-optimizer', 1);
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['tokens'], 'readonly');
      const store = transaction.objectStore('tokens');
      const getRequest = store.get('auth_token');
      
      getRequest.onsuccess = () => {
        resolve(getRequest.result?.value || '');
      };
      
      getRequest.onerror = () => {
        resolve('');
      };
    };
    
    request.onerror = () => {
      resolve('');
    };
  });
}

async function getPendingCostData() {
  // Mock implementation - in real app, get from IndexedDB
  return [];
}

async function clearPendingCostData() {
  // Mock implementation - in real app, clear from IndexedDB
  console.log('Pending cost data cleared');
}

async function getPendingNotifications() {
  // Mock implementation - in real app, get from IndexedDB
  return [];
}

async function clearPendingNotifications() {
  // Mock implementation - in real app, clear from IndexedDB
  console.log('Pending notifications cleared');
}

// Periodic background sync
self.addEventListener('periodicsync', (event) => {
  console.log('Periodic background sync:', event.tag);
  
  if (event.tag === 'cost-data-update') {
    event.waitUntil(updateCostData());
  }
});

async function updateCostData() {
  try {
    console.log('Updating cost data...');
    
    // Fetch latest cost data
    const response = await fetch('/api/cost-data/latest', {
      headers: {
        'Authorization': `Bearer ${await getAuthToken()}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Store in cache
      const cache = await caches.open(CACHE_NAME);
      await cache.put('/api/cost-data/latest', new Response(JSON.stringify(data)));
      
      console.log('Cost data updated successfully');
    }
  } catch (error) {
    console.error('Error updating cost data:', error);
  }
}
