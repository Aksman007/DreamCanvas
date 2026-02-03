/**
 * Chat Store - Zustand store for chat state
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { chatApi } from '../api/chat';
import type { ChatMessage } from '../types';

interface ChatState {
  // State
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  suggestedPrompt: string | null;

  // Actions
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  clearError: () => void;
  setSuggestedPrompt: (prompt: string | null) => void;
  useSuggestedPrompt: () => string | null;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      messages: [],
      isLoading: false,
      error: null,
      suggestedPrompt: null,

      // Send message to Claude
      sendMessage: async (message: string) => {
        const { messages } = get();

        // Add user message immediately
        const userMessage: ChatMessage = { role: 'user', content: message };
        set({
          messages: [...messages, userMessage],
          isLoading: true,
          error: null,
        });

        try {
          const response = await chatApi.chat({
            message,
            conversation_history: messages,
          });

          // Add assistant response
          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: response.message,
          };

          set((state) => ({
            messages: [...state.messages, assistantMessage],
            suggestedPrompt: response.suggested_prompt,
            isLoading: false,
          }));
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            error.message ||
            'Failed to send message';

          set({
            error: errorMessage,
            isLoading: false,
          });
        }
      },

      // Clear chat history
      clearChat: () =>
        set({
          messages: [],
          suggestedPrompt: null,
          error: null,
        }),

      // Clear error
      clearError: () => set({ error: null }),

      // Set suggested prompt
      setSuggestedPrompt: (prompt) => set({ suggestedPrompt: prompt }),

      // Use and clear suggested prompt
      useSuggestedPrompt: () => {
        const { suggestedPrompt } = get();
        set({ suggestedPrompt: null });
        return suggestedPrompt;
      },
    }),
    {
      name: 'dreamcanvas-chat',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        messages: state.messages.slice(-50), // Keep last 50 messages
      }),
    }
  )
);

// Selector hooks
export const useChatMessages = () => useChatStore((state) => state.messages);
export const useIsChatLoading = () => useChatStore((state) => state.isLoading);
export const useChatError = () => useChatStore((state) => state.error);
export const useSuggestedPrompt = () => useChatStore((state) => state.suggestedPrompt);