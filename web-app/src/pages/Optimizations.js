import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, 
  TrendingDown, 
  AlertCircle, 
  CheckCircle, 
  Clock,
  Filter,
  DollarSign,
  Activity,
  Target,
  Sparkles,
  Download
} from 'lucide-react';
import { exportOptimizations } from '../utils/export';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getApiBase } from '../services/api';
import toast from 'react-hot-toast';

const Optimizations = () => {
  const [serviceFilter, setServiceFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('savings');
  const [selectedIds, setSelectedIds] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const queryClient = useQueryClient();

  // Fetch optimizations
  const { data: optimizations = [], isLoading } = useQuery(
    ['optimizations', serviceFilter, statusFilter],
    async () => {
      const params = new URLSearchParams();
      if (serviceFilter !== 'all') params.append('service', serviceFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      
      const response = await fetch(`${getApiBase()}/optimizations?${params}`);
      if (!response.ok) throw new Error('Failed to fetch optimizations');
      return response.json();
    },
    {
      refetchInterval: 60000,
      retry: 2
    }
  );

  // Apply optimization
  const applyMutation = useMutation(
    async (optId) => {
      const response = await fetch(`${getApiBase()}/optimizations/${optId}/apply`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to apply optimization');
      return response.json();
    },
    {
      onSuccess: (data, optId) => {
        queryClient.invalidateQueries(['optimizations']);
        toast.success(data.message || 'Optimization applied successfully!');
      },
      onError: () => {
        toast.error('Failed to apply optimization');
      }
    }
  );

  // Sort and filter optimizations
  const sortedOptimizations = [...optimizations].sort((a, b) => {
    if (sortBy === 'savings') return b.potentialSavings - a.potentialSavings;
    if (sortBy === 'effort') {
      const effortOrder = { 'low': 1, 'medium': 2, 'high': 3 };
      return effortOrder[a.effort] - effortOrder[b.effort];
    }
    return 0;
  });

  const totalSavings = optimizations.reduce((sum, opt) => sum + opt.potentialSavings, 0);
  const recommendedCount = optimizations.filter(opt => opt.status === 'recommended').length;
  const selectedOptimizations = optimizations.filter(opt => selectedIds.includes(opt.id));
  const selectedSavings = selectedOptimizations.reduce((sum, opt) => sum + opt.potentialSavings, 0);

  // Handle select all
  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedIds(optimizations.map(opt => opt.id));
      setSelectAll(true);
    } else {
      setSelectedIds([]);
      setSelectAll(false);
    }
  };

  // Handle individual select
  const handleSelect = (id, checked) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
      setSelectAll(false);
    }
  };

  // Bulk apply
  const bulkApplyMutation = useMutation(
    async () => {
      const applyPromises = selectedIds.map(id => 
        fetch(`${getApiBase()}/optimizations/${id}/apply`, { method: 'POST' })
      );
      await Promise.all(applyPromises);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['optimizations']);
        toast.success(`Applied ${selectedIds.length} optimization(s) successfully!`);
        setSelectedIds([]);
        setSelectAll(false);
      },
      onError: () => {
        toast.error('Failed to apply optimizations');
      }
    }
  );

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'none': return 'text-green-600';
      case 'low': return 'text-blue-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getEffortColor = (effort) => {
    switch (effort) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatCurrency = (value) => {
    return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
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
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
              <Sparkles className="h-8 w-8 mr-3 text-blue-600" />
              Optimizations
            </h1>
            <p className="text-gray-600 dark:text-gray-400">Cost optimization recommendations and actions</p>
          </div>
          <button
            onClick={() => exportOptimizations(sortedOptimizations)}
            className="flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            title="Export optimizations"
          >
            <Download className="h-4 w-4 mr-2" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg shadow-sm text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm mb-1">Total Potential Savings</p>
              <p className="text-3xl font-bold">{formatCurrency(totalSavings)}</p>
            </div>
            <DollarSign className="h-12 w-12 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg shadow-sm text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm mb-1">Recommended</p>
              <p className="text-3xl font-bold">{recommendedCount}</p>
              <p className="text-blue-100 text-sm mt-1">optimizations</p>
            </div>
            <Target className="h-12 w-12 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg shadow-sm text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm mb-1">Total Recommendations</p>
              <p className="text-3xl font-bold">{optimizations.length}</p>
            </div>
            <Activity className="h-12 w-12 text-purple-200" />
          </div>
        </motion.div>
      </div>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                {selectedIds.length} optimization(s) selected
              </span>
              <span className="text-sm text-blue-700 dark:text-blue-300">
                Total savings: {formatCurrency(selectedSavings)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => bulkApplyMutation.mutate()}
                disabled={bulkApplyMutation.isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Zap className="h-4 w-4" />
                <span>Apply Selected ({selectedIds.length})</span>
              </button>
              <button
                onClick={() => { setSelectedIds([]); setSelectAll(false); }}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={serviceFilter}
            onChange={(e) => setServiceFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Services</option>
            <option value="EC2">EC2</option>
            <option value="RDS">RDS</option>
            <option value="S3">S3</option>
            <option value="Lambda">Lambda</option>
          </select>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Status</option>
          <option value="recommended">Recommended</option>
          <option value="draft">Draft</option>
          <option value="applied">Applied</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="savings">Sort by Savings</option>
          <option value="effort">Sort by Effort</option>
        </select>
      </div>

      {/* Optimizations List */}
            <div className="space-y-4">
        {/* Select All Checkbox */}
        {sortedOptimizations.length > 0 && (
          <div className="mb-4 flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectAll && selectedIds.length === sortedOptimizations.length}
              onChange={(e) => handleSelectAll(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Select all ({sortedOptimizations.length})
            </label>
          </div>
        )}

        {sortedOptimizations.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No optimizations found</h3>
            <p className="text-gray-500">No optimizations match your current filters</p>
          </div>
        ) : (
          sortedOptimizations.map((opt, index) => (
            <motion.div
              key={opt.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border ${
                selectedIds.includes(opt.id) 
                  ? 'border-blue-500 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'border-gray-200 dark:border-gray-700'
              } hover:shadow-md transition-shadow`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(opt.id)}
                    onChange={(e) => handleSelect(opt.id, e.target.checked)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3 flex-wrap">
                    <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(opt.priority)}`}>
                      {opt.priority} priority
                    </div>
                    <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
                      {opt.service}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      opt.status === 'recommended' ? 'bg-green-50 text-green-700 border border-green-200' :
                      opt.status === 'applied' ? 'bg-gray-50 text-gray-700 border border-gray-200' :
                      'bg-yellow-50 text-yellow-700 border border-yellow-200'
                    }`}>
                      {opt.status}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{opt.description}</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center space-x-2">
                      <TrendingDown className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="text-xs text-gray-500">Potential Savings</p>
                        <p className="text-sm font-bold text-gray-900">{formatCurrency(opt.potentialSavings)}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <AlertCircle className={`h-5 w-5 ${getImpactColor(opt.impact)}`} />
                      <div>
                        <p className="text-xs text-gray-500">Impact</p>
                        <p className={`text-sm font-semibold ${getImpactColor(opt.impact)}`}>
                          {opt.impact.charAt(0).toUpperCase() + opt.impact.slice(1)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className={`h-5 w-5 ${getEffortColor(opt.effort)}`} />
                      <div>
                        <p className="text-xs text-gray-500">Effort</p>
                        <p className={`text-sm font-semibold ${getEffortColor(opt.effort)}`}>
                          {opt.effort.charAt(0).toUpperCase() + opt.effort.slice(1)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                </div>

                <div className="ml-4 flex items-center space-x-2">
                  {opt.status === 'recommended' && (
                    <button
                      onClick={() => applyMutation.mutate(opt.id)}
                      disabled={applyMutation.isLoading}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      <Zap className="h-4 w-4" />
                      <span>Apply</span>
                    </button>
                  )}
                  {opt.status === 'applied' && (
                    <div className="px-4 py-2 bg-green-50 text-green-700 rounded-lg border border-green-200 flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4" />
                      <span>Applied</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default Optimizations;

