/**
 * Tabs Layout - Main app navigation with custom tab bar
 */

import React from 'react';
import { Tabs, Redirect } from 'expo-router';
import { useAuthStore } from '../../src/stores/authStore';
import { CustomTabBar } from '../../src/components/navigation';

export default function TabsLayout() {
  const user = useAuthStore((state) => state.user);

  // If not authenticated, redirect to login
  if (!user) {
    return <Redirect href="/(auth)/login" />;
  }

  return (
    <Tabs
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
        tabBarHideOnKeyboard: true,
      }}
    >
      <Tabs.Screen
        name="generate"
        options={{
          title: 'Create',
        }}
      />
      <Tabs.Screen
        name="gallery"
        options={{
          title: 'Gallery',
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Chat',
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
        }}
      />
    </Tabs>
  );
}