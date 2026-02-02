/**
 * Generation Detail Screen - Progress and Result
 */

import React, { useEffect, useCallback } from 'react';
import { View, ScrollView, Alert, BackHandler } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router, useFocusEffect } from 'expo-router';

import { Header } from '../../../src/components/navigation';
import { Button, LoadingScreen } from '../../../src/components/ui';
import {
  GenerationProgress,
  GenerationResult,
} from '../../../src/components/generate';
import {
  useGenerationStore,
  useCurrentGeneration,
  useIsGenerating,
  useGenerationError,
} from '../../../src/stores';
import { generateApi } from '../../../src/api';

export default function GenerationDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const {
    setCurrentGeneration,
    startPolling,
    stopPolling,
    clearCurrentGeneration,
    clearError,
  } = useGenerationStore();
  const currentGeneration = useCurrentGeneration();
  const isGenerating = useIsGenerating();
  const error = useGenerationError();

  // Load generation if not already loaded
  useEffect(() => {
    const loadGeneration = async () => {
      if (!id) return;

      // If we already have this generation loaded, start polling if needed
      if (currentGeneration?.id === id) {
        if (
          currentGeneration.status !== 'completed' &&
          currentGeneration.status !== 'failed'
        ) {
          startPolling(id);
        }
        return;
      }

      // Load generation from API
      try {
        const generation = await generateApi.getById(id);
        setCurrentGeneration(generation);

        // Start polling if not complete
        if (generation.status !== 'completed' && generation.status !== 'failed') {
          startPolling(id);
        }
      } catch (err) {
        console.error('Failed to load generation:', err);
        Alert.alert('Error', 'Failed to load generation details.');
        router.back();
      }
    };

    loadGeneration();

    return () => {
      stopPolling();
    };
  }, [id]);

  // Handle back button during generation
  useFocusEffect(
    useCallback(() => {
      const onBackPress = () => {
        if (isGenerating) {
          Alert.alert(
            'Generation in Progress',
            'Do you want to leave? The generation will continue in the background.',
            [
              { text: 'Stay', style: 'cancel' },
              {
                text: 'Leave',
                onPress: () => {
                  stopPolling();
                  router.back();
                },
              },
            ]
          );
          return true;
        }
        return false;
      };

      const subscription = BackHandler.addEventListener(
        'hardwareBackPress',
        onBackPress
      );

      return () => subscription.remove();
    }, [isGenerating, stopPolling])
  );

  const handleRegenerate = useCallback(() => {
    if (!currentGeneration) return;

    // Clear current and go back to create with same prompt
    clearCurrentGeneration();
    router.replace('/(tabs)/generate');
    
    // Note: In a full implementation, you might want to pass the prompt back
    // This would require some state management or navigation params
  }, [currentGeneration, clearCurrentGeneration]);

  const handleViewFullscreen = useCallback(() => {
    if (!currentGeneration?.image_url) return;
    
    // Navigate to fullscreen viewer
    // For now, just open the image URL
    // In a full implementation, you'd have a dedicated viewer screen
    Alert.alert('Fullscreen', 'Full-screen image viewer coming soon!');
  }, [currentGeneration]);

  const handleDone = useCallback(() => {
    clearCurrentGeneration();
    router.replace('/(tabs)/gallery');
  }, [clearCurrentGeneration]);

  const handleTryAgain = useCallback(() => {
    clearCurrentGeneration();
    clearError();
    router.back();
  }, [clearCurrentGeneration, clearError]);

  // Loading state
  if (!currentGeneration && !error) {
    return <LoadingScreen message="Loading generation..." />;
  }

  const isComplete = currentGeneration?.status === 'completed';
  const isFailed = currentGeneration?.status === 'failed';

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title={isComplete ? 'Result' : isFailed ? 'Failed' : 'Generating'}
        showBack={!isGenerating}
        onBackPress={
          isGenerating
            ? () => {
                Alert.alert(
                  'Generation in Progress',
                  'Do you want to leave? The generation will continue in the background.',
                  [
                    { text: 'Stay', style: 'cancel' },
                    {
                      text: 'Leave',
                      onPress: () => {
                        stopPolling();
                        router.back();
                      },
                    },
                  ]
                );
              }
            : undefined
        }
      />

      <ScrollView
        className="flex-1"
        contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Progress View */}
        {!isComplete && currentGeneration && (
          <GenerationProgress
            status={currentGeneration.status}
            error={currentGeneration.error_message || error}
          />
        )}

        {/* Result View */}
        {isComplete && currentGeneration && (
          <GenerationResult
            generation={currentGeneration}
            onRegenerate={handleRegenerate}
            onViewFullscreen={handleViewFullscreen}
          />
        )}
      </ScrollView>

      {/* Bottom Actions */}
      {(isComplete || isFailed) && (
        <View className="absolute bottom-0 left-0 right-0 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
          {isComplete ? (
            <View className="flex-row space-x-3">
              <Button
                title="Create Another"
                variant="outline"
                onPress={handleRegenerate}
                className="flex-1"
              />
              <Button
                title="View Gallery"
                onPress={handleDone}
                className="flex-1"
              />
            </View>
          ) : (
            <Button title="Try Again" onPress={handleTryAgain} />
          )}
        </View>
      )}
    </SafeAreaView>
  );
}