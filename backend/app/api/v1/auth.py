"""
Auth Router - Authentication endpoints.

Endpoints:
    POST /auth/register - Create new user account
    POST /auth/login - Authenticate and get tokens
    POST /auth/refresh - Refresh access token
    GET /auth/me - Get current user profile
    PATCH /auth/me - Update current user profile
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.core.dependencies import CurrentUser, DBSession
from app.core.security import (
    create_token_pair,
    verify_token,
)
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserProfileResponse,
    UserResponseForAuth,
)
from app.schemas.common import SuccessResponse
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# POST /auth/register
# ============================================================================


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
async def register(
    request: RegisterRequest,
    db: DBSession,
) -> AuthResponse:
    """
    Register a new user account.

    **Password Requirements:**
    - Minimum 8 characters
    - At least one letter
    - At least one digit
    """
    user_service = UserService(db)

    # Check if email already exists
    existing_user = await user_service.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    from app.schemas.user import UserCreate

    user_create = UserCreate(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    try:
        user = await user_service.create(user_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Generate tokens
    tokens = create_token_pair(subject=str(user.id))

    logger.info(f"New user registered: {user.email}")

    return AuthResponse(
        user=UserResponseForAuth.from_user(user),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
        ),
    )


# ============================================================================
# POST /auth/login
# ============================================================================


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user with email and password.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    db: DBSession,
) -> AuthResponse:
    """
    Authenticate user and return tokens.

    **Access Token:** Valid for 30 minutes. Use in Authorization header.
    **Refresh Token:** Valid for 7 days. Use to get new access token.
    """
    user_service = UserService(db)

    # Authenticate user
    user = await user_service.authenticate(
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    tokens = create_token_pair(subject=str(user.id))

    logger.info(f"User logged in: {user.email}")

    return AuthResponse(
        user=UserResponseForAuth.from_user(user),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
        ),
    )


# ============================================================================
# POST /auth/refresh
# ============================================================================


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a refresh token.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DBSession,
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    The refresh token is also rotated for security.
    """
    # Verify the refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user_service = UserService(db)
    user = await user_service.get_by_id(payload.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new token pair
    tokens = create_token_pair(subject=str(user.id))

    logger.info(f"Token refreshed for user: {user.email}")

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


# ============================================================================
# GET /auth/me
# ============================================================================


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the authenticated user's full profile information.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserProfileResponse:
    """
    Get the current authenticated user's profile.

    Returns all user information including:
    - Basic info (email, display_name, bio, avatar)
    - Account status (is_active, is_verified, is_superuser)
    - Preferences
    - Usage statistics (generation_count, last_generation_at)
    - Timestamps (created_at, updated_at)

    **Requires Authentication:** Include access token in Authorization header.
    """
    logger.info(f"Profile retrieved for user: {current_user.email}")

    return UserProfileResponse.model_validate(current_user)


# ============================================================================
# PATCH /auth/me
# ============================================================================


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the authenticated user's profile information.",
    responses={
        200: {"description": "Profile updated successfully"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
async def update_current_user_profile(
    request: UpdateProfileRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> UserProfileResponse:
    """
    Update the current authenticated user's profile.

    **Updatable Fields:**
    - `display_name` - User's display name (max 100 chars)
    - `bio` - User's biography (max 500 chars)
    - `avatar_url` - URL to avatar image
    - `preferences` - User preferences (merged with existing)

    Only provide fields you want to update. Omitted fields remain unchanged.

    **Requires Authentication:** Include access token in Authorization header.
    """
    user_service = UserService(db)

    # Get update data (only fields that were provided)
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        # No fields to update, return current user
        return UserProfileResponse.model_validate(current_user)

    # Handle preferences merge separately
    if "preferences" in update_data and update_data["preferences"] is not None:
        # Merge new preferences with existing
        merged_preferences = {**current_user.preferences, **update_data["preferences"]}
        current_user.preferences = merged_preferences
        del update_data["preferences"]

    # Update other fields
    for field, value in update_data.items():
        if value is not None:  # Only update non-None values
            setattr(current_user, field, value)

    # Commit changes
    await db.commit()
    await db.refresh(current_user)

    logger.info(f"Profile updated for user: {current_user.email}")

    return UserProfileResponse.model_validate(current_user)
