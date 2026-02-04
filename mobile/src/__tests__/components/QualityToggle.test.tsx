/**
 * QualityToggle Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { QualityToggle } from '../../components/generate/QualityToggle';

describe('QualityToggle', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render both quality options', () => {
    const { getByText } = render(
      <QualityToggle value="standard" onChange={mockOnChange} />
    );
    
    expect(getByText('Standard')).toBeTruthy();
    expect(getByText('HD')).toBeTruthy();
  });

  it('should call onChange when HD selected', () => {
    const { getByText } = render(
      <QualityToggle value="standard" onChange={mockOnChange} />
    );
    
    fireEvent.press(getByText('HD'));
    
    expect(mockOnChange).toHaveBeenCalledWith('hd');
  });

  it('should call onChange when Standard selected', () => {
    const { getByText } = render(
      <QualityToggle value="hd" onChange={mockOnChange} />
    );
    
    fireEvent.press(getByText('Standard'));
    
    expect(mockOnChange).toHaveBeenCalledWith('standard');
  });
});