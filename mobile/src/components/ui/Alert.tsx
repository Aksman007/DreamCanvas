/**
 * Alert Component - For displaying messages
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react-native';

interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export function Alert({
  type = 'info',
  title,
  message,
  onDismiss,
  className,
}: AlertProps) {
  const config = {
    success: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-200 dark:border-green-800',
      icon: CheckCircle,
      iconColor: '#22c55e',
      titleColor: 'text-green-800 dark:text-green-200',
      textColor: 'text-green-700 dark:text-green-300',
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      icon: XCircle,
      iconColor: '#ef4444',
      titleColor: 'text-red-800 dark:text-red-200',
      textColor: 'text-red-700 dark:text-red-300',
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      icon: AlertCircle,
      iconColor: '#f59e0b',
      titleColor: 'text-yellow-800 dark:text-yellow-200',
      textColor: 'text-yellow-700 dark:text-yellow-300',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      icon: Info,
      iconColor: '#3b82f6',
      titleColor: 'text-blue-800 dark:text-blue-200',
      textColor: 'text-blue-700 dark:text-blue-300',
    },
  };

  const { bg, border, icon: Icon, iconColor, titleColor, textColor } = config[type];

  return (
    <View
      className={`
        flex-row items-start p-4 rounded-xl border
        ${bg} ${border} ${className}
      `}
    >
      <Icon size={20} color={iconColor} />

      <View className="flex-1 ml-3">
        {title && (
          <Text className={`font-semibold ${titleColor} mb-1`}>{title}</Text>
        )}
        <Text className={textColor}>{message}</Text>
      </View>

      {onDismiss && (
        <TouchableOpacity
          onPress={onDismiss}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <X size={18} color="#9ca3af" />
        </TouchableOpacity>
      )}
    </View>
  );
}