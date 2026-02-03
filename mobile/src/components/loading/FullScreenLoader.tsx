/**
 * Full Screen Loader Component
 */

import React from 'react';
import { View, Text, Modal } from 'react-native';
import { LoadingSpinner } from './LoadingSpinner';

interface FullScreenLoaderProps {
  visible: boolean;
  message?: string;
  transparent?: boolean;
}

export function FullScreenLoader({
  visible,
  message = 'Loading...',
  transparent = true,
}: FullScreenLoaderProps) {
  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      transparent={transparent}
      animationType="fade"
      statusBarTranslucent
    >
      <View 
        className={`flex-1 items-center justify-center ${
          transparent ? 'bg-black/50' : 'bg-white dark:bg-gray-900'
        }`}
      >
        <View className="bg-white dark:bg-gray-800 rounded-2xl p-6 items-center shadow-xl">
          <LoadingSpinner size="lg" />
          <Text className="text-gray-700 dark:text-gray-300 mt-4 font-medium">
            {message}
          </Text>
        </View>
      </View>
    </Modal>
  );
}