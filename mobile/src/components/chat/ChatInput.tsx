/**
 * Chat Input Component
 */

import React, { useState } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { Send } from 'lucide-react-native';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  isLoading = false,
  placeholder = 'Ask me anything about image prompts...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    const trimmed = message.trim();
    if (trimmed && !isLoading) {
      onSend(trimmed);
      setMessage('');
    }
  };

  const canSend = message.trim().length > 0 && !isLoading;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3">
        <View className="flex-row items-end bg-gray-100 dark:bg-gray-800 rounded-2xl">
          <TextInput
            value={message}
            onChangeText={setMessage}
            placeholder={placeholder}
            placeholderTextColor="#9ca3af"
            multiline
            maxLength={1000}
            className="flex-1 px-4 py-3 text-base text-gray-900 dark:text-white max-h-32"
            style={{ minHeight: 44 }}
            editable={!isLoading}
            onSubmitEditing={handleSend}
          />

          <TouchableOpacity
            onPress={handleSend}
            disabled={!canSend}
            className={`
              w-10 h-10 rounded-full items-center justify-center mr-1 mb-1
              ${canSend ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'}
            `}
            activeOpacity={0.7}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Send size={18} color="#ffffff" />
            )}
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}