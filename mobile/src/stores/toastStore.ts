/**
 * Toast Store
 */

import { create } from 'zustand';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastState {
  visible: boolean;
  type: ToastType;
  message: string;
  show: (message: string, type?: ToastType) => void;
  hide: () => void;
}

export const useToastStore = create<ToastState>((set) => ({
  visible: false,
  type: 'info',
  message: '',
  
  show: (message, type = 'info') => set({ visible: true, message, type }),
  hide: () => set({ visible: false }),
}));

// Helper functions
export const toast = {
  success: (message: string) => useToastStore.getState().show(message, 'success'),
  error: (message: string) => useToastStore.getState().show(message, 'error'),
  warning: (message: string) => useToastStore.getState().show(message, 'warning'),
  info: (message: string) => useToastStore.getState().show(message, 'info'),
};