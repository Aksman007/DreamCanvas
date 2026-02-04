/**
 * MSW Request Handlers
 */

import { http, HttpResponse } from 'msw';
import { createMockUser, createMockGeneration } from '../utils/test-utils';

const API_URL = 'http://localhost:8000';

export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/api/v1/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string };
    
    if (body.email === 'test@example.com' && body.password === 'password123') {
      return HttpResponse.json({
        user: createMockUser(),
        tokens: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          token_type: 'bearer',
          expires_in: 3600,
        },
      });
    }
    
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post(`${API_URL}/api/v1/auth/register`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string };
    
    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { detail: 'Email already registered' },
        { status: 400 }
      );
    }
    
    return HttpResponse.json({
      user: createMockUser({ email: body.email }),
      tokens: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 3600,
      },
    });
  }),

  http.get(`${API_URL}/api/v1/auth/me`, () => {
    return HttpResponse.json(createMockUser());
  }),

  http.patch(`${API_URL}/api/v1/auth/me`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;
    return HttpResponse.json(createMockUser(body));
  }),

  // Generation endpoints
  http.post(`${API_URL}/api/v1/generate`, async ({ request }) => {
    const body = await request.json() as { prompt: string };
    return HttpResponse.json(
      createMockGeneration({
        original_prompt: body.prompt,
        status: 'pending',
      })
    );
  }),

  http.get(`${API_URL}/api/v1/generate/:id`, ({ params }) => {
    return HttpResponse.json(
      createMockGeneration({ id: params.id as string })
    );
  }),

  http.get(`${API_URL}/api/v1/generate/:id/status`, ({ params }) => {
    return HttpResponse.json({
      generation_id: params.id,
      status: 'completed',
      image_url: 'https://example.com/image.png',
      thumbnail_url: 'https://example.com/thumb.png',
    });
  }),

  http.delete(`${API_URL}/api/v1/generate/:id`, () => {
    return HttpResponse.json({ success: true });
  }),

  // Gallery endpoint
  http.get(`${API_URL}/api/v1/gallery`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const pageSize = parseInt(url.searchParams.get('page_size') || '20');
    
    const items = Array.from({ length: pageSize }, (_, i) =>
      createMockGeneration({ id: `gen-${(page - 1) * pageSize + i}` })
    );
    
    return HttpResponse.json({
      items,
      total: 50,
      page,
      page_size: pageSize,
      pages: Math.ceil(50 / pageSize),
    });
  }),

  // Chat endpoints
  http.post(`${API_URL}/api/v1/chat`, async ({ request }) => {
    const body = await request.json() as { message: string };
    return HttpResponse.json({
      message: `I can help you with: ${body.message}`,
      suggested_prompt: 'A beautiful landscape with mountains',
    });
  }),

  http.post(`${API_URL}/api/v1/chat/enhance`, ({ request }) => {
    const url = new URL(request.url);
    const prompt = url.searchParams.get('prompt') || '';
    
    return HttpResponse.json({
      original_prompt: prompt,
      enhanced_prompt: `Enhanced: ${prompt} with vivid colors and dramatic lighting`,
      style_suggestions: ['vivid', 'dramatic', 'colorful'],
    });
  }),
];