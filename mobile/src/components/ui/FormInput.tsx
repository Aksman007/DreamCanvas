/**
 * Form Input Component - Works with react-hook-form
 */

import React from 'react';
import {
  View,
  TextInput,
  Text,
  TextInputProps,
  TouchableOpacity,
} from 'react-native';
import { Control, Controller, FieldError } from 'react-hook-form';
import { Eye, EyeOff } from 'lucide-react-native';

interface FormInputProps extends Omit<TextInputProps, 'value' | 'onChangeText'> {
  name: string;
  control: Control<any>;
  label?: string;
  error?: FieldError;
  hint?: string;
  leftIcon?: React.ReactNode;
  isPassword?: boolean;
}

export function FormInput({
  name,
  control,
  label,
  error,
  hint,
  leftIcon,
  isPassword = false,
  className,
  ...props
}: FormInputProps) {
  const [showPassword, setShowPassword] = React.useState(false);
  const hasError = !!error;

  return (
    <View className={`mb-4 ${className}`}>
      {label && (
        <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
        </Text>
      )}

      <Controller
        name={name}
        control={control}
        render={({ field: { onChange, onBlur, value } }) => (
          <View
            className={`
              flex-row items-center bg-gray-100 dark:bg-gray-800 rounded-xl
              border-2 ${hasError ? 'border-red-500' : 'border-transparent focus:border-primary-500'}
            `}
          >
            {leftIcon && (
              <View className="pl-4">{leftIcon}</View>
            )}

            <TextInput
              className={`
                flex-1 px-4 py-3.5 text-base text-gray-900 dark:text-white
                ${leftIcon ? 'pl-3' : ''}
                ${isPassword ? 'pr-12' : ''}
              `}
              placeholderTextColor="#9ca3af"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              secureTextEntry={isPassword && !showPassword}
              autoCapitalize={isPassword ? 'none' : props.autoCapitalize}
              autoCorrect={isPassword ? false : props.autoCorrect}
              {...props}
            />

            {isPassword && (
              <TouchableOpacity
                className="absolute right-4"
                onPress={() => setShowPassword(!showPassword)}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                {showPassword ? (
                  <EyeOff size={20} color="#9ca3af" />
                ) : (
                  <Eye size={20} color="#9ca3af" />
                )}
              </TouchableOpacity>
            )}
          </View>
        )}
      />

      {error && (
        <Text className="text-sm text-red-500 mt-1.5">{error.message}</Text>
      )}

      {hint && !error && (
        <Text className="text-sm text-gray-500 mt-1.5">{hint}</Text>
      )}
    </View>
  );
}