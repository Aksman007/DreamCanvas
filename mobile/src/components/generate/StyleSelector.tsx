/**
 * Style Selector Component
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Platform } from 'react-native';
import {
  Sparkles,
  Leaf,
  Palette,
  Camera,
  Wand2,
  Mountain,
} from 'lucide-react-native';

import { STYLE_PRESETS } from '../../constants/config';

const STYLE_ICONS: Record<string, any> = {
  vivid: Sparkles,
  natural: Leaf,
  anime: Palette,
  photorealistic: Camera,
  artistic: Wand2,
  fantasy: Mountain,
};

interface StyleSelectorProps {
  value: string;
  onChange: (style: string) => void;
}

export function StyleSelector({ value, onChange }: StyleSelectorProps) {
  const handleSelect = async (styleId: string) => {
    if (Platform.OS !== 'web') {
      try {
        const Haptics = await import('expo-haptics');
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (e) {
        // Ignore haptics errors
      }
    }
    onChange(styleId);
  };

  return (
    <View>
      <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Style
      </Text>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingRight: 16 }}
      >
        {STYLE_PRESETS.map((style) => {
          const Icon = STYLE_ICONS[style.id] || Sparkles;
          const isSelected = value === style.id;

          return (
            <TouchableOpacity
              key={style.id}
              onPress={() => handleSelect(style.id)}
              className={`
                mr-3 px-4 py-3 rounded-xl border-2
                ${
                  isSelected
                    ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-500'
                    : 'bg-gray-50 dark:bg-gray-800 border-transparent'
                }
              `}
              style={{ minWidth: 100 }}
              activeOpacity={0.7}
            >
              <View className="items-center">
                <Icon
                  size={24}
                  color={isSelected ? '#0ea5e9' : '#6b7280'}
                  strokeWidth={isSelected ? 2.5 : 2}
                />
                <Text
                  className={`
                    font-medium mt-2
                    ${
                      isSelected
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-gray-700 dark:text-gray-300'
                    }
                  `}
                >
                  {style.label}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}