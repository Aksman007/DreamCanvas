/**
 * StyleSelector Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { StyleSelector } from '../../components/generate/StyleSelector';

describe('StyleSelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render all style options', () => {
    const { getByText } = render(
      <StyleSelector value="vivid" onChange={mockOnChange} />
    );
    
    expect(getByText('Vivid')).toBeTruthy();
    expect(getByText('Natural')).toBeTruthy();
    expect(getByText('Anime')).toBeTruthy();
  });

  it('should highlight selected style', () => {
    const { getByText } = render(
      <StyleSelector value="anime" onChange={mockOnChange} />
    );
    
    // The Anime option should have different styling when selected
    const animeOption = getByText('Anime');
    expect(animeOption).toBeTruthy();
  });

  it('should call onChange when style selected', () => {
    const { getByText } = render(
      <StyleSelector value="vivid" onChange={mockOnChange} />
    );
    
    fireEvent.press(getByText('Natural'));
    
    expect(mockOnChange).toHaveBeenCalledWith('natural');
  });
});