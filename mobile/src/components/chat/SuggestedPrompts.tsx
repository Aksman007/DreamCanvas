/**
 * Suggested Prompts Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { Lightbulb, ArrowRight } from 'lucide-react-native';

const SUGGESTIONS = [
  {
    category: 'Landscapes',
    prompts: [
      'Help me create a mystical forest scene',
      'I want to generate a futuristic cityscape',
      'Create a peaceful mountain landscape',
    ],
  },
  {
    category: 'Characters',
    prompts: [
      'Design a fantasy warrior character',
      'Help me visualize a cyberpunk detective',
      'Create an anime-style protagonist',
    ],
  },
  {
    category: 'Abstract',
    prompts: [
      'Generate something colorful and abstract',
      'Create a surreal dreamlike image',
      'Make an artistic geometric pattern',
    ],
  },
  {
    category: 'Styles',
    prompts: [
      'What styles work best for portraits?',
      'How do I get a photorealistic result?',
      'Tips for anime-style generations',
    ],
  },
];

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
}

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  return (
    <ScrollView
      className="flex-1"
      contentContainerStyle={{ padding: 16 }}
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View className="items-center mb-6">
        <View className="w-16 h-16 rounded-2xl bg-primary-100 dark:bg-primary-900/30 items-center justify-center mb-4">
          <Lightbulb size={32} color="#0ea5e9" />
        </View>
        <Text className="text-xl font-bold text-gray-900 dark:text-white">
          How can I help?
        </Text>
        <Text className="text-gray-500 dark:text-gray-400 text-center mt-2">
          I can help you craft the perfect prompt for your AI image
        </Text>
      </View>

      {/* Suggestions by category */}
      {SUGGESTIONS.map((category) => (
        <View key={category.category} className="mb-6">
          <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">
            {category.category}
          </Text>

          {category.prompts.map((prompt, index) => (
            <TouchableOpacity
              key={index}
              onPress={() => onSelect(prompt)}
              className="flex-row items-center bg-gray-50 dark:bg-gray-800 rounded-xl p-4 mb-2"
              activeOpacity={0.7}
            >
              <Text className="flex-1 text-gray-700 dark:text-gray-300">
                {prompt}
              </Text>
              <ArrowRight size={18} color="#9ca3af" />
            </TouchableOpacity>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}