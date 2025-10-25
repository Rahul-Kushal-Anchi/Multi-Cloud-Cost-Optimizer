/**
 * AWS Cost Optimizer - Web Authentication Context
 * React context for authentication state management
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

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
  const [session, setSession] = useState(null);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [mfaSetup, setMfaSetup] = useState(null);

  // Initialize authentication
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Check for stored session
      const storedToken = localStorage.getItem('auth_token');
      const storedRefreshToken = localStorage.getItem('refresh_token');
      
      if (storedToken && storedRefreshToken) {
        // Verify token
        const isValid = await verifyToken(storedToken);
        
        if (isValid) {
          // Get user data
          const userData = await getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          setSession({ token: storedToken, refreshToken: storedRefreshToken });
        } else {
          // Try to refresh token
          try {
            const newSession = await refreshToken(storedRefreshToken);
            setSession(newSession);
            const userData = await getCurrentUser();
            setUser(userData);
            setIsAuthenticated(true);
          } catch (error) {
            // Clear invalid tokens
            clearAuthData();
          }
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      clearAuthData();
    } finally {
      setIsLoading(false);
    }
  };

  const verifyToken = async (token) => {
    try {
      const response = await axios.get('/api/auth/verify', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  };

  const getCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${session?.token || localStorage.getItem('auth_token')}` }
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user data');
    }
  };

  const login = async (email, password, mfaToken = null) => {
    try {
      setIsLoading(true);
      
      const response = await axios.post('/api/auth/login', {
        email,
        password,
        mfaToken
      });

      const { user: userData, session: sessionData, mfaRequired: requiresMfa } = response.data;

      if (requiresMfa) {
        setMfaRequired(true);
        setUser(userData);
        return { success: true, mfaRequired: true };
      }

      // Store session data
      localStorage.setItem('auth_token', sessionData.token);
      localStorage.setItem('refresh_token', sessionData.refreshToken);
      
      setUser(userData);
      setSession(sessionData);
      setIsAuthenticated(true);
      setMfaRequired(false);

      return { success: true, mfaRequired: false };
    } catch (error) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyMfa = async (mfaToken) => {
    try {
      const response = await axios.post('/api/auth/verify-mfa', {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      const { session: sessionData } = response.data;

      // Store session data
      localStorage.setItem('auth_token', sessionData.token);
      localStorage.setItem('refresh_token', sessionData.refreshToken);
      
      setSession(sessionData);
      setIsAuthenticated(true);
      setMfaRequired(false);

      return { success: true };
    } catch (error) {
      console.error('MFA verification error:', error);
      throw new Error(error.response?.data?.message || 'MFA verification failed');
    }
  };

  const logout = async () => {
    try {
      if (session?.token) {
        await axios.post('/api/auth/logout', {}, {
          headers: { Authorization: `Bearer ${session.token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthData();
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setSession(null);
    setIsAuthenticated(false);
    setMfaRequired(false);
    setMfaSetup(null);
  };

  const refreshToken = async (refreshToken) => {
    try {
      const response = await axios.post('/api/auth/refresh', {
        refreshToken
      });

      const { session: sessionData } = response.data;

      // Store new tokens
      localStorage.setItem('auth_token', sessionData.token);
      localStorage.setItem('refresh_token', sessionData.refreshToken);

      return sessionData;
    } catch (error) {
      throw new Error('Token refresh failed');
    }
  };

  const register = async (email, username, password, role = 'viewer') => {
    try {
      setIsLoading(true);
      
      const response = await axios.post('/api/auth/register', {
        email,
        username,
        password,
        role
      });

      return { success: true, message: 'Registration successful. Please check your email for verification.' };
    } catch (error) {
      console.error('Registration error:', error);
      throw new Error(error.response?.data?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const requestPasswordReset = async (email) => {
    try {
      await axios.post('/api/auth/forgot-password', { email });
      return { success: true, message: 'Password reset email sent' };
    } catch (error) {
      console.error('Password reset request error:', error);
      throw new Error(error.response?.data?.message || 'Password reset request failed');
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      await axios.post('/api/auth/reset-password', {
        token,
        password: newPassword
      });
      return { success: true, message: 'Password reset successful' };
    } catch (error) {
      console.error('Password reset error:', error);
      throw new Error(error.response?.data?.message || 'Password reset failed');
    }
  };

  const verifyEmail = async (token) => {
    try {
      await axios.post('/api/auth/verify-email', { token });
      return { success: true, message: 'Email verified successfully' };
    } catch (error) {
      console.error('Email verification error:', error);
      throw new Error(error.response?.data?.message || 'Email verification failed');
    }
  };

  const setupMfa = async () => {
    try {
      const response = await axios.post('/api/auth/setup-mfa', {}, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      setMfaSetup(response.data);
      return response.data;
    } catch (error) {
      console.error('MFA setup error:', error);
      throw new Error(error.response?.data?.message || 'MFA setup failed');
    }
  };

  const enableMfa = async (mfaToken) => {
    try {
      await axios.post('/api/auth/enable-mfa', {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      // Update user data
      const userData = await getCurrentUser();
      setUser(userData);

      return { success: true, message: 'MFA enabled successfully' };
    } catch (error) {
      console.error('MFA enable error:', error);
      throw new Error(error.response?.data?.message || 'MFA enable failed');
    }
  };

  const disableMfa = async (mfaToken) => {
    try {
      await axios.post('/api/auth/disable-mfa', {
        mfaToken
      }, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      // Update user data
      const userData = await getCurrentUser();
      setUser(userData);

      return { success: true, message: 'MFA disabled successfully' };
    } catch (error) {
      console.error('MFA disable error:', error);
      throw new Error(error.response?.data?.message || 'MFA disable failed');
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/api/auth/profile', profileData, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      setUser(response.data);
      return { success: true, message: 'Profile updated successfully' };
    } catch (error) {
      console.error('Profile update error:', error);
      throw new Error(error.response?.data?.message || 'Profile update failed');
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      await axios.post('/api/auth/change-password', {
        currentPassword,
        newPassword
      }, {
        headers: { Authorization: `Bearer ${session?.token}` }
      });

      return { success: true, message: 'Password changed successfully' };
    } catch (error) {
      console.error('Password change error:', error);
      throw new Error(error.response?.data?.message || 'Password change failed');
    }
  };

  const getAuthHeaders = () => {
    return {
      Authorization: `Bearer ${session?.token || localStorage.getItem('auth_token')}`
    };
  };

  const hasRole = (requiredRole) => {
    if (!user) return false;
    
    const roleHierarchy = {
      'guest': 0,
      'viewer': 1,
      'analyst': 2,
      'manager': 3,
      'admin': 4
    };

    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;

    return userLevel >= requiredLevel;
  };

  const hasPermission = (permission) => {
    if (!user) return false;

    const permissions = {
      'admin': ['*'],
      'manager': ['read', 'write', 'delete', 'manage_users'],
      'analyst': ['read', 'write', 'create_reports'],
      'viewer': ['read'],
      'guest': []
    };

    const userPermissions = permissions[user.role] || [];
    return userPermissions.includes('*') || userPermissions.includes(permission);
  };

  // Auto-refresh token
  useEffect(() => {
    if (!session?.refreshToken) return;

    const interval = setInterval(async () => {
      try {
        const newSession = await refreshToken(session.refreshToken);
        setSession(newSession);
      } catch (error) {
        console.error('Auto token refresh failed:', error);
        clearAuthData();
      }
    }, 5 * 60 * 1000); // Refresh every 5 minutes

    return () => clearInterval(interval);
  }, [session?.refreshToken]);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    session,
    mfaRequired,
    mfaSetup,
    login,
    logout,
    register,
    verifyMfa,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    setupMfa,
    enableMfa,
    disableMfa,
    updateProfile,
    changePassword,
    getAuthHeaders,
    hasRole,
    hasPermission,
    clearAuthData
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
