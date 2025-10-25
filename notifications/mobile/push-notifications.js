/**
 * AWS Cost Optimizer - Mobile Push Notifications
 * React Native push notification service
 */

import PushNotification from 'react-native-push-notification';
import PushNotificationIOS from '@react-native-community/push-notification-ios';
import { Platform, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

class MobilePushNotificationService {
  constructor() {
    this.isInitialized = false;
    this.notificationHandlers = new Map();
    this.backgroundHandlers = new Map();
  }

  /**
   * Initialize push notification service
   */
  initialize() {
    if (this.isInitialized) {
      return;
    }

    // Configure push notifications
    PushNotification.configure({
      // Called when token is generated
      onRegister: (token) => {
        console.log('Push notification token:', token);
        this.saveTokenToServer(token);
      },

      // Called when a remote or local notification is opened or received
      onNotification: (notification) => {
        console.log('Push notification received:', notification);
        this.handleNotification(notification);
      },

      // Called when the user fails to register for remote notifications
      onRegistrationError: (err) => {
        console.error('Push notification registration error:', err);
      },

      // Permissions
      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },

      // Should the initial notification be popped automatically
      popInitialNotification: true,

      // Request permissions on init
      requestPermissions: true,
    });

    // iOS specific configuration
    if (Platform.OS === 'ios') {
      PushNotificationIOS.addEventListener('notification', (notification) => {
        this.handleNotification(notification);
      });

      PushNotificationIOS.addEventListener('localNotification', (notification) => {
        this.handleLocalNotification(notification);
      });
    }

    this.isInitialized = true;
    console.log('Mobile push notification service initialized');
  }

  /**
   * Request notification permissions
   */
  async requestPermissions() {
    try {
      if (Platform.OS === 'ios') {
        const permissions = await PushNotificationIOS.requestPermissions({
          alert: true,
          badge: true,
          sound: true,
        });
        return permissions;
      } else {
        // Android permissions are handled automatically
        return { alert: true, badge: true, sound: true };
      }
    } catch (error) {
      console.error('Error requesting permissions:', error);
      return { alert: false, badge: false, sound: false };
    }
  }

  /**
   * Check if notifications are enabled
   */
  async areNotificationsEnabled() {
    try {
      if (Platform.OS === 'ios') {
        const settings = await PushNotificationIOS.getAuthorizationStatus();
        return settings === PushNotificationIOS.AuthorizationStatus.AUTHORIZED;
      } else {
        // Android - check if app has notification permission
        return true; // Simplified for demo
      }
    } catch (error) {
      console.error('Error checking notification status:', error);
      return false;
    }
  }

  /**
   * Save token to server
   */
  async saveTokenToServer(token) {
    try {
      const authToken = await AsyncStorage.getItem('auth_token');
      
      const response = await fetch('/api/notifications/register-device', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          token: token,
          platform: Platform.OS,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        console.log('Device token saved to server');
      } else {
        console.error('Failed to save device token to server');
      }
    } catch (error) {
      console.error('Error saving token to server:', error);
    }
  }

  /**
   * Handle incoming notification
   */
  handleNotification(notification) {
    console.log('Handling notification:', notification);

    const { userInteraction, data, title, message } = notification;

    // Handle different notification types
    if (data && data.type) {
      switch (data.type) {
        case 'cost_spike':
          this.handleCostSpikeNotification(notification);
          break;
        case 'budget_exceeded':
          this.handleBudgetExceededNotification(notification);
          break;
        case 'anomaly_detected':
          this.handleAnomalyNotification(notification);
          break;
        case 'optimization_opportunity':
          this.handleOptimizationNotification(notification);
          break;
        default:
          this.handleGeneralNotification(notification);
      }
    }

    // Call registered handlers
    this.notificationHandlers.forEach((handler) => {
      try {
        handler(notification);
      } catch (error) {
        console.error('Error in notification handler:', error);
      }
    });

    // Handle user interaction
    if (userInteraction) {
      this.handleNotificationTap(notification);
    }
  }

  /**
   * Handle local notification
   */
  handleLocalNotification(notification) {
    console.log('Local notification received:', notification);
    
    // Handle local notification logic
    this.notificationHandlers.forEach((handler) => {
      try {
        handler(notification);
      } catch (error) {
        console.error('Error in local notification handler:', error);
      }
    });
  }

  /**
   * Handle notification tap
   */
  handleNotificationTap(notification) {
    console.log('Notification tapped:', notification);

    const { data } = notification;
    
    if (data && data.action) {
      switch (data.action) {
        case 'view_dashboard':
          this.navigateToScreen('Dashboard');
          break;
        case 'view_alerts':
          this.navigateToScreen('Alerts');
          break;
        case 'view_analytics':
          this.navigateToScreen('Analytics');
          break;
        case 'view_optimization':
          this.navigateToScreen('Optimization');
          break;
        default:
          this.navigateToScreen('Dashboard');
      }
    }
  }

  /**
   * Navigate to specific screen
   */
  navigateToScreen(screenName) {
    // This would typically use navigation service
    console.log(`Navigating to ${screenName}`);
    
    // Emit navigation event
    this.emit('navigate', { screen: screenName });
  }

  /**
   * Handle cost spike notification
   */
  handleCostSpikeNotification(notification) {
    const { data } = notification;
    
    if (data && data.percentage > 50) {
      // High priority cost spike
      this.showAlert(
        '🚨 High Cost Spike Detected',
        `Your AWS costs increased by ${data.percentage}% in the last ${data.timeframe}. Current cost: $${data.current_cost}`,
        [
          { text: 'View Details', onPress: () => this.navigateToScreen('Analytics') },
          { text: 'Dismiss', style: 'cancel' }
        ]
      );
    }
  }

  /**
   * Handle budget exceeded notification
   */
  handleBudgetExceededNotification(notification) {
    const { data } = notification;
    
    this.showAlert(
      '💰 Budget Exceeded',
      `Your monthly budget has been exceeded by ${data.percentage}%. Current spend: $${data.current_spend}`,
      [
        { text: 'View Budget', onPress: () => this.navigateToScreen('Settings') },
        { text: 'Dismiss', style: 'cancel' }
      ]
    );
  }

  /**
   * Handle anomaly notification
   */
  handleAnomalyNotification(notification) {
    const { data } = notification;
    
    this.showAlert(
      '🔍 Anomaly Detected',
      `Unusual cost pattern detected for ${data.service}. Anomaly score: ${data.score}`,
      [
        { text: 'Investigate', onPress: () => this.navigateToScreen('Analytics') },
        { text: 'Dismiss', style: 'cancel' }
      ]
    );
  }

  /**
   * Handle optimization notification
   */
  handleOptimizationNotification(notification) {
    const { data } = notification;
    
    this.showAlert(
      '💡 Optimization Opportunity',
      `Potential savings of $${data.savings} identified for ${data.service}. ${data.recommendation}`,
      [
        { text: 'View Details', onPress: () => this.navigateToScreen('Optimization') },
        { text: 'Dismiss', style: 'cancel' }
      ]
    );
  }

  /**
   * Handle general notification
   */
  handleGeneralNotification(notification) {
    const { title, message } = notification;
    
    this.showAlert(
      title || 'AWS Cost Optimizer',
      message || 'You have a new notification',
      [
        { text: 'View', onPress: () => this.navigateToScreen('Dashboard') },
        { text: 'Dismiss', style: 'cancel' }
      ]
    );
  }

  /**
   * Show alert dialog
   */
  showAlert(title, message, buttons) {
    Alert.alert(title, message, buttons);
  }

  /**
   * Schedule local notification
   */
  scheduleLocalNotification(title, message, date, data = {}) {
    PushNotification.localNotificationSchedule({
      title: title,
      message: message,
      date: date,
      userInfo: data,
      playSound: true,
      soundName: 'default',
      vibrate: true,
      vibration: 300,
    });
  }

  /**
   * Cancel local notification
   */
  cancelLocalNotification(id) {
    PushNotification.cancelLocalNotifications({ id: id });
  }

  /**
   * Cancel all local notifications
   */
  cancelAllLocalNotifications() {
    PushNotification.cancelAllLocalNotifications();
  }

  /**
   * Get delivered notifications
   */
  async getDeliveredNotifications() {
    try {
      if (Platform.OS === 'ios') {
        return await PushNotificationIOS.getDeliveredNotifications();
      } else {
        // Android implementation
        return [];
      }
    } catch (error) {
      console.error('Error getting delivered notifications:', error);
      return [];
    }
  }

  /**
   * Remove delivered notifications
   */
  async removeDeliveredNotifications(identifiers) {
    try {
      if (Platform.OS === 'ios') {
        await PushNotificationIOS.removeDeliveredNotifications(identifiers);
      } else {
        // Android implementation
        console.log('Removing delivered notifications:', identifiers);
      }
    } catch (error) {
      console.error('Error removing delivered notifications:', error);
    }
  }

  /**
   * Set application badge count
   */
  setApplicationIconBadgeNumber(count) {
    if (Platform.OS === 'ios') {
      PushNotificationIOS.setApplicationIconBadgeNumber(count);
    } else {
      // Android implementation
      PushNotification.setApplicationIconBadgeNumber(count);
    }
  }

  /**
   * Get application badge count
   */
  async getApplicationIconBadgeNumber() {
    try {
      if (Platform.OS === 'ios') {
        return await PushNotificationIOS.getApplicationIconBadgeNumber();
      } else {
        // Android implementation
        return 0;
      }
    } catch (error) {
      console.error('Error getting badge count:', error);
      return 0;
    }
  }

  /**
   * Register notification handler
   */
  addNotificationHandler(handler) {
    const id = Date.now().toString();
    this.notificationHandlers.set(id, handler);
    return id;
  }

  /**
   * Unregister notification handler
   */
  removeNotificationHandler(id) {
    this.notificationHandlers.delete(id);
  }

  /**
   * Register background handler
   */
  addBackgroundHandler(handler) {
    const id = Date.now().toString();
    this.backgroundHandlers.set(id, handler);
    return id;
  }

  /**
   * Unregister background handler
   */
  removeBackgroundHandler(id) {
    this.backgroundHandlers.delete(id);
  }

  /**
   * Emit event
   */
  emit(event, data) {
    console.log(`Event emitted: ${event}`, data);
    // This would typically use an event emitter
  }

  /**
   * Test notification
   */
  sendTestNotification() {
    this.scheduleLocalNotification(
      'Test Notification',
      'This is a test notification from AWS Cost Optimizer',
      new Date(Date.now() + 1000),
      { type: 'test' }
    );
  }
}

// Create singleton instance
const mobilePushNotificationService = new MobilePushNotificationService();

export default mobilePushNotificationService;
