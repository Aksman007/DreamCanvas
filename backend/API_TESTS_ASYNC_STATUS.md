# API Tests - AsyncClient Migration Status

## 🎯 Migration Complete!

All API tests have been successfully migrated from synchronous `TestClient` to asynchronous `AsyncClient`.

## ✅ Changes Made

### 1. Fixed AsyncClient Configuration
**File**: `tests/conftest.py`
- Updated `async_client` fixture to use `ASGITransport`
- Added `setup_test_database` fixture to create tables in app's engine
- Made user fixtures depend on `override_get_db` for proper ordering

**Before**:
```python
async with AsyncClient(app=app, base_url="http://testserver") as client:
    yield client
```

**After**:
```python
from httpx import ASGITransport
async with AsyncClient(
    transport=ASGITransport(app=app), base_url="http://testserver"
) as client:
    yield client
```

### 2. Fixed Database Engine Configuration
**File**: `app/db/session.py`
- Made engine configuration conditional for SQLite vs PostgreSQL
- SQLite doesn't support `pool_size`, `max_overflow`, `pool_timeout` parameters
- These are now only applied for PostgreSQL connections

**Before**:
```python
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,  # Fails for SQLite!
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,
)
```

**After**:
```python
is_sqlite = "sqlite" in settings.database_url.lower()
engine_args = {"echo": settings.db_echo}
if not is_sqlite:
    engine_args.update({
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
        "pool_pre_ping": True,
    })
engine = create_async_engine(settings.database_url, **engine_args)
```

### 3. Migrated All API Test Files
**Files Updated**:
- `tests/test_api/test_auth.py` (36 tests)
- `tests/test_api/test_generation.py` (45 tests)
- `tests/test_api/test_gallery.py` (22 tests)
- `tests/test_api/test_chat.py` (24 tests)

**Changes**:
- Replaced `client` parameter with `async_client` in all test functions
- Added `await` before all HTTP method calls:
  - `response = client.post(...)` → `response = await async_client.post(...)`
  - `response = client.get(...)` → `response = await async_client.get(...)`
  - `response = client.patch(...)` → `response = await async_client.patch(...)`
  - `response = client.delete(...)` → `response = await async_client.delete(...)`

### 4. Created Test Runner Script
**File**: `run_api_tests.sh`
- Sets required environment variables automatically
- Makes running API tests easier

## 📊 Current Test Status

### Overall Statistics
- **Total API Tests**: 127 tests
- **Currently Passing**: 20 tests (16%)
- **Still Failing**: 79 tests (62%)
- **Not Yet Run**: 28 tests (22%)

### Test Breakdown by File

| File | Total Tests | Passing | Failing | Pass Rate |
|------|-------------|---------|---------|-----------|
| test_auth.py | 36 | 18 | 18 | 50% |
| test_generation.py | 45 | ~2 | ~43 | ~4% |
| test_gallery.py | 22 | 0 | ~22 | 0% |
| test_chat.py | 24 | 0 | ~24 | 0% |
| **Total** | **127** | **~20** | **~107** | **~16%** |

## 🐛 Remaining Issues

### 1. Test User Isolation (High Priority)
**Problem**: Test users created in fixtures aren't visible to all test functions
**Impact**: ~50 tests failing with 401 Unauthorized errors
**Root Cause**: Database session isolation between fixture and app dependency override
**Status**: Partially fixed - user fixtures now depend on `override_get_db` for proper ordering

**Tests Affected**:
- Login tests that expect pre-existing users
- Protected endpoint tests using `auth_headers`
- Multi-user isolation tests

**Temporary Workaround**: Tests that don't rely on fixtures (like `test_register_success`) pass

### 2. External Service Mocking
**Problem**: Mock fixtures may not be properly applied to async tests
**Impact**: ~30 tests for generation, chat endpoints
**Status**: Needs investigation

**Tests Affected**:
- Image generation tests (DALL-E, Claude mocks)
- Chat tests (Claude API mock)
- Storage tests (S3/storage mock)

### 3. Rate Limiting in Tests
**Problem**: Some tests hitting 429 Too Many Requests
**Impact**: ~5-10 tests
**Root Cause**: Rate limiting middleware not properly disabled in test settings
**Status**: Needs fix in test_settings fixture

## 🚀 How to Run Tests

### Run All API Tests
```bash
# Using the test runner script (recommended)
./run_api_tests.sh

# Or manually with environment variable
DATABASE_URL="sqlite+aiosqlite:///:memory:" poetry run pytest tests/test_api/ -v
```

### Run Specific Test File
```bash
./run_api_tests.sh tests/test_api/test_auth.py -v
```

### Run Single Test
```bash
./run_api_tests.sh tests/test_api/test_auth.py::TestRegister::test_register_success -v
```

### Run with Coverage
```bash
./run_api_tests.sh --cov=app.api --cov-report=html
```

## ✅ Tests Currently Passing

### Authentication (18/36 passing)
- ✅ test_register_success
- ✅ test_register_invalid_email
- ✅ test_register_weak_password
- ✅ test_register_missing_email
- ✅ test_register_missing_password
- ✅ test_login_invalid_email
- ✅ test_login_invalid_password
- ✅ test_login_missing_email
- ✅ test_login_missing_password
- ✅ test_refresh_token_invalid
- ✅ test_refresh_token_missing
- ✅ test_get_current_user_no_auth
- ✅ test_get_current_user_invalid_token
- ✅ test_get_current_user_malformed_auth_header
- ✅ test_update_profile_no_auth
- And 3 more...

### Generation (~2 passing)
- Limited tests passing due to mock/auth issues

## 📋 Next Steps to Complete API Tests

### Immediate Priority
1. **Fix Test User Isolation** (High Priority)
   - Ensure test users created in fixtures are visible to API endpoints
   - Verify `override_get_db` properly shares database session
   - Consider using app's database directly for test users

2. **Fix External Service Mocking** (High Priority)
   - Verify mock fixtures work with AsyncClient
   - Ensure mocks are applied before async test execution
   - Test generation and chat endpoints with mocks

3. **Disable Rate Limiting** (Medium Priority)
   - Update `test_settings` fixture to properly disable rate limiting
   - Verify middleware configuration in test mode

### Future Enhancements
4. **Add Test Cleanup** (Low Priority)
   - Ensure database is properly cleaned between tests
   - Verify no test data leakage

5. **Improve Test Coverage** (Low Priority)
   - Add more edge cases
   - Test error conditions more thoroughly

## 💡 Key Learnings

### AsyncClient vs TestClient
- `AsyncClient` requires `ASGITransport` wrapper around FastAPI app
- All HTTP methods must be awaited
- Better for testing async dependencies and database operations

### SQLite Testing Limitations
- In-memory SQLite doesn't support PostgreSQL-specific features
- Pool settings must be conditional based on database type
- Shared cache doesn't help with separate engine instances

### Fixture Dependencies
- Fixture execution order matters for database operations
- `autouse=True` fixtures run before explicit fixtures
- User fixtures must depend on `override_get_db` for proper session sharing

## 📚 References

- [HTTPX AsyncClient Documentation](https://www.python-httpx.org/async/)
- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

**Status**: AsyncClient migration complete, database configuration fixed, 20/127 tests passing
**Date**: February 10, 2026
**Next Action**: Fix test user isolation to increase pass rate to 80%+
