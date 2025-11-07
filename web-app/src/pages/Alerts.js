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
import { costAPI } from '../services/api';

const Alerts = () => {
  const [filter, setFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const queryClient = useQueryClient();

  // Fetch alerts from REAL API
  const { data: alerts = [], isLoading, error } = useQuery(
    ['alerts', filter, severityFilter],
    async () => {
      const response = await costAPI.getAlerts({ 
        status: filter !== 'all' ? filter : undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined
      });
      
      // API may return array directly or wrapped in {alerts: [...]}
      let alertsData = response.data;
      if (Array.isArray(alertsData)) {
        return alertsData;
      } else if (alertsData?.alerts && Array.isArray(alertsData.alerts)) {
        return alertsData.alerts;
      }
      
      // Format alerts to match expected structure
      return (alertsData || []).map(alert => ({
        id: alert.id || alert._id,
        type: alert.type || 'info',
        severity: alert.severity || 'medium',
        title: alert.title || alert.type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        message: alert.message,
        timestamp: alert.timestamp,
        status: alert.status || 'active',
        threshold: alert.threshold || 0,
        currentValue: alert.currentValue || 0,
        service: alert.service || 'All',
        region: alert.region || 'All'
      }));
    },
    {
      refetchInterval: 30000,
      staleTime: 30000
    }
  );

  // Update alert status
  const updateAlertMutation = useMutation(
    async ({ id, status }) => {
      const response = await costAPI.updateAlert(id, { status });
      return response.data;
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
      const response = await costAPI.deleteAlert(id);
      return response.data;
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

  // Create alert
  const createAlertMutation = useMutation(
    async (alertData) => {
      const response = await costAPI.createAlert(alertData);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['alerts']);
        toast.success('Alert created successfully');
        setShowCreateModal(false);
      },
      onError: () => {
        toast.error('Failed to create alert');
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

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Create Alert</h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              createAlertMutation.mutate({
                type: formData.get('type'),
                severity: formData.get('severity'),
                message: formData.get('message'),
                service: formData.get('service') || 'All',
                threshold: parseFloat(formData.get('threshold')) || 0,
                currentValue: parseFloat(formData.get('currentValue')) || 0
              });
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select name="type" required className="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="cost_spike">Cost Spike</option>
                    <option value="budget_exceeded">Budget Exceeded</option>
                    <option value="anomaly_detected">Anomaly Detected</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                  <select name="severity" required className="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <textarea name="message" required rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Service</label>
                  <input type="text" name="service" defaultValue="All" className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                </div>
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Threshold</label>
                    <input type="number" name="threshold" step="0.01" className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Value</label>
                    <input type="number" name="currentValue" step="0.01" className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                  </div>
                </div>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createAlertMutation.isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {createAlertMutation.isLoading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
