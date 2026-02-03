/**
 * Prompt Banner Component - Shows when a prompt is ready to use
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Sparkles, X, ArrowRight } from 'lucide-react-native';

interface PromptBannerProps {
  prompt: string;
  onUse: () => void;
  onDismiss: () => void;
}

export function PromptBanner({ prompt, onUse, onDismiss }: PromptBannerProps) {
  return (
    <View className="mx-4 mb-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
      <View className="flex-row items-start justify-between mb-2">
        <View className="flex-row items-center flex-1">
          <Sparkles size={18} color="#0ea5e9" />
          <Text className="text-sm font-medium text-primary-700 dark:text-primary-300 ml-2">
            Suggested Prompt Ready
          </Text>
        </View>
        <TouchableOpacity onPress={onDismiss} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
          <X size={18} color="#9ca3af" />
        </TouchableOpacity>
      </View>

      <Text className="text-gray-700 dark:text-gray-300 mb-3" numberOfLines={3}>
        {prompt}
      </Text>

      <TouchableOpacity
        onPress={onUse}
        className="flex-row items-center justify-center bg-primary-600 rounded-lg py-2.5"
        activeOpacity={0.8}
      >
        <Text className="text-white font-semibold mr-2">Use This Prompt</Text>
        <ArrowRight size={18} color="#ffffff" />
      </TouchableOpacity>
    </View>
  );
}