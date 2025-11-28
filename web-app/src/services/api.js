import axios from 'axios';

// Get API base URL dynamically
export const getApiBase = () => {
  const { hostname } = window.location;
  const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
  return isLocal ? 'http://localhost:8000/api' : '/api';
};

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || getApiBase(),
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

  // ML Anomaly Detection
  trainAnomalyModel: (params) =>
    api.post('/ml/anomalies/train', params),
  
  detectAnomalies: (params) =>
    api.post('/ml/anomalies/detect', params),
  
  getAnomalies: (params) =>
    api.get('/ml/anomalies', { params }),
  
  getAnomalyModelStatus: () =>
    api.get('/ml/anomalies/model-status'),

  // ML Right-Sizing
  getRightSizingRecommendations: (params) =>
    api.get('/ml/right-sizing', { params }),
  
  getSavedRecommendations: (params) =>
    api.get('/ml/recommendations', { params }),

  // ML Cost Forecasting
  trainForecastModel: (params) =>
    api.post('/ml/forecast/train', params),
  
  getCostForecast: (params) =>
    api.get('/ml/forecast', { params }),

  // Auth
  login: (credentials) =>
    api.post('/auth/login', credentials),

  signup: (payload) =>
    api.post('/auth/signup', payload),

  post: (path, body) =>
    api.post(path, body),
};

// Always use real API
export default costAPI;

