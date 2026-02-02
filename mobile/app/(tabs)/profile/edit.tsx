/**
 * Edit Profile Screen
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { User, Camera } from 'lucide-react-native';
import { router } from 'expo-router';

import { Header } from '../../../src/components/navigation';
import { Button, FormInput, Alert } from '../../../src/components/ui';
import { useAuthStore } from '../../../src/stores/authStore';
import { profileSchema, ProfileFormData } from '../../../src/utils/validation';

export default function EditProfileScreen() {
  const { user, updateUser, isLoading, error, clearError } = useAuthStore();

  const {
    control,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      displayName: user?.display_name || '',
      bio: user?.bio || '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateUser({
        display_name: data.displayName,
        bio: data.bio,
      });
      router.back();
    } catch (err) {
      // Error is handled by the store
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title="Edit Profile"
        showBack
        rightAction={
          <Button
            title="Save"
            size="sm"
            onPress={handleSubmit(onSubmit)}
            isLoading={isLoading}
            disabled={!isDirty}
          />
        }
      />

      <ScrollView
        className="flex-1"
        contentContainerStyle={{ padding: 16 }}
        keyboardShouldPersistTaps="handled"
      >
        {error && (
          <Alert
            type="error"
            message={error}
            onDismiss={clearError}
            className="mb-6"
          />
        )}

        {/* Avatar */}
        <View className="items-center mb-8">
          <View className="relative">
            <View className="w-24 h-24 rounded-full bg-primary-100 dark:bg-primary-900/30 items-center justify-center">
              <User size={48} color="#0ea5e9" />
            </View>
            <TouchableOpacity
              className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary-600 items-center justify-center"
              onPress={() => {}}
            >
              <Camera size={16} color="#ffffff" />
            </TouchableOpacity>
          </View>
          <Text className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Tap to change photo
          </Text>
        </View>

        {/* Form */}
        <FormInput
          name="displayName"
          control={control}
          label="Display Name"
          placeholder="How should we call you?"
          error={errors.displayName}
          autoCapitalize="words"
        />

        <FormInput
          name="bio"
          control={control}
          label="Bio"
          placeholder="Tell us about yourself..."
          error={errors.bio}
          multiline
          numberOfLines={4}
          style={{ height: 100, textAlignVertical: 'top' }}
        />

        <Text className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Your email ({user?.email}) cannot be changed.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}