/**
 * Profile Screen
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  User,
  Settings,
  ChevronRight,
  Image as ImageIcon,
  Clock,
  LogOut,
  Edit,
  HelpCircle,
  Shield,
} from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';
import { Button } from '../../../src/components/ui';
import { useAuthStore } from '../../../src/stores/authStore';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();

  const MenuItem = ({
    icon: Icon,
    label,
    value,
    onPress,
    showArrow = true,
    danger = false,
  }: {
    icon: any;
    label: string;
    value?: string;
    onPress: () => void;
    showArrow?: boolean;
    danger?: boolean;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      className="flex-row items-center py-4 px-4 bg-white dark:bg-gray-900"
      activeOpacity={0.7}
    >
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
        {value && (
          <Text className="text-sm text-gray-500 dark:text-gray-400">
            {value}
          </Text>
        )}
      </View>
      {showArrow && <ChevronRight size={20} color="#9ca3af" />}
    </TouchableOpacity>
  );

  const handleLogout = async () => {
    await logout();
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-gray-950" edges={['top']}>
      <Header title="Profile" showSettings />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <View className="bg-white dark:bg-gray-900 px-4 py-6 mb-4">
          <View className="flex-row items-center">
            <View className="w-20 h-20 rounded-full bg-primary-100 dark:bg-primary-900/30 items-center justify-center">
              {user?.avatar_url ? (
                <View className="w-full h-full rounded-full bg-gray-300" />
              ) : (
                <User size={40} color="#0ea5e9" />
              )}
            </View>

            <View className="flex-1 ml-4">
              <Text className="text-xl font-bold text-gray-900 dark:text-white">
                {user?.display_name || 'Creator'}
              </Text>
              <Text className="text-gray-500 dark:text-gray-400">
                {user?.email}
              </Text>
            </View>

            <TouchableOpacity
              onPress={() => router.push('/(tabs)/profile/edit')}
              className="p-2 rounded-full bg-gray-100 dark:bg-gray-800"
            >
              <Edit size={20} color="#6b7280" />
            </TouchableOpacity>
          </View>

          {user?.bio && (
            <Text className="text-gray-600 dark:text-gray-400 mt-4">
              {user.bio}
            </Text>
          )}
        </View>

        {/* Stats */}
        <View className="bg-white dark:bg-gray-900 flex-row mb-4">
          <View className="flex-1 items-center py-4 border-r border-gray-200 dark:border-gray-800">
            <View className="flex-row items-center mb-1">
              <ImageIcon size={18} color="#0ea5e9" />
              <Text className="text-2xl font-bold text-gray-900 dark:text-white ml-2">
                {user?.generation_count || 0}
              </Text>
            </View>
            <Text className="text-sm text-gray-500 dark:text-gray-400">
              Creations
            </Text>
          </View>

          <View className="flex-1 items-center py-4">
            <View className="flex-row items-center mb-1">
              <Clock size={18} color="#d946ef" />
              <Text className="text-sm font-medium text-gray-900 dark:text-white ml-2">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      year: 'numeric',
                    })
                  : 'N/A'}
              </Text>
            </View>
            <Text className="text-sm text-gray-500 dark:text-gray-400">
              Member since
            </Text>
          </View>
        </View>

        {/* Menu Items */}
        <View className="bg-white dark:bg-gray-900 mb-4">
          <MenuItem
            icon={Settings}
            label="Settings"
            onPress={() => router.push('/(tabs)/profile/settings')}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={HelpCircle}
            label="Help & Support"
            onPress={() => {}}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={Shield}
            label="Privacy Policy"
            onPress={() => {}}
          />
        </View>

        {/* Logout */}
        <View className="bg-white dark:bg-gray-900 mb-8">
          <MenuItem
            icon={LogOut}
            label="Log Out"
            onPress={handleLogout}
            showArrow={false}
            danger
          />
        </View>

        {/* Version */}
        <Text className="text-center text-sm text-gray-400 dark:text-gray-600 mb-8">
          DreamCanvas v1.0.0
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}