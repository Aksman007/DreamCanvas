/**
 * Skeleton Loader Component
 */

import React, { useEffect, useRef, useMemo } from 'react';
import { View, Animated, ViewStyle, StyleProp } from 'react-native';

interface SkeletonLoaderProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: StyleProp<ViewStyle>;
}

export function SkeletonLoader({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
}: SkeletonLoaderProps) {
  const shimmerValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const shimmer = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmerValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(shimmerValue, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    shimmer.start();
    return () => shimmer.stop();
  }, []);

  const opacity = shimmerValue.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.7],
  });

  const animatedStyle = useMemo(
    () => ({
      width: typeof width === 'string' ? width : width,
      height,
      borderRadius,
      backgroundColor: '#e5e7eb',
      opacity,
    } as any),
    [width, height, borderRadius, opacity]
  );

  return (
    <Animated.View
      style={[animatedStyle, style]}
    />
  );
}

// Preset skeleton layouts
export function SkeletonCard() {
  return (
    <View className="bg-white dark:bg-gray-800 rounded-2xl p-4 mb-4">
      <View className="flex-row items-center mb-4">
        <SkeletonLoader width={48} height={48} borderRadius={24} />
        <View className="flex-1 ml-3">
          <SkeletonLoader width="60%" height={16} style={{ marginBottom: 8 }} />
          <SkeletonLoader width="40%" height={12} />
        </View>
      </View>
      <SkeletonLoader height={120} style={{ marginBottom: 12 }} />
      <SkeletonLoader width="80%" height={14} />
    </View>
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <View>
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </View>
  );
}

export function SkeletonGrid({ count = 9 }: { count?: number }) {
  return (
    <View className="flex-row flex-wrap">
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={{ width: '33.33%', padding: 2 }}>
          <SkeletonLoader height={120} borderRadius={4} />
        </View>
      ))}
    </View>
  );
}