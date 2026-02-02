/**
 * Custom Tab Bar Component
 */

import React from 'react';
import { View, TouchableOpacity, Text, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import * as Haptics from 'expo-haptics';
import { Sparkles, Images, User, MessageCircle } from 'lucide-react-native';

const TAB_ICONS: Record<string, any> = {
  generate: Sparkles,
  gallery: Images,
  chat: MessageCircle,
  profile: User,
};

const TAB_LABELS: Record<string, string> = {
  generate: 'Create',
  gallery: 'Gallery',
  chat: 'Chat',
  profile: 'Profile',
};

export function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  return (
    <View
      className="flex-row bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800"
      style={{
        paddingBottom: insets.bottom > 0 ? insets.bottom : 8,
        paddingTop: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.05,
        shadowRadius: 8,
        elevation: 10,
      }}
    >
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const isFocused = state.index === index;

        // Get the base route name (remove /index if present)
        const routeName = route.name.replace('/index', '').replace('index', '');
        const Icon = TAB_ICONS[routeName] || Sparkles;
        const label = TAB_LABELS[routeName] || options.title || route.name;

        const onPress = () => {
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            // Haptic feedback
            if (Platform.OS !== 'web') {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }
            navigation.navigate(route.name);
          }
        };

        const onLongPress = () => {
          if (Platform.OS !== 'web') {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          }
          navigation.emit({
            type: 'tabLongPress',
            target: route.key,
          });
        };

        return (
          <TouchableOpacity
            key={route.key}
            accessibilityRole="button"
            accessibilityState={isFocused ? { selected: true } : {}}
            accessibilityLabel={options.tabBarAccessibilityLabel}
            onPress={onPress}
            onLongPress={onLongPress}
            className="flex-1 items-center justify-center py-2"
            activeOpacity={0.7}
          >
            <View
              className={`
                items-center justify-center rounded-full px-4 py-1.5
                ${isFocused ? 'bg-primary-100 dark:bg-primary-900/30' : ''}
              `}
            >
              <Icon
                size={22}
                color={isFocused ? '#0ea5e9' : '#9ca3af'}
                strokeWidth={isFocused ? 2.5 : 2}
              />
            </View>
            <Text
              className={`
                text-xs mt-1 font-medium
                ${isFocused ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'}
              `}
            >
              {label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}