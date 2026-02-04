/**
 * Alert Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { Alert } from '../../components/ui/Alert';

describe('Alert', () => {
  it('should render message', () => {
    const { getByText } = render(<Alert message="Test message" />);
    
    expect(getByText('Test message')).toBeTruthy();
  });

  it('should render title when provided', () => {
    const { getByText } = render(
      <Alert title="Test Title" message="Test message" />
    );
    
    expect(getByText('Test Title')).toBeTruthy();
    expect(getByText('Test message')).toBeTruthy();
  });

  it('should render different types', () => {
    const { rerender, getByText } = render(
      <Alert type="success" message="Success!" />
    );
    expect(getByText('Success!')).toBeTruthy();

    rerender(<Alert type="error" message="Error!" />);
    expect(getByText('Error!')).toBeTruthy();

    rerender(<Alert type="warning" message="Warning!" />);
    expect(getByText('Warning!')).toBeTruthy();

    rerender(<Alert type="info" message="Info!" />);
    expect(getByText('Info!')).toBeTruthy();
  });

  it('should call onDismiss when dismiss button pressed', () => {
    const onDismiss = jest.fn();
    const { getByTestId } = render(
      <Alert message="Test" onDismiss={onDismiss} testID="alert" />
    );
    
    // Find the dismiss button (X icon)
    const dismissButton = getByTestId('alert').findByProps({ onPress: onDismiss });
    if (dismissButton) {
      fireEvent.press(dismissButton);
      expect(onDismiss).toHaveBeenCalled();
    }
  });
});