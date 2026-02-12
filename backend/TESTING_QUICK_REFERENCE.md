# Testing Quick Reference

Quick commands and patterns for DreamCanvas backend testing.

## 🚀 Quick Commands

```bash
# Run all core tests
./run_tests.sh

# Run with coverage
./run_tests.sh --coverage

# Run specific file
./run_tests.sh tests/test_core/test_security.py

# Run verbose
./run_tests.sh --verbose

# Run fast (skip slow tests)
./run_tests.sh --fast

# Using poetry directly
poetry run pytest tests/test_core/ -v
poetry run pytest tests/test_core/test_security.py::TestPasswordHashing -v
```

## 📋 Common Fixtures

```python
# Database
db_session          # Async database session
sync_db_session     # Sync database session

# Users
test_user           # Active test user
test_user_2         # Second test user
inactive_user       # Inactive user

# Authentication
auth_token          # Valid JWT access token
refresh_token       # Valid JWT refresh token
auth_headers        # Authorization headers

# Mocks
mock_redis          # Mock Redis client
mock_celery         # Mock Celery tasks
mock_claude_api     # Mock Claude API
mock_dalle_api      # Mock DALL-E API
mock_storage        # Mock storage service

# Data
faker               # Faker instance
user_data           # Random user data
generation_data     # Random generation data
```

## 🧪 Test Template

```python
"""Tests for [module] - [description]."""

import pytest
from app.[module] import [component]


class Test[Component]:
    """Test [component] functionality."""

    @pytest.mark.asyncio
    async def test_[feature]_success(self, db_session, test_user):
        """Test that [feature] works successfully."""
        # Arrange
        data = {"field": "value"}

        # Act
        result = await some_function(data)

        # Assert
        assert result is not None
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_[feature]_failure(self):
        """Test that [feature] fails appropriately."""
        with pytest.raises(SomeException) as exc_info:
            await some_function_that_fails()

        assert exc_info.value.status_code == 400
        assert "error message" in exc_info.value.detail
```

## 🎯 Test Patterns

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_function(self, db_session):
    result = await async_function()
    assert result is not None
```

### Testing Exceptions
```python
def test_raises_exception(self):
    with pytest.raises(ValueError) as exc_info:
        function_that_raises()

    assert exc_info.value.message == "Expected error"
```

### Testing with Mocks
```python
@pytest.mark.asyncio
async def test_with_mock(self, mock_claude_api):
    # Mock is automatically injected
    result = await function_that_uses_claude()

    assert result is not None
    mock_claude_api.messages.create.assert_called_once()
```

### Testing HTTP Status Codes
```python
def test_endpoint_returns_200(self, client, auth_headers):
    response = client.get("/api/v1/test", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "success"
```

### Testing Database Operations
```python
@pytest.mark.asyncio
async def test_database_operation(self, db_session):
    # Create
    obj = Model(field="value")
    db_session.add(obj)
    await db_session.commit()
    await db_session.refresh(obj)

    # Read
    result = await db_session.execute(select(Model))
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.field == "value"
```

## 📊 Coverage Commands

```bash
# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Coverage for specific module
poetry run pytest --cov=app.core --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

## 🏷️ Test Markers

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow test (skip with -m "not slow")
@pytest.mark.api           # API test
@pytest.mark.service       # Service test
@pytest.mark.core          # Core test
```

Run tests by marker:
```bash
poetry run pytest -m unit
poetry run pytest -m "not slow"
poetry run pytest -m api
```

## 🐛 Debugging

```bash
# Show print statements
poetry run pytest -s

# Drop into debugger on failure
poetry run pytest --pdb

# Show full traceback
poetry run pytest --tb=long

# Show only failed tests
poetry run pytest --lf

# Stop after first failure
poetry run pytest -x
```

## 📝 Assertion Helpers

```python
# Basic assertions
assert value == expected
assert value is not None
assert "substring" in text

# Collection assertions
assert len(collection) == 3
assert item in collection
assert collection  # Not empty

# Numeric assertions
assert count > 0
assert 0.99 < value < 1.01  # Float comparison

# Exception assertions
with pytest.raises(ValueError):
    function_that_raises()

# Approximate comparison
assert pytest.approx(0.1 + 0.2) == 0.3
```

## 🔧 Common Issues

### "Event loop is closed"
Add `@pytest.mark.asyncio` to async test functions.

### "Fixture not found"
Check `conftest.py` or import the fixture.

### "Database locked"
Ensure using async sessions correctly with `await`.

### "Import error"
Run tests from `backend/` directory:
```bash
cd backend
poetry run pytest
```

## 📚 File Structure

```
backend/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_core/               # ✅ Complete
│   │   ├── test_security.py
│   │   ├── test_dependencies.py
│   │   ├── test_exceptions.py
│   │   └── test_middleware.py
│   ├── test_api/                # 🔲 TODO
│   ├── test_services/           # 🔲 TODO
│   ├── test_models/             # 🔲 TODO
│   └── test_tasks/              # 🔲 TODO
├── pytest.ini                   # Pytest config
└── run_tests.sh                 # Test runner
```

## 🎓 Best Practices

1. ✅ Use descriptive test names
2. ✅ One assertion per test (usually)
3. ✅ Follow AAA pattern (Arrange, Act, Assert)
4. ✅ Use fixtures for common setup
5. ✅ Mock external services
6. ✅ Test both success and failure paths
7. ✅ Test edge cases
8. ✅ Keep tests fast
9. ✅ Make tests independent
10. ✅ Document complex test logic

## 📖 Documentation

- **Comprehensive Guide**: `tests/README.md`
- **Full Test Plan**: `TEST_PLAN.md`
- **Progress Summary**: `TESTING_SUMMARY.md`
- **Completion Status**: `CORE_TESTS_COMPLETE.md`

## 💡 Tips

- Use `faker` fixture for realistic test data
- Use `test_user` fixture for authenticated tests
- Mock external APIs with provided fixtures
- Check `conftest.py` for all available fixtures
- Follow existing test patterns in test files
- Run tests frequently during development

---

**Quick Help**: `./run_tests.sh --help`
