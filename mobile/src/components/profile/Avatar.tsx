/**
 * Avatar Component with edit functionality
 */

import React from 'react';
import { View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Image } from 'expo-image';
import { User, Camera, X } from 'lucide-react-native';

interface AvatarProps {
  uri?: string | null;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  editable?: boolean;
  onEdit?: () => void;
  onRemove?: () => void;
  isLoading?: boolean;
}

const SIZES = {
  sm: { container: 40, icon: 20, badge: 20, badgeIcon: 10 },
  md: { container: 64, icon: 32, badge: 24, badgeIcon: 12 },
  lg: { container: 96, icon: 48, badge: 32, badgeIcon: 16 },
  xl: { container: 128, icon: 64, badge: 36, badgeIcon: 18 },
};

export function Avatar({
  uri,
  size = 'md',
  editable = false,
  onEdit,
  onRemove,
  isLoading = false,
}: AvatarProps) {
  const dimensions = SIZES[size];

  return (
    <View className="relative">
      {/* Main avatar */}
      <View
        style={{
          width: dimensions.container,
          height: dimensions.container,
          borderRadius: dimensions.container / 2,
        }}
        className="bg-primary-100 dark:bg-primary-900/30 items-center justify-center overflow-hidden"
      >
        {isLoading ? (
          <ActivityIndicator size="small" color="#0ea5e9" />
        ) : uri ? (
          <Image
            source={{ uri }}
            style={{ width: '100%', height: '100%' }}
            contentFit="cover"
            transition={200}
          />
        ) : (
          <User size={dimensions.icon} color="#0ea5e9" />
        )}
      </View>

      {/* Edit badge */}
      {editable && onEdit && (
        <TouchableOpacity
          onPress={onEdit}
          style={{
            width: dimensions.badge,
            height: dimensions.badge,
            borderRadius: dimensions.badge / 2,
          }}
          className="absolute bottom-0 right-0 bg-primary-600 items-center justify-center border-2 border-white dark:border-gray-900"
          activeOpacity={0.8}
        >
          <Camera size={dimensions.badgeIcon} color="#ffffff" />
        </TouchableOpacity>
      )}

      {/* Remove badge (when has avatar) */}
      {editable && uri && onRemove && (
        <TouchableOpacity
          onPress={onRemove}
          style={{
            width: dimensions.badge * 0.8,
            height: dimensions.badge * 0.8,
            borderRadius: (dimensions.badge * 0.8) / 2,
          }}
          className="absolute top-0 right-0 bg-red-500 items-center justify-center border-2 border-white dark:border-gray-900"
          activeOpacity={0.8}
        >
          <X size={dimensions.badgeIcon * 0.8} color="#ffffff" />
        </TouchableOpacity>
      )}
    </View>
  );
}