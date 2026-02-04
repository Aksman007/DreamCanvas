/**
 * EmptyState Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { EmptyState } from '../../components/empty/EmptyState';

describe('EmptyState', () => {
  it('should render gallery preset', () => {
    const { getByText } = render(<EmptyState type="gallery" />);
    
    expect(getByText('No Creations Yet')).toBeTruthy();
    expect(getByText('Your AI-generated images will appear here')).toBeTruthy();
  });

  it('should render chat preset', () => {
    const { getByText } = render(<EmptyState type="chat" />);
    
    expect(getByText('Start a Conversation')).toBeTruthy();
  });

  it('should render custom title and message', () => {
    const { getByText } = render(
      <EmptyState
        title="Custom Title"
        message="Custom message here"
      />
    );
    
    expect(getByText('Custom Title')).toBeTruthy();
    expect(getByText('Custom message here')).toBeTruthy();
  });

  it('should render action button when provided', () => {
    const onAction = jest.fn();
    const { getByText } = render(
      <EmptyState
        type="gallery"
        actionLabel="Create Now"
        onAction={onAction}
      />
    );
    
    const button = getByText('Create Now');
    expect(button).toBeTruthy();
    
    fireEvent.press(button);
    expect(onAction).toHaveBeenCalled();
  });

  it('should not render action button when not provided', () => {
    const { queryByText } = render(<EmptyState type="gallery" />);
    
    expect(queryByText('Create Now')).toBeNull();
  });
});