/**
 * Error Boundary Component
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react-native';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error to console in development
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
    
    // Call optional error handler
    this.props.onError?.(error, errorInfo);
    
    // In production, you would send this to an error tracking service
    // e.g., Sentry, Bugsnag, etc.
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <View className="flex-1 bg-white dark:bg-gray-900 items-center justify-center p-6">
          <View className="w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/30 items-center justify-center mb-6">
            <AlertTriangle size={40} color="#ef4444" />
          </View>

          <Text className="text-2xl font-bold text-gray-900 dark:text-white mb-2 text-center">
            Something went wrong
          </Text>
          
          <Text className="text-gray-500 dark:text-gray-400 text-center mb-6">
            We're sorry, but something unexpected happened. Please try again.
          </Text>

          {__DEV__ && this.state.error && (
            <ScrollView 
              className="max-h-32 w-full mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-3"
              showsVerticalScrollIndicator={false}
            >
              <Text className="text-xs text-red-600 dark:text-red-400 font-mono">
                {this.state.error.toString()}
              </Text>
            </ScrollView>
          )}

          <View className="flex-row space-x-3">
            <TouchableOpacity
              onPress={this.handleRetry}
              className="flex-row items-center bg-primary-600 px-6 py-3 rounded-xl"
              activeOpacity={0.8}
            >
              <RefreshCw size={18} color="#ffffff" />
              <Text className="text-white font-semibold ml-2">Try Again</Text>
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}