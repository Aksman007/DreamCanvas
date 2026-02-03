/**
 * API Configuration
 */

import { Platform } from 'react-native';
import { config, isDev } from './env';

// Base URL - use config or fallback
const getBaseUrl = () => {
  if (isDev) {
    // Android emulator uses 10.0.2.2 to reach host machine
    // iOS simulator can use localhost
    return Platform.OS === 'android'
      ? 'http://10.0.2.2:8000'
      : 'http://localhost:8000';
  }
  return config.apiUrl;
};

export const API_BASE_URL = getBaseUrl();

export const API_VERSION = 'v1';

export const API_ENDPOINTS = {
  // Auth
  AUTH_REGISTER: `/api/${API_VERSION}/auth/register`,
  AUTH_LOGIN: `/api/${API_VERSION}/auth/login`,
  AUTH_REFRESH: `/api/${API_VERSION}/auth/refresh`,
  AUTH_ME: `/api/${API_VERSION}/auth/me`,
  
  // Generation
  GENERATE: `/api/${API_VERSION}/generate`,
  GENERATION: (id: string) => `/api/${API_VERSION}/generate/${id}`,
  GENERATION_STATUS: (id: string) => `/api/${API_VERSION}/generate/${id}/status`,
  
  // Gallery
  GALLERY: `/api/${API_VERSION}/gallery`,
  
  // Chat
  CHAT: `/api/${API_VERSION}/chat`,
  CHAT_ENHANCE: `/api/${API_VERSION}/chat/enhance`,
  
  // WebSocket
  WS_GENERATIONS: `/api/${API_VERSION}/ws/generations`,
} as const;

// Request timeouts (ms)
export const TIMEOUTS = {
  DEFAULT: 30000,
  GENERATION: 120000,
  UPLOAD: 60000,
} as const;