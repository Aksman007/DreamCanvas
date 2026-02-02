/**
 * Generation Progress Component
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, Easing } from 'react-native';
import {
  Sparkles,
  Wand2,
  Image as ImageIcon,
  Upload,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react-native';

import type { GenerationStatus } from '../../types';

const STEPS = [
  { status: 'pending', label: 'Queued', icon: Loader2 },
  { status: 'enhancing', label: 'Enhancing Prompt', icon: Wand2 },
  { status: 'generating', label: 'Creating Image', icon: ImageIcon },
  { status: 'uploading', label: 'Saving', icon: Upload },
  { status: 'completed', label: 'Complete', icon: CheckCircle },
];

interface GenerationProgressProps {
  status: GenerationStatus;
  error?: string | null;
}

export function GenerationProgress({ status, error }: GenerationProgressProps) {
  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;

  // Spinning animation for loading icon
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

  // Pulse animation for active step
  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseValue, {
          toValue: 1.1,
          duration: 800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseValue, {
          toValue: 1,
          duration: 800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, []);

  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const getCurrentStepIndex = () => {
    if (status === 'failed') return -1;
    if (status === 'processing') return 0;
    return STEPS.findIndex((s) => s.status === status);
  };

  const currentIndex = getCurrentStepIndex();

  if (status === 'failed') {
    return (
      <View className="items-center py-8">
        <View className="w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/30 items-center justify-center mb-4">
          <XCircle size={40} color="#ef4444" />
        </View>
        <Text className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          Generation Failed
        </Text>
        <Text className="text-gray-500 dark:text-gray-400 text-center px-8">
          {error || 'Something went wrong. Please try again.'}
        </Text>
      </View>
    );
  }

  return (
    <View className="py-4">
      {/* Main Progress Icon */}
      <View className="items-center mb-8">
        <Animated.View
          style={[
            {
              transform:
                status !== 'completed'
                  ? [{ rotate: spin }, { scale: pulseValue }]
                  : [],
            },
          ]}
          className="w-24 h-24 rounded-full bg-primary-100 dark:bg-primary-900/30 items-center justify-center"
        >
          {status === 'completed' ? (
            <CheckCircle size={48} color="#22c55e" />
          ) : (
            <Sparkles size={48} color="#0ea5e9" />
          )}
        </Animated.View>

        <Text className="text-xl font-bold text-gray-900 dark:text-white mt-4">
          {status === 'completed'
            ? 'Generation Complete!'
            : status === 'pending' || status === 'processing'
            ? 'Starting...'
            : STEPS.find((s) => s.status === status)?.label || 'Processing...'}
        </Text>
      </View>

      {/* Step Indicators */}
      <View className="px-4">
        {STEPS.filter((s) => s.status !== 'pending').map((step, index) => {
          const Icon = step.icon;
          const stepIndex = STEPS.findIndex((s) => s.status === step.status);
          const isComplete = currentIndex > stepIndex || status === 'completed';
          const isActive =
            currentIndex === stepIndex && status !== 'completed';

          return (
            <View key={step.status} className="flex-row items-center mb-4">
              {/* Icon */}
              <View
                className={`
                  w-10 h-10 rounded-full items-center justify-center
                  ${
                    isComplete
                      ? 'bg-green-100 dark:bg-green-900/30'
                      : isActive
                      ? 'bg-primary-100 dark:bg-primary-900/30'
                      : 'bg-gray-100 dark:bg-gray-800'
                  }
                `}
              >
                {isComplete ? (
                  <CheckCircle size={20} color="#22c55e" />
                ) : (
                  <Icon
                    size={20}
                    color={isActive ? '#0ea5e9' : '#9ca3af'}
                  />
                )}
              </View>

              {/* Label */}
              <Text
                className={`
                  ml-3 font-medium
                  ${
                    isComplete
                      ? 'text-green-600 dark:text-green-400'
                      : isActive
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-400 dark:text-gray-500'
                  }
                `}
              >
                {step.label}
              </Text>

              {/* Active indicator */}
              {isActive && (
                <Animated.View
                  style={{ transform: [{ rotate: spin }] }}
                  className="ml-auto"
                >
                  <Loader2 size={16} color="#0ea5e9" />
                </Animated.View>
              )}
            </View>
          );
        })}
      </View>
    </View>
  );
}