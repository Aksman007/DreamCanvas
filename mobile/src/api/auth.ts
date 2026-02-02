/**
 * Auth API Functions
 */

import apiClient, { tokenStorage } from './client';
import { API_ENDPOINTS } from '../constants/api';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '../types';

export const authApi = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH_REGISTER,
      data
    );
    
    // Store tokens
    await tokenStorage.setTokens(
      response.data.tokens.access_token,
      response.data.tokens.refresh_token
    );
    
    return response.data;
  },
  
  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH_LOGIN,
      data
    );
    
    // Store tokens
    await tokenStorage.setTokens(
      response.data.tokens.access_token,
      response.data.tokens.refresh_token
    );
    
    return response.data;
  },
  
  /**
   * Refresh access token
   */
  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(
      API_ENDPOINTS.AUTH_REFRESH,
      { refresh_token: refreshToken }
    );
    
    // Store new tokens
    await tokenStorage.setTokens(
      response.data.access_token,
      response.data.refresh_token
    );
    
    return response.data;
  },
  
  /**
   * Get current user profile
   */
  async getMe(): Promise<User> {
    const response = await apiClient.get<User>(API_ENDPOINTS.AUTH_ME);
    return response.data;
  },
  
  /**
   * Update current user profile
   */
  async updateMe(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>(API_ENDPOINTS.AUTH_ME, data);
    return response.data;
  },
  
  /**
   * Logout - clear tokens
   */
  async logout(): Promise<void> {
    await tokenStorage.clearTokens();
  },
};