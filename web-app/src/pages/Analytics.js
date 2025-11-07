import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  PieChart,
  Activity,
  Calendar,
  Filter,
  AlertTriangle
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell
} from 'recharts';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';
import { costAPI } from '../services/api';

// Color palette for services
const serviceColors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#0088FE', '#00C49F', '#FFBB28'];

// Fallback mock data for regions (API doesn't provide this yet)
const mockRegionData = [
  { region: 'us-east-1', cost: 4800, instances: 45 },
  { region: 'us-west-2', cost: 3200, instances: 32 },
  { region: 'eu-west-1', cost: 2400, instances: 28 },
  { region: 'ap-southeast-1', cost: 1600, instances: 18 }
];

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('cost');
  const [chartType, setChartType] = useState('line');

  // Fetch analytics data from REAL API
  const { data: analyticsData, isLoading, error } = useQuery(
    ['analytics', timeRange],
    async () => {
      const [dashboardRes, trendsRes, servicesRes] = await Promise.all([
        costAPI.getDashboardData(timeRange),
        costAPI.getCostTrends(timeRange),
        costAPI.getServiceBreakdown(timeRange)
      ]);
      
      // Calculate cost change from trends
      const trends = trendsRes.data.data || [];
      let costChange = 0;
      if (trends.length >= 2) {
        const recent = trends.slice(-7); // Last 7 days
        const older = trends.slice(-14, -7); // Previous 7 days
        if (older.length > 0 && recent.length > 0) {
          const recentAvg = recent.reduce((sum, t) => sum + (t.cost || 0), 0) / recent.length;
          const olderAvg = older.reduce((sum, t) => sum + (t.cost || 0), 0) / older.length;
          costChange = olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0;
        }
      }

      return {
        totalCost: dashboardRes.data.totalCost,
        costChange: Math.round(costChange * 10) / 10, // Round to 1 decimal
        savings: dashboardRes.data.savings,
        optimizationScore: dashboardRes.data.optimizationScore,
        topServices: servicesRes.data.services || [],
        trends: trends,
        regions: mockRegionData // Still using mock for regions until API supports it
      };
    },
    {
      refetchInterval: 30000,
      staleTime: 60000
    }
  );

  const metrics = [
    {
      name: 'Total Cost',
      value: `$${analyticsData?.totalCost?.toLocaleString() || '0'}`,
      change: `+${analyticsData?.costChange || 0}%`,
      changeType: 'increase',
      icon: BarChart3,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Cost Change',
      value: `${analyticsData?.costChange || 0}%`,
      change: 'vs last month',
      changeType: 'increase',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Savings',
      value: `$${analyticsData?.savings?.toLocaleString() || '0'}`,
      change: '+12.1%',
      changeType: 'increase',
      icon: TrendingDown,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      name: 'Optimization Score',
      value: `${analyticsData?.optimizationScore || 0}%`,
      change: '+5%',
      changeType: 'increase',
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
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
    toast.error('Failed to load analytics data');
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading analytics</h3>
          <p className="text-gray-500">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
        <p className="text-gray-600">Detailed cost analysis and insights</p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <Calendar className="h-5 w-5 text-gray-500" />
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="cost">Cost</option>
            <option value="usage">Usage</option>
            <option value="savings">Savings</option>
          </select>
        </div>
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
            <h3 className="text-lg font-semibold text-gray-900">Cost Trends</h3>
            <div className="flex space-x-2">
              {['line', 'area', 'bar'].map((type) => (
                <button
                  key={type}
                  onClick={() => setChartType(type)}
                  className={`px-3 py-1 text-sm rounded-md ${
                    chartType === type
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'line' ? (
                <LineChart data={analyticsData?.trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cost" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="forecast" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              ) : chartType === 'area' ? (
                <AreaChart data={analyticsData?.trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="cost" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="savings" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                </AreaChart>
              ) : (
                <BarChart data={analyticsData?.trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="cost" fill="#3b82f6" />
                  <Bar dataKey="savings" fill="#10b981" />
                </BarChart>
              )}
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
              <RechartsPieChart>
                <Pie
                  data={analyticsData?.topServices || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="cost"
                >
                  {(analyticsData?.topServices || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || serviceColors[index % serviceColors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Cost']} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {(analyticsData?.topServices || []).map((service, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2" 
                    style={{ backgroundColor: service.color || serviceColors[index % serviceColors.length] }}
                  ></div>
                  <span className="text-sm text-gray-600">{service.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    ${service.cost.toLocaleString()}
                  </span>
                  <span className={`text-xs ${
                    service.trend > 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {service.trend > 0 ? '+' : ''}{service.trend}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Regional Analysis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Cost Analysis</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mockRegionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="cost" fill="#3b82f6" name="Cost ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  );
};

export default Analytics;
