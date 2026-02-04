# CLAUDE.md

This file provides guidance for Claude Code when working with the DreamCanvas project.

## Project Overview

DreamCanvas is an AI-powered image generation app with a FastAPI backend and React Native (Expo) mobile app.

## Repository Structure

```
├── backend/          # FastAPI Python backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   ├── tests/        # pytest tests
│   └── pyproject.toml
├── mobile/           # Expo React Native app
│   ├── app/          # expo-router pages
│   ├── src/          # Source code
│   │   ├── api/      # API client
│   │   ├── components/
│   │   ├── constants/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/   # Zustand stores
│   │   ├── types/
│   │   └── utils/
│   └── src/__tests__/ # Jest tests
└── docker-compose.yml
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Python**: 3.11+
- **Package Manager**: Poetry
- **Database Migrations**: Alembic
- **Testing**: pytest

### Mobile
- **Framework**: Expo SDK 54 / React Native 0.81
- **Routing**: expo-router
- **Language**: TypeScript
- **Styling**: NativeWind (TailwindCSS)
- **State Management**: Zustand
- **Data Fetching**: TanStack React Query
- **Forms**: React Hook Form + Zod
- **Testing**: Jest + React Native Testing Library

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
docker-compose up -d # Start backend services
poetry install       # Install Python dependencies
pytest               # Run tests
```

## Key Patterns

### Mobile
- Components use NativeWind className for styling
- API calls go through `src/api/` with React Query hooks
- Global state managed by Zustand stores in `src/stores/`
- Use `expo-file-system/legacy` for file operations (v19 has new API)

### Backend
- FastAPI routes in `app/`
- Alembic migrations in `alembic/versions/`
- Environment config via `.env` file

## Testing Notes

- Mobile tests require jest-expo setup with mocks for native modules
- Backend tests use pytest with fixtures
