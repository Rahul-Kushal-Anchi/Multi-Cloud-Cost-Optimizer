import React, { useEffect, useState } from 'react';
import { StatusBar, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from 'react-query';
import NetInfo from '@react-native-netinfo/netinfo';
import SplashScreen from 'react-native-splash-screen';

// Navigation
import AppNavigator from './navigation/AppNavigator';

// Services
import { AuthProvider } from './services/AuthContext';
import { ThemeProvider } from './services/ThemeContext';
import { NotificationProvider } from './services/NotificationContext';

// Utils
import { checkBiometrics } from './utils/biometrics';
import { initializeStorage } from './utils/storage';

// Theme
import { theme } from './utils/theme';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

const App = () => {
  const [isReady, setIsReady] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize storage
      await initializeStorage();
      
      // Check biometrics availability
      await checkBiometrics();
      
      // Hide splash screen
      SplashScreen.hide();
      
      setIsReady(true);
    } catch (error) {
      console.error('App initialization error:', error);
      SplashScreen.hide();
      setIsReady(true);
    }
  };

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected);
    });

    return () => unsubscribe();
  }, []);

  if (!isReady) {
    return null; // Splash screen is shown
  }

  return (
    <QueryClientProvider client={queryClient}>
      <PaperProvider theme={theme}>
        <ThemeProvider>
          <AuthProvider>
            <NotificationProvider>
              <NavigationContainer>
                <StatusBar
                  barStyle={Platform.OS === 'ios' ? 'dark-content' : 'light-content'}
                  backgroundColor={theme.colors.primary}
                />
                <AppNavigator />
              </NavigationContainer>
            </NotificationProvider>
          </AuthProvider>
        </ThemeProvider>
      </PaperProvider>
    </QueryClientProvider>
  );
};

export default App;
