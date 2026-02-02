/**
 * Input Component
 */

import React, { forwardRef } from 'react';
import {
  View,
  TextInput,
  Text,
  TextInputProps,
} from 'react-native';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<TextInput, InputProps>(
  ({ label, error, hint, leftIcon, rightIcon, className, ...props }, ref) => {
    const hasError = !!error;
    
    const inputStyles = `
      flex-1 px-4 py-3 text-base text-gray-900 dark:text-white
      ${leftIcon ? 'pl-12' : ''}
      ${rightIcon ? 'pr-12' : ''}
    `;
    
    const containerStyles = `
      flex-row items-center bg-gray-100 dark:bg-gray-800 rounded-xl
      border-2 ${hasError ? 'border-red-500' : 'border-transparent'}
    `;
    
    return (
      <View className={`mb-4 ${className}`}>
        {label && (
          <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {label}
          </Text>
        )}
        
        <View className={containerStyles}>
          {leftIcon && (
            <View className="absolute left-4 z-10">{leftIcon}</View>
          )}
          
          <TextInput
            ref={ref}
            className={inputStyles}
            placeholderTextColor="#9ca3af"
            {...props}
          />
          
          {rightIcon && (
            <View className="absolute right-4 z-10">{rightIcon}</View>
          )}
        </View>
        
        {error && (
          <Text className="text-sm text-red-500 mt-1">{error}</Text>
        )}
        
        {hint && !error && (
          <Text className="text-sm text-gray-500 mt-1">{hint}</Text>
        )}
      </View>
    );
  }
);

Input.displayName = 'Input';