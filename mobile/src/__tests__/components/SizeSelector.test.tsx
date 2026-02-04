/**
 * SizeSelector Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { SizeSelector } from '../../components/generate/SizeSelector';

describe('SizeSelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render all size options', () => {
    const { getByText } = render(
      <SizeSelector value="1024x1024" onChange={mockOnChange} />
    );
    
    expect(getByText('Square')).toBeTruthy();
    expect(getByText('Landscape')).toBeTruthy();
    expect(getByText('Portrait')).toBeTruthy();
  });

  it('should display aspect ratios', () => {
    const { getByText } = render(
      <SizeSelector value="1024x1024" onChange={mockOnChange} />
    );
    
    expect(getByText('1:1')).toBeTruthy();
    expect(getByText('16:9')).toBeTruthy();
    expect(getByText('9:16')).toBeTruthy();
  });

  it('should call onChange when size selected', () => {
    const { getByText } = render(
      <SizeSelector value="1024x1024" onChange={mockOnChange} />
    );
    
    fireEvent.press(getByText('Landscape'));
    
    expect(mockOnChange).toHaveBeenCalledWith('1792x1024');
  });
});