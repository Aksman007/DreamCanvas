/**
 * Size Selector Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, Platform } from 'react-native';
import { Square, RectangleHorizontal, RectangleVertical } from 'lucide-react-native';

import { SIZE_OPTIONS } from '../../constants/config';

const SIZE_ICONS: Record<string, any> = {
  '1024x1024': Square,
  '1792x1024': RectangleHorizontal,
  '1024x1792': RectangleVertical,
};

interface SizeSelectorProps {
  value: string;
  onChange: (size: string) => void;
}

export function SizeSelector({ value, onChange }: SizeSelectorProps) {
  const handleSelect = async (sizeId: string) => {
    if (Platform.OS !== 'web') {
      try {
        const Haptics = await import('expo-haptics');
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (e) {
        // Ignore haptics errors
      }
    }
    onChange(sizeId);
  };

  return (
    <View>
      <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Size
      </Text>

      <View className="flex-row">
        {SIZE_OPTIONS.map((size) => {
          const Icon = SIZE_ICONS[size.id] || Square;
          const isSelected = value === size.id;

          return (
            <TouchableOpacity
              key={size.id}
              onPress={() => handleSelect(size.id)}
              className={`
                flex-1 mx-1 py-3 rounded-xl border-2 items-center
                ${
                  isSelected
                    ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-500'
                    : 'bg-gray-50 dark:bg-gray-800 border-transparent'
                }
              `}
              activeOpacity={0.7}
            >
              <Icon
                size={20}
                color={isSelected ? '#0ea5e9' : '#6b7280'}
                strokeWidth={isSelected ? 2.5 : 2}
              />
              <Text
                className={`
                  text-xs font-medium mt-1
                  ${
                    isSelected
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }
                `}
              >
                {size.label}
              </Text>
              <Text className="text-xs text-gray-400 dark:text-gray-500">
                {size.aspect}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}