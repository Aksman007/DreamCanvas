/**
 * Generation API Functions
 */

import apiClient from './client';
import { API_ENDPOINTS, TIMEOUTS } from '../constants/api';
import type {
  Generation,
  GenerationRequest,
  GenerationListResponse,
} from '../types';

export const generateApi = {
  /**
   * Create a new generation
   */
  async create(data: GenerationRequest, sync: boolean = false): Promise<Generation> {
    const response = await apiClient.post<Generation>(
      `${API_ENDPOINTS.GENERATE}${sync ? '?sync=true' : ''}`,
      data,
      { timeout: sync ? TIMEOUTS.GENERATION : TIMEOUTS.DEFAULT }
    );
    return response.data;
  },

  /**
   * Get generation by ID
   */
  async getById(id: string): Promise<Generation> {
    const response = await apiClient.get<Generation>(
      API_ENDPOINTS.GENERATION(id)
    );
    return response.data;
  },

  /**
   * Get generation status (lightweight)
   */
  async getStatus(id: string): Promise<{
    generation_id: string;
    status: string;
    message?: string;
    image_url?: string;
    thumbnail_url?: string;
    error?: string;
  }> {
    const response = await apiClient.get(
      API_ENDPOINTS.GENERATION_STATUS(id)
    );
    return response.data;
  },

  /**
   * Delete a generation
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.GENERATION(id));
  },

  /**
   * List user's generations (gallery)
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<GenerationListResponse> {
    const response = await apiClient.get<GenerationListResponse>(
      API_ENDPOINTS.GALLERY,
      { params }
    );
    return response.data;
  },
};