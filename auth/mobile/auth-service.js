/**
 * AWS Cost Optimizer - Mobile Authentication Service
 * React Native authentication service with biometric support
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';
import * as LocalAuthentication from 'expo-local-authentication';
import { Alert } from 'react-native';
import axios from 'axios';

class MobileAuthService {
  constructor() {
    this.baseURL = 'https://api.awscostoptimizer.com';
    this.isAuthenticated = false;
    this.user = null;
    this.session = null;
    this.biometricAvailable = false;
    
    // Initialize auth service
    this.init();
  }

  /**
   * Initialize authentication service
   */
  async init() {
    try {
      // Check biometric availability
      await this.checkBiometricAvailability();
      
      // Check for existing session
      await this.checkExistingSession();
      
      console.log('Mobile auth service initialized');
    } catch (error) {
      console.error('Error initializing mobile auth service:', error);
    }
  }

  /**
   * Check biometric availability
   */
  async checkBiometricAvailability() {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      
      this.biometricAvailable = hasHardware && isEnrolled;
      
      console.log('Biometric availability:', this.biometricAvailable);
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      this.biometricAvailable = false;
    }
  }

  /**
   * Check existing session
   */
  async checkExistingSession() {
    try {
      const credentials = await Keychain.getInternetCredentials('awscostoptimizer');
      
      if (credentials) {
        const sessionData = JSON.parse(credentials.username);
        const token = credentials.password;
        
        // Verify token
        const isValid = await this.verifyToken(token);
        
        if (isValid) {
          this.session = sessionData;
          this.user = sessionData.user;
          this.isAuthenticated = true;
          console.log('Existing session restored');
        } else {
          // Clear invalid credentials
          await Keychain.resetInternetCredentials('awscostoptimizer');
        }
      }
    } catch (error) {
      console.error('Error checking existing session:', error);
    }
  }

  /**
   * Verify token
   */
  async verifyToken(token) {
    try {
      const response = await axios.get(`${this.baseURL}/api/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Login with email and password
   */
  async login(email, password, mfaToken = null) {
    try {
      const response = await axios.post(`${this.baseURL}/api/auth/login`, {
        email,
        password,
        mfaToken
      });

      const { user, session, mfaRequired } = response.data;

      if (mfaRequired) {
        return { success: true, mfaRequired: true, user };
      }

      // Store credentials securely
      await this.storeCredentials(user, session);
      
      this.user = user;
      this.session = session;
      this.isAuthenticated = true;

      return { success: true, mfaRequired: false };
    } catch (error) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  }

  /**
   * Login with biometrics
   */
  async loginWithBiometrics() {
    try {
      if (!this.biometricAvailable) {
        throw new Error('Biometrics not available');
      }

      // Authenticate with biometrics
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to access AWS Cost Optimizer',
        cancelLabel: 'Cancel',
        fallbackLabel: 'Use Password',
        disableDeviceFallback: false
      });

      if (!result.success) {
        throw new Error('Biometric authentication failed');
      }

      // Get stored credentials
      const credentials = await Keychain.getInternetCredentials('awscostoptimizer', {
        accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
        authenticationPrompt: {
          title: 'Authenticate',
          subtitle: 'Use your biometric to sign in',
          description: 'Use your fingerprint or face to authenticate',
          cancel: 'Cancel'
        }
      });

      if (credentials) {
        const sessionData = JSON.parse(credentials.username);
        const token = credentials.password;

        // Verify token
        const isValid = await this.verifyToken(token);
        
        if (isValid) {
          this.session = sessionData;
          this.user = sessionData.user;
          this.isAuthenticated = true;
          
          return { success: true };
        } else {
          throw new Error('Invalid stored credentials');
        }
      } else {
        throw new Error('No stored credentials found');
      }
    } catch (error) {
      console.error('Biometric login error:', error);
      throw error;
    }
  }

  /**
   * Verify MFA token
   */
  async verifyMfa(mfaToken) {
    try {
      const response = await axios.post(`${this.baseURL}/api/auth/verify-mfa`, {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      const { session: sessionData } = response.data;

      // Update stored credentials
      await this.storeCredentials(this.user, sessionData);
      
      this.session = sessionData;
      this.isAuthenticated = true;

      return { success: true };
    } catch (error) {
      console.error('MFA verification error:', error);
      throw new Error(error.response?.data?.message || 'MFA verification failed');
    }
  }

  /**
   * Register new user
   */
  async register(email, username, password, role = 'viewer') {
    try {
      const response = await axios.post(`${this.baseURL}/api/auth/register`, {
        email,
        username,
        password,
        role
      });

      return { success: true, message: 'Registration successful. Please check your email for verification.' };
    } catch (error) {
      console.error('Registration error:', error);
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  }

  /**
   * Logout
   */
  async logout() {
    try {
      if (this.session?.token) {
        await axios.post(`${this.baseURL}/api/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${this.session.token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await this.clearAuthData();
    }
  }

  /**
   * Clear authentication data
   */
  async clearAuthData() {
    try {
      // Clear keychain
      await Keychain.resetInternetCredentials('awscostoptimizer');
      
      // Clear async storage
      await AsyncStorage.multiRemove(['auth_token', 'refresh_token', 'user_data']);
      
      this.user = null;
      this.session = null;
      this.isAuthenticated = false;
      
      console.log('Authentication data cleared');
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  }

  /**
   * Store credentials securely
   */
  async storeCredentials(user, session) {
    try {
      const sessionData = {
        user,
        token: session.token,
        refreshToken: session.refreshToken,
        expiresAt: session.expiresAt
      };

      // Store in keychain with biometric protection
      await Keychain.setInternetCredentials(
        'awscostoptimizer',
        JSON.stringify(sessionData),
        session.token,
        {
          accessControl: this.biometricAvailable ? 
            Keychain.ACCESS_CONTROL.BIOMETRY_ANY : 
            Keychain.ACCESS_CONTROL.DEFAULT
        }
      );

      // Store in async storage for quick access
      await AsyncStorage.setItem('user_data', JSON.stringify(user));
      await AsyncStorage.setItem('auth_token', session.token);
      await AsyncStorage.setItem('refresh_token', session.refreshToken);
      
      console.log('Credentials stored securely');
    } catch (error) {
      console.error('Error storing credentials:', error);
      throw error;
    }
  }

  /**
   * Refresh token
   */
  async refreshToken() {
    try {
      if (!this.session?.refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post(`${this.baseURL}/api/auth/refresh`, {
        refreshToken: this.session.refreshToken
      });

      const { session: sessionData } = response.data;

      // Update stored credentials
      await this.storeCredentials(this.user, sessionData);
      
      this.session = sessionData;
      
      return sessionData;
    } catch (error) {
      console.error('Token refresh error:', error);
      await this.clearAuthData();
      throw error;
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email) {
    try {
      await axios.post(`${this.baseURL}/api/auth/forgot-password`, { email });
      return { success: true, message: 'Password reset email sent' };
    } catch (error) {
      console.error('Password reset request error:', error);
      throw new Error(error.response?.data?.message || 'Password reset request failed');
    }
  }

  /**
   * Reset password
   */
  async resetPassword(token, newPassword) {
    try {
      await axios.post(`${this.baseURL}/api/auth/reset-password`, {
        token,
        password: newPassword
      });
      return { success: true, message: 'Password reset successful' };
    } catch (error) {
      console.error('Password reset error:', error);
      throw new Error(error.response?.data?.message || 'Password reset failed');
    }
  }

  /**
   * Verify email
   */
  async verifyEmail(token) {
    try {
      await axios.post(`${this.baseURL}/api/auth/verify-email`, { token });
      return { success: true, message: 'Email verified successfully' };
    } catch (error) {
      console.error('Email verification error:', error);
      throw new Error(error.response?.data?.message || 'Email verification failed');
    }
  }

  /**
   * Setup MFA
   */
  async setupMfa() {
    try {
      const response = await axios.post(`${this.baseURL}/api/auth/setup-mfa`, {}, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      return response.data;
    } catch (error) {
      console.error('MFA setup error:', error);
      throw new Error(error.response?.data?.message || 'MFA setup failed');
    }
  }

  /**
   * Enable MFA
   */
  async enableMfa(mfaToken) {
    try {
      await axios.post(`${this.baseURL}/api/auth/enable-mfa`, {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      // Update user data
      const userData = await this.getCurrentUser();
      this.user = userData;

      return { success: true, message: 'MFA enabled successfully' };
    } catch (error) {
      console.error('MFA enable error:', error);
      throw new Error(error.response?.data?.message || 'MFA enable failed');
    }
  }

  /**
   * Disable MFA
   */
  async disableMfa(mfaToken) {
    try {
      await axios.post(`${this.baseURL}/api/auth/disable-mfa`, {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      // Update user data
      const userData = await this.getCurrentUser();
      this.user = userData;

      return { success: true, message: 'MFA disabled successfully' };
    } catch (error) {
      console.error('MFA disable error:', error);
      throw new Error(error.response?.data?.message || 'MFA disable failed');
    }
  }

  /**
   * Get current user
   */
  async getCurrentUser() {
    try {
      const response = await axios.get(`${this.baseURL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw new Error('Failed to get user data');
    }
  }

  /**
   * Update profile
   */
  async updateProfile(profileData) {
    try {
      const response = await axios.put(`${this.baseURL}/api/auth/profile`, profileData, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      this.user = response.data;
      return { success: true, message: 'Profile updated successfully' };
    } catch (error) {
      console.error('Profile update error:', error);
      throw new Error(error.response?.data?.message || 'Profile update failed');
    }
  }

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    try {
      await axios.post(`${this.baseURL}/api/auth/change-password`, {
        currentPassword,
        newPassword
      }, {
        headers: { Authorization: `Bearer ${this.session?.token}` }
      });

      return { success: true, message: 'Password changed successfully' };
    } catch (error) {
      console.error('Password change error:', error);
      throw new Error(error.response?.data?.message || 'Password change failed');
    }
  }

  /**
   * Get auth headers
   */
  getAuthHeaders() {
    return {
      Authorization: `Bearer ${this.session?.token}`
    };
  }

  /**
   * Check if user has role
   */
  hasRole(requiredRole) {
    if (!this.user) return false;
    
    const roleHierarchy = {
      'guest': 0,
      'viewer': 1,
      'analyst': 2,
      'manager': 3,
      'admin': 4
    };

    const userLevel = roleHierarchy[this.user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;

    return userLevel >= requiredLevel;
  }

  /**
   * Check if user has permission
   */
  hasPermission(permission) {
    if (!this.user) return false;

    const permissions = {
      'admin': ['*'],
      'manager': ['read', 'write', 'delete', 'manage_users'],
      'analyst': ['read', 'write', 'create_reports'],
      'viewer': ['read'],
      'guest': []
    };

    const userPermissions = permissions[this.user.role] || [];
    return userPermissions.includes('*') || userPermissions.includes(permission);
  }

  /**
   * Show biometric setup alert
   */
  showBiometricSetupAlert() {
    Alert.alert(
      'Enable Biometric Authentication',
      'Would you like to enable biometric authentication for quick and secure access?',
      [
        {
          text: 'Not Now',
          style: 'cancel'
        },
        {
          text: 'Enable',
          onPress: () => {
            this.setupBiometricAuth();
          }
        }
      ]
    );
  }

  /**
   * Setup biometric authentication
   */
  async setupBiometricAuth() {
    try {
      if (!this.biometricAvailable) {
        Alert.alert('Biometrics Not Available', 'Biometric authentication is not available on this device.');
        return;
      }

      // Authenticate with biometrics
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Enable biometric authentication',
        cancelLabel: 'Cancel',
        fallbackLabel: 'Use Password'
      });

      if (result.success) {
        // Store biometric preference
        await AsyncStorage.setItem('biometric_enabled', 'true');
        Alert.alert('Success', 'Biometric authentication enabled successfully!');
      }
    } catch (error) {
      console.error('Biometric setup error:', error);
      Alert.alert('Error', 'Failed to setup biometric authentication.');
    }
  }

  /**
   * Check if biometric is enabled
   */
  async isBiometricEnabled() {
    try {
      const enabled = await AsyncStorage.getItem('biometric_enabled');
      return enabled === 'true';
    } catch (error) {
      return false;
    }
  }

  /**
   * Get authentication status
   */
  getAuthStatus() {
    return {
      isAuthenticated: this.isAuthenticated,
      user: this.user,
      session: this.session,
      biometricAvailable: this.biometricAvailable
    };
  }
}

// Create singleton instance
const mobileAuthService = new MobileAuthService();

export default mobileAuthService;
