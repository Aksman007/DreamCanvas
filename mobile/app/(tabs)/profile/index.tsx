/**
 * Profile Screen
 */

import React from 'react';
import { View, Text, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  Settings,
  HelpCircle,
  Shield,
  FileText,
  LogOut,
  Star,
  Bell,
} from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';
import { Avatar, StatsCard, MenuItem } from '../../../src/components/profile';
import { Button } from '../../../src/components/ui';
import { useAuthStore } from '../../../src/stores/authStore';

export default function ProfileScreen() {
  const { user, logout, isLoading } = useAuthStore();

  const handleLogout = () => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Log Out',
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ]
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-gray-950" edges={['top']}>
      <Header title="Profile" showSettings />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <View className="bg-white dark:bg-gray-900 px-4 py-6 mb-4">
          <View className="flex-row items-center">
            <Avatar
              uri={user?.avatar_url}
              size="lg"
              editable
              onEdit={() => router.push('/(tabs)/profile/edit')}
            />

            <View className="flex-1 ml-4">
              <Text className="text-xl font-bold text-gray-900 dark:text-white">
                {user?.display_name || 'Creator'}
              </Text>
              <Text className="text-gray-500 dark:text-gray-400">
                {user?.email}
              </Text>
              {user?.is_verified && (
                <View className="flex-row items-center mt-1">
                  <Star size={14} color="#f59e0b" fill="#f59e0b" />
                  <Text className="text-xs text-yellow-600 ml-1">Verified</Text>
                </View>
              )}
            </View>

            <Button
              title="Edit"
              variant="outline"
              size="sm"
              onPress={() => router.push('/(tabs)/profile/edit')}
            />
          </View>

          {user?.bio && (
            <Text className="text-gray-600 dark:text-gray-400 mt-4">
              {user.bio}
            </Text>
          )}
        </View>

        {/* Stats */}
        <View className="px-4 mb-4">
          <StatsCard
            generationCount={user?.generation_count || 0}
            memberSince={user?.created_at || new Date().toISOString()}
            lastGeneration={user?.last_generation_at}
          />
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
            icon={Bell}
            label="Notifications"
            onPress={() => router.push('/(tabs)/profile/notifications')}
          />
        </View>

        <View className="bg-white dark:bg-gray-900 mb-4">
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
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={FileText}
            label="Terms of Service"
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