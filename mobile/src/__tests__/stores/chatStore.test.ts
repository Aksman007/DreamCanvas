/**
 * Chat Store Tests
 */

import { act, renderHook } from '@testing-library/react-native';
import { useChatStore } from '../../stores/chatStore';

// Reset store before each test
beforeEach(() => {
  useChatStore.setState({
    messages: [],
    isLoading: false,
    error: null,
    suggestedPrompt: null,
  });
});

describe('useChatStore', () => {
  describe('initial state', () => {
    it('should have empty messages', () => {
      const { result } = renderHook(() => useChatStore());
      
      expect(result.current.messages).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.suggestedPrompt).toBeNull();
    });
  });

  describe('clearChat', () => {
    it('should clear all messages', () => {
      useChatStore.setState({
        messages: [
          { role: 'user', content: 'Hello' },
          { role: 'assistant', content: 'Hi there!' },
        ],
        suggestedPrompt: 'A sunset',
      });
      
      const { result } = renderHook(() => useChatStore());
      
      act(() => {
        result.current.clearChat();
      });
      
      expect(result.current.messages).toEqual([]);
      expect(result.current.suggestedPrompt).toBeNull();
    });
  });

  describe('setSuggestedPrompt', () => {
    it('should set suggested prompt', () => {
      const { result } = renderHook(() => useChatStore());
      
      act(() => {
        result.current.setSuggestedPrompt('A beautiful mountain');
      });
      
      expect(result.current.suggestedPrompt).toBe('A beautiful mountain');
    });
  });

  describe('useSuggestedPrompt', () => {
    it('should return and clear suggested prompt', () => {
      useChatStore.setState({ suggestedPrompt: 'A sunset' });
      
      const { result } = renderHook(() => useChatStore());
      
      let prompt: string | null = null;
      act(() => {
        prompt = result.current.useSuggestedPrompt();
      });
      
      expect(prompt).toBe('A sunset');
      expect(result.current.suggestedPrompt).toBeNull();
    });
  });

  describe('clearError', () => {
    it('should clear error', () => {
      useChatStore.setState({ error: 'Some error' });
      
      const { result } = renderHook(() => useChatStore());
      
      act(() => {
        result.current.clearError();
      });
      
      expect(result.current.error).toBeNull();
    });
  });
});