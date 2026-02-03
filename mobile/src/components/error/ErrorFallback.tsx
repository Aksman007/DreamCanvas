/**
 * Error Fallback Component - For inline errors
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { AlertCircle, RefreshCw } from 'lucide-react-native';

interface ErrorFallbackProps {
  error?: Error | string | null;
  onRetry?: () => void;
  title?: string;
  compact?: boolean;
}

export function ErrorFallback({
  error,
  onRetry,
  title = 'Something went wrong',
  compact = false,
}: ErrorFallbackProps) {
  const errorMessage = error instanceof Error ? error.message : error;

  if (compact) {
    return (
      <View className="flex-row items-center bg-red-50 dark:bg-red-900/20 rounded-xl p-4">
        <AlertCircle size={20} color="#ef4444" />
        <Text className="flex-1 text-red-700 dark:text-red-300 ml-3 text-sm">
          {errorMessage || title}
        </Text>
        {onRetry && (
          <TouchableOpacity onPress={onRetry} className="p-2">
            <RefreshCw size={18} color="#ef4444" />
          </TouchableOpacity>
        )}
      </View>
    );
  }

  return (
    <View className="flex-1 items-center justify-center p-8">
      <View className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 items-center justify-center mb-4">
        <AlertCircle size={32} color="#ef4444" />
      </View>

      <Text className="text-xl font-bold text-gray-900 dark:text-white mb-2 text-center">
        {title}
      </Text>

      {errorMessage && (
        <Text className="text-gray-500 dark:text-gray-400 text-center mb-6">
          {errorMessage}
        </Text>
      )}

      {onRetry && (
        <TouchableOpacity
          onPress={onRetry}
          className="flex-row items-center bg-primary-600 px-6 py-3 rounded-xl"
          activeOpacity={0.8}
        >
          <RefreshCw size={18} color="#ffffff" />
          <Text className="text-white font-semibold ml-2">Try Again</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}