/**
 * Test Utilities
 */

import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a fresh QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

interface WrapperProps {
  children: ReactNode;
}

const AllTheProviders = ({ children }: WrapperProps) => {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react-native';
export { customRender as render };

// Helper to wait for async operations
export const waitForAsync = () => new Promise((resolve) => setTimeout(resolve, 0));

// Helper to create mock user
export const createMockUser = (overrides = {}) => ({
  id: 'user-123',
  email: 'test@example.com',
  display_name: 'Test User',
  avatar_url: null,
  bio: null,
  is_active: true,
  is_verified: false,
  is_superuser: false,
  preferences: {},
  generation_count: 5,
  last_generation_at: null,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

// Helper to create mock generation
export const createMockGeneration = (overrides = {}) => ({
  id: 'gen-123',
  user_id: 'user-123',
  original_prompt: 'A beautiful sunset',
  enhanced_prompt: 'A beautiful sunset over the ocean with vibrant colors',
  negative_prompt: null,
  status: 'completed',
  provider: 'dalle',
  model: 'dall-e-3',
  style: 'vivid',
  size: '1024x1024',
  quality: 'standard',
  image_url: 'https://example.com/image.png',
  thumbnail_url: 'https://example.com/thumb.png',
  error_message: null,
  error_code: null,
  started_at: '2024-01-01T00:00:00Z',
  completed_at: '2024-01-01T00:00:01Z',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:01Z',
  duration_seconds: 1.5,
  ...overrides,
});