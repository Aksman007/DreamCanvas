/**
 * Logo Component
 */

import React from 'react';
import { View, Text } from 'react-native';
import { Sparkles } from 'lucide-react-native';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export function Logo({ size = 'md', showText = true }: LogoProps) {
  const sizeConfig = {
    sm: { icon: 24, text: 'text-xl', container: 'w-10 h-10' },
    md: { icon: 32, text: 'text-2xl', container: 'w-14 h-14' },
    lg: { icon: 48, text: 'text-4xl', container: 'w-20 h-20' },
  };

  const { icon, text, container } = sizeConfig[size];

  return (
    <View className="items-center">
      <View
        className={`
          ${container} items-center justify-center
          bg-gradient-to-br from-primary-500 to-secondary-500
          rounded-2xl mb-3
        `}
        style={{
          backgroundColor: '#0ea5e9',
          shadowColor: '#0ea5e9',
          shadowOffset: { width: 0, height: 4 },
          shadowOpacity: 0.3,
          shadowRadius: 8,
          elevation: 8,
        }}
      >
        <Sparkles size={icon} color="#ffffff" />
      </View>

      {showText && (
        <Text className={`font-bold text-gray-900 dark:text-white ${text}`}>
          DreamCanvas
        </Text>
      )}
    </View>
  );
}