import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';
import { Alert } from 'react-native';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      setIsLoading(true);
      
      // Check for stored credentials
      const credentials = await Keychain.getInternetCredentials('awscostoptimizer');
      
      if (credentials) {
        // Verify token with backend
        const isValid = await verifyToken(credentials.password);
        
        if (isValid) {
          const userData = JSON.parse(credentials.username);
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Clear invalid credentials
          await Keychain.resetInternetCredentials('awscostoptimizer');
        }
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const verifyToken = async (token) => {
    try {
      // Simulate token verification
      await new Promise(resolve => setTimeout(resolve, 500));
      return true; // Mock successful verification
    } catch (error) {
      return false;
    }
  };

  const login = async (email, password) => {
    try {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock authentication
      if (email === 'admin@example.com' && password === 'password123') {
        const userData = {
          id: '1',
          name: 'John Doe',
          email: email,
          role: 'admin',
          avatar: null,
          lastLogin: new Date().toISOString(),
        };

        const token = 'mock-jwt-token-' + Date.now();
        
        // Store credentials securely
        await Keychain.setInternetCredentials(
          'awscostoptimizer',
          JSON.stringify(userData),
          token
        );
        
        // Store user data in AsyncStorage for quick access
        await AsyncStorage.setItem('user', JSON.stringify(userData));
        
        setUser(userData);
        setIsAuthenticated(true);
        
        return { success: true };
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithBiometrics = async () => {
    try {
      // Check if biometrics are available
      const biometrics = await Keychain.getSupportedBiometryType();
      
      if (!biometrics) {
        throw new Error('Biometrics not available');
      }

      // Authenticate with biometrics
      const credentials = await Keychain.getInternetCredentials('awscostoptimizer', {
        accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
        authenticationPrompt: {
          title: 'Authenticate',
          subtitle: 'Use your biometric to sign in',
          description: 'Use your fingerprint or face to authenticate',
          cancel: 'Cancel',
        },
      });

      if (credentials) {
        const userData = JSON.parse(credentials.username);
        setUser(userData);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        throw new Error('Biometric authentication failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Clear stored credentials
      await Keychain.resetInternetCredentials('awscostoptimizer');
      await AsyncStorage.removeItem('user');
      
      setUser(null);
      setIsAuthenticated(false);
      
      Alert.alert('Success', 'Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('Error', 'Failed to logout');
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const updatedUser = { ...user, ...profileData };
      
      // Update stored credentials
      const credentials = await Keychain.getInternetCredentials('awscostoptimizer');
      if (credentials) {
        await Keychain.setInternetCredentials(
          'awscostoptimizer',
          JSON.stringify(updatedUser),
          credentials.password
        );
      }
      
      // Update AsyncStorage
      await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
      
      setUser(updatedUser);
      
      Alert.alert('Success', 'Profile updated successfully');
      return { success: true };
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Update stored credentials with new token
      const newToken = 'mock-jwt-token-' + Date.now();
      await Keychain.setInternetCredentials(
        'awscostoptimizer',
        JSON.stringify(user),
        newToken
      );
      
      Alert.alert('Success', 'Password changed successfully');
      return { success: true };
    } catch (error) {
      Alert.alert('Error', 'Failed to change password');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    loginWithBiometrics,
    logout,
    updateProfile,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
