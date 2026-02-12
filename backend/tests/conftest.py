"""
Pytest configuration and shared fixtures for DreamCanvas backend tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.core.security import create_token_pair, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

# Initialize Faker for test data generation
fake = Faker()

# ==================== Test Settings ====================


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings with overrides for testing."""
    return Settings(
        # Use in-memory SQLite for tests
        database_url="sqlite+aiosqlite:///:memory:",
        sync_database_url="sqlite:///:memory:",
        # Disable external services
        redis_url="redis://localhost:6379/15",  # Use separate DB for tests
        celery_task_always_eager=True,  # Run tasks synchronously in tests
        # Disable rate limiting for tests
        rate_limit_enabled=False,
        # Use test secret
        secret_key="test-secret-key-for-testing-only-min-32-chars",
        # Disable CORS for tests
        cors_origins=["*"],
        # Use local storage for tests
        storage_provider="local",
        local_storage_path="./test_storage",
        local_storage_url="http://testserver/storage",
        # Disable async generation for easier testing
        generation_async=False,
        # Test environment
        environment="development",
        debug=True,
    )


@pytest.fixture(scope="session", autouse=True)
def override_settings(test_settings: Settings) -> Generator:
    """Override app settings for all tests."""
    with patch("app.config.get_settings", return_value=test_settings):
        with patch("app.config.settings", test_settings):
            yield


# ==================== Database Fixtures ====================


@pytest.fixture(scope="session")
def sync_engine(test_settings: Settings):
    """Create synchronous SQLite engine for tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def async_engine(test_settings: Settings):
    """Create async SQLite engine for tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Each test runs in a transaction that's rolled back after the test.
    """
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        # Start a transaction
        await session.begin()
        yield session
        # Rollback transaction after test
        await session.rollback()

    # Drop tables after test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def sync_db_session(sync_engine) -> Generator[Session, None, None]:
    """Create a synchronous test database session."""
    SessionLocal = sessionmaker(bind=sync_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create tables in the app's database engine for tests."""
    from app.db.session import engine

    # Create all tables in the app's database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function", autouse=True)
async def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for tests."""
    async def _get_test_db():
        try:
            yield db_session
        finally:
            pass  # Don't commit/rollback here, let the test control it

    # Override the dependency
    app.dependency_overrides[get_db] = _get_test_db
    yield
    # Clear overrides after test
    app.dependency_overrides.clear()


# ==================== Test Client Fixtures ====================


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """
    Create a test client for sync tests.

    Use this for simple endpoint tests that don't need async.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client.

    Use this for async tests and when you need more control.
    """
    from httpx import ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


# ==================== User Fixtures ====================


@pytest.fixture
def user_data() -> dict:
    """Generate random user registration data."""
    return {
        "email": fake.email(),
        "password": "SecurePass123!",  # Valid password
        "display_name": fake.name(),
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, override_get_db) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        display_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_2(db_session: AsyncSession, override_get_db) -> User:
    """Create a second test user for multi-user tests."""
    user = User(
        email="test2@example.com",
        hashed_password=hash_password("password123"),
        display_name="Test User 2",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession, override_get_db) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        display_name="Inactive User",
        is_active=False,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ==================== Authentication Fixtures ====================


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate a valid JWT access token for test user."""
    tokens = create_token_pair(subject=str(test_user.id))
    return tokens.access_token


@pytest.fixture
def refresh_token(test_user: User) -> str:
    """Generate a valid JWT refresh token for test user."""
    tokens = create_token_pair(subject=str(test_user.id))
    return tokens.refresh_token


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Generate authentication headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def auth_headers_user_2(test_user_2: User) -> dict:
    """Generate authentication headers for second test user."""
    tokens = create_token_pair(subject=str(test_user_2.id))
    return {"Authorization": f"Bearer {tokens.access_token}"}


# ==================== Mock External Services ====================


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("redis.asyncio.from_url") as mock:
        redis_mock = AsyncMock()
        redis_mock.ping = AsyncMock(return_value=True)
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.delete = AsyncMock(return_value=1)
        redis_mock.publish = AsyncMock(return_value=1)
        mock.return_value = redis_mock
        yield redis_mock


@pytest.fixture
def mock_celery():
    """Mock Celery task execution."""
    with patch("app.tasks.generation_tasks.process_generation_task.delay") as mock:
        task_mock = MagicMock()
        task_mock.id = "test-task-id-123"
        mock.return_value = task_mock
        yield mock


@pytest.fixture
def mock_claude_api():
    """Mock Anthropic Claude API."""
    with patch("anthropic.Anthropic") as mock:
        client_mock = MagicMock()

        # Mock enhance_prompt response
        response_mock = MagicMock()
        response_mock.content = [
            MagicMock(
                text='{"enhanced_prompt": "A beautiful sunset over mountains with vibrant colors", "style_suggestions": ["landscape", "nature", "vibrant"]}'
            )
        ]
        client_mock.messages.create.return_value = response_mock

        mock.return_value = client_mock
        yield client_mock


@pytest.fixture
def mock_dalle_api():
    """Mock OpenAI DALL-E API."""
    with patch("openai.OpenAI") as mock:
        client_mock = MagicMock()

        # Mock image generation response
        image_data = MagicMock()
        image_data.url = "https://example.com/generated-image.png"
        image_data.revised_prompt = "Enhanced prompt by DALL-E"

        response_mock = MagicMock()
        response_mock.data = [image_data]

        client_mock.images.generate.return_value = response_mock
        mock.return_value = client_mock
        yield client_mock


@pytest.fixture
def mock_stability_api():
    """Mock Stability AI API."""
    with patch("httpx.AsyncClient.post") as mock:
        response_mock = AsyncMock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            "artifacts": [
                {
                    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "finishReason": "SUCCESS",
                }
            ]
        }
        mock.return_value = response_mock
        yield mock


@pytest.fixture
def mock_storage():
    """Mock storage service (S3/local)."""
    with patch("app.services.storage_service.StorageService") as mock:
        storage_mock = MagicMock()

        # Mock upload_image
        async def mock_upload_image(*args, **kwargs):
            from app.services.storage_service import StorageResult
            return StorageResult(
                success=True,
                url="http://testserver/storage/images/test-image.png",
                thumbnail_url="http://testserver/storage/thumbnails/test-image.png",
                key="test-image.png",
            )

        storage_mock.upload_image = AsyncMock(side_effect=mock_upload_image)
        storage_mock.upload_from_url = AsyncMock(side_effect=mock_upload_image)
        storage_mock.delete_image = AsyncMock(return_value=True)

        mock.return_value = storage_mock
        yield storage_mock


@pytest.fixture
def mock_httpx():
    """Mock httpx for external HTTP requests."""
    with patch("httpx.AsyncClient.get") as mock:
        response_mock = AsyncMock()
        response_mock.status_code = 200
        response_mock.content = b"fake-image-data"
        mock.return_value = response_mock
        yield mock


# ==================== Generation Fixtures ====================


@pytest.fixture
def generation_data() -> dict:
    """Generate random image generation request data."""
    return {
        "prompt": fake.text(max_nb_chars=200),
        "enhance_prompt": True,
        "style": fake.random_element(["vivid", "natural", "anime", "photorealistic"]),
        "size": "1024x1024",
        "quality": "standard",
        "provider": "dalle",
    }


# ==================== Faker Instance ====================


@pytest.fixture
def faker() -> Faker:
    """Provide Faker instance for generating test data."""
    return fake


# ==================== Pytest Configuration ====================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Helper Functions ====================


def assert_valid_uuid(value: str) -> bool:
    """Assert that a string is a valid UUID."""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False
