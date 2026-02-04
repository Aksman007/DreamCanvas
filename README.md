# DreamCanvas

DreamCanvas is a personal project that provides an AI-assisted image creation and sharing experience. It includes a FastAPI backend for generation orchestration and a React Native (Expo) mobile app for creating, viewing, and managing generated images.

## Repository structure

- `backend/` — FastAPI backend, database migrations, Celery tasks and services.
- `mobile/` — Expo React Native mobile application, tests, and UI components.
- `maestro/` — flow definitions used by the app for guided UX flows and state machines.

## Quick start

Prerequisites:
- Node.js (recommended via nvm)
- Python 3.11+
- Docker & docker-compose (for backend local dev)

Backend (development):

```bash
# from repo root
cd backend
cp .env.example .env
# start services with Docker Compose
docker-compose up -d
# (optional) run migrations or start the app locally
```

Mobile (development):

```bash
cd mobile
npm install
npx expo start
```

## Testing

Mobile tests use Jest + React Native Testing Library. Run from `mobile/`:

```bash
cd mobile
npm test
```

Backend tests (if present) use pytest. Example:

```bash
cd backend
pytest
```

## Notes for contributors

- The mobile app uses Expo and jest-expo for testing. The repo contains jest configuration and setup mocks for common native and Expo modules to run tests in Node environment.
- The backend is a FastAPI app with Alembic migrations under `backend/alembic/versions`.
- Use the provided Docker Compose setup to run backend services locally during development.

If you need help getting started or running tests, open an issue or contact the repository owner.

---
Generated on project workspace by contributor tooling.
