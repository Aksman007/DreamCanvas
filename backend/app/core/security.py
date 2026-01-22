"""
Security Module

Handles password hashing and JWT token operations.
"""

import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


# ============================================================================
# PASSWORD HASHING (using bcrypt directly)
# ============================================================================


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Encode password to bytes, truncate to 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Encode both to bytes, truncate plain password to 72 bytes
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")

        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================================================
# JWT TOKEN MODELS
# ============================================================================


class TokenPayload(BaseModel):
    """JWT Token payload structure."""

    sub: str
    exp: datetime
    iat: datetime
    type: str
    jti: str | None = None


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# JWT TOKEN CREATION
# ============================================================================


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": secrets.token_urlsafe(16),
    }

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_token_pair(subject: str | int) -> TokenPair:
    """Create both access and refresh tokens."""
    return TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


# ============================================================================
# JWT TOKEN VERIFICATION
# ============================================================================


def decode_token(token: str) -> TokenPayload | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        return TokenPayload(
            sub=payload.get("sub", ""),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
            type=payload.get("type", ""),
            jti=payload.get("jti"),
        )
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> TokenPayload | None:
    """Verify a token and check its type."""
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.type != token_type:
        return None

    return payload


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def generate_api_key(prefix: str = "dc") -> str:
    """Generate a secure API key."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def generate_verification_token() -> str:
    """Generate a token for email verification or password reset."""
    return secrets.token_urlsafe(32)
