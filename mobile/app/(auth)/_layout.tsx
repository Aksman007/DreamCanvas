/**
 * Auth Layout - For login/register screens
 */

import { Stack } from 'expo-router';
import { Redirect } from 'expo-router';
import { useAuthStore } from '../../src/stores/authStore';

export default function AuthLayout() {
  const { isAuthenticated } = useAuthStore();
  
  // If authenticated, redirect to main app
  if (isAuthenticated) {
    return <Redirect href="/(tabs)/generate" />;
  }
  
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="login" />
      <Stack.Screen name="register" />
    </Stack>
  );
}