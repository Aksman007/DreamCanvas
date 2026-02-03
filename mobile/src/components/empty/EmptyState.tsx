/**
 * Empty State Component
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import {
  Image as ImageIcon,
  MessageCircle,
  Search,
  Inbox,
  Plus,
} from 'lucide-react-native';

type EmptyStateType = 'gallery' | 'chat' | 'search' | 'notifications' | 'default';

interface EmptyStateProps {
  type?: EmptyStateType;
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

const PRESETS: Record<EmptyStateType, { icon: any; title: string; message: string }> = {
  gallery: {
    icon: ImageIcon,
    title: 'No Creations Yet',
    message: 'Your AI-generated images will appear here',
  },
  chat: {
    icon: MessageCircle,
    title: 'Start a Conversation',
    message: 'Ask me anything about creating image prompts',
  },
  search: {
    icon: Search,
    title: 'No Results Found',
    message: 'Try adjusting your search or filters',
  },
  notifications: {
    icon: Inbox,
    title: 'All Caught Up',
    message: "You don't have any notifications",
  },
  default: {
    icon: Inbox,
    title: 'Nothing Here',
    message: 'This section is empty',
  },
};

export function EmptyState({
  type = 'default',
  title,
  message,
  actionLabel,
  onAction,
  icon,
}: EmptyStateProps) {
  const preset = PRESETS[type];
  const Icon = icon || preset.icon;

  return (
    <View className="flex-1 items-center justify-center p-8">
      <View className="w-20 h-20 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center mb-6">
        {typeof Icon === 'function' ? (
          <Icon size={40} color="#9ca3af" />
        ) : (
          Icon
        )}
      </View>

      <Text className="text-xl font-bold text-gray-900 dark:text-white mb-2 text-center">
        {title || preset.title}
      </Text>

      <Text className="text-gray-500 dark:text-gray-400 text-center mb-6">
        {message || preset.message}
      </Text>

      {actionLabel && onAction && (
        <TouchableOpacity
          onPress={onAction}
          className="flex-row items-center bg-primary-600 px-6 py-3 rounded-xl"
          activeOpacity={0.8}
        >
          <Plus size={18} color="#ffffff" />
          <Text className="text-white font-semibold ml-2">{actionLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}