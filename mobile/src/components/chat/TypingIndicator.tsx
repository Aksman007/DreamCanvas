/**
 * Typing Indicator Component
 */

import React, { useEffect, useRef } from 'react';
import { View, Animated, Easing } from 'react-native';
import { Sparkles } from 'lucide-react-native';

export function TypingIndicator() {
  const dot1 = useRef(new Animated.Value(0)).current;
  const dot2 = useRef(new Animated.Value(0)).current;
  const dot3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animate = (dot: Animated.Value, delay: number) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(dot, {
            toValue: 1,
            duration: 300,
            easing: Easing.ease,
            useNativeDriver: true,
          }),
          Animated.timing(dot, {
            toValue: 0,
            duration: 300,
            easing: Easing.ease,
            useNativeDriver: true,
          }),
        ])
      );
    };

    const anim1 = animate(dot1, 0);
    const anim2 = animate(dot2, 150);
    const anim3 = animate(dot3, 300);

    anim1.start();
    anim2.start();
    anim3.start();

    return () => {
      anim1.stop();
      anim2.stop();
      anim3.stop();
    };
  }, []);

  const dotStyle = (animValue: Animated.Value) => ({
    transform: [
      {
        translateY: animValue.interpolate({
          inputRange: [0, 1],
          outputRange: [0, -6],
        }),
      },
    ],
    opacity: animValue.interpolate({
      inputRange: [0, 1],
      outputRange: [0.4, 1],
    }),
  });

  return (
    <View className="flex-row mb-4">
      {/* Avatar */}
      <View className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 items-center justify-center mr-2">
        <Sparkles size={16} color="#0ea5e9" />
      </View>

      {/* Typing bubble */}
      <View className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md px-4 py-3 flex-row items-center">
        <Animated.View
          style={[dotStyle(dot1)]}
          className="w-2 h-2 rounded-full bg-gray-400 mr-1"
        />
        <Animated.View
          style={[dotStyle(dot2)]}
          className="w-2 h-2 rounded-full bg-gray-400 mr-1"
        />
        <Animated.View
          style={[dotStyle(dot3)]}
          className="w-2 h-2 rounded-full bg-gray-400"
        />
      </View>
    </View>
  );
}