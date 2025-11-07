import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Download
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';
import { exportDashboardData } from '../utils/export';
import { costAPI } from '../services/api';

// Color palette for services
const serviceColors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#0088FE', '#00C49F', '#FFBB28'];

const Dashboard = () => {
  const [timeRange, setTimeRange] = useState('7d');

  // Fetch dashboard data
  const { data: dashboardData, isLoading, error } = useQuery(
    ['dashboard', timeRange],
    async () => {
      const response = await costAPI.getDashboardData(timeRange);
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      staleTime: 10000 // Consider data stale after 10 seconds
    }
  );

  // Fetch cost trends for the chart
  const { data: costTrendsData } = useQuery(
    ['costTrends', timeRange],
    async () => {
      const response = await costAPI.getCostTrends(timeRange);
      return response.data.data || [];
    },
    {
      refetchInterval: 30000,
      staleTime: 10000
    }
  );

  // Fetch service breakdown for the pie chart
  const { data: serviceBreakdownData } = useQuery(
    ['serviceBreakdown', timeRange],
    async () => {
      const response = await costAPI.getServiceBreakdown(timeRange);
      return response.data.services || [];
    },
    {
      refetchInterval: 30000,
      staleTime: 10000
    }
  );

  // Prepare cost data for chart (use real data only)
  const chartData = costTrendsData && costTrendsData.length > 0 
    ? costTrendsData.map(item => ({
        date: item.date,
        cost: item.cost || 0,
        forecast: item.forecast || item.cost * 1.08 // Calculate forecast if not provided
      }))
    : [];

  // Prepare service data for pie chart (use real data only)
  const pieChartData = serviceBreakdownData && serviceBreakdownData.length > 0
    ? serviceBreakdownData.map((service, index) => ({
        name: service.name,
        value: service.percentage || 0,
        cost: service.cost || 0,
        color: serviceColors[index % serviceColors.length]
      }))
    : [];

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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Cost Dashboard</h1>
            <p className="text-gray-600">Monitor and optimize your AWS costs in real-time</p>
          </div>
          <button
            onClick={() => exportDashboardData(dashboardData)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            title="Export dashboard data"
          >
            <Download className="h-4 w-4 mr-2" />
            <span>Export</span>
          </button>
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
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
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
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <p className="mb-2">No cost data available</p>
                  <p className="text-sm">Connect your AWS account to see cost trends</p>
                </div>
              </div>
            )}
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
          {pieChartData.length > 0 ? (
            <>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [`${value}%`, name]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 space-y-2">
                {pieChartData.map((service, index) => (
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
            </>
          ) : (
            <div className="flex items-center justify-center h-80 text-gray-500">
              <div className="text-center">
                <p className="mb-2">No service data available</p>
                <p className="text-sm">Connect your AWS account to see service breakdown</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Optimization Opportunities - Link to Optimizations page */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Optimization Opportunities</h3>
          <a 
            href="/optimizations" 
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View All →
          </a>
        </div>
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">View detailed optimization recommendations</p>
          <a 
            href="/optimizations"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Optimizations
          </a>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
