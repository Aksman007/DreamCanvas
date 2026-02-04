/**
 * Auth Store Tests
 */

import { act, renderHook } from '@testing-library/react-native';
import { useAuthStore } from '../../stores/authStore';
import * as SecureStore from 'expo-secure-store';

// Reset store before each test
beforeEach(() => {
  useAuthStore.setState({
    user: null,
    isLoading: false,
    isInitialized: false,
    error: null,
  });
  jest.clearAllMocks();
});

describe('useAuthStore', () => {
  describe('initial state', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.user).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isInitialized).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('initialize', () => {
    it('should set isInitialized to true after initialization', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.initialize();
      });
      
      expect(result.current.isInitialized).toBe(true);
      expect(result.current.user).toBeNull();
    });
  });

  describe('clearError', () => {
    it('should clear error state', () => {
      useAuthStore.setState({ error: 'Some error' });
      
      const { result } = renderHook(() => useAuthStore());
      
      expect(result.current.error).toBe('Some error');
      
      act(() => {
        result.current.clearError();
      });
      
      expect(result.current.error).toBeNull();
    });
  });

  describe('logout', () => {
    it('should clear user and tokens', async () => {
      useAuthStore.setState({
        user: {
          id: 'user-123',
          email: 'test@example.com',
          display_name: 'Test',
          avatar_url: null,
          bio: null,
          is_active: true,
          is_verified: false,
          is_superuser: false,
          preferences: {},
          generation_count: 0,
          last_generation_at: null,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      });
      
      const { result } = renderHook(() => useAuthStore());
      
      await act(async () => {
        await result.current.logout();
      });
      
      expect(result.current.user).toBeNull();
      expect(SecureStore.deleteItemAsync).toHaveBeenCalled();
    });
  });
});