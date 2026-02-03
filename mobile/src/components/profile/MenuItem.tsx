/**
 * Menu Item Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, Switch } from 'react-native';
import { ChevronRight } from 'lucide-react-native';

interface MenuItemProps {
  icon: React.ComponentType<{ size: number; color: string }>;
  label: string;
  value?: string;
  onPress?: () => void;
  showArrow?: boolean;
  danger?: boolean;
  // For toggle items
  isToggle?: boolean;
  toggleValue?: boolean;
  onToggle?: (value: boolean) => void;
}

export function MenuItem({
  icon: Icon,
  label,
  value,
  onPress,
  showArrow = true,
  danger = false,
  isToggle = false,
  toggleValue,
  onToggle,
}: MenuItemProps) {
  const content = (
    <>
      <View
        className={`w-10 h-10 rounded-full items-center justify-center ${
          danger ? 'bg-red-100 dark:bg-red-900/30' : 'bg-gray-100 dark:bg-gray-800'
        }`}
      >
        <Icon size={20} color={danger ? '#ef4444' : '#6b7280'} />
      </View>

      <View className="flex-1 ml-3">
        <Text
          className={`font-medium ${
            danger ? 'text-red-600' : 'text-gray-900 dark:text-white'
          }`}
        >
          {label}
        </Text>
      </View>

      {isToggle && onToggle !== undefined ? (
        <Switch
          value={toggleValue}
          onValueChange={onToggle}
          trackColor={{ false: '#d1d5db', true: '#0ea5e9' }}
          thumbColor="#ffffff"
        />
      ) : (
        <>
          {value && (
            <Text className="text-gray-500 dark:text-gray-400 mr-2">{value}</Text>
          )}
          {showArrow && <ChevronRight size={20} color="#9ca3af" />}
        </>
      )}
    </>
  );

  if (isToggle) {
    return (
      <View className="flex-row items-center py-4 px-4 bg-white dark:bg-gray-900">
        {content}
      </View>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      className="flex-row items-center py-4 px-4 bg-white dark:bg-gray-900"
      activeOpacity={0.7}
    >
      {content}
    </TouchableOpacity>
  );
}