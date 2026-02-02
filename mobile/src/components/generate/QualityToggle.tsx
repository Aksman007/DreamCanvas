/**
 * Quality Toggle Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, Platform } from 'react-native';
import { Zap, Gem } from 'lucide-react-native';

import { QUALITY_OPTIONS } from '../../constants/config';

interface QualityToggleProps {
  value: 'standard' | 'hd';
  onChange: (quality: 'standard' | 'hd') => void;
}

export function QualityToggle({ value, onChange }: QualityToggleProps) {
  const handleSelect = async (quality: 'standard' | 'hd') => {
    // Import haptics dynamically to avoid issues
    if (Platform.OS !== 'web') {
      try {
        const Haptics = await import('expo-haptics');
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (e) {
        // Ignore haptics errors
      }
    }
    onChange(quality);
  };

  return (
    <View>
      <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Quality
      </Text>

      <View className="flex-row bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
        {QUALITY_OPTIONS.map((option) => {
          const isSelected = value === option.id;
          const Icon = option.id === 'standard' ? Zap : Gem;

          return (
            <TouchableOpacity
              key={option.id}
              onPress={() => handleSelect(option.id as 'standard' | 'hd')}
              className={`
                flex-1 flex-row items-center justify-center py-3 rounded-lg
                ${isSelected ? 'bg-white dark:bg-gray-700 shadow-sm' : ''}
              `}
              activeOpacity={0.7}
            >
              <Icon
                size={16}
                color={isSelected ? '#0ea5e9' : '#6b7280'}
              />
              <Text
                className={`
                  font-medium ml-2
                  ${
                    isSelected
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }
                `}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}