/**
 * Button Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { Button } from '../../components/ui/Button';

describe('Button', () => {
  it('should render with title', () => {
    const { getByText } = render(<Button title="Click me" />);
    
    expect(getByText('Click me')).toBeTruthy();
  });

  it('should call onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(<Button title="Click me" onPress={onPress} />);
    
    fireEvent.press(getByText('Click me'));
    
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('should not call onPress when disabled', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <Button title="Click me" onPress={onPress} disabled />
    );
    
    fireEvent.press(getByText('Click me'));
    
    expect(onPress).not.toHaveBeenCalled();
  });

  it('should not call onPress when loading', () => {
    const onPress = jest.fn();
    const { getByTestId } = render(
      <Button title="Click me" onPress={onPress} isLoading testID="button" />
    );
    
    fireEvent.press(getByTestId('button'));
    
    expect(onPress).not.toHaveBeenCalled();
  });

  it('should render different variants', () => {
    const { rerender, getByText } = render(
      <Button title="Primary" variant="primary" />
    );
    expect(getByText('Primary')).toBeTruthy();

    rerender(<Button title="Secondary" variant="secondary" />);
    expect(getByText('Secondary')).toBeTruthy();

    rerender(<Button title="Outline" variant="outline" />);
    expect(getByText('Outline')).toBeTruthy();

    rerender(<Button title="Ghost" variant="ghost" />);
    expect(getByText('Ghost')).toBeTruthy();
  });

  it('should render different sizes', () => {
    const { rerender, getByText } = render(
      <Button title="Small" size="sm" />
    );
    expect(getByText('Small')).toBeTruthy();

    rerender(<Button title="Medium" size="md" />);
    expect(getByText('Medium')).toBeTruthy();

    rerender(<Button title="Large" size="lg" />);
    expect(getByText('Large')).toBeTruthy();
  });
});