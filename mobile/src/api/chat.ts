/**
 * Chat API Functions
 */

import apiClient from './client';
import { API_ENDPOINTS } from '../constants/api';
import type {
  ChatRequest,
  ChatResponse,
  PromptEnhanceResponse,
} from '../types';

export const chatApi = {
  /**
   * Chat with Claude for prompt assistance
   */
  async chat(data: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      API_ENDPOINTS.CHAT,
      data
    );
    return response.data;
  },

  /**
   * Enhance a prompt without generating
   */
  async enhancePrompt(
    prompt: string,
    style?: string,
    negativePrompt?: string
  ): Promise<PromptEnhanceResponse> {
    const params = new URLSearchParams({ prompt });
    if (style) params.append('style', style);
    if (negativePrompt) params.append('negative_prompt', negativePrompt);

    const response = await apiClient.post<PromptEnhanceResponse>(
      `${API_ENDPOINTS.CHAT_ENHANCE}?${params.toString()}`
    );
    return response.data;
  },
};