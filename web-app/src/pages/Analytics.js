import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  PieChart,
  Activity,
  Calendar,
  Filter
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

// Mock data for analytics
const mockTrendData = [
  { date: '2025-01-01', cost: 1200, forecast: 1250, savings: 200 },
  { date: '2025-01-02', cost: 1350, forecast: 1300, savings: 150 },
  { date: '2025-01-03', cost: 1100, forecast: 1280, savings: 180 },
  { date: '2025-01-04', cost: 1450, forecast: 1320, savings: 120 },
  { date: '2025-01-05', cost: 1300, forecast: 1350, savings: 50 },
  { date: '2025-01-06', cost: 1600, forecast: 1380, savings: 220 },
  { date: '2025-01-07', cost: 1400, forecast: 1400, savings: 0 }
];

const mockServiceData = [
  { name: 'EC2', cost: 5400, percentage: 45, trend: 5.2, color: '#8884d8' },
  { name: 'RDS', cost: 3000, percentage: 25, trend: -2.1, color: '#82ca9d' },
  { name: 'S3', cost: 1800, percentage: 15, trend: 8.3, color: '#ffc658' },
  { name: 'Lambda', cost: 1200, percentage: 10, trend: 12.5, color: '#ff7300' },
  { name: 'Other', cost: 600, percentage: 5, trend: -1.2, color: '#00ff00' }
];

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

  // Fetch analytics data
  const { data: analyticsData, isLoading } = useQuery(
    ['analytics', timeRange],
    async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return {
        totalCost: 12000,
        costChange: 5.2,
        savings: 2400,
        optimizationScore: 85,
        topServices: mockServiceData,
        trends: mockTrendData,
        regions: mockRegionData
      };
    },
    {
      refetchInterval: 30000
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
                <LineChart data={mockTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cost" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="forecast" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              ) : chartType === 'area' ? (
                <AreaChart data={mockTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="cost" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="savings" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                </AreaChart>
              ) : (
                <BarChart data={mockTrendData}>
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
                  data={mockServiceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="cost"
                >
                  {mockServiceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Cost']} />
              </RechartsPieChart>
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
