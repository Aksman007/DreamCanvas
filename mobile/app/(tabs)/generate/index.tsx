/**
 * Generate Screen - Main creation interface
 */
import { useSettingsStore } from '../../../src/stores/settingsStore';

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router, useLocalSearchParams } from 'expo-router';

import { Header } from '../../../src/components/navigation';
import { Button, Alert as AlertComponent } from '../../../src/components/ui';
import {
  PromptInput,
  StyleSelector,
  SizeSelector,
  QualityToggle,
} from '../../../src/components/generate';
import {
  useGenerationStore,
  useIsGenerating,
  useGenerationError,
} from '../../../src/stores';
import { useAuthStore } from '../../../src/stores/authStore';
import { APP_CONFIG } from '../../../src/constants/config';

export default function GenerateScreen() {
  const user = useAuthStore((state) => state.user);
  const params = useLocalSearchParams<{ prompt?: string }>();

  const {
    generate,
    enhancePrompt,
    clearError,
    clearCurrentGeneration,
    enhancedPrompt,
    isEnhancing,
  } = useGenerationStore();
  const isGenerating = useIsGenerating();
  const error = useGenerationError();
    const { defaultStyle, defaultQuality, defaultSize, autoEnhancePrompts } = useSettingsStore();
  // Form state
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState(defaultStyle);
  const [size, setSize] = useState(defaultSize);
  const [quality, setQuality] = useState<'standard' | 'hd'>(defaultQuality);
  const [useEnhancement, setUseEnhancement] = useState(autoEnhancePrompts);

  // Handle incoming prompt from chat
  useEffect(() => {
    if (params.prompt) {
      setPrompt(params.prompt);
      // Clear the param to avoid re-setting on re-render
      router.setParams({ prompt: undefined });
    }
  }, [params.prompt]);

  const canGenerate = prompt.trim().length >= 3 && !isGenerating;

  const handleEnhance = useCallback(async () => {
    if (!prompt.trim()) return;

    try {
      await enhancePrompt(prompt, style);
    } catch (err) {
      Alert.alert(
        'Enhancement Failed',
        'Could not enhance prompt. You can still generate with your original prompt.'
      );
    }
  }, [prompt, style, enhancePrompt]);

  const handleUseEnhanced = useCallback(() => {
    if (enhancedPrompt?.enhanced_prompt) {
      setPrompt(enhancedPrompt.enhanced_prompt);
      clearCurrentGeneration();
    }
  }, [enhancedPrompt, clearCurrentGeneration]);

  const handleClearEnhanced = useCallback(() => {
    clearCurrentGeneration();
  }, [clearCurrentGeneration]);

  const handleGenerate = useCallback(async () => {
    if (!canGenerate) return;

    try {
      clearError();

      const generation = await generate({
        prompt: prompt.trim(),
        enhance_prompt: useEnhancement,
        style,
        size: size as any,
        quality,
      });

      // Navigate to progress screen
      router.push(`/(tabs)/generate/${generation.id}`);
    } catch (err: any) {
      // Error handled by store
    }
  }, [canGenerate, prompt, useEnhancement, style, size, quality, generate, clearError]);

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title="Create"
        subtitle={`Welcome, ${user?.display_name || user?.email?.split('@')[0] || 'Creator'}`}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1"
      >
        <ScrollView
          className="flex-1"
          contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Error Alert */}
          {error && (
            <AlertComponent
              type="error"
              message={error}
              onDismiss={clearError}
              className="mb-4"
            />
          )}

          {/* Prompt Input */}
          <PromptInput
            value={prompt}
            onChange={setPrompt}
            onEnhance={handleEnhance}
            isEnhancing={isEnhancing}
            enhancedPrompt={enhancedPrompt?.enhanced_prompt}
            onUseEnhanced={handleUseEnhanced}
            onClearEnhanced={handleClearEnhanced}
          />

          {/* Style Selector */}
          <View className="mt-6">
            <StyleSelector value={style} onChange={setStyle} />
          </View>

          {/* Size Selector */}
          <View className="mt-6">
            <SizeSelector value={size} onChange={setSize} />
          </View>

          {/* Quality Toggle */}
          <View className="mt-6">
            <QualityToggle value={quality} onChange={setQuality} />
          </View>

          {/* Enhancement Toggle */}
          <View className="mt-6 flex-row items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
            <View className="flex-1 mr-4">
              <Text className="font-medium text-gray-900 dark:text-white">
                AI Prompt Enhancement
              </Text>
              <Text className="text-sm text-gray-500 dark:text-gray-400">
                Let AI improve your prompt for better results
              </Text>
            </View>
            <Button
              title={useEnhancement ? 'On' : 'Off'}
              variant={useEnhancement ? 'primary' : 'outline'}
              size="sm"
              onPress={() => setUseEnhancement(!useEnhancement)}
            />
          </View>

          {/* Generation Count */}
          <View className="mt-6 items-center">
            <Text className="text-sm text-gray-500 dark:text-gray-400">
              You have created{' '}
              <Text className="font-semibold text-primary-600">
                {user?.generation_count || 0}
              </Text>{' '}
              images
            </Text>
          </View>
        </ScrollView>

        {/* Generate Button - Fixed at bottom */}
        <View className="absolute bottom-0 left-0 right-0 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
          <Button
            title={isGenerating ? 'Generating...' : 'Generate Image'}
            onPress={handleGenerate}
            disabled={!canGenerate}
            isLoading={isGenerating}
          />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}