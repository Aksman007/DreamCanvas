/**
 * Generate Stack Layout
 */

import { Stack } from 'expo-router';

export default function GenerateLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: 'Create',
        }}
      />
      <Stack.Screen
        name="[id]"
        options={{
          title: 'Generation',
          presentation: 'card',
        }}
      />
    </Stack>
  );
}