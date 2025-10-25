/**
 * AWS Cost Optimizer - Progressive Web App (PWA) Configuration
 * Handles PWA features for offline functionality
 */

class ProgressiveWebApp {
  constructor() {
    this.isInstalled = false;
    this.deferredPrompt = null;
    this.swRegistration = null;
    
    // Initialize PWA
    this.init();
  }

  /**
   * Initialize PWA
   */
  async init() {
    try {
      // Set up event listeners
      this.setupEventListeners();
      
      // Check if app is already installed
      this.checkInstallStatus();
      
      // Set up service worker
      await this.setupServiceWorker();
      
      // Set up app manifest
      this.setupAppManifest();
      
      console.log('PWA initialized successfully');
    } catch (error) {
      console.error('Error initializing PWA:', error);
    }
  }

  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Before install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('PWA install prompt triggered');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallBanner();
    });

    // App installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA installed successfully');
      this.isInstalled = true;
      this.hideInstallBanner();
      this.trackInstallation();
    });

    // Service worker updates
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('Service worker controller changed');
      this.handleServiceWorkerUpdate();
    });

    // Online/offline events
    window.addEventListener('online', () => {
      this.handleOnlineEvent();
    });

    window.addEventListener('offline', () => {
      this.handleOfflineEvent();
    });

    // Visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        this.handleAppVisible();
      } else {
        this.handleAppHidden();
      }
    });
  }

  /**
   * Check if app is installed
   */
  checkInstallStatus() {
    // Check if running in standalone mode (installed)
    if (window.matchMedia('(display-mode: standalone)').matches) {
      this.isInstalled = true;
      console.log('App is running in standalone mode');
    }

    // Check if running in fullscreen mode
    if (window.matchMedia('(display-mode: fullscreen)').matches) {
      this.isInstalled = true;
      console.log('App is running in fullscreen mode');
    }
  }

  /**
   * Set up service worker
   */
  async setupServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        this.swRegistration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', this.swRegistration);

        // Check for updates
        this.swRegistration.addEventListener('updatefound', () => {
          this.handleServiceWorkerUpdate();
        });

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
   * Set up app manifest
   */
  setupAppManifest() {
    // Create manifest link if it doesn't exist
    if (!document.querySelector('link[rel="manifest"]')) {
      const manifestLink = document.createElement('link');
      manifestLink.rel = 'manifest';
      manifestLink.href = '/manifest.json';
      document.head.appendChild(manifestLink);
    }

    // Set theme color
    const themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (themeColorMeta) {
      themeColorMeta.content = '#3b82f6';
    } else {
      const meta = document.createElement('meta');
      meta.name = 'theme-color';
      meta.content = '#3b82f6';
      document.head.appendChild(meta);
    }

    // Set viewport for mobile
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta) {
      viewportMeta.content = 'width=device-width, initial-scale=1, user-scalable=no';
    }
  }

  /**
   * Show install banner
   */
  showInstallBanner() {
    // Create install banner
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      right: 20px;
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      color: white;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 12px;
      animation: slideUp 0.3s ease-out;
    `;

    banner.innerHTML = `
      <div style="flex: 1;">
        <div style="font-weight: 600; margin-bottom: 4px;">Install AWS Cost Optimizer</div>
        <div style="font-size: 14px; opacity: 0.9;">Get quick access and offline functionality</div>
      </div>
      <button id="pwa-install-btn" style="
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
      ">Install</button>
      <button id="pwa-dismiss-btn" style="
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        opacity: 0.7;
        padding: 4px;
      ">×</button>
    `;

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideUp {
        from {
          transform: translateY(100%);
          opacity: 0;
        }
        to {
          transform: translateY(0);
          opacity: 1;
        }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(banner);

    // Add event listeners
    document.getElementById('pwa-install-btn').addEventListener('click', () => {
      this.installApp();
    });

    document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
      this.hideInstallBanner();
    });

    // Auto-hide after 10 seconds
    setTimeout(() => {
      this.hideInstallBanner();
    }, 10000);
  }

  /**
   * Hide install banner
   */
  hideInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.style.animation = 'slideUp 0.3s ease-out reverse';
      setTimeout(() => {
        if (banner.parentNode) {
          banner.parentNode.removeChild(banner);
        }
      }, 300);
    }
  }

  /**
   * Install app
   */
  async installApp() {
    if (!this.deferredPrompt) {
      console.log('Install prompt not available');
      return;
    }

    try {
      // Show install prompt
      this.deferredPrompt.prompt();
      
      // Wait for user response
      const { outcome } = await this.deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
        this.trackInstallation('accepted');
      } else {
        console.log('User dismissed the install prompt');
        this.trackInstallation('dismissed');
      }
      
      // Clear the deferred prompt
      this.deferredPrompt = null;
      this.hideInstallBanner();
      
    } catch (error) {
      console.error('Error installing app:', error);
    }
  }

  /**
   * Handle service worker update
   */
  handleServiceWorkerUpdate() {
    if (this.swRegistration && this.swRegistration.waiting) {
      // Show update notification
      this.showUpdateNotification();
    }
  }

  /**
   * Show update notification
   */
  showUpdateNotification() {
    const notification = document.createElement('div');
    notification.id = 'pwa-update-notification';
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      left: 20px;
      right: 20px;
      background: #10b981;
      color: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 12px;
    `;

    notification.innerHTML = `
      <div style="flex: 1;">
        <div style="font-weight: 600;">Update Available</div>
        <div style="font-size: 14px; opacity: 0.9;">A new version is ready to install</div>
      </div>
      <button id="pwa-update-btn" style="
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        cursor: pointer;
      ">Update</button>
    `;

    document.body.appendChild(notification);

    // Add event listener
    document.getElementById('pwa-update-btn').addEventListener('click', () => {
      this.updateApp();
    });
  }

  /**
   * Update app
   */
  updateApp() {
    if (this.swRegistration && this.swRegistration.waiting) {
      // Tell the waiting service worker to skip waiting
      this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      
      // Reload the page
      window.location.reload();
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
      case 'UPDATE_AVAILABLE':
        this.showUpdateNotification();
        break;
      default:
        console.log('Unknown service worker message:', data);
    }
  }

  /**
   * Handle online event
   */
  handleOnlineEvent() {
    console.log('App is online');
    // Trigger background sync
    if (this.swRegistration) {
      this.swRegistration.sync.register('cost-data-sync');
    }
  }

  /**
   * Handle offline event
   */
  handleOfflineEvent() {
    console.log('App is offline');
    // Show offline indicator
    this.showOfflineIndicator();
  }

  /**
   * Show offline indicator
   */
  showOfflineIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'pwa-offline-indicator';
    indicator.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #ef4444;
      color: white;
      padding: 8px;
      text-align: center;
      font-size: 14px;
      z-index: 1001;
    `;
    indicator.textContent = 'You are offline. Some features may be limited.';
    document.body.appendChild(indicator);
  }

  /**
   * Hide offline indicator
   */
  hideOfflineIndicator() {
    const indicator = document.getElementById('pwa-offline-indicator');
    if (indicator && indicator.parentNode) {
      indicator.parentNode.removeChild(indicator);
    }
  }

  /**
   * Handle app visible
   */
  handleAppVisible() {
    console.log('App is visible');
    // Check for updates
    if (this.swRegistration) {
      this.swRegistration.update();
    }
  }

  /**
   * Handle app hidden
   */
  handleAppHidden() {
    console.log('App is hidden');
    // Save current state
    this.saveAppState();
  }

  /**
   * Save app state
   */
  saveAppState() {
    try {
      const state = {
        url: window.location.href,
        scrollPosition: window.pageYOffset,
        timestamp: Date.now()
      };
      
      localStorage.setItem('pwa-app-state', JSON.stringify(state));
    } catch (error) {
      console.error('Error saving app state:', error);
    }
  }

  /**
   * Restore app state
   */
  restoreAppState() {
    try {
      const state = localStorage.getItem('pwa-app-state');
      if (state) {
        const parsedState = JSON.parse(state);
        
        // Restore scroll position
        if (parsedState.scrollPosition) {
          window.scrollTo(0, parsedState.scrollPosition);
        }
      }
    } catch (error) {
      console.error('Error restoring app state:', error);
    }
  }

  /**
   * Track installation
   */
  trackInstallation(outcome = 'installed') {
    // Send analytics event
    if (typeof gtag !== 'undefined') {
      gtag('event', 'pwa_install', {
        event_category: 'PWA',
        event_label: outcome,
        value: 1
      });
    }
    
    console.log(`PWA installation tracked: ${outcome}`);
  }

  /**
   * Get PWA status
   */
  getPWAStatus() {
    return {
      isInstalled: this.isInstalled,
      isOnline: navigator.onLine,
      hasServiceWorker: !!this.swRegistration,
      canInstall: !!this.deferredPrompt,
      displayMode: this.getDisplayMode()
    };
  }

  /**
   * Get display mode
   */
  getDisplayMode() {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return 'standalone';
    } else if (window.matchMedia('(display-mode: fullscreen)').matches) {
      return 'fullscreen';
    } else {
      return 'browser';
    }
  }

  /**
   * Check if app is installable
   */
  isInstallable() {
    return !!this.deferredPrompt;
  }

  /**
   * Check if app is installed
   */
  isAppInstalled() {
    return this.isInstalled;
  }
}

// Create global instance
window.pwa = new ProgressiveWebApp();

// Export for use in other modules
export default ProgressiveWebApp;
