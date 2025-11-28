import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Server, DollarSign, TrendingDown, CheckCircle, AlertCircle, Activity } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { costAPI } from '../services/api';

const RightSizing = () => {
  const queryClient = useQueryClient();

  // Fetch right-sizing recommendations
  const { data: recommendationsData, isLoading: loadingRecs } = useQuery(
    'right-sizing',
    async () => {
      const response = await costAPI.getRightSizingRecommendations();
      return response.data;
    },
    {
      refetchInterval: 300000, // Refetch every 5 minutes
    }
  );

  // Generate recommendations mutation
  const generateMutation = useMutation(
    async () => {
      const response = await costAPI.getRightSizingRecommendations();
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success(`Found ${data.recommendations_generated} optimization opportunities! Potential savings: $${data.total_potential_savings}/month`);
        queryClient.invalidateQueries('right-sizing');
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to generate recommendations');
      }
    }
  );

  const recommendations = recommendationsData?.recommendations || [];
  const totalSavings = recommendationsData?.total_potential_savings || 0;

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Right-Sizing Recommendations</h1>
            <p className="text-gray-600">ML-powered instance optimization based on actual usage</p>
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            {generateMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Analyzing...
              </>
            ) : (
              <>
                <Activity className="h-4 w-4" />
                Analyze Instances
              </>
            )}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Potential Monthly Savings</p>
              <p className="text-3xl font-bold text-green-600">${totalSavings.toFixed(2)}</p>
            </div>
            <TrendingDown className="h-10 w-10 text-green-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recommendations</p>
              <p className="text-3xl font-bold text-blue-600">{recommendations.length}</p>
            </div>
            <Server className="h-10 w-10 text-blue-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Annual Savings</p>
              <p className="text-3xl font-bold text-purple-600">${(totalSavings * 12).toFixed(2)}</p>
            </div>
            <DollarSign className="h-10 w-10 text-purple-600" />
          </div>
        </motion.div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {loadingRecs ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading recommendations...</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="bg-white p-12 rounded-lg text-center border border-gray-200">
            <Server className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Recommendations Yet</h3>
            <p className="text-gray-600 mb-4">
              Click "Analyze Instances" to get right-sizing recommendations based on your actual usage.
            </p>
            <button
              onClick={() => generateMutation.mutate()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Analyze Instances Now
            </button>
          </div>
        ) : (
          recommendations.map((rec, index) => (
            <motion.div
              key={rec.instance_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4">
                  <Server className="h-6 w-6 text-blue-600 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {rec.instance_id}
                    </h3>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(rec.risk_level)}`}>
                        {rec.risk_level} risk
                      </span>
                      <span className="text-sm text-gray-600">
                        {rec.confidence}% confidence
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500 mb-1">Monthly Savings</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${rec.monthly_savings.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">
                    {rec.savings_percentage.toFixed(1)}% reduction
                  </p>
                </div>
              </div>

              {/* Recommendation Details */}
              <div className="grid grid-cols-2 gap-6 mb-4">
                <div>
                  <p className="text-xs text-gray-500 mb-2">Current Instance</p>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="font-mono text-sm font-semibold text-gray-900">
                      {rec.current_type}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      ${rec.current_monthly_cost?.toFixed(2) || '0.00'}/month
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-2">Recommended Instance</p>
                  <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                    <p className="font-mono text-sm font-semibold text-green-900">
                      {rec.recommended_type}
                    </p>
                    <p className="text-xs text-green-700 mt-1">
                      ${rec.recommended_monthly_cost?.toFixed(2) || '0.00'}/month
                    </p>
                  </div>
                </div>
              </div>

              {/* Utilization */}
              {rec.cpu_utilization_avg !== undefined && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 mb-2">Resource Utilization</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">CPU Average: <span className="font-medium text-gray-900">{rec.cpu_utilization_avg?.toFixed(1) || 'N/A'}%</span></p>
                      <p className="text-gray-600">CPU P95: <span className="font-medium text-gray-900">{rec.cpu_utilization_p95?.toFixed(1) || 'N/A'}%</span></p>
                    </div>
                    {rec.memory_utilization_avg && (
                      <div>
                        <p className="text-gray-600">Memory Average: <span className="font-medium text-gray-900">{rec.memory_utilization_avg?.toFixed(1)}%</span></p>
                        <p className="text-gray-600">Memory P95: <span className="font-medium text-gray-900">{rec.memory_utilization_p95?.toFixed(1)}%</span></p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Reasoning */}
              {rec.reasoning && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-900">{rec.reasoning}</p>
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default RightSizing;


