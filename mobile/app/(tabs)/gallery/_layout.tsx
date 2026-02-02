/**
 * Gallery Stack Layout
 */

import { Stack } from 'expo-router';

export default function GalleryLayout() {
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
          title: 'Gallery',
        }}
      />
      <Stack.Screen
        name="[id]"
        options={{
          title: 'Image',
          presentation: 'card',
        }}
      />
    </Stack>
  );
}