/**
 * Notifications Settings Screen
 */

import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  Bell,
  Image as ImageIcon,
  MessageCircle,
  Gift,
  Megaphone,
} from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';
import { MenuItem } from '../../../src/components/profile';

export default function NotificationsScreen() {
  const [generationComplete, setGenerationComplete] = React.useState(true);
  const [chatResponses, setChatResponses] = React.useState(true);
  const [promotions, setPromotions] = React.useState(false);
  const [announcements, setAnnouncements] = React.useState(true);

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-gray-950" edges={['top']}>
      <Header title="Notifications" showBack />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Generation */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Generation
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={ImageIcon}
            label="Generation Complete"
            isToggle
            toggleValue={generationComplete}
            onToggle={setGenerationComplete}
          />
        </View>

        {/* Chat */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Chat
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={MessageCircle}
            label="AI Responses"
            isToggle
            toggleValue={chatResponses}
            onToggle={setChatResponses}
          />
        </View>

        {/* Marketing */}
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 px-4 pt-6 pb-2 uppercase tracking-wide">
          Marketing
        </Text>
        <View className="bg-white dark:bg-gray-900">
          <MenuItem
            icon={Gift}
            label="Promotions & Offers"
            isToggle
            toggleValue={promotions}
            onToggle={setPromotions}
          />
          <View className="h-px bg-gray-200 dark:bg-gray-800 ml-16" />
          <MenuItem
            icon={Megaphone}
            label="Product Announcements"
            isToggle
            toggleValue={announcements}
            onToggle={setAnnouncements}
          />
        </View>

        {/* Info */}
        <View className="p-4 mt-4">
          <Text className="text-sm text-gray-400 dark:text-gray-500 text-center">
            Push notifications require system permission. You can manage this in your device settings.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}