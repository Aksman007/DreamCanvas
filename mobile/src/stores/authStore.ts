/**
 * Auth Store - Zustand store for authentication state
 */

import { create } from 'zustand';
import { authApi } from '../api/auth';
import { tokenStorage } from '../api/client';
import type { User, LoginRequest, RegisterRequest } from '../types';

interface AuthState {
  // State
  user: User | null;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;

  // Actions
  initialize: () => Promise<void>;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
  setError: (error: string) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Initial state
  user: null,
  isLoading: false,
  isInitialized: false,
  error: null,

  // Initialize - check for existing session
  initialize: async () => {
    try {
      set({ isLoading: true, error: null });

      const token = await tokenStorage.getAccessToken();
      if (token) {
        try {
          const user = await authApi.getMe();
          set({ user });
        } catch (error) {
          // Token invalid or expired
          console.log('Token invalid, clearing...');
          await tokenStorage.clearTokens();
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
    } finally {
      set({ isLoading: false, isInitialized: true });
    }
  },

  // Login
  login: async (data: LoginRequest) => {
    try {
      set({ isLoading: true, error: null });

      const response = await authApi.login(data);
      set({ user: response.user });
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Login failed. Please check your credentials.';
      set({ error: message });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  // Register
  register: async (data: RegisterRequest) => {
    try {
      set({ isLoading: true, error: null });

      const response = await authApi.register(data);
      set({ user: response.user });
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Registration failed. Please try again.';
      set({ error: message });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  // Logout
  logout: async () => {
    try {
      set({ isLoading: true });
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({ user: null, isLoading: false, error: null });
    }
  },

  // Refresh user data
  refreshUser: async () => {
    try {
      const user = await authApi.getMe();
      set({ user });
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // If refresh fails, the interceptor will handle token refresh
      // If that also fails, user will be logged out
    }
  },

  // Update user profile
  updateUser: async (data: Partial<User>) => {
    try {
      set({ isLoading: true, error: null });
      const updatedUser = await authApi.updateMe(data);
      set({ user: updatedUser });
    } catch (error: any) {
      const message =
        error.response?.data?.detail ||
        error.message ||
        'Failed to update profile.';
      set({ error: message });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Set error manually
  setError: (error: string) => set({ error }),
}));

// Selector hooks for better performance
export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => !!state.user);
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);