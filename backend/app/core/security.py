# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings


# ============== Password Hashing ==============

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Adjust for security/performance balance
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============== JWT Tokens ==============


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # Subject (user ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # "access" or "refresh"
    jti: str | None = None  # JWT ID for token revocation


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: User ID or unique identifier
        expires_delta: Custom expiration time
        additional_claims: Extra data to include in token

    Returns:
        Encoded JWT string
    """
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT refresh token (longer-lived).

    Args:
        subject: User ID or unique identifier
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT string
    """
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": secrets.token_urlsafe(16),
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload | None:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT string to decode

    Returns:
        TokenPayload if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> TokenPayload | None:
    """
    Verify a token and check its type.

    Args:
        token: JWT string to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenPayload if valid and correct type, None otherwise
    """
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.type != token_type:
        return None

    return payload


# ============== Utility Functions ==============


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"dc_{secrets.token_urlsafe(32)}"


def generate_verification_token() -> str:
    """Generate a token for email verification."""
    return secrets.token_urlsafe(32)
