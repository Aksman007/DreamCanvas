/**
 * Generation Store - Zustand store for image generation state
 */

import { create } from 'zustand';
import { generateApi } from '../api/generate';
import { chatApi } from '../api/chat';
import type {
  Generation,
  GenerationRequest,
  GenerationStatus,
  PromptEnhanceResponse,
} from '../types';
import { APP_CONFIG } from '../constants/config';

interface GenerationState {
  // Current generation being processed
  currentGeneration: Generation | null;
  isGenerating: boolean;
  generationError: string | null;

  // Prompt enhancement
  enhancedPrompt: PromptEnhanceResponse | null;
  isEnhancing: boolean;

  // Polling
  pollingInterval: NodeJS.Timeout | null;

  // Actions
  generate: (request: GenerationRequest) => Promise<Generation>;
  pollStatus: (id: string) => Promise<void>;
  startPolling: (id: string) => void;
  stopPolling: () => void;
  enhancePrompt: (prompt: string, style?: string) => Promise<PromptEnhanceResponse>;
  clearCurrentGeneration: () => void;
  clearError: () => void;
  setCurrentGeneration: (generation: Generation | null) => void;
}

export const useGenerationStore = create<GenerationState>((set, get) => ({
  // Initial state
  currentGeneration: null,
  isGenerating: false,
  generationError: null,
  enhancedPrompt: null,
  isEnhancing: false,
  pollingInterval: null,

  // Generate image
  generate: async (request: GenerationRequest) => {
    try {
      set({ isGenerating: true, generationError: null });

      // Create generation (async mode)
      const generation = await generateApi.create(request, false);
      set({ currentGeneration: generation });

      // Start polling for status
      get().startPolling(generation.id);

      return generation;
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Failed to start generation';
      set({ generationError: message, isGenerating: false });
      throw error;
    }
  },

  // Poll for generation status
  pollStatus: async (id: string) => {
    try {
      const status = await generateApi.getStatus(id);

      // Update current generation with new status
      set((state) => ({
        currentGeneration: state.currentGeneration
          ? {
              ...state.currentGeneration,
              status: status.status as GenerationStatus,
              image_url: status.image_url || state.currentGeneration.image_url,
              thumbnail_url:
                status.thumbnail_url || state.currentGeneration.thumbnail_url,
              error_message: status.error || state.currentGeneration.error_message,
            }
          : null,
      }));

      // Check if generation is complete
      if (status.status === 'completed' || status.status === 'failed') {
        get().stopPolling();
        set({ isGenerating: false });

        // Fetch full generation details
        if (status.status === 'completed') {
          const fullGeneration = await generateApi.getById(id);
          set({ currentGeneration: fullGeneration });
        } else if (status.error) {
          set({ generationError: status.error });
        }
      }
    } catch (error: any) {
      console.error('Polling error:', error);
      // Don't stop polling on network errors, might be temporary
    }
  },

  // Start polling
  startPolling: (id: string) => {
    // Stop any existing polling
    get().stopPolling();

    // Start new polling interval
    const interval = setInterval(() => {
      get().pollStatus(id);
    }, APP_CONFIG.generationPollInterval);

    set({ pollingInterval: interval as unknown as NodeJS.Timeout });

    // Also poll immediately
    get().pollStatus(id);
  },

  // Stop polling
  stopPolling: () => {
    const { pollingInterval } = get();
    if (pollingInterval) {
      clearInterval(pollingInterval);
      set({ pollingInterval: null });
    }
  },

  // Enhance prompt
  enhancePrompt: async (prompt: string, style?: string) => {
    try {
      set({ isEnhancing: true });
      const result = await chatApi.enhancePrompt(prompt, style);
      set({ enhancedPrompt: result, isEnhancing: false });
      return result;
    } catch (error: any) {
      set({ isEnhancing: false });
      throw error;
    }
  },

  // Clear current generation
  clearCurrentGeneration: () => {
    get().stopPolling();
    set({
      currentGeneration: null,
      isGenerating: false,
      generationError: null,
      enhancedPrompt: null,
    });
  },

  // Clear error
  clearError: () => set({ generationError: null }),

  // Set current generation (for viewing existing ones)
  setCurrentGeneration: (generation) => set({ currentGeneration: generation }),
}));

// Selector hooks
export const useCurrentGeneration = () =>
  useGenerationStore((state) => state.currentGeneration);
export const useIsGenerating = () =>
  useGenerationStore((state) => state.isGenerating);
export const useGenerationError = () =>
  useGenerationStore((state) => state.generationError);