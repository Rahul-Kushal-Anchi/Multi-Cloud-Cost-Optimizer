import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Calendar, DollarSign } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { costAPI } from '../services/api';

const Anomalies = () => {
  const [severityFilter, setSeverityFilter] = useState('all');
  const [daysFilter, setDaysFilter] = useState(30);
  const queryClient = useQueryClient();

  // Fetch anomalies
  const { data: anomaliesData, isLoading } = useQuery(
    ['anomalies', daysFilter, severityFilter],
    async () => {
      const params = { days: daysFilter };
      if (severityFilter !== 'all') params.severity = severityFilter;
      const response = await costAPI.getAnomalies(params);
      return response.data;
    },
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  // Fetch model status
  const { data: modelStatus } = useQuery(
    'anomaly-model-status',
    async () => {
      const response = await costAPI.getAnomalyModelStatus();
      return response.data;
    }
  );

  // Train model mutation
  const trainModelMutation = useMutation(
    async () => {
      const response = await costAPI.trainAnomalyModel({ lookback_days: 90 });
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success(`Model trained! Detected ${data.num_anomalies} anomalies`);
        queryClient.invalidateQueries('anomaly-model-status');
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to train model');
      }
    }
  );

  // Detect anomalies mutation
  const detectAnomaliesMutation = useMutation(
    async () => {
      const response = await costAPI.detectAnomalies({ lookback_days: 7 });
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success(`Detection complete! Found ${data.total_anomalies} anomalies`);
        queryClient.invalidateQueries('anomalies');
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to detect anomalies');
      }
    }
  );

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAnomalyIcon = (type) => {
    switch (type) {
      case 'spike': return <TrendingUp className="h-5 w-5 text-red-600" />;
      case 'drop': return <TrendingDown className="h-5 w-5 text-blue-600" />;
      default: return <Activity className="h-5 w-5 text-yellow-600" />;
    }
  };

  const anomalies = anomaliesData?.anomalies || [];
  const filteredAnomalies = severityFilter === 'all' 
    ? anomalies 
    : anomalies.filter(a => a.severity === severityFilter);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Cost Anomaly Detection</h1>
            <p className="text-gray-600">ML-powered detection of unusual spending patterns</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => trainModelMutation.mutate()}
              disabled={trainModelMutation.isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {trainModelMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Training...
                </>
              ) : (
                <>
                  <Activity className="h-4 w-4" />
                  Train Model
                </>
              )}
            </button>
            <button
              onClick={() => detectAnomaliesMutation.mutate()}
              disabled={detectAnomaliesMutation.isLoading || !modelStatus?.is_trained}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              {detectAnomaliesMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Detecting...
                </>
              ) : (
                <>
                  <AlertTriangle className="h-4 w-4" />
                  Detect Anomalies
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Model Status */}
      {modelStatus && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 bg-white p-4 rounded-lg border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                modelStatus.is_trained ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {modelStatus.is_trained ? '✅ Model Trained' : '⚠️ Model Not Trained'}
              </div>
              {modelStatus.training_date && (
                <span className="text-sm text-gray-600">
                  Last trained: {new Date(modelStatus.training_date).toLocaleDateString()}
                </span>
              )}
            </div>
            {!modelStatus.is_trained && (
              <span className="text-sm text-gray-500">
                Click "Train Model" to start detecting anomalies
              </span>
            )}
          </div>
        </motion.div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Anomalies</p>
              <p className="text-2xl font-bold text-gray-900">{anomaliesData?.total || 0}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
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
              <p className="text-sm font-medium text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-red-600">
                {anomalies.filter(a => a.severity === 'critical').length}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-red-600" />
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
              <p className="text-sm font-medium text-gray-600">High</p>
              <p className="text-2xl font-bold text-orange-600">
                {anomalies.filter(a => a.severity === 'high').length}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-orange-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Medium/Low</p>
              <p className="text-2xl font-bold text-yellow-600">
                {anomalies.filter(a => a.severity === 'medium' || a.severity === 'low').length}
              </p>
            </div>
            <Activity className="h-8 w-8 text-yellow-600" />
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <select
          value={daysFilter}
          onChange={(e) => setDaysFilter(Number(e.target.value))}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Anomalies List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading anomalies...</p>
          </div>
        ) : filteredAnomalies.length === 0 ? (
          <div className="bg-white p-12 rounded-lg text-center border border-gray-200">
            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Anomalies Detected</h3>
            <p className="text-gray-600 mb-4">
              {modelStatus?.is_trained 
                ? 'Your costs are looking normal! No unusual patterns detected.'
                : 'Train the model first to start detecting anomalies.'}
            </p>
            {!modelStatus?.is_trained && (
              <button
                onClick={() => trainModelMutation.mutate()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Train Model Now
              </button>
            )}
          </div>
        ) : (
          filteredAnomalies.map((anomaly, index) => (
            <motion.div
              key={anomaly.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="mt-1">
                    {getAnomalyIcon(anomaly.anomaly_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {anomaly.anomaly_type.charAt(0).toUpperCase() + anomaly.anomaly_type.slice(1)} Detected
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(anomaly.severity)}`}>
                        {anomaly.severity}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500 mb-1 flex items-center gap-1">
                          <Calendar className="h-4 w-4" /> Date
                        </p>
                        <p className="font-medium text-gray-900">{anomaly.date}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-1 flex items-center gap-1">
                          <DollarSign className="h-4 w-4" /> Cost
                        </p>
                        <p className="font-medium text-gray-900">${anomaly.cost?.toFixed(2) || '0.00'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-1">Anomaly Score</p>
                        <p className="font-medium text-gray-900">{anomaly.anomaly_score?.toFixed(3) || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 mb-1">Status</p>
                        <p className="font-medium text-gray-900 capitalize">{anomaly.status}</p>
                      </div>
                    </div>
                    {anomaly.affected_service && (
                      <p className="mt-3 text-sm text-gray-600">
                        Service: <span className="font-medium">{anomaly.affected_service}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default Anomalies;


