/**
 * FormInput Component Tests
 */

import React from 'react';
import { render, fireEvent } from '../utils/test-utils';
import { useForm } from 'react-hook-form';
import { FormInput } from '../../components/ui/FormInput';

// Wrapper component to provide form context
const FormInputWrapper = ({
  name,
  error,
  ...props
}: {
  name: string;
  error?: { message: string };
  [key: string]: any;
}) => {
  const { control } = useForm({
    defaultValues: { [name]: '' },
  });

  return <FormInput name={name} control={control} error={error} {...props} />;
};

describe('FormInput', () => {
  it('should render with label', () => {
    const { getByText } = render(
      <FormInputWrapper name="email" label="Email" />
    );
    
    expect(getByText('Email')).toBeTruthy();
  });

  it('should render placeholder', () => {
    const { getByPlaceholderText } = render(
      <FormInputWrapper name="email" placeholder="Enter email" />
    );
    
    expect(getByPlaceholderText('Enter email')).toBeTruthy();
  });

  it('should display error message', () => {
    const { getByText } = render(
      <FormInputWrapper
        name="email"
        error={{ message: 'Email is required' }}
      />
    );
    
    expect(getByText('Email is required')).toBeTruthy();
  });

  it('should display hint when no error', () => {
    const { getByText } = render(
      <FormInputWrapper name="password" hint="At least 8 characters" />
    );
    
    expect(getByText('At least 8 characters')).toBeTruthy();
  });

  it('should hide hint when error present', () => {
    const { queryByText, getByText } = render(
      <FormInputWrapper
        name="password"
        hint="At least 8 characters"
        error={{ message: 'Password too short' }}
      />
    );
    
    expect(getByText('Password too short')).toBeTruthy();
    expect(queryByText('At least 8 characters')).toBeNull();
  });
});