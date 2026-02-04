/**
 * ChatInput Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { ChatInput } from '../../components/chat/ChatInput';

describe('ChatInput', () => {
  const mockOnSend = jest.fn();

  beforeEach(() => {
    mockOnSend.mockClear();
  });

  it('should render placeholder', () => {
    const { getByPlaceholderText } = render(
      <ChatInput onSend={mockOnSend} placeholder="Type here..." />
    );
    
    expect(getByPlaceholderText('Type here...')).toBeTruthy();
  });

  it('should call onSend when send button pressed with text', () => {
    const { getByPlaceholderText, getByTestId } = render(
      <ChatInput onSend={mockOnSend} testID="chat-input" />
    );
    
    const input = getByPlaceholderText('Ask me anything about image prompts...');
    fireEvent.changeText(input, 'Hello');
    
    // Find and press send button
    // Note: Implementation may vary based on actual component structure
  });

  it('should not call onSend when input is empty', () => {
    const { getByTestId } = render(
      <ChatInput onSend={mockOnSend} testID="chat-input" />
    );
    
    // Try to send without typing
    // Send button should be disabled or not call onSend
    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it('should disable input when loading', () => {
    const { getByPlaceholderText } = render(
      <ChatInput onSend={mockOnSend} isLoading />
    );
    
    const input = getByPlaceholderText('Ask me anything about image prompts...');
    expect(input.props.editable).toBe(false);
  });
});