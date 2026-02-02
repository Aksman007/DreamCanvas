/**
 * Gallery Image Detail Screen
 */

import React, { useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { Image } from 'expo-image';
import {
  Download,
  Share2,
  Trash2,
  Copy,
  RefreshCw,
  AlertCircle,
} from 'lucide-react-native';
import * as Haptics from 'expo-haptics';
import { Platform, Dimensions } from 'react-native';

import { Header } from '../../../src/components/navigation';
import { Button } from '../../../src/components/ui';
import { useGeneration, useDeleteGeneration } from '../../../src/hooks';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function GalleryDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data: generation, isLoading, isError, refetch } = useGeneration(id);
  const deleteGeneration = useDeleteGeneration();

  const handleDelete = useCallback(() => {
    Alert.alert(
      'Delete Image',
      'Are you sure you want to delete this image? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteGeneration.mutateAsync(id!);
              if (Platform.OS !== 'web') {
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
              }
              router.back();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete image. Please try again.');
            }
          },
        },
      ]
    );
  }, [id, deleteGeneration]);

  const handleRegenerate = useCallback(() => {
    // Navigate to generate screen
    // In a full implementation, you might pass the prompt
    router.push('/(tabs)/generate');
  }, []);

  const ActionButton = ({
    icon: Icon,
    label,
    onPress,
    danger = false,
  }: {
    icon: any;
    label: string;
    onPress: () => void;
    danger?: boolean;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      className="items-center p-3"
      activeOpacity={0.7}
    >
      <View
        className={`
          w-12 h-12 rounded-full items-center justify-center
          ${danger ? 'bg-red-100 dark:bg-red-900/30' : 'bg-gray-100 dark:bg-gray-800'}
        `}
      >
        <Icon size={22} color={danger ? '#ef4444' : '#374151'} />
      </View>
      <Text
        className={`
          text-xs mt-1
          ${danger ? 'text-red-600' : 'text-gray-600 dark:text-gray-400'}
        `}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
        <Header title="Image" showBack />
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#0ea5e9" />
        </View>
      </SafeAreaView>
    );
  }

  if (isError || !generation) {
    return (
      <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
        <Header title="Image" showBack />
        <View className="flex-1 items-center justify-center p-8">
          <AlertCircle size={48} color="#ef4444" />
          <Text className="text-xl font-bold text-gray-900 dark:text-white mt-4 mb-2">
            Image Not Found
          </Text>
          <Button title="Go Back" onPress={() => router.back()} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header title="Image" showBack />

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Image */}
        {generation.image_url && (
          <Image
            source={{ uri: generation.image_url }}
            style={{
              width: SCREEN_WIDTH,
              height: SCREEN_WIDTH,
            }}
            contentFit="cover"
            transition={300}
          />
        )}

        {/* Actions */}
        <View className="flex-row justify-around py-4 border-b border-gray-200 dark:border-gray-800">
          <ActionButton icon={Download} label="Save" onPress={() => {}} />
          <ActionButton icon={Share2} label="Share" onPress={() => {}} />
          <ActionButton icon={Copy} label="Copy" onPress={() => {}} />
          <ActionButton icon={RefreshCw} label="Remake" onPress={handleRegenerate} />
        </View>

        {/* Details */}
        <View className="p-4">
          <Text className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Details
          </Text>

          <View className="space-y-4">
            {/* Prompt */}
            <View>
              <Text className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                {generation.enhanced_prompt ? 'Enhanced Prompt' : 'Prompt'}
              </Text>
              <Text className="text-gray-900 dark:text-white">
                {generation.enhanced_prompt || generation.original_prompt}
              </Text>
            </View>

            {/* Original Prompt (if enhanced) */}
            {generation.enhanced_prompt &&
              generation.original_prompt !== generation.enhanced_prompt && (
                <View>
                  <Text className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    Original Prompt
                  </Text>
                  <Text className="text-gray-600 dark:text-gray-400">
                    {generation.original_prompt}
                  </Text>
                </View>
              )}

            {/* Metadata */}
            <View className="flex-row flex-wrap pt-2">
              <View className="w-1/2 mb-3">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Style
                </Text>
                <Text className="text-gray-900 dark:text-white font-medium">
                  {generation.style || 'Default'}
                </Text>
              </View>
              <View className="w-1/2 mb-3">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Size
                </Text>
                <Text className="text-gray-900 dark:text-white font-medium">
                  {generation.size}
                </Text>
              </View>
              <View className="w-1/2 mb-3">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Quality
                </Text>
                <Text className="text-gray-900 dark:text-white font-medium">
                  {generation.quality}
                </Text>
              </View>
              <View className="w-1/2 mb-3">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Provider
                </Text>
                <Text className="text-gray-900 dark:text-white font-medium">
                  {generation.provider === 'dalle' ? 'DALL-E' : generation.provider}
                </Text>
              </View>
              {generation.duration_seconds && (
                <View className="w-1/2 mb-3">
                  <Text className="text-sm text-gray-500 dark:text-gray-400">
                    Generation Time
                  </Text>
                  <Text className="text-gray-900 dark:text-white font-medium">
                    {generation.duration_seconds.toFixed(1)}s
                  </Text>
                </View>
              )}
              <View className="w-1/2 mb-3">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Created
                </Text>
                <Text className="text-gray-900 dark:text-white font-medium">
                  {new Date(generation.created_at).toLocaleDateString()}
                </Text>
              </View>
            </View>
          </View>

          {/* Delete Button */}
          <Button
            title="Delete Image"
            variant="outline"
            leftIcon={<Trash2 size={18} color="#ef4444" />}
            onPress={handleDelete}
            isLoading={deleteGeneration.isPending}
            className="mt-6"
            style={{ borderColor: '#fecaca' }}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}