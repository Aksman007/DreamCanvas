/**
 * Register Screen
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
import { Link } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock, User, ArrowLeft } from 'lucide-react-native';
import { router } from 'expo-router';

import { useAuthStore } from '../../src/stores/authStore';
import { registerSchema, RegisterFormData } from '../../src/utils/validation';
import {
  Button,
  FormInput,
  Alert,
  Logo,
  Divider,
} from '../../src/components/ui';

export default function RegisterScreen() {
  const { register, isLoading, error, clearError } = useAuthStore();
  const [localError, setLocalError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      displayName: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setLocalError(null);
      clearError();
      await register({
        email: data.email,
        password: data.password,
        display_name: data.displayName || undefined,
      });
      // Navigation is handled by auth state change
    } catch (err: any) {
      setLocalError(
        err.response?.data?.detail || 'Registration failed. Please try again.'
      );
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
            {/* Back Button */}
            <TouchableOpacity
              onPress={() => router.back()}
              className="flex-row items-center mb-6"
            >
              <ArrowLeft size={24} color="#6b7280" />
              <Text className="text-gray-500 ml-2">Back</Text>
            </TouchableOpacity>

            {/* Logo */}
            <View className="items-center mb-8">
              <Logo size="md" />
            </View>

            {/* Header */}
            <View className="mb-8">
              <Text className="text-2xl font-bold text-gray-900 dark:text-white">
                Create account
              </Text>
              <Text className="text-gray-500 dark:text-gray-400 mt-1">
                Join DreamCanvas and start creating
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
                name="displayName"
                control={control}
                label="Display Name (optional)"
                placeholder="How should we call you?"
                error={errors.displayName}
                leftIcon={<User size={20} color="#9ca3af" />}
                autoCapitalize="words"
              />

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
                placeholder="Create a password"
                error={errors.password}
                leftIcon={<Lock size={20} color="#9ca3af" />}
                isPassword
                hint="At least 8 characters with a letter and number"
              />

              <FormInput
                name="confirmPassword"
                control={control}
                label="Confirm Password"
                placeholder="Confirm your password"
                error={errors.confirmPassword}
                leftIcon={<Lock size={20} color="#9ca3af" />}
                isPassword
              />

              {/* Terms */}
              <Text className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6">
                By signing up, you agree to our{' '}
                <Text className="text-primary-600">Terms of Service</Text>
                {' '}and{' '}
                <Text className="text-primary-600">Privacy Policy</Text>
              </Text>

              {/* Submit Button */}
              <Button
                title="Create Account"
                onPress={handleSubmit(onSubmit)}
                isLoading={isLoading}
                className="mb-4"
              />
            </View>

            <Divider text="or" />

            {/* Social Sign Up */}
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

            {/* Login Link */}
            <View className="flex-row justify-center mt-8">
              <Text className="text-gray-600 dark:text-gray-400">
                Already have an account?{' '}
              </Text>
              <Link href="/(auth)/login" asChild>
                <TouchableOpacity>
                  <Text className="text-primary-600 font-semibold">
                    Sign In
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