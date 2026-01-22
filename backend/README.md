# DreamCanvas API

AI-Powered Visual Storytelling Backend

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Database**: PostgreSQL (async with asyncpg)
- **Cache**: Redis
- **Task Queue**: Celery
- **AI**: Claude (Anthropic), DALL-E (OpenAI)

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### Installation
```bash
# Clone repository
cd backend

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start services (PostgreSQL, Redis)
docker-compose up -d postgres redis

# Run development server
poetry run uvicorn app.main:app --reload
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure
```bash
backend/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Settings & configuration
│   ├── api/v1/          # API routes
│   ├── core/            # Security, exceptions, middleware
│   ├── db/              # Database configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── tasks/           # Celery tasks
├── alembic/             # Database migrations
├── tests/               # Test suite
└── pyproject.toml       # Dependencies
```
## Development
```bash
# Run server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run ruff format .

# Type check
poetry run mypy app
```

## License

MIT