import React, { createContext, useContext } from 'react';
import { useQuery } from 'react-query';
import costAPI from '../services/api';

const DashboardMetricsContext = createContext({
  metrics: null,
  isLoading: false,
  error: null,
  refetch: () => {}
});

export const DashboardMetricsProvider = ({ children }) => {
  const query = useQuery(
    ['dashboard-quick-stats', localStorage.getItem('tenant_id')],
    async () => {
      const response = await costAPI.getDashboardData('7d');
      return response.data;
    },
    {
      staleTime: 60_000,
      refetchOnWindowFocus: false
    }
  );

  return (
    <DashboardMetricsContext.Provider
      value={{
        metrics: query.data,
        isLoading: query.isLoading,
        error: query.error,
        refetch: query.refetch
      }}
    >
      {children}
    </DashboardMetricsContext.Provider>
  );
};

export const useDashboardMetrics = () => useContext(DashboardMetricsContext);

export default DashboardMetricsContext;

