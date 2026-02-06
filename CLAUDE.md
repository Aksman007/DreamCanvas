# CLAUDE.md

This file provides guidance for Claude Code when working with the DreamCanvas project.

## Project Overview

DreamCanvas is an AI-powered image generation app. Users can generate images via DALL-E 3, enhance prompts with Claude, and manage a gallery of their creations. The app uses a FastAPI backend with async Celery workers and a React Native (Expo) mobile frontend.

## Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/           # Route handlers (auth, generation, gallery, chat, websocket)
│   │   ├── services/         # Business logic (claude, image_gen, generation, storage, user)
│   │   ├── models/           # SQLAlchemy models (user, generation)
│   │   ├── schemas/          # Pydantic schemas (auth, generation, user, conversation)
│   │   ├── core/             # Security, middleware, exceptions, dependencies
│   │   ├── db/               # Database session, base, init
│   │   ├── tasks/            # Celery async tasks (generation_tasks)
│   │   ├── celery_app.py
│   │   ├── config.py         # Settings via environment variables
│   │   └── main.py
│   ├── alembic/              # Database migrations
│   ├── tests/
│   └── pyproject.toml
├── mobile/
│   ├── app/                  # Expo Router pages (file-based routing)
│   │   ├── (auth)/           # login, register
│   │   ├── (tabs)/           # chat, gallery/, generate/, profile/
│   │   └── _layout.tsx
│   ├── src/
│   │   ├── api/              # API client (auth, chat, generate, client)
│   │   ├── components/       # UI components by feature area
│   │   ├── stores/           # Zustand stores (auth, chat, generation, settings, toast)
│   │   ├── hooks/            # useGenerations, useNetworkStatus
│   │   ├── constants/        # api, config, env, theme
│   │   ├── types/
│   │   └── utils/
│   ├── maestro/              # E2E test flows
│   ├── app.json
│   ├── tailwind.config.js
│   └── jest.config.js
├── docker-compose.yml
└── .env.example
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.128.x
- **Python**: 3.12+ (mypy targets 3.12)
- **Package Manager**: Poetry
- **Database**: PostgreSQL 16 (async via asyncpg + SQLAlchemy 2.0)
- **Migrations**: Alembic
- **Task Queue**: Celery 5.6.x with Redis broker
- **Cache**: Redis 7
- **AI APIs**: OpenAI (DALL-E 3), Anthropic (Claude)
- **Storage**: Local filesystem, S3, or Cloudflare R2 (configurable)
- **Auth**: JWT (python-jose) + bcrypt
- **Linting**: Ruff (line-length 100), MyPy (strict)
- **Testing**: pytest (asyncio_mode: auto)

### Mobile
- **Framework**: Expo SDK 54 / React Native 0.81 (New Architecture enabled)
- **Routing**: expo-router 6.x (typed routes)
- **Language**: TypeScript 5.9.x (strict)
- **Styling**: NativeWind 4.2.x (TailwindCSS)
- **State Management**: Zustand 5.x
- **Data Fetching**: TanStack React Query 5.x
- **Forms**: React Hook Form 7.x + Zod 4.x
- **Secure Storage**: expo-secure-store, MMKV
- **Testing**: Jest 30.x + React Native Testing Library, MSW for API mocking
- **E2E Testing**: Maestro

## Common Commands

### Mobile (run from `mobile/`)
```bash
npm install          # Install dependencies
npx expo start       # Start development server
npm test             # Run tests
npm run typecheck    # TypeScript check
npm run lint         # ESLint
```

### Backend (run from `backend/`)
```bash
docker-compose up -d           # Start PostgreSQL + Redis
poetry install                 # Install Python dependencies
poetry run uvicorn app.main:app --reload  # Start dev server
poetry run pytest              # Run tests
poetry run ruff check .        # Lint
poetry run mypy .              # Type check
poetry run alembic upgrade head           # Run migrations
poetry run alembic revision --autogenerate -m "description"  # Create migration
```

## API Routes

- `POST /api/v1/auth/register`, `/login`, `/refresh` — Authentication
- `GET /api/v1/auth/me`, `PATCH /api/v1/auth/me` — User profile
- `POST /api/v1/generate/` — Create image generation (async via Celery)
- `GET /api/v1/generate/{id}`, `GET /api/v1/generate/{id}/status` — Generation details/status
- `DELETE /api/v1/generate/{id}` — Delete generation
- `GET /api/v1/gallery/` — List user's generated images
- `POST /api/v1/chat/` — Chat conversation with Claude
- `POST /api/v1/chat/enhance` — Enhance prompts via Claude
- `WS /api/v1/ws/generations` — Real-time generation status updates

## Key Patterns

### Mobile
- Components use NativeWind `className` for styling
- API calls go through `src/api/` with React Query hooks
- Global state managed by Zustand stores in `src/stores/`
- Use `expo-file-system/legacy` for file operations (v19 has new API)
- File-based routing with route groups: `(auth)` for login/register, `(tabs)` for main app
- Bundle ID: `com.dreamcanvas.app`, deep link scheme: `dreamcanvas://`

### Backend
- Routes defined in `app/api/v1/` with versioned prefix
- Services layer in `app/services/` contains business logic
- Config loaded from environment via `app/config.py` (Pydantic Settings)
- Image generation is async: request → Celery task → WebSocket status update
- DALL-E 3 is the primary image provider; Claude enhances prompts
- Rate limiting: 10 generations per hour (configurable)
- Max prompt length: 4000 characters

## Environment Variables

Key variables (see `.env.example` for full list):
- `DATABASE_URL` — Async PostgreSQL connection string
- `REDIS_URL` — Redis connection for cache and Celery
- `SECRET_KEY` — JWT signing key
- `ANTHROPIC_API_KEY` — Claude API access
- `OPENAI_API_KEY` — DALL-E 3 API access
- `STABILITY_API_KEY` — Optional Stability AI access
- `STORAGE_PROVIDER` — `local`, `s3`, or `r2`
- `CORS_ORIGINS` — Allowed CORS origins

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`):
- **Unit tests**: Node 18, npm install, typecheck, Jest, codecov upload
- **E2E tests**: macOS runner, Maestro CLI, iOS simulator
- Triggered on push to `main`/`develop` and PRs to `main`

## Testing Notes

- Mobile tests use jest-expo preset with mocks for native modules
- MSW (Mock Service Worker) handles API mocking in mobile tests
- Backend tests use pytest with async fixtures (`asyncio_mode: auto`)
- E2E tests in `mobile/maestro/` use Maestro flows against iOS simulator
