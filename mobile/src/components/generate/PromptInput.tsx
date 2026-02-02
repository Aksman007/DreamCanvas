/**
 * Prompt Input Component
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Wand2, X, Sparkles } from 'lucide-react-native';

import { APP_CONFIG } from '../../constants/config';

interface PromptInputProps {
  value: string;
  onChange: (text: string) => void;
  onEnhance?: () => void;
  isEnhancing?: boolean;
  enhancedPrompt?: string;
  onUseEnhanced?: () => void;
  onClearEnhanced?: () => void;
  placeholder?: string;
  maxLength?: number;
}

export function PromptInput({
  value,
  onChange,
  onEnhance,
  isEnhancing = false,
  enhancedPrompt,
  onUseEnhanced,
  onClearEnhanced,
  placeholder = 'Describe the image you want to create...',
  maxLength = APP_CONFIG.maxPromptLength,
}: PromptInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const characterCount = value.length;
  const isNearLimit = characterCount > maxLength * 0.8;

  return (
    <View>
      <View className="flex-row items-center justify-between mb-2">
        <Text className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Prompt
        </Text>
        <Text
          className={`text-xs ${
            isNearLimit ? 'text-orange-500' : 'text-gray-400'
          }`}
        >
          {characterCount}/{maxLength}
        </Text>
      </View>

      {/* Main Input */}
      <View
        className={`
          bg-gray-50 dark:bg-gray-800 rounded-xl border-2
          ${isFocused ? 'border-primary-500' : 'border-transparent'}
        `}
      >
        <TextInput
          value={value}
          onChangeText={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          placeholderTextColor="#9ca3af"
          multiline
          numberOfLines={4}
          maxLength={maxLength}
          className="p-4 text-base text-gray-900 dark:text-white"
          style={{ minHeight: 120, textAlignVertical: 'top' }}
        />

        {/* Enhance Button */}
        {onEnhance && value.length > 10 && (
          <View className="flex-row items-center justify-end px-3 pb-3">
            <TouchableOpacity
              onPress={onEnhance}
              disabled={isEnhancing}
              className="flex-row items-center bg-primary-100 dark:bg-primary-900/30 px-3 py-2 rounded-lg"
              activeOpacity={0.7}
            >
              {isEnhancing ? (
                <ActivityIndicator size="small" color="#0ea5e9" />
              ) : (
                <Wand2 size={16} color="#0ea5e9" />
              )}
              <Text className="text-primary-600 dark:text-primary-400 font-medium ml-2">
                {isEnhancing ? 'Enhancing...' : 'Enhance with AI'}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Enhanced Prompt Preview */}
      {enhancedPrompt && (
        <View className="mt-3 bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center">
              <Sparkles size={16} color="#0ea5e9" />
              <Text className="text-sm font-medium text-primary-600 dark:text-primary-400 ml-2">
                AI Enhanced
              </Text>
            </View>
            <TouchableOpacity onPress={onClearEnhanced}>
              <X size={18} color="#9ca3af" />
            </TouchableOpacity>
          </View>

          <Text className="text-gray-700 dark:text-gray-300 text-sm mb-3">
            {enhancedPrompt}
          </Text>

          <TouchableOpacity
            onPress={onUseEnhanced}
            className="bg-primary-600 rounded-lg py-2 items-center"
            activeOpacity={0.8}
          >
            <Text className="text-white font-semibold">Use Enhanced Prompt</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}