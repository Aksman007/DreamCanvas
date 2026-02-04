/**
 * MessageBubble Component Tests
 */

import React from 'react';
import { render } from '../utils/test-utils';
import { MessageBubble } from '../../components/chat/MessageBubble';

describe('MessageBubble', () => {
  it('should render user message', () => {
    const { getByText } = render(
      <MessageBubble message={{ role: 'user', content: 'Hello!' }} />
    );
    
    expect(getByText('Hello!')).toBeTruthy();
  });

  it('should render assistant message', () => {
    const { getByText } = render(
      <MessageBubble message={{ role: 'assistant', content: 'Hi there!' }} />
    );
    
    expect(getByText('Hi there!')).toBeTruthy();
  });

  it('should render long messages', () => {
    const longMessage = 'This is a very long message '.repeat(10);
    const { getByText } = render(
      <MessageBubble message={{ role: 'user', content: longMessage }} />
    );
    
    expect(getByText(longMessage)).toBeTruthy();
  });
});