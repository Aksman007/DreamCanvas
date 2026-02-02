/**
 * App Configuration
 */

export const APP_CONFIG = {
  name: 'DreamCanvas',
  version: '1.0.0',
  
  // Generation settings
  maxPromptLength: 4000,
  defaultStyle: 'vivid',
  defaultQuality: 'standard' as const,
  defaultSize: '1024x1024' as const,
  
  // Polling intervals (ms)
  generationPollInterval: 2000,
  
  // Cache settings
  imageCacheDuration: 7 * 24 * 60 * 60 * 1000, // 7 days
  
  // Pagination
  defaultPageSize: 20,
  
  // WebSocket
  wsReconnectInterval: 5000,
  wsHeartbeatInterval: 30000,
} as const;

export const STYLE_PRESETS = [
  { id: 'vivid', label: 'Vivid', description: 'Bold and vibrant colors' },
  { id: 'natural', label: 'Natural', description: 'Realistic and subtle' },
  { id: 'anime', label: 'Anime', description: 'Japanese animation style' },
  { id: 'photorealistic', label: 'Photo', description: 'Photorealistic rendering' },
  { id: 'artistic', label: 'Artistic', description: 'Painterly and expressive' },
  { id: 'fantasy', label: 'Fantasy', description: 'Magical and otherworldly' },
] as const;

export const SIZE_OPTIONS = [
  { id: '1024x1024', label: 'Square', aspect: '1:1' },
  { id: '1792x1024', label: 'Landscape', aspect: '16:9' },
  { id: '1024x1792', label: 'Portrait', aspect: '9:16' },
] as const;

export const QUALITY_OPTIONS = [
  { id: 'standard', label: 'Standard', description: 'Faster generation' },
  { id: 'hd', label: 'HD', description: 'Higher quality, slower' },
] as const;