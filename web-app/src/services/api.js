import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const costAPI = {
  // Dashboard data
  getDashboardData: (timeRange = '7d') => 
    api.get(`/dashboard?timeRange=${timeRange}`),
  
  // Cost data
  getCostData: (params) => 
    api.get('/costs', { params }),
  
  getCostTrends: (timeRange) => 
    api.get(`/costs/trends?timeRange=${timeRange}`),
  
  getServiceBreakdown: (timeRange) => 
    api.get(`/costs/services?timeRange=${timeRange}`),
  
  // Analytics
  getAnalytics: (params) => 
    api.get('/analytics', { params }),
  
  getForecasting: (params) => 
    api.get('/analytics/forecasting', { params }),
  
  getAnomalies: (params) => 
    api.get('/analytics/anomalies', { params }),
  
  // Alerts
  getAlerts: (params) => 
    api.get('/alerts', { params }),
  
  createAlert: (alertData) => 
    api.post('/alerts', alertData),
  
  updateAlert: (id, alertData) => 
    api.put(`/alerts/${id}`, alertData),
  
  deleteAlert: (id) => 
    api.delete(`/alerts/${id}`),
  
  // Optimization
  getOptimizations: (params) => 
    api.get('/optimizations', { params }),
  
  getRecommendations: (params) => 
    api.get('/optimizations/recommendations', { params }),
  
  applyOptimization: (id) => 
    api.post(`/optimizations/${id}/apply`),
  
  // Settings
  getSettings: () => 
    api.get('/settings'),
  
  updateSettings: (settings) => 
    api.put('/settings', settings),
  
  // User management
  getProfile: () => 
    api.get('/user/profile'),
  
  updateProfile: (profileData) => 
    api.put('/user/profile', profileData),
  
  changePassword: (passwordData) => 
    api.put('/user/password', passwordData),
};

// Mock data for development
export const mockAPI = {
  getDashboardData: async (timeRange) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      data: {
        totalCost: 12000,
        monthlyCost: 12000,
        dailyCost: 400,
        savings: 2400,
        alerts: 3,
        optimizationScore: 85,
        costTrend: 5.2,
        forecast: 13000
      }
    };
  },
  
  getCostData: async (params) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    return {
      data: [
        { date: '2025-01-01', cost: 1200, service: 'EC2' },
        { date: '2025-01-02', cost: 1350, service: 'RDS' },
        { date: '2025-01-03', cost: 1100, service: 'S3' },
        { date: '2025-01-04', cost: 1450, service: 'Lambda' },
        { date: '2025-01-05', cost: 1300, service: 'EC2' }
      ]
    };
  },
  
  getAlerts: async (params) => {
    await new Promise(resolve => setTimeout(resolve, 600));
    return {
      data: [
        {
          id: '1',
          type: 'cost_spike',
          severity: 'high',
          message: 'Cost increased by 200% in the last 24 hours',
          timestamp: new Date().toISOString(),
          status: 'active'
        },
        {
          id: '2',
          type: 'budget_exceeded',
          severity: 'medium',
          message: 'Monthly budget exceeded by 15%',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          status: 'active'
        }
      ]
    };
  }
};

// Use mock data in development
const isDevelopment = process.env.NODE_ENV === 'development';

export default isDevelopment ? mockAPI : costAPI;
