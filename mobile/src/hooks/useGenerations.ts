/**
 * useGenerations Hook - React Query hook for gallery
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { generateApi } from '../api';
import type { Generation, GenerationListResponse } from '../types';

// Query keys
export const generationKeys = {
  all: ['generations'] as const,
  lists: () => [...generationKeys.all, 'list'] as const,
  list: (params: { page?: number; status?: string }) =>
    [...generationKeys.lists(), params] as const,
  details: () => [...generationKeys.all, 'detail'] as const,
  detail: (id: string) => [...generationKeys.details(), id] as const,
};

// Hook for fetching generations list
export function useGenerations(params?: { page?: number; page_size?: number; status?: string }) {
  return useQuery({
    queryKey: generationKeys.list({ page: params?.page, status: params?.status }),
    queryFn: () => generateApi.list(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

// Hook for fetching single generation
export function useGeneration(id: string | undefined) {
  return useQuery({
    queryKey: generationKeys.detail(id!),
    queryFn: () => generateApi.getById(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Hook for deleting generation
export function useDeleteGeneration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => generateApi.delete(id),
    onSuccess: () => {
      // Invalidate and refetch generations list
      queryClient.invalidateQueries({ queryKey: generationKeys.lists() });
    },
  });
}

// Hook for infinite scrolling
export function useInfiniteGenerations(params?: { page_size?: number; status?: string }) {
  return useQuery({
    queryKey: generationKeys.list({ status: params?.status }),
    queryFn: ({ pageParam = 1 }) =>
      generateApi.list({ page: pageParam as number, ...params }),
    staleTime: 1000 * 60 * 2,
  });
}