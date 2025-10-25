/**
 * AWS Cost Optimizer - Web Push Notifications
 * Handles browser push notifications for the web application
 */

class PushNotificationService {
  constructor() {
    this.registration = null;
    this.subscription = null;
    this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
    this.vapidPublicKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI8F7Y1zAQcw0uXNu9T3QzFvN44ys5p9yLsfOL3yZR3pAeU5YI4Ff2uD2iI';
  }

  /**
   * Initialize push notification service
   */
  async initialize() {
    if (!this.isSupported) {
      console.warn('Push notifications are not supported in this browser');
      return false;
    }

    try {
      // Register service worker
      this.registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered successfully');

      // Check if user has granted permission
      const permission = await this.getPermissionStatus();
      if (permission === 'granted') {
        await this.subscribe();
      }

      return true;
    } catch (error) {
      console.error('Error initializing push notifications:', error);
      return false;
    }
  }

  /**
   * Request permission for push notifications
   */
  async requestPermission() {
    if (!this.isSupported) {
      throw new Error('Push notifications are not supported');
    }

    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      await this.subscribe();
      return true;
    } else {
      console.log('Permission denied for push notifications');
      return false;
    }
  }

  /**
   * Get current permission status
   */
  async getPermissionStatus() {
    if (!this.isSupported) {
      return 'unsupported';
    }

    return Notification.permission;
  }

  /**
   * Subscribe to push notifications
   */
  async subscribe() {
    if (!this.registration) {
      throw new Error('Service worker not registered');
    }

    try {
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });

      this.subscription = subscription;
      
      // Send subscription to server
      await this.sendSubscriptionToServer(subscription);
      
      console.log('Push subscription created successfully');
      return subscription;
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      throw error;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe() {
    if (!this.subscription) {
      return;
    }

    try {
      const success = await this.subscription.unsubscribe();
      if (success) {
        this.subscription = null;
        await this.removeSubscriptionFromServer();
        console.log('Push subscription removed successfully');
      }
      return success;
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
      throw error;
    }
  }

  /**
   * Send subscription to server
   */
  async sendSubscriptionToServer(subscription) {
    try {
      const response = await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          subscription: subscription,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send subscription to server');
      }

      console.log('Subscription sent to server successfully');
    } catch (error) {
      console.error('Error sending subscription to server:', error);
      throw error;
    }
  }

  /**
   * Remove subscription from server
   */
  async removeSubscriptionFromServer() {
    try {
      const response = await fetch('/api/notifications/unsubscribe', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove subscription from server');
      }

      console.log('Subscription removed from server successfully');
    } catch (error) {
      console.error('Error removing subscription from server:', error);
      throw error;
    }
  }

  /**
   * Show local notification
   */
  async showNotification(title, options = {}) {
    if (!this.registration) {
      throw new Error('Service worker not registered');
    }

    const defaultOptions = {
      body: '',
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

    const notificationOptions = { ...defaultOptions, ...options };

    try {
      await this.registration.showNotification(title, notificationOptions);
      console.log('Local notification shown:', title);
    } catch (error) {
      console.error('Error showing notification:', error);
      throw error;
    }
  }

  /**
   * Handle notification click
   */
  handleNotificationClick(event) {
    event.notification.close();

    const action = event.action;
    const data = event.notification.data;

    if (action === 'view') {
      // Open the app and navigate to relevant page
      window.focus();
      if (data.url) {
        window.location.href = data.url;
      }
    } else if (action === 'dismiss') {
      // Just close the notification
      console.log('Notification dismissed');
    } else {
      // Default click behavior
      window.focus();
      if (data.url) {
        window.location.href = data.url;
      }
    }
  }

  /**
   * Handle push message
   */
  handlePushMessage(event) {
    console.log('Push message received:', event);

    const data = event.data ? event.data.json() : {};
    const title = data.title || 'AWS Cost Optimizer';
    const options = {
      body: data.message || 'You have a new notification',
      icon: data.icon || '/icons/icon-192x192.png',
      badge: data.badge || '/icons/badge-72x72.png',
      tag: data.tag || 'cost-optimizer-notification',
      requireInteraction: data.requireInteraction || false,
      silent: data.silent || false,
      vibrate: data.vibrate || [200, 100, 200],
      actions: data.actions || [
        {
          action: 'view',
          title: 'View Details'
        },
        {
          action: 'dismiss',
          title: 'Dismiss'
        }
      ],
      data: {
        url: data.url || '/dashboard',
        type: data.type || 'general',
        priority: data.priority || 'medium',
        timestamp: Date.now()
      }
    };

    event.waitUntil(
      this.showNotification(title, options)
    );
  }

  /**
   * Get authentication token
   */
  getAuthToken() {
    return localStorage.getItem('token') || '';
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  /**
   * Check if notifications are enabled
   */
  isEnabled() {
    return this.subscription !== null && Notification.permission === 'granted';
  }

  /**
   * Get subscription info
   */
  getSubscriptionInfo() {
    if (!this.subscription) {
      return null;
    }

    return {
      endpoint: this.subscription.endpoint,
      keys: this.subscription.getKey ? {
        p256dh: this.subscription.getKey('p256dh'),
        auth: this.subscription.getKey('auth')
      } : null
    };
  }
}

// Create global instance
window.pushNotificationService = new PushNotificationService();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await window.pushNotificationService.initialize();
    console.log('Push notification service initialized');
  } catch (error) {
    console.error('Failed to initialize push notification service:', error);
  }
});

// Handle service worker messages
navigator.serviceWorker.addEventListener('message', (event) => {
  console.log('Service worker message:', event.data);
  
  if (event.data.type === 'NOTIFICATION_CLICK') {
    window.pushNotificationService.handleNotificationClick(event.data);
  }
});

// Handle push events
navigator.serviceWorker.addEventListener('push', (event) => {
  window.pushNotificationService.handlePushMessage(event);
});

// Export for use in other modules
export default PushNotificationService;
