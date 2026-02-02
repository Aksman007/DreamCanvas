/**
 * DreamCanvas Mobile App - Type Definitions
 */

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  preferences: UserPreferences;
  generation_count: number;
  last_generation_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system';
  default_style?: string;
  default_quality?: 'standard' | 'hd';
  notifications_enabled?: boolean;
}

// ============================================================================
// Auth Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

// ============================================================================
// Generation Types
// ============================================================================

export type GenerationStatus =
  | 'pending'
  | 'processing'
  | 'enhancing'
  | 'generating'
  | 'uploading'
  | 'completed'
  | 'failed';

export type ImageProvider = 'dalle' | 'stability';

export interface GenerationRequest {
  prompt: string;
  enhance_prompt?: boolean;
  negative_prompt?: string;
  style?: string;
  size?: '1024x1024' | '1792x1024' | '1024x1792';
  quality?: 'standard' | 'hd';
  provider?: ImageProvider;
}

export interface Generation {
  id: string;
  user_id: string;
  original_prompt: string;
  enhanced_prompt: string | null;
  negative_prompt: string | null;
  status: GenerationStatus;
  provider: ImageProvider;
  model: string;
  style: string | null;
  size: string;
  quality: string;
  image_url: string | null;
  thumbnail_url: string | null;
  error_message: string | null;
  error_code: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  duration_seconds: number | null;
}

export interface GenerationListResponse {
  items: Generation[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ============================================================================
// Chat Types
// ============================================================================

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  suggested_prompt: string | null;
}

export interface PromptEnhanceResponse {
  original_prompt: string;
  enhanced_prompt: string;
  style_suggestions: string[] | null;
}

// ============================================================================
// API Types
// ============================================================================

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
}

export interface SuccessResponse {
  success: boolean;
  message: string;
}

// ============================================================================
// App Types
// ============================================================================

export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  hapticFeedback: boolean;
  autoEnhancePrompts: boolean;
  defaultStyle: string;
  defaultQuality: 'standard' | 'hd';
}