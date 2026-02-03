/**
 * Stats Card Component
 */

import React from 'react';
import { View, Text } from 'react-native';
import { Image as ImageIcon, Clock, Sparkles, TrendingUp } from 'lucide-react-native';

interface StatsCardProps {
  generationCount: number;
  memberSince: string;
  lastGeneration?: string | null;
}

export function StatsCard({
  generationCount,
  memberSince,
  lastGeneration,
}: StatsCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      year: 'numeric',
    });
  };

  const formatRelativeTime = (dateString: string | null | undefined) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateString);
  };

  const stats = [
    {
      icon: ImageIcon,
      label: 'Creations',
      value: generationCount.toString(),
      color: '#0ea5e9',
    },
    {
      icon: Clock,
      label: 'Member Since',
      value: formatDate(memberSince),
      color: '#d946ef',
    },
    {
      icon: Sparkles,
      label: 'Last Creation',
      value: formatRelativeTime(lastGeneration),
      color: '#22c55e',
    },
  ];

  return (
    <View className="bg-white dark:bg-gray-900 rounded-2xl p-4">
      <Text className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wide">
        Statistics
      </Text>

      <View className="flex-row">
        {stats.map((stat, index) => (
          <View
            key={stat.label}
            className={`flex-1 items-center ${
              index < stats.length - 1
                ? 'border-r border-gray-200 dark:border-gray-800'
                : ''
            }`}
          >
            <View
              className="w-10 h-10 rounded-full items-center justify-center mb-2"
              style={{ backgroundColor: `${stat.color}20` }}
            >
              <stat.icon size={20} color={stat.color} />
            </View>
            <Text className="text-lg font-bold text-gray-900 dark:text-white">
              {stat.value}
            </Text>
            <Text className="text-xs text-gray-500 dark:text-gray-400">
              {stat.label}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}