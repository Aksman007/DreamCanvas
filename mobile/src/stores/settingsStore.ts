/**
 * Settings Store - Zustand store for app settings with persistence
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance } from 'react-native';

export type ThemeMode = 'light' | 'dark' | 'system';
export type DefaultQuality = 'standard' | 'hd';

interface SettingsState {
  // Appearance
  theme: ThemeMode;
  
  // Generation defaults
  defaultStyle: string;
  defaultQuality: DefaultQuality;
  defaultSize: string;
  autoEnhancePrompts: boolean;
  
  // Notifications
  notificationsEnabled: boolean;
  
  // System
  hapticFeedbackEnabled: boolean;
  
  // Computed
  isDarkMode: boolean;
  
  // Actions
  setTheme: (theme: ThemeMode) => void;
  setDefaultStyle: (style: string) => void;
  setDefaultQuality: (quality: DefaultQuality) => void;
  setDefaultSize: (size: string) => void;
  setAutoEnhancePrompts: (enabled: boolean) => void;
  setNotificationsEnabled: (enabled: boolean) => void;
  setHapticFeedbackEnabled: (enabled: boolean) => void;
  resetToDefaults: () => void;
}

const DEFAULT_SETTINGS = {
  theme: 'system' as ThemeMode,
  defaultStyle: 'vivid',
  defaultQuality: 'standard' as DefaultQuality,
  defaultSize: '1024x1024',
  autoEnhancePrompts: true,
  notificationsEnabled: true,
  hapticFeedbackEnabled: true,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      // Initial state
      ...DEFAULT_SETTINGS,
      
      // Computed
      get isDarkMode() {
        const { theme } = get();
        if (theme === 'system') {
          return Appearance.getColorScheme() === 'dark';
        }
        return theme === 'dark';
      },
      
      // Actions
      setTheme: (theme) => set({ theme }),
      setDefaultStyle: (defaultStyle) => set({ defaultStyle }),
      setDefaultQuality: (defaultQuality) => set({ defaultQuality }),
      setDefaultSize: (defaultSize) => set({ defaultSize }),
      setAutoEnhancePrompts: (autoEnhancePrompts) => set({ autoEnhancePrompts }),
      setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
      setHapticFeedbackEnabled: (hapticFeedbackEnabled) => set({ hapticFeedbackEnabled }),
      resetToDefaults: () => set(DEFAULT_SETTINGS),
    }),
    {
      name: 'dreamcanvas-settings',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Selector hooks
export const useTheme = () => useSettingsStore((state) => state.theme);
export const useIsDarkMode = () => useSettingsStore((state) => state.isDarkMode);
export const useDefaultStyle = () => useSettingsStore((state) => state.defaultStyle);
export const useDefaultQuality = () => useSettingsStore((state) => state.defaultQuality);
export const useAutoEnhance = () => useSettingsStore((state) => state.autoEnhancePrompts);
export const useHapticFeedback = () => useSettingsStore((state) => state.hapticFeedbackEnabled);