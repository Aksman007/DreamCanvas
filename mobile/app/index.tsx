/**
 * Index - Entry redirect based on auth state
 */

import { useEffect } from 'react';
import { Redirect } from 'expo-router';
import { useAuthStore } from '../src/stores/authStore';
import { LoadingScreen } from '../src/components/ui';

export default function Index() {
  const user = useAuthStore((state) => state.user);
  const isInitialized = useAuthStore((state) => state.isInitialized);

  if (!isInitialized) {
    return <LoadingScreen message="Starting DreamCanvas..." />;
  }

  // Redirect based on auth state
  if (user) {
    return <Redirect href="/(tabs)/generate" />;
  }

  return <Redirect href="/(auth)/login" />;
}