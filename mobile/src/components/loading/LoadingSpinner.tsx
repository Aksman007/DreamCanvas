/**
 * Loading Spinner Component
 */

import React, { useEffect, useRef } from 'react';
import { View, Animated, Easing } from 'react-native';
import { Sparkles } from 'lucide-react-native';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

const SIZES = {
  sm: { container: 32, icon: 16 },
  md: { container: 48, icon: 24 },
  lg: { container: 64, icon: 32 },
};

export function LoadingSpinner({
  size = 'md',
  color = '#0ea5e9',
}: LoadingSpinnerProps) {
  const spinValue = useRef(new Animated.Value(0)).current;
  const dimensions = SIZES[size];

  useEffect(() => {
    const spin = Animated.loop(
      Animated.timing(spinValue, {
        toValue: 1,
        duration: 1500,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );
    spin.start();
    return () => spin.stop();
  }, []);

  const rotate = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <Animated.View
      style={{
        width: dimensions.container,
        height: dimensions.container,
        transform: [{ rotate }],
      }}
      className="items-center justify-center"
    >
      <Sparkles size={dimensions.icon} color={color} />
    </Animated.View>
  );
}