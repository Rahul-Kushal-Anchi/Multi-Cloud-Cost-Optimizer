/**
 * AWS Cost Optimizer - Mobile Offline Manager
 * Handles offline functionality for the React Native mobile application
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';
import { Alert } from 'react-native';
import SQLite from 'react-native-sqlite-storage';

class MobileOfflineManager {
  constructor() {
    this.isOnline = true;
    this.syncQueue = [];
    this.db = null;
    this.dbName = 'aws_cost_optimizer_offline.db';
    this.dbVersion = 1;
    
    // Initialize offline manager
    this.init();
  }

  /**
   * Initialize offline manager
   */
  async init() {
    try {
      // Set up network listener
      this.setupNetworkListener();
      
      // Initialize SQLite database
      await this.initSQLite();
      
      // Start background sync
      this.startBackgroundSync();
      
      console.log('Mobile offline manager initialized successfully');
    } catch (error) {
      console.error('Error initializing mobile offline manager:', error);
    }
  }

  /**
   * Set up network listener
   */
  setupNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected;
      
      if (!wasOnline && this.isOnline) {
        this.onConnectionRestored();
      } else if (wasOnline && !this.isOnline) {
        this.onConnectionLost();
      }
    });
  }

  /**
   * Initialize SQLite database
   */
  async initSQLite() {
    try {
      // Open database
      this.db = await SQLite.openDatabase({
        name: this.dbName,
        version: this.dbVersion,
        description: 'AWS Cost Optimizer Offline Database',
        size: 200000
      });

      // Create tables
      await this.createTables();
      
      console.log('SQLite database initialized successfully');
    } catch (error) {
      console.error('Error initializing SQLite database:', error);
    }
  }

  /**
   * Create database tables
   */
  async createTables() {
    const createTables = [
      // Cost data table
      `CREATE TABLE IF NOT EXISTS cost_data (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        service TEXT NOT NULL,
        cost REAL NOT NULL,
        region TEXT,
        synced INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT (strftime('%s', 'now')),
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      )`,
      
      // Notifications table
      `CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT NOT NULL,
        read INTEGER DEFAULT 0,
        synced INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      )`,
      
      // Sync queue table
      `CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        priority TEXT DEFAULT 'normal',
        attempts INTEGER DEFAULT 0,
        max_attempts INTEGER DEFAULT 3,
        created_at INTEGER DEFAULT (strftime('%s', 'now'))
      )`,
      
      // User preferences table
      `CREATE TABLE IF NOT EXISTS user_preferences (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        synced INTEGER DEFAULT 0,
        updated_at INTEGER DEFAULT (strftime('%s', 'now'))
      )`,
      
      // Cache metadata table
      `CREATE TABLE IF NOT EXISTS cache_metadata (
        key TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        timestamp INTEGER DEFAULT (strftime('%s', 'now')),
        size INTEGER DEFAULT 0,
        synced INTEGER DEFAULT 1
      )`
    ];

    for (const sql of createTables) {
      await this.db.executeSql(sql);
    }
  }

  /**
   * Start background sync
   */
  startBackgroundSync() {
    // Set up periodic sync
    setInterval(async () => {
      if (this.isOnline) {
        await this.syncPendingData();
      }
    }, 30000); // Sync every 30 seconds when online
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
  }

  /**
   * Show connection status
   */
  showConnectionStatus(status) {
    // This would typically show a toast or banner
    console.log(`Connection status: ${status}`);
    
    if (status === 'offline') {
      // Show offline banner
      Alert.alert(
        'Offline Mode',
        'You are currently offline. Some features may be limited.',
        [{ text: 'OK' }]
      );
    }
  }

  /**
   * Cache data for offline use
   */
  async cacheData(key, data, metadata = {}) {
    try {
      const cacheItem = {
        key: key,
        data: JSON.stringify(data),
        timestamp: Date.now(),
        size: JSON.stringify(data).length,
        synced: true
      };

      await this.db.executeSql(
        'INSERT OR REPLACE INTO cache_metadata (key, data, timestamp, size, synced) VALUES (?, ?, ?, ?, ?)',
        [cacheItem.key, cacheItem.data, cacheItem.timestamp, cacheItem.size, cacheItem.synced ? 1 : 0]
      );

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
      const result = await this.db.executeSql(
        'SELECT data FROM cache_metadata WHERE key = ?',
        [key]
      );

      if (result[0].rows.length > 0) {
        const data = result[0].rows.item(0).data;
        return JSON.parse(data);
      }

      return null;
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
        data: JSON.stringify(data),
        priority: priority,
        attempts: 0,
        maxAttempts: 3
      };

      await this.db.executeSql(
        'INSERT INTO sync_queue (id, type, data, priority, attempts, max_attempts) VALUES (?, ?, ?, ?, ?, ?)',
        [syncItem.id, syncItem.type, syncItem.data, syncItem.priority, syncItem.attempts, syncItem.maxAttempts]
      );

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
      const result = await this.db.executeSql(
        'SELECT * FROM sync_queue ORDER BY created_at ASC'
      );

      const pendingItems = [];
      for (let i = 0; i < result[0].rows.length; i++) {
        pendingItems.push(result[0].rows.item(i));
      }

      for (const item of pendingItems) {
        try {
          await this.syncItem(item);
          
          // Remove from queue after successful sync
          await this.db.executeSql(
            'DELETE FROM sync_queue WHERE id = ?',
            [item.id]
          );
        } catch (error) {
          console.error(`Error syncing item ${item.id}:`, error);
          
          // Increment attempts
          const newAttempts = item.attempts + 1;
          
          if (newAttempts >= item.max_attempts) {
            console.error(`Max attempts reached for item ${item.id}, removing from queue`);
            await this.db.executeSql(
              'DELETE FROM sync_queue WHERE id = ?',
              [item.id]
            );
          } else {
            // Update attempts
            await this.db.executeSql(
              'UPDATE sync_queue SET attempts = ? WHERE id = ?',
              [newAttempts, item.id]
            );
          }
        }
      }
    } catch (error) {
      console.error('Error syncing pending data:', error);
    }
  }

  /**
   * Sync individual item
   */
  async syncItem(item) {
    const { type, data } = item;
    const parsedData = JSON.parse(data);
    
    switch (type) {
      case 'cost_data':
        await this.syncCostData(parsedData);
        break;
      case 'notification':
        await this.syncNotification(parsedData);
        break;
      case 'user_preference':
        await this.syncUserPreference(parsedData);
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
      const authToken = await this.getAuthToken();
      
      const response = await fetch('/api/cost-data/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
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
      const authToken = await this.getAuthToken();
      
      const response = await fetch('/api/notifications/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
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
      const authToken = await this.getAuthToken();
      
      const response = await fetch('/api/user/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
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
      const authToken = await this.getAuthToken();
      
      const response = await fetch('/api/cost-data/latest', {
        headers: {
          'Authorization': `Bearer ${authToken}`
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
      const authToken = await this.getAuthToken();
      
      const response = await fetch('/api/notifications/latest', {
        headers: {
          'Authorization': `Bearer ${authToken}`
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
   * Store cost data locally
   */
  async storeCostData(costData) {
    try {
      await this.db.executeSql(
        'INSERT OR REPLACE INTO cost_data (id, date, service, cost, region, synced) VALUES (?, ?, ?, ?, ?, ?)',
        [costData.id, costData.date, costData.service, costData.cost, costData.region, 0]
      );

      // Queue for sync
      await this.queueForSync('cost_data', costData);
    } catch (error) {
      console.error('Error storing cost data:', error);
    }
  }

  /**
   * Get local cost data
   */
  async getLocalCostData(limit = 100) {
    try {
      const result = await this.db.executeSql(
        'SELECT * FROM cost_data ORDER BY date DESC LIMIT ?',
        [limit]
      );

      const costData = [];
      for (let i = 0; i < result[0].rows.length; i++) {
        costData.push(result[0].rows.item(i));
      }

      return costData;
    } catch (error) {
      console.error('Error getting local cost data:', error);
      return [];
    }
  }

  /**
   * Store notification locally
   */
  async storeNotification(notification) {
    try {
      await this.db.executeSql(
        'INSERT OR REPLACE INTO notifications (id, type, title, message, priority, read, synced) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [notification.id, notification.type, notification.title, notification.message, notification.priority, 0, 0]
      );

      // Queue for sync
      await this.queueForSync('notification', notification);
    } catch (error) {
      console.error('Error storing notification:', error);
    }
  }

  /**
   * Get local notifications
   */
  async getLocalNotifications(limit = 50) {
    try {
      const result = await this.db.executeSql(
        'SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?',
        [limit]
      );

      const notifications = [];
      for (let i = 0; i < result[0].rows.length; i++) {
        notifications.push(result[0].rows.item(i));
      }

      return notifications;
    } catch (error) {
      console.error('Error getting local notifications:', error);
      return [];
    }
  }

  /**
   * Mark notification as read
   */
  async markNotificationAsRead(notificationId) {
    try {
      await this.db.executeSql(
        'UPDATE notifications SET read = 1 WHERE id = ?',
        [notificationId]
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }

  /**
   * Store user preference
   */
  async storeUserPreference(key, value) {
    try {
      await this.db.executeSql(
        'INSERT OR REPLACE INTO user_preferences (key, value, synced) VALUES (?, ?, ?)',
        [key, JSON.stringify(value), 0]
      );

      // Queue for sync
      await this.queueForSync('user_preference', { key, value });
    } catch (error) {
      console.error('Error storing user preference:', error);
    }
  }

  /**
   * Get user preference
   */
  async getUserPreference(key) {
    try {
      const result = await this.db.executeSql(
        'SELECT value FROM user_preferences WHERE key = ?',
        [key]
      );

      if (result[0].rows.length > 0) {
        return JSON.parse(result[0].rows.item(0).value);
      }

      return null;
    } catch (error) {
      console.error('Error getting user preference:', error);
      return null;
    }
  }

  /**
   * Get authentication token
   */
  async getAuthToken() {
    try {
      return await AsyncStorage.getItem('auth_token') || '';
    } catch (error) {
      console.error('Error getting auth token:', error);
      return '';
    }
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
  async getOfflineStatus() {
    try {
      const result = await this.db.executeSql(
        'SELECT COUNT(*) as count FROM sync_queue'
      );

      const pendingCount = result[0].rows.item(0).count;
      const lastSync = await AsyncStorage.getItem('last-sync');

      return {
        isOnline: this.isOnline,
        pendingSyncCount: pendingCount,
        lastSync: lastSync
      };
    } catch (error) {
      console.error('Error getting offline status:', error);
      return {
        isOnline: this.isOnline,
        pendingSyncCount: 0,
        lastSync: null
      };
    }
  }

  /**
   * Clear offline data
   */
  async clearOfflineData() {
    try {
      // Clear all tables
      await this.db.executeSql('DELETE FROM cost_data');
      await this.db.executeSql('DELETE FROM notifications');
      await this.db.executeSql('DELETE FROM sync_queue');
      await this.db.executeSql('DELETE FROM user_preferences');
      await this.db.executeSql('DELETE FROM cache_metadata');

      // Clear AsyncStorage
      await AsyncStorage.removeItem('last-sync');

      console.log('Offline data cleared successfully');
    } catch (error) {
      console.error('Error clearing offline data:', error);
    }
  }

  /**
   * Get database size
   */
  async getDatabaseSize() {
    try {
      const result = await this.db.executeSql(
        'SELECT COUNT(*) as count FROM cost_data'
      );
      const costDataCount = result[0].rows.item(0).count;

      const result2 = await this.db.executeSql(
        'SELECT COUNT(*) as count FROM notifications'
      );
      const notificationsCount = result2[0].rows.item(0).count;

      const result3 = await this.db.executeSql(
        'SELECT COUNT(*) as count FROM sync_queue'
      );
      const syncQueueCount = result3[0].rows.item(0).count;

      return {
        costDataCount,
        notificationsCount,
        syncQueueCount,
        totalRecords: costDataCount + notificationsCount + syncQueueCount
      };
    } catch (error) {
      console.error('Error getting database size:', error);
      return {
        costDataCount: 0,
        notificationsCount: 0,
        syncQueueCount: 0,
        totalRecords: 0
      };
    }
  }
}

// Create singleton instance
const mobileOfflineManager = new MobileOfflineManager();

export default mobileOfflineManager;
