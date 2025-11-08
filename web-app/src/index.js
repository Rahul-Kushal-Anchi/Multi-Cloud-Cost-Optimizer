import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import App from './App';
import { AuthProvider } from './services/auth';
import { DashboardMetricsProvider } from './contexts/DashboardMetricsContext';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const root = createRoot(document.getElementById('root'));
root.render(
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <DashboardMetricsProvider>
        <App />
        <Toaster position="top-right" />
      </DashboardMetricsProvider>
    </AuthProvider>
  </QueryClientProvider>
);