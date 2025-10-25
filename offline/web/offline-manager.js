/**
 * AWS Cost Optimizer - Web Offline Manager
 * Handles offline functionality for the web application
 */

class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.syncQueue = [];
    this.cacheName = 'aws-cost-optimizer-v1';
    this.dbName = 'aws-cost-optimizer-offline';
    this.dbVersion = 1;
    this.db = null;
    
    // Initialize offline manager
    this.init();
  }

  /**
   * Initialize offline manager
   */
  async init() {
    try {
      // Set up event listeners
      this.setupEventListeners();
      
      // Initialize IndexedDB
      await this.initIndexedDB();
      
      // Set up service worker
      await this.setupServiceWorker();
      
      // Start background sync
      this.startBackgroundSync();
      
      console.log('Offline manager initialized successfully');
    } catch (error) {
      console.error('Error initializing offline manager:', error);
    }
  }

  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Online/offline events
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.onConnectionRestored();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.onConnectionLost();
    });

    // Visibility change events
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isOnline) {
        this.syncPendingData();
      }
    });

    // Before unload event
    window.addEventListener('beforeunload', () => {
      this.savePendingData();
    });
  }

  /**
   * Initialize IndexedDB
   */
  async initIndexedDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('Error opening IndexedDB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('IndexedDB opened successfully');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores
        this.createObjectStores(db);
      };
    });
  }

  /**
   * Create IndexedDB object stores
   */
  createObjectStores(db) {
    // Cost data store
    if (!db.objectStoreNames.contains('costData')) {
      const costDataStore = db.createObjectStore('costData', { keyPath: 'id' });
      costDataStore.createIndex('date', 'date', { unique: false });
      costDataStore.createIndex('service', 'service', { unique: false });
      costDataStore.createIndex('synced', 'synced', { unique: false });
    }

    // Notifications store
    if (!db.objectStoreNames.contains('notifications')) {
      const notificationsStore = db.createObjectStore('notifications', { keyPath: 'id' });
      notificationsStore.createIndex('timestamp', 'timestamp', { unique: false });
      notificationsStore.createIndex('read', 'read', { unique: false });
    }

    // Sync queue store
    if (!db.objectStoreNames.contains('syncQueue')) {
      const syncQueueStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
      syncQueueStore.createIndex('timestamp', 'timestamp', { unique: false });
      syncQueueStore.createIndex('type', 'type', { unique: false });
    }

    // User preferences store
    if (!db.objectStoreNames.contains('userPreferences')) {
      db.createObjectStore('userPreferences', { keyPath: 'key' });
    }

    // Cache metadata store
    if (!db.objectStoreNames.contains('cacheMetadata')) {
      const cacheStore = db.createObjectStore('cacheMetadata', { keyPath: 'url' });
      cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
    }
  }

  /**
   * Set up service worker
   */
  async setupServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
        
        // Listen for service worker messages
        navigator.serviceWorker.addEventListener('message', (event) => {
          this.handleServiceWorkerMessage(event.data);
        });
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }

  /**
   * Start background sync
   */
  startBackgroundSync() {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      // Register background sync
      navigator.serviceWorker.ready.then((registration) => {
        registration.sync.register('cost-data-sync');
        registration.sync.register('notification-sync');
      });
    }

    // Set up periodic sync
    if ('serviceWorker' in navigator && 'periodicSync' in window.ServiceWorkerRegistration.prototype) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.periodicSync.register('cost-data-update', {
          minInterval: 24 * 60 * 60 * 1000 // 24 hours
        });
      });
    }
  }

  /**
   * Handle connection restored
   */
  async onConnectionRestored() {
    console.log('Connection restored, syncing pending data...');
    
    // Show online indicator
    this.showConnectionStatus('online');
    
    // Sync pending data
    await this.syncPendingData();
    
    // Update cache
    await this.updateCache();
  }

  /**
   * Handle connection lost
   */
  onConnectionLost() {
    console.log('Connection lost, switching to offline mode...');
    
    // Show offline indicator
    this.showConnectionStatus('offline');
    
    // Save current state
    this.saveCurrentState();
  }

  /**
   * Show connection status
   */
  showConnectionStatus(status) {
    // Create or update status indicator
    let indicator = document.getElementById('connection-status');
    
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'connection-status';
      indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 8px 16px;
        border-radius: 4px;
        color: white;
        font-size: 14px;
        z-index: 1000;
        transition: all 0.3s ease;
      `;
      document.body.appendChild(indicator);
    }

    if (status === 'online') {
      indicator.textContent = '🟢 Online';
      indicator.style.backgroundColor = '#10b981';
    } else {
      indicator.textContent = '🔴 Offline';
      indicator.style.backgroundColor = '#ef4444';
    }

    // Auto-hide after 3 seconds if online
    if (status === 'online') {
      setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => {
          if (indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
          }
        }, 300);
      }, 3000);
    }
  }

  /**
   * Cache data for offline use
   */
  async cacheData(key, data, metadata = {}) {
    try {
      // Store in IndexedDB
      const transaction = this.db.transaction(['costData'], 'readwrite');
      const store = transaction.objectStore('costData');
      
      const cacheItem = {
        id: key,
        data: data,
        timestamp: Date.now(),
        synced: true,
        metadata: metadata
      };
      
      await store.put(cacheItem);
      
      // Store in cache metadata
      const cacheTransaction = this.db.transaction(['cacheMetadata'], 'readwrite');
      const cacheStore = cacheTransaction.objectStore('cacheMetadata');
      
      await cacheStore.put({
        url: key,
        timestamp: Date.now(),
        size: JSON.stringify(data).length,
        metadata: metadata
      });
      
      console.log(`Data cached for offline use: ${key}`);
    } catch (error) {
      console.error('Error caching data:', error);
    }
  }

  /**
   * Get cached data
   */
  async getCachedData(key) {
    try {
      const transaction = this.db.transaction(['costData'], 'readonly');
      const store = transaction.objectStore('costData');
      const request = store.get(key);
      
      return new Promise((resolve, reject) => {
        request.onsuccess = () => {
          resolve(request.result?.data || null);
        };
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Error getting cached data:', error);
      return null;
    }
  }

  /**
   * Queue data for sync
   */
  async queueForSync(type, data, priority = 'normal') {
    try {
      const syncItem = {
        id: `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: type,
        data: data,
        priority: priority,
        timestamp: Date.now(),
        attempts: 0,
        maxAttempts: 3
      };
      
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      await store.add(syncItem);
      
      console.log(`Data queued for sync: ${type}`);
      
      // Try to sync immediately if online
      if (this.isOnline) {
        await this.syncPendingData();
      }
    } catch (error) {
      console.error('Error queuing data for sync:', error);
    }
  }

  /**
   * Sync pending data
   */
  async syncPendingData() {
    if (!this.isOnline) {
      console.log('Offline, cannot sync data');
      return;
    }

    try {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.getAll();
      
      request.onsuccess = async () => {
        const pendingItems = request.result;
        
        for (const item of pendingItems) {
          try {
            await this.syncItem(item);
            
            // Remove from queue after successful sync
            store.delete(item.id);
          } catch (error) {
            console.error(`Error syncing item ${item.id}:`, error);
            
            // Increment attempts
            item.attempts++;
            
            if (item.attempts >= item.maxAttempts) {
              console.error(`Max attempts reached for item ${item.id}, removing from queue`);
              store.delete(item.id);
            } else {
              // Update attempts
              store.put(item);
            }
          }
        }
      };
    } catch (error) {
      console.error('Error syncing pending data:', error);
    }
  }

  /**
   * Sync individual item
   */
  async syncItem(item) {
    const { type, data } = item;
    
    switch (type) {
      case 'cost_data':
        await this.syncCostData(data);
        break;
      case 'notification':
        await this.syncNotification(data);
        break;
      case 'user_preference':
        await this.syncUserPreference(data);
        break;
      default:
        console.warn(`Unknown sync type: ${type}`);
    }
  }

  /**
   * Sync cost data
   */
  async syncCostData(data) {
    try {
      const response = await fetch('/api/cost-data/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      console.log('Cost data synced successfully');
    } catch (error) {
      console.error('Error syncing cost data:', error);
      throw error;
    }
  }

  /**
   * Sync notification
   */
  async syncNotification(data) {
    try {
      const response = await fetch('/api/notifications/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      console.log('Notification synced successfully');
    } catch (error) {
      console.error('Error syncing notification:', error);
      throw error;
    }
  }

  /**
   * Sync user preference
   */
  async syncUserPreference(data) {
    try {
      const response = await fetch('/api/user/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      console.log('User preference synced successfully');
    } catch (error) {
      console.error('Error syncing user preference:', error);
      throw error;
    }
  }

  /**
   * Update cache
   */
  async updateCache() {
    try {
      // Update cost data cache
      await this.updateCostDataCache();
      
      // Update notifications cache
      await this.updateNotificationsCache();
      
      console.log('Cache updated successfully');
    } catch (error) {
      console.error('Error updating cache:', error);
    }
  }

  /**
   * Update cost data cache
   */
  async updateCostDataCache() {
    try {
      const response = await fetch('/api/cost-data/latest', {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        await this.cacheData('cost-data-latest', data);
      }
    } catch (error) {
      console.error('Error updating cost data cache:', error);
    }
  }

  /**
   * Update notifications cache
   */
  async updateNotificationsCache() {
    try {
      const response = await fetch('/api/notifications/latest', {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        await this.cacheData('notifications-latest', data);
      }
    } catch (error) {
      console.error('Error updating notifications cache:', error);
    }
  }

  /**
   * Save current state
   */
  saveCurrentState() {
    try {
      const state = {
        timestamp: Date.now(),
        url: window.location.href,
        formData: this.collectFormData(),
        scrollPosition: window.pageYOffset
      };
      
      localStorage.setItem('offline-state', JSON.stringify(state));
    } catch (error) {
      console.error('Error saving current state:', error);
    }
  }

  /**
   * Collect form data
   */
  collectFormData() {
    const forms = document.querySelectorAll('form');
    const formData = {};
    
    forms.forEach((form, index) => {
      const data = new FormData(form);
      const formObject = {};
      
      for (const [key, value] of data.entries()) {
        formObject[key] = value;
      }
      
      if (Object.keys(formObject).length > 0) {
        formData[`form_${index}`] = formObject;
      }
    });
    
    return formData;
  }

  /**
   * Save pending data
   */
  savePendingData() {
    try {
      // Save any unsaved form data
      const formData = this.collectFormData();
      if (Object.keys(formData).length > 0) {
        localStorage.setItem('pending-form-data', JSON.stringify(formData));
      }
      
      // Save current page state
      this.saveCurrentState();
    } catch (error) {
      console.error('Error saving pending data:', error);
    }
  }

  /**
   * Handle service worker message
   */
  handleServiceWorkerMessage(data) {
    switch (data.type) {
      case 'CACHE_UPDATED':
        console.log('Cache updated:', data.details);
        break;
      case 'SYNC_COMPLETED':
        console.log('Background sync completed:', data.details);
        break;
      case 'SYNC_FAILED':
        console.error('Background sync failed:', data.details);
        break;
      default:
        console.log('Unknown service worker message:', data);
    }
  }

  /**
   * Get authentication token
   */
  getAuthToken() {
    return localStorage.getItem('auth_token') || '';
  }

  /**
   * Check if offline
   */
  isOffline() {
    return !this.isOnline;
  }

  /**
   * Get offline status
   */
  getOfflineStatus() {
    return {
      isOnline: this.isOnline,
      pendingSyncCount: this.syncQueue.length,
      lastSync: localStorage.getItem('last-sync') || null
    };
  }

  /**
   * Clear offline data
   */
  async clearOfflineData() {
    try {
      // Clear IndexedDB
      const transaction = this.db.transaction(['costData', 'notifications', 'syncQueue'], 'readwrite');
      
      await Promise.all([
        transaction.objectStore('costData').clear(),
        transaction.objectStore('notifications').clear(),
        transaction.objectStore('syncQueue').clear()
      ]);
      
      // Clear localStorage
      localStorage.removeItem('offline-state');
      localStorage.removeItem('pending-form-data');
      localStorage.removeItem('last-sync');
      
      console.log('Offline data cleared successfully');
    } catch (error) {
      console.error('Error clearing offline data:', error);
    }
  }
}

// Create global instance
window.offlineManager = new OfflineManager();

// Export for use in other modules
export default OfflineManager;
