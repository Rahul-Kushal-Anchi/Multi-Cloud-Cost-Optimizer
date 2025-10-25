import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock,
  Filter,
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';

// Mock alerts data
const mockAlerts = [
  {
    id: '1',
    type: 'cost_spike',
    severity: 'high',
    title: 'Cost Spike Detected',
    message: 'AWS costs increased by 200% in the last 24 hours',
    timestamp: new Date().toISOString(),
    status: 'active',
    threshold: 1000,
    currentValue: 3000,
    service: 'EC2',
    region: 'us-east-1'
  },
  {
    id: '2',
    type: 'budget_exceeded',
    severity: 'medium',
    title: 'Budget Exceeded',
    message: 'Monthly budget exceeded by 15%',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    status: 'active',
    threshold: 10000,
    currentValue: 11500,
    service: 'All',
    region: 'All'
  },
  {
    id: '3',
    type: 'anomaly',
    severity: 'low',
    title: 'Unusual Usage Pattern',
    message: 'Detected unusual usage pattern in S3 storage',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    status: 'resolved',
    threshold: 500,
    currentValue: 750,
    service: 'S3',
    region: 'us-west-2'
  }
];

const Alerts = () => {
  const [filter, setFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const queryClient = useQueryClient();

  // Fetch alerts
  const { data: alerts = [], isLoading } = useQuery(
    ['alerts', filter, severityFilter],
    async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      let filteredAlerts = mockAlerts;
      
      if (filter !== 'all') {
        filteredAlerts = filteredAlerts.filter(alert => alert.status === filter);
      }
      
      if (severityFilter !== 'all') {
        filteredAlerts = filteredAlerts.filter(alert => alert.severity === severityFilter);
      }
      
      return filteredAlerts;
    },
    {
      refetchInterval: 30000
    }
  );

  // Update alert status
  const updateAlertMutation = useMutation(
    async ({ id, status }) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return { id, status };
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['alerts']);
        toast.success(`Alert ${data.status === 'resolved' ? 'resolved' : 'reactivated'}`);
      },
      onError: () => {
        toast.error('Failed to update alert');
      }
    }
  );

  // Delete alert
  const deleteAlertMutation = useMutation(
    async (id) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return id;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['alerts']);
        toast.success('Alert deleted');
      },
      onError: () => {
        toast.error('Failed to delete alert');
      }
    }
  );

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return <XCircle className="h-5 w-5" />;
      case 'medium': return <AlertTriangle className="h-5 w-5" />;
      case 'low': return <CheckCircle className="h-5 w-5" />;
      default: return <Bell className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-red-600 bg-red-50';
      case 'resolved': return 'text-green-600 bg-green-50';
      case 'acknowledged': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Alerts</h1>
            <p className="text-gray-600">Monitor and manage cost alerts</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Alert
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
            <option value="acknowledged">Acknowledged</option>
          </select>
        </div>
        
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Severity</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
            <p className="text-gray-500">No alerts match your current filters</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className={`p-2 rounded-lg ${getSeverityColor(alert.severity)}`}>
                      {getSeverityIcon(alert.severity)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{alert.title}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {formatTimestamp(alert.timestamp)}
                        </span>
                        <span>{alert.service} • {alert.region}</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{alert.message}</p>
                  
                  <div className="flex items-center space-x-6 text-sm">
                    <div>
                      <span className="text-gray-500">Threshold: </span>
                      <span className="font-medium">${alert.threshold.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Current: </span>
                      <span className="font-medium">${alert.currentValue.toLocaleString()}</span>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
                      {alert.status}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => setSelectedAlert(alert)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  
                  {alert.status === 'active' ? (
                    <button
                      onClick={() => updateAlertMutation.mutate({ id: alert.id, status: 'resolved' })}
                      className="p-2 text-green-600 hover:text-green-700 transition-colors"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => updateAlertMutation.mutate({ id: alert.id, status: 'active' })}
                      className="p-2 text-yellow-600 hover:text-yellow-700 transition-colors"
                    >
                      <EyeOff className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => deleteAlertMutation.mutate(alert.id)}
                    className="p-2 text-red-600 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default Alerts;
