/**
 * Offline Banner Component
 */

import React from 'react';
import { View, Text, Animated } from 'react-native';
import { WifiOff } from 'lucide-react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useNetworkStatus } from '../../hooks/useNetworkStatus';

export function OfflineBanner() {
  const { isOffline } = useNetworkStatus();
  const insets = useSafeAreaInsets();

  if (!isOffline) return null;

  return (
    <View
      className="bg-red-500 px-4 py-2 flex-row items-center justify-center"
      style={{ paddingTop: insets.top > 0 ? insets.top : 8 }}
    >
      <WifiOff size={16} color="#ffffff" />
      <Text className="text-white font-medium ml-2">
        No internet connection
      </Text>
    </View>
  );
}