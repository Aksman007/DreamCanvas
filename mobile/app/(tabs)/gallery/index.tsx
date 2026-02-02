/**
 * Gallery Screen - Grid of user's generations
 */

import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Dimensions,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { Image as ImageIcon, Filter, AlertCircle } from 'lucide-react-native';

import { Header } from '../../../src/components/navigation';
import { Button } from '../../../src/components/ui';
import { useGenerations } from '../../../src/hooks';
import type { Generation } from '../../../src/types';

const { width } = Dimensions.get('window');
const GRID_SPACING = 2;
const NUM_COLUMNS = 3;
const ITEM_SIZE = (width - GRID_SPACING * (NUM_COLUMNS + 1)) / NUM_COLUMNS;

export default function GalleryScreen() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, refetch, isFetching } = useGenerations({
    page,
    page_size: 30,
    status: 'completed',
  });

  const handleRefresh = useCallback(() => {
    setPage(1);
    refetch();
  }, [refetch]);

  const renderItem = useCallback(
    ({ item }: { item: Generation }) => (
      <TouchableOpacity
        onPress={() => router.push(`/(tabs)/gallery/${item.id}`)}
        style={{
          width: ITEM_SIZE,
          height: ITEM_SIZE,
          margin: GRID_SPACING / 2,
        }}
        activeOpacity={0.8}
      >
        {item.thumbnail_url ? (
          <Image
            source={{ uri: item.thumbnail_url }}
            style={{ width: '100%', height: '100%' }}
            contentFit="cover"
            transition={200}
          />
        ) : item.image_url ? (
          <Image
            source={{ uri: item.image_url }}
            style={{ width: '100%', height: '100%' }}
            contentFit="cover"
            transition={200}
          />
        ) : (
          <View className="flex-1 bg-gray-200 dark:bg-gray-800 items-center justify-center">
            {item.status === 'failed' ? (
              <AlertCircle size={24} color="#ef4444" />
            ) : (
              <ImageIcon size={24} color="#9ca3af" />
            )}
          </View>
        )}
      </TouchableOpacity>
    ),
    []
  );

  const renderEmpty = useCallback(
    () => (
      <View className="flex-1 items-center justify-center p-8">
        <View className="w-20 h-20 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center mb-6">
          <ImageIcon size={40} color="#9ca3af" />
        </View>

        <Text className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          No Creations Yet
        </Text>
        <Text className="text-gray-500 dark:text-gray-400 text-center mb-6">
          Your AI-generated images will appear here
        </Text>

        <Button
          title="Create Your First Image"
          onPress={() => router.push('/(tabs)/generate')}
        />
      </View>
    ),
    []
  );

  const renderFooter = useCallback(() => {
    if (!isFetching || isLoading) return null;
    return (
      <View className="py-4 items-center">
        <ActivityIndicator size="small" color="#0ea5e9" />
      </View>
    );
  }, [isFetching, isLoading]);

  const renderError = () => (
    <View className="flex-1 items-center justify-center p-8">
      <AlertCircle size={48} color="#ef4444" />
      <Text className="text-xl font-bold text-gray-900 dark:text-white mt-4 mb-2">
        Something went wrong
      </Text>
      <Text className="text-gray-500 dark:text-gray-400 text-center mb-6">
        Failed to load your gallery
      </Text>
      <Button title="Try Again" onPress={() => refetch()} />
    </View>
  );

  if (isError) {
    return (
      <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
        <Header title="Gallery" />
        {renderError()}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title="Gallery"
        subtitle={data?.total ? `${data.total} creations` : undefined}
        rightAction={
          <TouchableOpacity
            onPress={() => {}}
            className="p-2 rounded-full active:bg-gray-100 dark:active:bg-gray-800"
          >
            <Filter size={22} color="#374151" />
          </TouchableOpacity>
        }
      />

      {isLoading ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color="#0ea5e9" />
          <Text className="text-gray-500 mt-4">Loading gallery...</Text>
        </View>
      ) : (
        <FlatList
          data={data?.items || []}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          numColumns={NUM_COLUMNS}
          contentContainerStyle={{
            padding: GRID_SPACING / 2,
            flexGrow: 1,
          }}
          ListEmptyComponent={renderEmpty}
          ListFooterComponent={renderFooter}
          refreshControl={
            <RefreshControl
              refreshing={isFetching && !isLoading}
              onRefresh={handleRefresh}
              colors={['#0ea5e9']}
              tintColor="#0ea5e9"
            />
          }
          showsVerticalScrollIndicator={false}
          onEndReached={() => {
            if (data && page < data.pages) {
              setPage((p) => p + 1);
            }
          }}
          onEndReachedThreshold={0.5}
        />
      )}
    </SafeAreaView>
  );
}