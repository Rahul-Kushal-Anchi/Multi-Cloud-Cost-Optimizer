import { useState, useEffect, createContext, useContext } from 'react';
import toast from 'react-hot-toast';
import costAPI from './api';

const normalizeUser = (payload = {}) => {
  if (!payload) return null;
  const email = payload.email || '';
  return {
    id: payload.id,
    name: payload.name || (email ? email.split('@')[0] : ''),
    email,
    role: payload.role || 'member',
    settings: payload.settings || null,
  };
};

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hydrateUser = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const { data } = await costAPI.getProfile();
        const normalized = normalizeUser(data);
        if (normalized) {
          localStorage.setItem('user', JSON.stringify(normalized));
          setUser(normalized);
        }
      } catch (error) {
        console.error('Failed to hydrate user profile', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };

    hydrateUser();
  }, []);

  useEffect(() => {
    const handleStorageSync = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setUser(null);
        return;
      }

      try {
        const stored = localStorage.getItem('user');
        if (stored) {
          setUser(JSON.parse(stored));
        }
      } catch (error) {
        console.error('Failed to parse cached user from storage', error);
      }
    };

    window.addEventListener('storage', handleStorageSync);
    return () => window.removeEventListener('storage', handleStorageSync);
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);

      const { data } = await costAPI.login({ email, password });
      localStorage.setItem('token', data.access_token);

      let profilePayload = null;
      try {
        const profileResponse = await costAPI.getProfile();
        profilePayload = profileResponse.data;
      } catch (profileError) {
        console.warn('Unable to fetch profile after login', profileError);
      }

      const normalized = normalizeUser(profilePayload || {
        id: data.user_id || data.id,
        email,
        role: data.role || 'member'
      });

      if (normalized) {
        localStorage.setItem('user', JSON.stringify(normalized));
        setUser(normalized);
      }

      toast.success('Login successful!');
      window.dispatchEvent(new Event('focus'));
      return { success: true, role: normalized?.role || data.role };
    } catch (error) {
      const message = error?.response?.data?.detail || error.message || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out successfully');
    window.dispatchEvent(new Event('focus'));
  };

  const refreshProfile = async () => {
    try {
      const { data } = await costAPI.getProfile();
      const normalized = normalizeUser(data);
      if (normalized) {
        localStorage.setItem('user', JSON.stringify(normalized));
        setUser(normalized);
        window.dispatchEvent(new Event('focus'));
      }
      return data;
    } catch (error) {
      console.error('Failed to refresh profile', error);
      return null;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      const { data } = await costAPI.updateProfile(profileData);
      const normalized = normalizeUser(data);
      if (normalized) {
        localStorage.setItem('user', JSON.stringify(normalized));
        setUser(normalized);
        toast.success('Profile updated successfully');
        window.dispatchEvent(new Event('focus'));
      }
      return { success: true, data };
    } catch (error) {
      toast.error('Failed to update profile');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setLoading(true);
      await costAPI.changePassword({ currentPassword, newPassword });
      toast.success('Password changed successfully');
      return { success: true };
    } catch (error) {
      toast.error(error.message || 'Failed to change password');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async ({ email, password, company }) => {
    try {
      setLoading(true);
      await costAPI.signup({ email, password, company });
      toast.success('Account created! Logging you in…');
      setLoading(false);
      return await login(email, password);
    } catch (error) {
      const message = error?.response?.data?.detail || error.message || 'Signup failed';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateProfile,
    changePassword,
    refreshProfile,
    register
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
