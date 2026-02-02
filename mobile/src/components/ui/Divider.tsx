/**
 * Divider Component
 */

import React from 'react';
import { View, Text } from 'react-native';

interface DividerProps {
  text?: string;
  className?: string;
}

export function Divider({ text, className }: DividerProps) {
  if (text) {
    return (
      <View className={`flex-row items-center my-6 ${className}`}>
        <View className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
        <Text className="mx-4 text-sm text-gray-500 dark:text-gray-400">
          {text}
        </Text>
        <View className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
      </View>
    );
  }

  return (
    <View className={`h-px bg-gray-200 dark:bg-gray-700 my-4 ${className}`} />
  );
}