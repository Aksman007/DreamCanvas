/**
 * Settings Screen with persistent settings
 */

import React from 'react';
import { View, Text, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  Moon,
  Sun,
  Smartphone,
  Bell,
  Sparkles,
  Palette,
  Image as ImageIcon,
  Gem,
  RotateCcw,
} from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';
import { MenuItem } from '../../../src/components/profile';
import { Button } from '../../../src/components/ui';
import { useSettingsStore } from '../../../src/stores/settingsStore';
import { STYLE_PRESETS, SIZE_OPTIONS, QUALITY_OPTIONS } from '../../../src/constants/config';

export default function SettingsScreen() {
  const {
    theme,
    defaultStyle,
    defaultQuality,
    defaultSize,
    autoEnhancePrompts,
    notificationsEnabled,
    hapticFeedbackEnabled,
    setTheme,
    setDefaultStyle,
    setDefaultQuality,
    setDefaultSize,
    setAutoEnhancePrompts,
    setNotificationsEnabled,
    setHapticFeedbackEnabled,
    resetToDefaults,
  } = useSettingsStore();

  const handleThemeChange = () => {
    Alert.alert(
      'Theme',
      'Choose your preferred theme',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Light', onPress: () => setTheme('light') },
        { text: 'Dark', onPress: () => setTheme('dark') },
        { text: 'System', onPress: () => setTheme('system') },
      ]
    );
  };

  const handleStyleChange = () => {
    Alert.alert(
      'Default Style',
      'Choose your default generation style',
      [
        { text: 'Cancel', style: 'cancel' },
        ...STYLE_PRESETS.map((style) => ({
          text: style.label,
          onPress: () => setDefaultStyle(style.id),
        })),
      ]
    );
  };

  const handleSizeChange = () => {
    Alert.alert(
      'Default Size',
      'Choose your default image size',
      [
        { text: 'Cancel', style: 'cancel' },
        ...SIZE_OPTIONS.map((size) => ({
          text: `${size.label} (${size.aspect})`,
          onPress: () => setDefaultSize(size.id),
        })),
      ]
    );
  };

  const handleQualityChange = () => {
    Alert.alert(
      'Default Quality',
      'Choose your default image quality',
      [
        { text: 'Cancel', style: 'cancel' },
        ...QUALITY_OPTIONS.map((quality) => ({
          text: quality.label,
          onPress: () => setDefaultQuality(quality.id as 'standard' | 'hd'),
        })),
      ]
    );
  };

  const handleResetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to defaults?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: resetToDefaults,
        },
      ]
    );
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      default:
        return 'System';
    }
  };

  const getStyleLabel = () => {
    return STYLE_PRESETS.find((s) => s.id === defaultStyle)?.label || 'Vivid';
  };

  const getSizeLabel = () => {
    const size = SIZE_OPTIONS.find((s) => s.id === defaultSize);
    return size ? `${size.label}` : 'Square';
  };

  const getQualityLabel = () => {
    return QUALITY_OPTIONS.find((q) => q.id === defaultQuality)?.label || 'Standard';
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-gray-950" edges={['top']}>
      <Header title="Settings" showBack />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Appearance */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Appearance
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={theme === 'dark' ? Moon : theme === 'light' ? Sun : Smartphone}
            label="Theme"
            value={getThemeLabel()}
            onPress={handleThemeChange}
          />
        </View>

        {/* Generation Defaults */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Generation Defaults
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={Palette}
            label="Default Style"
            value={getStyleLabel()}
            onPress={handleStyleChange}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={ImageIcon}
            label="Default Size"
            value={getSizeLabel()}
            onPress={handleSizeChange}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={Gem}
            label="Default Quality"
            value={getQualityLabel()}
            onPress={handleQualityChange}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={Sparkles}
            label="Auto-Enhance Prompts"
            isToggle
            toggleValue={autoEnhancePrompts}
            onToggle={setAutoEnhancePrompts}
          />
        </View>

        {/* Notifications */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Notifications
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={Bell}
            label="Push Notifications"
            isToggle
            toggleValue={notificationsEnabled}
            onToggle={setNotificationsEnabled}
          />
        </View>

        {/* System */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          System
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={Smartphone}
            label="Haptic Feedback"
            isToggle
            toggleValue={hapticFeedbackEnabled}
            onToggle={setHapticFeedbackEnabled}
          />
        </View>

        {/* Reset */}
        <View className="p-4 mt-4">
          <Button
            title="Reset All Settings"
            variant="outline"
            leftIcon={<RotateCcw size={18} color="#ef4444" />}
            onPress={handleResetSettings}
            style={{ borderColor: '#fecaca' }}
          />
        </View>

        {/* Info */}
        <View className="p-4">
          <Text className="text-sm text-gray-400 dark:text-gray-500 text-center">
            Settings are automatically saved and synced across sessions.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}