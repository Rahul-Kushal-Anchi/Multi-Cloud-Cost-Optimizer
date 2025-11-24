import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  BarChart3, 
  Bell, 
  Settings, 
  X,
  DollarSign,
  TrendingUp,
  Activity,
  Shield,
  Cloud,
  AlertTriangle
} from 'lucide-react';
import { useDashboardMetrics } from '../contexts/DashboardMetricsContext';

// System Status Component
const SystemStatus = () => {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('Checking...');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/healthz`);
        if (response.ok) {
          setStatus('operational');
          setMessage('All systems operational');
        } else {
          setStatus('degraded');
          setMessage('Some services degraded');
        }
      } catch (error) {
        setStatus('down');
        setMessage('System unavailable');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const statusColor = {
    operational: 'bg-green-500',
    degraded: 'bg-yellow-500',
    down: 'bg-red-500',
    checking: 'bg-gray-500'
  };

  const textColor = {
    operational: 'text-green-600',
    degraded: 'text-yellow-600',
    down: 'text-red-600',
    checking: 'text-gray-600'
  };

  return (
    <div className="p-4 border-t border-gray-200">
      <div className="flex items-center space-x-3">
        <div className={`w-8 h-8 ${statusColor[status]} rounded-full flex items-center justify-center`}>
          <Activity className="h-4 w-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900">System Status</p>
          <p className={`text-xs ${textColor[status]}`}>{message}</p>
        </div>
      </div>
    </div>
  );
};

const Sidebar = ({ isOpen, onClose }) => {
  // Get user role from localStorage
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  const role = user?.role || 'member';

  // Base navigation items
  const baseNavigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Overview and key metrics',
      roles: ['global_owner', 'owner', 'admin', 'member']
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Detailed cost analysis',
      roles: ['global_owner', 'owner', 'admin', 'member']
    },
    {
      name: 'Optimizations',
      href: '/optimizations',
      icon: Activity,
      description: 'Cost optimization recommendations',
      roles: ['global_owner', 'owner', 'admin', 'member']
    },
    {
      name: 'Alerts',
      href: '/alerts',
      icon: Bell,
      description: 'Cost alerts and notifications',
      roles: ['global_owner', 'owner', 'admin', 'member']
    }
  ];

  // Role-specific navigation items
  const adminNavigation = [
    {
      name: 'Admin',
      href: '/admin',
      icon: Shield,
      description: 'Manage tenants and platform',
      roles: ['global_owner']
    },
    {
      name: 'Connect AWS',
      href: '/connect',
      icon: Cloud,
      description: 'Connect your AWS account',
      roles: ['owner', 'admin']
    }
  ];

  // Filter navigation based on role
  const navigation = [
    ...baseNavigation.filter(item => item.roles.includes(role)),
    ...adminNavigation.filter(item => item.roles.includes(role)),
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'Application settings',
      roles: ['global_owner', 'owner', 'admin', 'member']
    }
  ];

  const { metrics, isLoading: metricsLoading, error: metricsError } = useDashboardMetrics();

  const quickStats = useMemo(() => {
    if (!metrics) return [];

    const formatCurrency = (value) =>
      typeof value === 'number'
        ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
        : '—';

    const monthlySpend = metrics?.monthlyCost ?? metrics?.totalCost ?? null;
    const forecast = metrics?.forecast;
    let monthlyChange = '—';
    let monthlyTrend = 'neutral';
    if (typeof monthlySpend === 'number' && typeof forecast === 'number' && monthlySpend > 0) {
      const diff = forecast - monthlySpend;
      const pct = (diff / monthlySpend) * 100;
      monthlyChange = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
      monthlyTrend = pct >= 0 ? 'up' : 'down';
    }

    const savings = metrics?.savings ?? null;
    let savingsChange = '—';
    let savingsTrend = 'neutral';
    if (typeof savings === 'number' && monthlySpend) {
      const pct = (savings / monthlySpend) * 100;
      savingsChange = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
      savingsTrend = pct >= 0 ? 'up' : 'down';
    }

    const alerts = typeof metrics?.alerts === 'number' ? metrics.alerts : '—';

    return [
      { label: 'Monthly Spend', value: formatCurrency(monthlySpend), change: monthlyChange, trend: monthlyTrend },
      { label: 'Savings', value: formatCurrency(savings), change: savingsChange, trend: savingsTrend },
      { label: 'Alerts', value: alerts, change: '—', trend: 'neutral' }
    ];
  }, [metrics]);

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      {isOpen && (
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          exit={{ x: -300 }}
          transition={{ type: 'tween', duration: 0.3 }}
          className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg lg:translate-x-0 lg:static lg:inset-0 transition-colors"
        >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <DollarSign className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Cost Optimizer</h2>
                    <p className="text-xs text-gray-500">AWS Management</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Quick Stats */}
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
                {metricsLoading ? (
                  <div className="space-y-3 animate-pulse">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="h-3 w-20 bg-gray-200 rounded" />
                          <div className="h-4 w-24 bg-gray-300 rounded" />
                        </div>
                        <div className="h-3 w-10 bg-gray-200 rounded" />
                      </div>
                    ))}
                  </div>
                ) : metricsError ? (
                  <div className="text-xs text-red-600">
                    Unable to load metrics. Connect AWS to view live data.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {quickStats.map((stat, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div>
                          <p className="text-xs text-gray-500">{stat.label}</p>
                          <p className="text-sm font-semibold text-gray-900">{stat.value}</p>
                        </div>
                        <div
                          className={`flex items-center text-xs ${
                            stat.trend === 'up'
                              ? 'text-green-600'
                              : stat.trend === 'down'
                              ? 'text-red-600'
                              : 'text-gray-500'
                          }`}
                        >
                          <span className="mr-1">{stat.change}</span>
                          {stat.trend === 'neutral' ? (
                            <AlertTriangle className="h-3 w-3 text-gray-400" />
                          ) : stat.trend === 'up' ? (
                            <TrendingUp className="h-3 w-3" />
                          ) : (
                            <TrendingUp className="h-3 w-3 rotate-180" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Navigation */}
              <nav className="flex-1 p-4 space-y-1">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          isActive
                            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                        }`
                      }
                      onClick={onClose}
                    >
                      <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                      <div className="flex-1">
                        <div>{item.name}</div>
                        <div className="text-xs text-gray-500">{item.description}</div>
                      </div>
                    </NavLink>
                  );
                })}
              </nav>

              {/* Footer */}
              <SystemStatus />
            </div>
        </motion.div>
      )}
    </>
  );
};

export default Sidebar;
