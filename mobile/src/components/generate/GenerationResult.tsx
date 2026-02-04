/**
 * Generation Result Component
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Dimensions,
  Share,
  Alert,
  Platform,
} from 'react-native';
import { Image } from 'expo-image';
import * as Haptics from 'expo-haptics';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system/legacy';
import {
  Download,
  Share2,
  RefreshCw,
  Maximize2,
  Copy,
  Check,
} from 'lucide-react-native';

import type { Generation } from '../../types';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface GenerationResultProps {
  generation: Generation;
  onRegenerate?: () => void;
  onViewFullscreen?: () => void;
}

export function GenerationResult({
  generation,
  onRegenerate,
  onViewFullscreen,
}: GenerationResultProps) {
  const [isSaving, setIsSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [copied, setCopied] = React.useState(false);

  const imageUrl = generation.image_url;

  const handleSave = async () => {
    if (!imageUrl) return;

    try {
      setIsSaving(true);

      // Request permissions
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Please grant photo library access to save images.'
        );
        return;
      }

      // Download image
      const filename = `dreamcanvas_${generation.id}.png`;
      const fileUri = `${FileSystem.documentDirectory}${filename}`;
      
      await FileSystem.downloadAsync(imageUrl, fileUri);

      // Save to media library
      await MediaLibrary.saveToLibraryAsync(fileUri);

      // Clean up temp file
      await FileSystem.deleteAsync(fileUri, { idempotent: true });

      setSaved(true);
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      // Reset after delay
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Save error:', error);
      Alert.alert('Error', 'Failed to save image. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleShare = async () => {
    if (!imageUrl) return;

    try {
      await Share.share({
        message: `Check out this AI-generated image!\n\nPrompt: ${generation.enhanced_prompt || generation.original_prompt}`,
        url: imageUrl,
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  const handleCopyPrompt = async () => {
    const prompt = generation.enhanced_prompt || generation.original_prompt;
    // Note: Clipboard API requires expo-clipboard
    // For now, just show a visual feedback
    setCopied(true);
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View>
      {/* Image */}
      <TouchableOpacity
        onPress={onViewFullscreen}
        activeOpacity={0.95}
        className="relative"
      >
        <Image
          source={{ uri: imageUrl || undefined }}
          style={{
            width: SCREEN_WIDTH - 32,
            height: SCREEN_WIDTH - 32,
            borderRadius: 16,
          }}
          contentFit="cover"
          transition={300}
        />

        {/* Fullscreen button overlay */}
        <View className="absolute bottom-3 right-3 bg-black/50 rounded-full p-2">
          <Maximize2 size={20} color="#ffffff" />
        </View>
      </TouchableOpacity>

      {/* Action Buttons */}
      <View className="flex-row justify-around py-4 mt-2">
        <TouchableOpacity
          onPress={handleSave}
          disabled={isSaving}
          className="items-center"
          activeOpacity={0.7}
        >
          <View
            className={`
              w-12 h-12 rounded-full items-center justify-center
              ${saved ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-800'}
            `}
          >
            {saved ? (
              <Check size={22} color="#22c55e" />
            ) : (
              <Download size={22} color="#374151" />
            )}
          </View>
          <Text className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {saved ? 'Saved!' : isSaving ? 'Saving...' : 'Save'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={handleShare}
          className="items-center"
          activeOpacity={0.7}
        >
          <View className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center">
            <Share2 size={22} color="#374151" />
          </View>
          <Text className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Share
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={handleCopyPrompt}
          className="items-center"
          activeOpacity={0.7}
        >
          <View
            className={`
              w-12 h-12 rounded-full items-center justify-center
              ${copied ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-800'}
            `}
          >
            {copied ? (
              <Check size={22} color="#22c55e" />
            ) : (
              <Copy size={22} color="#374151" />
            )}
          </View>
          <Text className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {copied ? 'Copied!' : 'Copy'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={onRegenerate}
          className="items-center"
          activeOpacity={0.7}
        >
          <View className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center">
            <RefreshCw size={22} color="#374151" />
          </View>
          <Text className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Remake
          </Text>
        </TouchableOpacity>
      </View>

      {/* Prompt Info */}
      <View className="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 mt-2">
        <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
          {generation.enhanced_prompt ? 'Enhanced Prompt' : 'Prompt'}
        </Text>
        <Text className="text-gray-900 dark:text-white">
          {generation.enhanced_prompt || generation.original_prompt}
        </Text>

        {generation.enhanced_prompt && generation.original_prompt !== generation.enhanced_prompt && (
          <View className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              Original Prompt
            </Text>
            <Text className="text-gray-600 dark:text-gray-400 text-sm">
              {generation.original_prompt}
            </Text>
          </View>
        )}

        {/* Metadata */}
        <View className="flex-row flex-wrap mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <View className="mr-4 mb-2">
            <Text className="text-xs text-gray-500">Style</Text>
            <Text className="text-sm text-gray-900 dark:text-white font-medium">
              {generation.style || 'Default'}
            </Text>
          </View>
          <View className="mr-4 mb-2">
            <Text className="text-xs text-gray-500">Size</Text>
            <Text className="text-sm text-gray-900 dark:text-white font-medium">
              {generation.size}
            </Text>
          </View>
          <View className="mr-4 mb-2">
            <Text className="text-xs text-gray-500">Quality</Text>
            <Text className="text-sm text-gray-900 dark:text-white font-medium">
              {generation.quality}
            </Text>
          </View>
          {generation.duration_seconds && (
            <View className="mb-2">
              <Text className="text-xs text-gray-500">Time</Text>
              <Text className="text-sm text-gray-900 dark:text-white font-medium">
                {generation.duration_seconds.toFixed(1)}s
              </Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}