/**
 * Settings Screen
 */

import React from 'react';
import { View, Text, ScrollView, Switch, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  Moon,
  Bell,
  Sparkles,
  Palette,
  ChevronRight,
  Smartphone,
} from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';

export default function SettingsScreen() {
  const [darkMode, setDarkMode] = React.useState(false);
  const [notifications, setNotifications] = React.useState(true);
  const [autoEnhance, setAutoEnhance] = React.useState(true);
  const [haptics, setHaptics] = React.useState(true);

  const SettingToggle = ({
    icon: Icon,
    label,
    description,
    value,
    onValueChange,
  }: {
    icon: any;
    label: string;
    description?: string;
    value: boolean;
    onValueChange: (value: boolean) => void;
  }) => (
    <View className="flex-row items-center py-4 px-4">
      <View className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center">
        <Icon size={20} color="#6b7280" />
      </View>
      <View className="flex-1 ml-3">
        <Text className="font-medium text-gray-900 dark:text-white">{label}</Text>
        {description && (
          <Text className="text-sm text-gray-500 dark:text-gray-400">
            {description}
          </Text>
        )}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#d1d5db', true: '#0ea5e9' }}
        thumbColor="#ffffff"
      />
    </View>
  );

  const SettingOption = ({
    icon: Icon,
    label,
    value,
    onPress,
  }: {
    icon: any;
    label: string;
    value: string;
    onPress: () => void;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      className="flex-row items-center py-4 px-4"
      activeOpacity={0.7}
    >
      <View className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center">
        <Icon size={20} color="#6b7280" />
      </View>
      <View className="flex-1 ml-3">
        <Text className="font-medium text-gray-900 dark:text-white">{label}</Text>
      </View>
      <Text className="text-gray-500 dark:text-gray-400 mr-2">{value}</Text>
      <ChevronRight size={20} color="#9ca3af" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-gray-950" edges={['top']}>
      <Header title="Settings" showBack />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Appearance */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2">
          APPEARANCE
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <SettingToggle
            icon={Moon}
            label="Dark Mode"
            description="Use dark theme"
            value={darkMode}
            onValueChange={setDarkMode}
          />
        </View>

        {/* Generation */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2">
          GENERATION
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <SettingToggle
            icon={Sparkles}
            label="Auto-Enhance Prompts"
            description="Use AI to improve your prompts"
            value={autoEnhance}
            onValueChange={setAutoEnhance}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <SettingOption
            icon={Palette}
            label="Default Style"
            value="Vivid"
            onPress={() => {}}
          />
        </View>

        {/* Notifications */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2">
          NOTIFICATIONS
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <SettingToggle
            icon={Bell}
            label="Push Notifications"
            description="Get notified when generations complete"
            value={notifications}
            onValueChange={setNotifications}
          />
        </View>

        {/* System */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2">
          SYSTEM
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <SettingToggle
            icon={Smartphone}
            label="Haptic Feedback"
            description="Vibrate on interactions"
            value={haptics}
            onValueChange={setHaptics}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}