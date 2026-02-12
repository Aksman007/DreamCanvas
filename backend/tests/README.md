# DreamCanvas Backend Tests

This directory contains comprehensive tests for the DreamCanvas backend API.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_core/              # Core functionality tests
│   ├── test_security.py    # JWT tokens, password hashing
│   ├── test_dependencies.py # Auth injection, pagination
│   ├── test_exceptions.py  # Custom exception classes
│   └── test_middleware.py  # Logging, rate limiting, security headers
├── test_api/               # API endpoint tests (TODO)
├── test_services/          # Service layer tests (TODO)
├── test_models/            # Database model tests (TODO)
└── test_tasks/             # Background task tests (TODO)
```

## Running Tests

### Run all tests
```bash
poetry run pytest
```

### Run specific test file
```bash
poetry run pytest tests/test_core/test_security.py
```

### Run specific test
```bash
poetry run pytest tests/test_core/test_security.py::TestPasswordHashing::test_hash_password
```

### Run tests by marker
```bash
# Run only unit tests
poetry run pytest -m unit

# Run only core tests
poetry run pytest -m core

# Skip slow tests
poetry run pytest -m "not slow"
```

### Run with coverage
```bash
poetry run pytest --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

## Test Categories

### ✅ **Core Tests** (Completed)
- **test_security.py**: 40+ tests for password hashing and JWT tokens
- **test_dependencies.py**: 20+ tests for dependency injection and auth
- **test_exceptions.py**: 50+ tests for custom exception classes
- **test_middleware.py**: 25+ tests for middleware (logging, rate limiting, security)

### 🔲 **API Tests** (TODO)
- Authentication endpoints (register, login, refresh, profile)
- Generation endpoints (create, get, status, delete)
- Gallery endpoints (list, filter, pagination)
- Chat endpoints (chat, enhance prompt)
- WebSocket endpoints (connections, subscriptions)

### 🔲 **Service Tests** (TODO)
- User service (CRUD, authentication)
- Generation service (workflow, rate limiting)
- Claude service (prompt enhancement, chat)
- Image generation service (DALL-E, Stability AI)
- Storage service (local, S3, R2)

### 🔲 **Model Tests** (TODO)
- User model methods
- Generation model state transitions

### 🔲 **Background Task Tests** (TODO)
- Generation processing tasks
- Cleanup/maintenance tasks

## Test Fixtures

### Database Fixtures
- `db_session`: Async database session with automatic rollback
- `sync_db_session`: Sync database session for sync tests
- `test_user`: Pre-created test user
- `test_user_2`: Second test user for multi-user tests
- `inactive_user`: Inactive test user

### Authentication Fixtures
- `auth_token`: Valid JWT access token for test user
- `refresh_token`: Valid JWT refresh token
- `auth_headers`: Authorization headers with Bearer token

### Mock Fixtures
- `mock_redis`: Mock Redis client
- `mock_celery`: Mock Celery task execution
- `mock_claude_api`: Mock Anthropic Claude API
- `mock_dalle_api`: Mock OpenAI DALL-E API
- `mock_stability_api`: Mock Stability AI API
- `mock_storage`: Mock storage service

### Data Fixtures
- `user_data`: Random user registration data
- `generation_data`: Random image generation request data
- `faker`: Faker instance for generating test data

## Writing New Tests

### Test File Template

```python
"""
Tests for [module name] - [description].
"""

import pytest
from app.[module] import [components]


class Test[Component]:
    """Test [component] functionality."""

    @pytest.mark.asyncio
    async def test_[feature]_success(self, db_session, test_user):
        """Test that [feature] works successfully."""
        # Arrange
        ...

        # Act
        result = await some_function()

        # Assert
        assert result is not None
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_[feature]_failure(self):
        """Test that [feature] fails appropriately."""
        with pytest.raises(SomeException) as exc_info:
            await some_function_that_fails()

        assert exc_info.value.status_code == 400
```

### Best Practices

1. **Use descriptive test names**: `test_create_user_with_valid_data_succeeds`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per test**: Focus on testing one thing
4. **Use fixtures**: Leverage shared fixtures from conftest.py
5. **Mock external services**: Don't make real API calls
6. **Test edge cases**: Empty strings, None values, invalid UUIDs
7. **Test error paths**: Ensure errors are handled correctly
8. **Use markers**: Tag tests with appropriate markers

## Coverage Goals

- **Overall**: 85%+
- **Core modules**: 95%+
- **Services**: 90%+
- **API endpoints**: 90%+

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request to `main`

CI will fail if:
- Any test fails
- Coverage drops below 85%
- Type checking fails
- Linting fails

## Troubleshooting

### Tests fail with "database locked"
SQLite has concurrency limitations. Ensure you're using async sessions correctly.

### Tests fail with "event loop closed"
Make sure you're using `@pytest.mark.asyncio` for async tests.

### Import errors
Ensure you're running tests from the `backend/` directory:
```bash
cd backend
poetry run pytest
```

### Fixture not found
Check that fixtures are defined in `conftest.py` or imported correctly.

## Need Help?

- Check the test plan: `../TEST_PLAN.md`
- Review existing tests for examples
- Check pytest documentation: https://docs.pytest.org/
