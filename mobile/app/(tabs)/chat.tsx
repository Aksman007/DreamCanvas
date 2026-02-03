/**
 * Chat Screen - Claude AI Assistant
 */

import React, { useRef, useEffect, useCallback } from 'react';
import {
  View,
  FlatList,
  TouchableOpacity,
  Text,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { Trash2 } from 'lucide-react-native';

import { Header } from '../../src/components/navigation';
import {
  MessageBubble,
  ChatInput,
  SuggestedPrompts,
  TypingIndicator,
  PromptBanner,
} from '../../src/components/chat';
import {
  useChatStore,
  useChatMessages,
  useIsChatLoading,
  useChatError,
  useSuggestedPrompt,
} from '../../src/stores';
import { Alert as AlertComponent } from '../../src/components/ui';
import type { ChatMessage } from '../../src/types';

export default function ChatScreen() {
  const flatListRef = useRef<FlatList>(null);
  const messages = useChatMessages();
  const isLoading = useIsChatLoading();
  const error = useChatError();
  const suggestedPrompt = useSuggestedPrompt();

  const { sendMessage, clearChat, clearError, setSuggestedPrompt } = useChatStore();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages.length, isLoading]);

  const handleSend = useCallback(
    async (message: string) => {
      await sendMessage(message);
    },
    [sendMessage]
  );

  const handleSuggestionSelect = useCallback(
    (prompt: string) => {
      handleSend(prompt);
    },
    [handleSend]
  );

  const handleUsePrompt = useCallback(() => {
    if (suggestedPrompt) {
      // Navigate to generate screen with the prompt
      // We'll use a global state or params to pass the prompt
      router.push({
        pathname: '/(tabs)/generate',
        params: { prompt: suggestedPrompt },
      });
      setSuggestedPrompt(null);
    }
  }, [suggestedPrompt, setSuggestedPrompt]);

  const handleClearChat = useCallback(() => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear all messages?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: clearChat,
        },
      ]
    );
  }, [clearChat]);

  const renderMessage = useCallback(
    ({ item, index }: { item: ChatMessage; index: number }) => (
      <MessageBubble
        message={item}
        isLast={index === messages.length - 1}
      />
    ),
    [messages.length]
  );

  const hasMessages = messages.length > 0;

  return (
    <SafeAreaView className="flex-1 bg-white dark:bg-gray-900" edges={['top']}>
      <Header
        title="AI Assistant"
        rightAction={
          hasMessages ? (
            <TouchableOpacity
              onPress={handleClearChat}
              className="p-2 rounded-full active:bg-gray-100 dark:active:bg-gray-800"
            >
              <Trash2 size={22} color="#6b7280" />
            </TouchableOpacity>
          ) : undefined
        }
      />

      {/* Error Alert */}
      {error && (
        <AlertComponent
          type="error"
          message={error}
          onDismiss={clearError}
          className="mx-4 mb-2"
        />
      )}

      {/* Suggested Prompt Banner */}
      {suggestedPrompt && (
        <PromptBanner
          prompt={suggestedPrompt}
          onUse={handleUsePrompt}
          onDismiss={() => setSuggestedPrompt(null)}
        />
      )}

      {/* Chat Content */}
      {hasMessages ? (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(_, index) => `message-${index}`}
          contentContainerStyle={{ padding: 16, paddingBottom: 8 }}
          showsVerticalScrollIndicator={false}
          ListFooterComponent={isLoading ? <TypingIndicator /> : null}
        />
      ) : (
        <SuggestedPrompts onSelect={handleSuggestionSelect} />
      )}

      {/* Chat Input */}
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </SafeAreaView>
  );
}