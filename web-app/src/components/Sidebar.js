import React from 'react';
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
  AlertTriangle,
  PieChart,
  Activity
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose }) => {
  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      description: 'Overview and key metrics'
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Detailed cost analysis'
    },
    {
      name: 'Cost Breakdown',
      href: '/cost-breakdown',
      icon: PieChart,
      description: 'Service-wise cost analysis'
    },
    {
      name: 'Trends',
      href: '/trends',
      icon: TrendingUp,
      description: 'Cost trends and forecasting'
    },
    {
      name: 'Alerts',
      href: '/alerts',
      icon: Bell,
      description: 'Cost alerts and notifications'
    },
    {
      name: 'Optimization',
      href: '/optimization',
      icon: Activity,
      description: 'Cost optimization recommendations'
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'Application settings'
    }
  ];

  const quickStats = [
    { label: 'Monthly Spend', value: '$12,450', change: '+5.2%', trend: 'up' },
    { label: 'Savings', value: '$2,100', change: '+12.1%', trend: 'up' },
    { label: 'Alerts', value: '3', change: '-1', trend: 'down' }
  ];

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
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg lg:translate-x-0 lg:static lg:inset-0"
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
                <div className="space-y-3">
                  {quickStats.map((stat, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <p className="text-xs text-gray-500">{stat.label}</p>
                        <p className="text-sm font-semibold text-gray-900">{stat.value}</p>
                      </div>
                      <div className={`flex items-center text-xs ${
                        stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        <span className="mr-1">{stat.change}</span>
                        {stat.trend === 'up' ? (
                          <TrendingUp className="h-3 w-3" />
                        ) : (
                          <TrendingUp className="h-3 w-3 rotate-180" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
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
              <div className="p-4 border-t border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Activity className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">System Status</p>
                    <p className="text-xs text-green-600">All systems operational</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
