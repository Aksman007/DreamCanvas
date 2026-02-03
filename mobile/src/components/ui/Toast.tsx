/**
 * Toast Component
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react-native';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  visible: boolean;
  type?: ToastType;
  message: string;
  duration?: number;
  onDismiss: () => void;
}

const ICONS = {
  success: { icon: CheckCircle, color: '#22c55e', bg: 'bg-green-500' },
  error: { icon: XCircle, color: '#ef4444', bg: 'bg-red-500' },
  warning: { icon: AlertCircle, color: '#f59e0b', bg: 'bg-yellow-500' },
  info: { icon: Info, color: '#3b82f6', bg: 'bg-blue-500' },
};

export function Toast({
  visible,
  type = 'info',
  message,
  duration = 3000,
  onDismiss,
}: ToastProps) {
  const insets = useSafeAreaInsets();
  const translateY = useRef(new Animated.Value(-100)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.spring(translateY, {
          toValue: 0,
          useNativeDriver: true,
          tension: 80,
          friction: 10,
        }),
        Animated.timing(opacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();

      if (duration > 0) {
        const timer = setTimeout(() => {
          handleDismiss();
        }, duration);
        return () => clearTimeout(timer);
      }
    }
  }, [visible]);

  const handleDismiss = () => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: -100,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start(() => onDismiss());
  };

  if (!visible) return null;

  const { icon: Icon, color, bg } = ICONS[type];

  return (
    <Animated.View
      style={{
        position: 'absolute',
        top: insets.top + 8,
        left: 16,
        right: 16,
        transform: [{ translateY }],
        opacity,
        zIndex: 9999,
      }}
    >
      <View className={`${bg} rounded-xl px-4 py-3 flex-row items-center shadow-lg`}>
        <Icon size={20} color="#ffffff" />
        <Text className="flex-1 text-white font-medium ml-3">{message}</Text>
        <TouchableOpacity onPress={handleDismiss} className="p-1">
          <X size={18} color="#ffffff" />
        </TouchableOpacity>
      </View>
    </Animated.View>
  );
}