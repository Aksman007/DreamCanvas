"""
Tests for security module - password hashing and JWT tokens.
"""

from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    generate_api_key,
    generate_verification_token,
    hash_password,
    verify_password,
    verify_token,
)

# ==================== Password Hashing Tests ====================


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password(self) -> None:
        """Test that password hashing works."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Hash should be different from plain text
        assert len(hashed) == 60  # bcrypt hashes are always 60 chars

    def test_hash_password_different_each_time(self) -> None:
        """Test that hashing the same password produces different hashes (due to salt)."""
        password = "SamePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts produce different hashes

    def test_verify_password_success(self) -> None:
        """Test that correct password verification works."""
        password = "CorrectPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self) -> None:
        """Test that incorrect password is rejected."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_invalid_hash(self) -> None:
        """Test that verification with invalid hash returns False."""
        password = "SomePassword"
        invalid_hash = "not-a-valid-bcrypt-hash"

        assert verify_password(password, invalid_hash) is False

    def test_hash_password_truncates_at_72_bytes(self) -> None:
        """Test that passwords longer than 72 bytes are handled correctly."""
        # bcrypt has a 72-byte limit
        long_password = "a" * 100
        hashed = hash_password(long_password)

        # Should still hash successfully
        assert hashed is not None

        # Should verify with the same long password
        assert verify_password(long_password, hashed) is True

    def test_hash_password_with_unicode(self) -> None:
        """Test password hashing with unicode characters."""
        password = "Pässwörd123!\U0001f512"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_empty_string(self) -> None:
        """Test verification with empty password."""
        password = "ValidPassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False


# ==================== JWT Access Token Tests ====================


class TestAccessToken:
    """Test JWT access token creation and verification."""

    def test_create_access_token(self) -> None:
        """Test creating an access token."""
        user_id = "user-123"
        token = create_access_token(subject=user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_payload(self) -> None:
        """Test that access token contains correct payload."""
        user_id = "user-456"
        token = create_access_token(subject=user_id)

        # Decode without verification to inspect payload
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_create_access_token_custom_expiry(self) -> None:
        """Test creating access token with custom expiration."""
        user_id = "user-789"
        expires_delta = timedelta(minutes=60)
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # Calculate expected expiration (approximately)
        now = datetime.now(UTC)
        expected_exp = now + expires_delta

        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)

        # Allow 5 second tolerance
        assert abs((exp - expected_exp).total_seconds()) < 5

    def test_create_access_token_additional_claims(self) -> None:
        """Test creating access token with additional claims."""
        user_id = "user-abc"
        additional_claims = {
            "email": "user@example.com",
            "role": "admin",
        }

        token = create_access_token(
            subject=user_id,
            additional_claims=additional_claims,
        )

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["email"] == "user@example.com"
        assert payload["role"] == "admin"

    def test_create_access_token_with_integer_subject(self) -> None:
        """Test creating token with integer subject (should convert to string)."""
        user_id = 12345
        token = create_access_token(subject=user_id)

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["sub"] == "12345"


# ==================== JWT Refresh Token Tests ====================


class TestRefreshToken:
    """Test JWT refresh token creation."""

    def test_create_refresh_token(self) -> None:
        """Test creating a refresh token."""
        user_id = "user-refresh-123"
        token = create_refresh_token(subject=user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_payload(self) -> None:
        """Test that refresh token has correct payload."""
        user_id = "user-refresh-456"
        token = create_refresh_token(subject=user_id)

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token_longer_expiry(self) -> None:
        """Test that refresh token expires later than access token."""
        user_id = "user-compare"
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        access_payload = jwt.decode(
            access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        refresh_payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        access_exp = access_payload["exp"]
        refresh_exp = refresh_payload["exp"]

        # Refresh token should expire much later
        assert refresh_exp > access_exp

    def test_create_refresh_token_custom_expiry(self) -> None:
        """Test creating refresh token with custom expiration."""
        user_id = "user-custom-refresh"
        expires_delta = timedelta(days=14)  # 2 weeks
        token = create_refresh_token(subject=user_id, expires_delta=expires_delta)

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        now = datetime.now(UTC)
        expected_exp = now + expires_delta
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)

        # Allow 5 second tolerance
        assert abs((exp - expected_exp).total_seconds()) < 5


# ==================== Token Pair Tests ====================


class TestTokenPair:
    """Test creating token pairs."""

    def test_create_token_pair(self) -> None:
        """Test creating both access and refresh tokens."""
        user_id = "user-pair-123"
        tokens = create_token_pair(subject=user_id)

        assert tokens is not None
        assert hasattr(tokens, "access_token")
        assert hasattr(tokens, "refresh_token")
        assert hasattr(tokens, "token_type")
        assert hasattr(tokens, "expires_in")

    def test_token_pair_structure(self) -> None:
        """Test that token pair has correct structure."""
        user_id = "user-pair-456"
        tokens = create_token_pair(subject=user_id)

        assert isinstance(tokens.access_token, str)
        assert isinstance(tokens.refresh_token, str)
        assert tokens.token_type == "bearer"
        assert isinstance(tokens.expires_in, int)
        assert tokens.expires_in > 0

    def test_token_pair_different_tokens(self) -> None:
        """Test that access and refresh tokens are different."""
        user_id = "user-pair-789"
        tokens = create_token_pair(subject=user_id)

        assert tokens.access_token != tokens.refresh_token

    def test_token_pair_both_valid(self) -> None:
        """Test that both tokens in pair are valid."""
        user_id = "user-pair-abc"
        tokens = create_token_pair(subject=user_id)

        # Decode both to verify they're valid
        access_payload = jwt.decode(
            tokens.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        refresh_payload = jwt.decode(
            tokens.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert access_payload["sub"] == user_id
        assert refresh_payload["sub"] == user_id


# ==================== Token Decoding Tests ====================


class TestTokenDecoding:
    """Test JWT token decoding and validation."""

    def test_decode_token_valid(self) -> None:
        """Test decoding a valid token."""
        user_id = "user-decode-123"
        token = create_access_token(subject=user_id)

        payload = decode_token(token)

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "access"

    def test_decode_token_invalid(self) -> None:
        """Test that decoding invalid token returns None."""
        invalid_token = "not.a.valid.jwt.token"

        payload = decode_token(invalid_token)

        assert payload is None

    def test_decode_token_expired(self) -> None:
        """Test that decoding expired token returns None."""
        user_id = "user-expired"
        expires_delta = timedelta(seconds=-10)  # Expired 10 seconds ago
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        payload = decode_token(token)

        assert payload is None

    def test_decode_token_wrong_secret(self) -> None:
        """Test that token signed with different secret is rejected."""
        user_id = "user-wrong-secret"

        # Create token with different secret
        wrong_payload = {
            "sub": user_id,
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "type": "access",
        }
        wrong_token = jwt.encode(
            wrong_payload,
            "wrong-secret-key",
            algorithm=settings.algorithm,
        )

        payload = decode_token(wrong_token)

        assert payload is None

    def test_decode_token_malformed(self) -> None:
        """Test that malformed token returns None."""
        malformed_tokens = [
            "",
            "abc",
            "header.payload",  # Missing signature
            "...",
        ]

        for token in malformed_tokens:
            payload = decode_token(token)
            assert payload is None, f"Expected None for token: {token}"


# ==================== Token Verification Tests ====================


class TestTokenVerification:
    """Test token verification with type checking."""

    def test_verify_token_access(self) -> None:
        """Test verifying an access token."""
        user_id = "user-verify-access"
        token = create_access_token(subject=user_id)

        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "access"

    def test_verify_token_refresh(self) -> None:
        """Test verifying a refresh token."""
        user_id = "user-verify-refresh"
        token = create_refresh_token(subject=user_id)

        payload = verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "refresh"

    def test_verify_token_wrong_type(self) -> None:
        """Test that verifying with wrong type returns None."""
        user_id = "user-wrong-type"
        access_token = create_access_token(subject=user_id)

        # Try to verify access token as refresh token
        payload = verify_token(access_token, token_type="refresh")

        assert payload is None

    def test_verify_token_refresh_as_access(self) -> None:
        """Test that refresh token can't be used as access token."""
        user_id = "user-refresh-as-access"
        refresh_token = create_refresh_token(subject=user_id)

        # Try to verify refresh token as access token
        payload = verify_token(refresh_token, token_type="access")

        assert payload is None

    def test_verify_token_expired(self) -> None:
        """Test that expired token fails verification."""
        user_id = "user-verify-expired"
        expires_delta = timedelta(seconds=-10)
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        payload = verify_token(token, token_type="access")

        assert payload is None

    def test_verify_token_invalid(self) -> None:
        """Test that invalid token fails verification."""
        invalid_token = "invalid.token.here"

        payload = verify_token(invalid_token, token_type="access")

        assert payload is None


# ==================== Utility Function Tests ====================


class TestUtilityFunctions:
    """Test utility functions for API keys and tokens."""

    def test_generate_api_key(self) -> None:
        """Test generating an API key."""
        api_key = generate_api_key()

        assert api_key is not None
        assert isinstance(api_key, str)
        assert api_key.startswith("dc_")
        assert len(api_key) > 10

    def test_generate_api_key_custom_prefix(self) -> None:
        """Test generating API key with custom prefix."""
        api_key = generate_api_key(prefix="test")

        assert api_key.startswith("test_")

    def test_generate_api_key_unique(self) -> None:
        """Test that generated API keys are unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()

        assert key1 != key2

    def test_generate_verification_token(self) -> None:
        """Test generating a verification token."""
        token = generate_verification_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # URL-safe tokens are reasonably long

    def test_generate_verification_token_unique(self) -> None:
        """Test that verification tokens are unique."""
        token1 = generate_verification_token()
        token2 = generate_verification_token()

        assert token1 != token2

    def test_generate_verification_token_url_safe(self) -> None:
        """Test that verification token is URL-safe."""
        token = generate_verification_token()

        # URL-safe tokens should not contain special chars except - and _
        import string

        allowed_chars = string.ascii_letters + string.digits + "-_"
        assert all(c in allowed_chars for c in token)
