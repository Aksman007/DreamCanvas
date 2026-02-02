/**
 * Login Screen
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Link, router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock } from 'lucide-react-native';

import { useAuthStore } from '../../src/stores/authStore';
import { loginSchema, LoginFormData } from '../../src/utils/validation';
import {
  Button,
  FormInput,
  Alert,
  Logo,
  Divider,
} from '../../src/components/ui';

export default function LoginScreen() {
  const { login, isLoading, error, clearError } = useAuthStore();
  const [localError, setLocalError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setLocalError(null);
      clearError();
      await login(data);
      // Navigation is handled by auth state change in _layout
    } catch (err: any) {
      setLocalError(err.response?.data?.detail || 'Login failed. Please try again.');
    }
  };

  const displayError = localError || error;

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900">
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1"
      >
        <ScrollView
          contentContainerStyle={{ flexGrow: 1 }}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View className="flex-1 px-6 py-8">
            {/* Logo */}
            <View className="items-center mt-8 mb-12">
              <Logo size="lg" />
              <Text className="text-gray-500 dark:text-gray-400 mt-3 text-center">
                Create amazing AI-generated art
              </Text>
            </View>

            {/* Welcome Text */}
            <View className="mb-8">
              <Text className="text-2xl font-bold text-gray-900 dark:text-white">
                Welcome back
              </Text>
              <Text className="text-gray-500 dark:text-gray-400 mt-1">
                Sign in to continue creating
              </Text>
            </View>

            {/* Error Alert */}
            {displayError && (
              <Alert
                type="error"
                message={displayError}
                onDismiss={() => {
                  setLocalError(null);
                  clearError();
                }}
                className="mb-6"
              />
            )}

            {/* Form */}
            <View>
              <FormInput
                name="email"
                control={control}
                label="Email"
                placeholder="Enter your email"
                error={errors.email}
                leftIcon={<Mail size={20} color="#9ca3af" />}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
              />

              <FormInput
                name="password"
                control={control}
                label="Password"
                placeholder="Enter your password"
                error={errors.password}
                leftIcon={<Lock size={20} color="#9ca3af" />}
                isPassword
                autoComplete="password"
              />

              {/* Forgot Password */}
              <TouchableOpacity className="self-end mb-6">
                <Text className="text-primary-600 font-medium">
                  Forgot password?
                </Text>
              </TouchableOpacity>

              {/* Submit Button */}
              <Button
                title="Sign In"
                onPress={handleSubmit(onSubmit)}
                isLoading={isLoading}
                className="mb-4"
              />
            </View>

            <Divider text="or" />

            {/* Social Login (Placeholder) */}
            <View className="space-y-3">
              <Button
                title="Continue with Google"
                variant="outline"
                onPress={() => {}}
                className="mb-3"
              />
              <Button
                title="Continue with Apple"
                variant="outline"
                onPress={() => {}}
              />
            </View>

            {/* Register Link */}
            <View className="flex-row justify-center mt-8">
              <Text className="text-gray-600 dark:text-gray-400">
                Don't have an account?{' '}
              </Text>
              <Link href="/(auth)/register" asChild>
                <TouchableOpacity>
                  <Text className="text-primary-600 font-semibold">
                    Sign Up
                  </Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}