import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Activity,
  Server,
  Database,
  Cloud
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

// Mock data for demonstration
const mockCostData = [
  { date: '2025-01-01', cost: 1200, forecast: 1250 },
  { date: '2025-01-02', cost: 1350, forecast: 1300 },
  { date: '2025-01-03', cost: 1100, forecast: 1280 },
  { date: '2025-01-04', cost: 1450, forecast: 1320 },
  { date: '2025-01-05', cost: 1300, forecast: 1350 },
  { date: '2025-01-06', cost: 1600, forecast: 1380 },
  { date: '2025-01-07', cost: 1400, forecast: 1400 }
];

const mockServiceData = [
  { name: 'EC2', value: 45, cost: 5400, color: '#8884d8' },
  { name: 'RDS', value: 25, cost: 3000, color: '#82ca9d' },
  { name: 'S3', value: 15, cost: 1800, color: '#ffc658' },
  { name: 'Lambda', value: 10, cost: 1200, color: '#ff7300' },
  { name: 'Other', value: 5, cost: 600, color: '#00ff00' }
];

const mockOptimizationData = [
  { service: 'EC2', current: 5400, optimized: 4320, savings: 1080 },
  { service: 'RDS', current: 3000, optimized: 2400, savings: 600 },
  { service: 'S3', current: 1800, optimized: 1440, savings: 360 }
];

const Dashboard = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('cost');

  // Fetch dashboard data
  const { data: dashboardData, isLoading, error } = useQuery(
    ['dashboard', timeRange],
    async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return {
        totalCost: 12000,
        monthlyCost: 12000,
        dailyCost: 400,
        savings: 2400,
        alerts: 3,
        optimizationScore: 85,
        costTrend: 5.2,
        forecast: 13000
      };
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      staleTime: 10000 // Consider data stale after 10 seconds
    }
  );

  const metrics = [
    {
      name: 'Total Cost',
      value: `$${dashboardData?.totalCost?.toLocaleString() || '0'}`,
      change: `+${dashboardData?.costTrend || 0}%`,
      changeType: 'increase',
      icon: DollarSign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Monthly Cost',
      value: `$${dashboardData?.monthlyCost?.toLocaleString() || '0'}`,
      change: `+${dashboardData?.costTrend || 0}%`,
      changeType: 'increase',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Savings',
      value: `$${dashboardData?.savings?.toLocaleString() || '0'}`,
      change: '+12.1%',
      changeType: 'increase',
      icon: TrendingDown,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      name: 'Alerts',
      value: dashboardData?.alerts || 0,
      change: '-1',
      changeType: 'decrease',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    }
  ];

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    toast.error('Failed to load dashboard data');
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading dashboard</h3>
          <p className="text-gray-500">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Cost Dashboard</h1>
        <p className="text-gray-600">Monitor and optimize your AWS costs in real-time</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <motion.div
              key={metric.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  <div className="flex items-center mt-2">
                    <span className={`text-sm font-medium ${
                      metric.changeType === 'increase' ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {metric.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">vs last month</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                  <Icon className={`h-6 w-6 ${metric.color}`} />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Cost Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Cost Trend</h3>
            <div className="flex space-x-2">
              {['7d', '30d', '90d'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 text-sm rounded-md ${
                    timeRange === range
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockCostData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="cost" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Actual Cost"
                />
                <Line 
                  type="monotone" 
                  dataKey="forecast" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Forecast"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Service Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Breakdown</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={mockServiceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mockServiceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value}%`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {mockServiceData.map((service, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2" 
                    style={{ backgroundColor: service.color }}
                  ></div>
                  <span className="text-sm text-gray-600">{service.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">
                  ${service.cost.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Optimization Opportunities */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Optimization Opportunities</h3>
          <span className="text-sm text-gray-500">Potential savings: $2,040/month</span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mockOptimizationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="service" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="current" fill="#ef4444" name="Current Cost" />
              <Bar dataKey="optimized" fill="#10b981" name="Optimized Cost" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
