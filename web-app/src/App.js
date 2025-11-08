import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';
import Optimizations from './pages/Optimizations';
import Settings from './pages/Settings';
import Login from './pages/Login';
import ConnectAWS from './pages/ConnectAWS';
import Admin from './pages/Admin';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import { useAuth } from './services/auth';

// Layout component for authenticated routes
function AuthenticatedLayout({ children, user, sidebarOpen, setSidebarOpen, healthy, connectionStatus, isOnline }) {
  return (
    <>
      <Navbar 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        user={user}
        connectionStatus={connectionStatus}
        isOnline={isOnline}
      />
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : ''}`}>
          <div className="p-6">
            {/* API Health Indicator */}
            <div className="mb-4 flex items-center justify-end">
              <span className={`text-sm font-medium ${healthy ? 'text-green-600' : 'text-red-600'}`}>
                API: {healthy ? '✓ Connected' : '✗ Disconnected'}
              </span>
            </div>
            {children}
          </div>
        </main>
      </div>
    </>
  );
}

export default function App() {
  const { user, loading } = useAuth();
  const [healthy, setHealthy] = useState(false);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);
  const [sidebarOpen, setSidebarOpen] = useState(isDesktop);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const isAuthenticated = !!user;
  
  // Update desktop state on window resize
  useEffect(() => {
    const handleResize = () => {
      const desktop = window.innerWidth >= 1024;
      setIsDesktop(desktop);
      if (desktop) setSidebarOpen(true);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
    fetch(`${base}/api/healthz`)
      .then(r => r.json())
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false));

    // Check online status
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your workspace…</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors" style={{ fontFamily: 'Inter, system-ui, Arial, sans-serif' }}>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Dashboard />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/dashboard" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Dashboard />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/analytics" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Analytics />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/alerts" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Alerts />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/optimizations" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Optimizations />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/settings" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Settings />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/connect" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <ConnectAWS />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          <Route path="/admin" element={
            isAuthenticated ? (
              <AuthenticatedLayout 
                user={user} 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                healthy={healthy}
                connectionStatus={connectionStatus}
                isOnline={isOnline}
              >
                <Admin />
              </AuthenticatedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } />
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
        </Routes>
      </div>
    </Router>
  );
}
