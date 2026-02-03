/**
 * Message Bubble Component
 */

import React from 'react';
import { View, Text } from 'react-native';
import { User, Sparkles } from 'lucide-react-native';

import type { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
  isLast?: boolean;
}

export function MessageBubble({ message, isLast = false }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <View
      className={`flex-row mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {/* Avatar for assistant */}
      {!isUser && (
        <View className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 items-center justify-center mr-2 mt-1">
          <Sparkles size={16} color="#0ea5e9" />
        </View>
      )}

      {/* Message bubble */}
      <View
        className={`
          max-w-[80%] rounded-2xl px-4 py-3
          ${
            isUser
              ? 'bg-primary-600 rounded-br-md'
              : 'bg-gray-100 dark:bg-gray-800 rounded-bl-md'
          }
        `}
      >
        <Text
          className={`
            text-base leading-6
            ${isUser ? 'text-white' : 'text-gray-900 dark:text-white'}
          `}
        >
          {message.content}
        </Text>
      </View>

      {/* Avatar for user */}
      {isUser && (
        <View className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 items-center justify-center ml-2 mt-1">
          <User size={16} color="#6b7280" />
        </View>
      )}
    </View>
  );
}