/**
 * Root Layout - App entry point
 */

import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { useAuthStore } from '../src/stores/authStore';
import { useToastStore } from '../src/stores/toastStore'
import { LoadingScreen } from '../src/components/ui';
import { ErrorBoundary } from '../src/components/error';
import '../global.css';
import { Toast } from '../src/components/ui/Toast';
import { OfflineBanner } from '@/src/components/ui/OfflineBanner';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

function ToastContainer() {
  const { visible, type, message, hide } = useToastStore();
  return <Toast visible={visible} type={type} message={message} onDismiss={hide} />;
}

export default function RootLayout() {
  const { initialize, isInitialized, isLoading } = useAuthStore();
  
  useEffect(() => {
    initialize();
  }, []);
  
  // Show loading screen while initializing
  if (!isInitialized || isLoading) {
    return <LoadingScreen message="Starting DreamCanvas..." />;
  }
  
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <GestureHandlerRootView style={{ flex: 1 }}>
          <SafeAreaProvider>
            <StatusBar style="auto" />
            <OfflineBanner />
            <Stack screenOptions={{ headerShown: false }}>
              <Stack.Screen name="index" />
              <Stack.Screen name="(auth)" />
              <Stack.Screen name="(tabs)" />
            </Stack>
            <ToastContainer />
          </SafeAreaProvider>
        </GestureHandlerRootView>
        </QueryClientProvider>
      </ErrorBoundary>
  );
}