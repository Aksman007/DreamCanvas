/**
 * Edit Profile Screen
 */

import React, { useState } from 'react';
import { View, Text, ScrollView, Alert, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as ImagePicker from 'expo-image-picker';
import { router, useNavigation } from 'expo-router';

import { Header } from '../../../src/components/navigation';
import { Button, FormInput, Alert as AlertComponent } from '../../../src/components/ui';
import { Avatar } from '../../../src/components/profile';
import { useAuthStore } from '../../../src/stores/authStore';
import { profileSchema, ProfileFormData } from '../../../src/utils/validation';

export default function EditProfileScreen() {
  const navigation = useNavigation();
  const { user, updateUser, isLoading, error, clearError } = useAuthStore();
  const [avatarUri, setAvatarUri] = useState<string | null>(user?.avatar_url || null);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);

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

  // Safe navigation back
  const goBack = () => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    } else {
      // Fallback to profile tab
      router.replace('/(tabs)/profile');
    }
  };

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(
        'Permission Required',
        'Please grant photo library access to change your avatar.'
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setAvatarUri(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(
        'Permission Required',
        'Please grant camera access to take a photo.'
      );
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setAvatarUri(result.assets[0].uri);
    }
  };

  const handleAvatarEdit = () => {
    Alert.alert(
      'Change Avatar',
      'Choose how you want to update your profile picture',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Take Photo', onPress: takePhoto },
        { text: 'Choose from Library', onPress: pickImage },
      ]
    );
  };

  const handleRemoveAvatar = () => {
    Alert.alert(
      'Remove Avatar',
      'Are you sure you want to remove your profile picture?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => setAvatarUri(null),
        },
      ]
    );
  };

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateUser({
        display_name: data.displayName || null,
        bio: data.bio || null,
      });
      
      // Show success and navigate back safely
      Alert.alert('Success', 'Profile updated successfully', [
        {
          text: 'OK',
          onPress: goBack,
        },
      ]);
    } catch (err) {
      // Error is handled by the store
    }
  };

  const hasChanges = isDirty || avatarUri !== user?.avatar_url;

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title="Edit Profile"
        showBack
        onBackPress={goBack}
        rightAction={
          <Button
            title="Save"
            size="sm"
            onPress={handleSubmit(onSubmit)}
            isLoading={isLoading}
            disabled={!hasChanges}
          />
        }
      />

      <ScrollView
        className="flex-1"
        contentContainerStyle={{ padding: 16 }}
        keyboardShouldPersistTaps="handled"
      >
        {error && (
          <AlertComponent
            type="error"
            message={error}
            onDismiss={clearError}
            className="mb-6"
          />
        )}

        {/* Avatar */}
        <View className="items-center mb-8">
          <Avatar
            uri={avatarUri}
            size="xl"
            editable
            onEdit={handleAvatarEdit}
            onRemove={avatarUri ? handleRemoveAvatar : undefined}
            isLoading={isUploadingAvatar}
          />
          <Text className="text-sm text-gray-500 dark:text-gray-400 mt-3">
            Tap the camera icon to change your photo
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

        {/* Email (read-only) */}
        <View className="mb-4">
          <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email
          </Text>
          <View className="bg-gray-100 dark:bg-gray-800 rounded-xl px-4 py-3.5">
            <Text className="text-gray-500 dark:text-gray-400">
              {user?.email}
            </Text>
          </View>
          <Text className="text-xs text-gray-500 dark:text-gray-400 mt-1.5">
            Email cannot be changed
          </Text>
        </View>

        {/* Account Info */}
        <View className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <Text className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Account Information
          </Text>
          <View className="flex-row justify-between">
            <Text className="text-gray-500 dark:text-gray-400">Member since</Text>
            <Text className="text-gray-900 dark:text-white">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : 'Unknown'}
            </Text>
          </View>
          <View className="flex-row justify-between mt-2">
            <Text className="text-gray-500 dark:text-gray-400">Account status</Text>
            <Text className="text-green-600">
              {user?.is_active ? 'Active' : 'Inactive'}
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}