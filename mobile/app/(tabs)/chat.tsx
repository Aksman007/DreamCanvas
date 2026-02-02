/**
 * Chat Screen - Claude AI Assistant
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MessageCircle, Sparkles, ArrowRight } from 'lucide-react-native';
import { router } from 'expo-router';

import { Header } from '../../src/components/navigation';
import { Button } from '../../src/components/ui';

const SUGGESTED_PROMPTS = [
  'Help me create a fantasy landscape',
  'I want to make a portrait in anime style',
  'Generate something abstract and colorful',
  'Create a futuristic city scene',
];

export default function ChatScreen() {
  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header title="AI Assistant" />

      <View className="flex-1 p-4">
        {/* Welcome Section */}
        <View className="items-center py-8">
          <View
            className="w-16 h-16 rounded-2xl items-center justify-center mb-4"
            style={{ backgroundColor: '#d946ef' }}
          >
            <MessageCircle size={32} color="#ffffff" />
          </View>

          <Text className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Chat with AI
          </Text>
          <Text className="text-gray-500 dark:text-gray-400 text-center px-8">
            Get help crafting the perfect prompt for your creation
          </Text>
        </View>

        {/* Suggested Prompts */}
        <View className="mt-4">
          <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">
            TRY ASKING
          </Text>

          {SUGGESTED_PROMPTS.map((prompt, index) => (
            <TouchableOpacity
              key={index}
              onPress={() => {}}
              className="flex-row items-center bg-gray-50 dark:bg-gray-800 rounded-xl p-4 mb-2"
              activeOpacity={0.7}
            >
              <Sparkles size={18} color="#0ea5e9" />
              <Text className="flex-1 text-gray-700 dark:text-gray-300 ml-3">
                {prompt}
              </Text>
              <ArrowRight size={18} color="#9ca3af" />
            </TouchableOpacity>
          ))}
        </View>

        {/* Coming Soon Note */}
        <View className="flex-1 items-center justify-center">
          <Text className="text-gray-400 dark:text-gray-500 text-center">
            Full chat interface coming in Phase 6
          </Text>
        </View>

        {/* Input Placeholder */}
        <View className="border-t border-gray-200 dark:border-gray-800 pt-4">
          <View className="flex-row items-center bg-gray-100 dark:bg-gray-800 rounded-full px-4 py-3">
            <Text className="flex-1 text-gray-400">
              Type your message...
            </Text>
            <TouchableOpacity
              className="w-10 h-10 rounded-full bg-primary-600 items-center justify-center"
              disabled
            >
              <ArrowRight size={20} color="#ffffff" />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}