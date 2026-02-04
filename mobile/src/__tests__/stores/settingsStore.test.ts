/**
 * Settings Store Tests
 */

import { act } from '@testing-library/react-native';
import { expect, describe, it, beforeEach } from '@jest/globals';

// Import the store
import { useSettingsStore } from '../../stores/settingsStore';

describe('useSettingsStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    const { setState } = useSettingsStore;
    setState({
      theme: 'system',
      defaultStyle: 'vivid',
      defaultQuality: 'standard',
      defaultSize: '1024x1024',
      autoEnhancePrompts: true,
      notificationsEnabled: true,
      hapticFeedbackEnabled: true,
    });
  });

  describe('initial state', () => {
    it('should have correct default values', () => {
      const state = useSettingsStore.getState();
      
      expect(state.theme).toBe('system');
      expect(state.defaultStyle).toBe('vivid');
      expect(state.defaultQuality).toBe('standard');
      expect(state.defaultSize).toBe('1024x1024');
      expect(state.autoEnhancePrompts).toBe(true);
      expect(state.notificationsEnabled).toBe(true);
      expect(state.hapticFeedbackEnabled).toBe(true);
    });
  });

  describe('setTheme', () => {
    it('should update theme to dark', () => {
      const { setState, getState } = useSettingsStore;
      
      act(() => {
        getState().setTheme('dark');
      });
      
      expect(getState().theme).toBe('dark');
    });

    it('should update theme to light', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setTheme('light');
      });
      
      expect(getState().theme).toBe('light');
    });
  });

  describe('setDefaultStyle', () => {
    it('should update default style', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setDefaultStyle('anime');
      });
      
      expect(getState().defaultStyle).toBe('anime');
    });
  });

  describe('setDefaultQuality', () => {
    it('should update default quality', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setDefaultQuality('hd');
      });
      
      expect(getState().defaultQuality).toBe('hd');
    });
  });

  describe('setDefaultSize', () => {
    it('should update default size', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setDefaultSize('1792x1024');
      });
      
      expect(getState().defaultSize).toBe('1792x1024');
    });
  });

  describe('toggles', () => {
    it('should toggle auto enhance prompts', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setAutoEnhancePrompts(false);
      });
      
      expect(getState().autoEnhancePrompts).toBe(false);
    });

    it('should toggle notifications', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setNotificationsEnabled(false);
      });
      
      expect(getState().notificationsEnabled).toBe(false);
    });

    it('should toggle haptic feedback', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setHapticFeedbackEnabled(false);
      });
      
      expect(getState().hapticFeedbackEnabled).toBe(false);
    });
  });

  describe('resetToDefaults', () => {
    it('should reset all settings to defaults', () => {
      const { getState } = useSettingsStore;
      
      // Change some settings
      act(() => {
        getState().setTheme('dark');
        getState().setDefaultStyle('anime');
        getState().setAutoEnhancePrompts(false);
      });
      
      // Verify changes
      expect(getState().theme).toBe('dark');
      expect(getState().defaultStyle).toBe('anime');
      
      // Reset
      act(() => {
        getState().resetToDefaults();
      });
      
      // Verify reset
      expect(getState().theme).toBe('system');
      expect(getState().defaultStyle).toBe('vivid');
      expect(getState().autoEnhancePrompts).toBe(true);
    });
  });

  describe('getIsDarkMode', () => {
    it('should return false when theme is light', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setTheme('light');
      });
      
      expect(getState().getIsDarkMode()).toBe(false);
    });

    it('should return true when theme is dark', () => {
      const { getState } = useSettingsStore;
      
      act(() => {
        getState().setTheme('dark');
      });
      
      expect(getState().getIsDarkMode()).toBe(true);
    });
  });
});