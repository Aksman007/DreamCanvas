/**
 * Custom Header Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { BlurView } from 'expo-blur';
import { ArrowLeft, Settings, Bell } from 'lucide-react-native';
import { router } from 'expo-router';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  showBack?: boolean;
  showSettings?: boolean;
  showNotifications?: boolean;
  rightAction?: React.ReactNode;
  leftAction?: React.ReactNode;
  transparent?: boolean;
  onBackPress?: () => void;
}

export function Header({
  title,
  subtitle,
  showBack = false,
  showSettings = false,
  showNotifications = false,
  rightAction,
  leftAction,
  transparent = false,
  onBackPress,
}: HeaderProps) {
  const insets = useSafeAreaInsets();

  const handleBack = () => {
    if (onBackPress) {
      onBackPress();
    } else {
      router.back();
    }
  };

  const content = (
    <View
      className={`
        flex-row items-center justify-between px-4 pb-3
        ${transparent ? '' : 'bg-white dark:bg-gray-900'}
      `}
      style={{ paddingTop: insets.top + 8 }}
    >
      {/* Left Section */}
      <View className="flex-row items-center flex-1">
        {showBack && (
          <TouchableOpacity
            onPress={handleBack}
            className="mr-3 p-2 -ml-2 rounded-full active:bg-gray-100 dark:active:bg-gray-800"
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <ArrowLeft size={24} color="#374151" />
          </TouchableOpacity>
        )}

        {leftAction && <View className="mr-3">{leftAction}</View>}

        <View className="flex-1">
          {title && (
            <Text
              className="text-xl font-bold text-gray-900 dark:text-white"
              numberOfLines={1}
            >
              {title}
            </Text>
          )}
          {subtitle && (
            <Text
              className="text-sm text-gray-500 dark:text-gray-400"
              numberOfLines={1}
            >
              {subtitle}
            </Text>
          )}
        </View>
      </View>

      {/* Right Section */}
      <View className="flex-row items-center">
        {showNotifications && (
          <TouchableOpacity
            onPress={() => {}}
            className="p-2 rounded-full active:bg-gray-100 dark:active:bg-gray-800"
          >
            <Bell size={22} color="#374151" />
          </TouchableOpacity>
        )}

        {showSettings && (
          <TouchableOpacity
            onPress={() => router.push('/(tabs)/profile/settings')}
            className="p-2 rounded-full active:bg-gray-100 dark:active:bg-gray-800"
          >
            <Settings size={22} color="#374151" />
          </TouchableOpacity>
        )}

        {rightAction}
      </View>
    </View>
  );

  // Use blur effect on iOS for transparent headers
  if (transparent && Platform.OS === 'ios') {
    return (
      <BlurView intensity={80} tint="light" className="absolute top-0 left-0 right-0 z-10">
        {content}
      </BlurView>
    );
  }

  return (
    <View className={transparent ? 'absolute top-0 left-0 right-0 z-10' : ''}>
      {content}
    </View>
  );
}