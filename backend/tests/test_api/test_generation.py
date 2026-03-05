"""
Tests for image generation API endpoints.

Endpoints tested:
    - POST /api/v1/generate
    - GET /api/v1/generate/{id}
    - GET /api/v1/generate/{id}/status
    - DELETE /api/v1/generate/{id}
"""

import pytest
from fastapi import status

from app.models.generation import GenerationStatus

# ==================== Create Generation Tests ====================


class TestCreateGeneration:
    """Test POST /api/v1/generate endpoint."""

    @pytest.mark.asyncio
    async def test_create_generation_sync_success(  # type: ignore[no-untyped-def]
        self, async_client, auth_headers, generation_data, mock_claude_api, mock_dalle_api, mock_storage
    ) -> None:
        """Test creating a generation in sync mode."""
        response = await async_client.post(
            "/api/v1/generate?sync=true",
            headers=auth_headers,
            json=generation_data,
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()

        # Check response structure
        assert "id" in data
        assert "status" in data
        assert "original_prompt" in data
        assert data["original_prompt"] == generation_data["prompt"]

    @pytest.mark.asyncio
    async def test_create_generation_async_success(  # type: ignore[no-untyped-def]
        self, async_client, auth_headers, generation_data
    ) -> None:
        """Test creating a generation in async mode (default)."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json=generation_data,
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()

        # Should return immediately with pending status
        assert data["status"] == GenerationStatus.PENDING.value
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_generation_minimal_request(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with minimal required fields."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A beautiful sunset"},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["original_prompt"] == "A beautiful sunset"

    @pytest.mark.asyncio
    async def test_create_generation_custom_size(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with custom size."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A cat", "size": "1792x1024"},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["size"] == "1792x1024"

    @pytest.mark.asyncio
    async def test_create_generation_custom_quality(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with HD quality."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A dog", "quality": "hd"},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["quality"] == "hd"

    @pytest.mark.asyncio
    async def test_create_generation_with_style(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with style preset."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A landscape", "style": "vivid"},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["style"] == "vivid"

    @pytest.mark.asyncio
    async def test_create_generation_with_negative_prompt(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with negative prompt."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={
                "prompt": "A city",
                "negative_prompt": "people, cars",
            },
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["negative_prompt"] == "people, cars"

    @pytest.mark.asyncio
    async def test_create_generation_enhance_disabled(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with prompt enhancement disabled."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A tree", "enhance_prompt": False},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

    @pytest.mark.asyncio
    async def test_create_generation_no_auth(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation without authentication."""
        response = await async_client.post(
            "/api/v1/generate",
            json={"prompt": "A sunset"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_generation_empty_prompt(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with empty prompt."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": ""},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_generation_missing_prompt(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation without prompt."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_generation_prompt_too_long(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with excessively long prompt."""
        long_prompt = "x" * 4001  # Max is 4000

        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": long_prompt},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_generation_invalid_size(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with invalid size."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A flower", "size": "invalid"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_generation_invalid_quality(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test creating generation with invalid quality."""
        response = await async_client.post(
            "/api/v1/generate",
            headers=auth_headers,
            json={"prompt": "A flower", "quality": "invalid"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Get Generation Tests ====================


class TestGetGeneration:
    """Test GET /api/v1/generate/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_generation_success(self, async_client, auth_headers, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test getting a generation by ID."""
        # Create a generation
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test prompt",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            image_url="https://example.com/image.png",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        # Get the generation
        response = await async_client.get(
            f"/api/v1/generate/{generation.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == str(generation.id)
        assert data["original_prompt"] == "Test prompt"
        assert data["status"] == GenerationStatus.COMPLETED.value
        assert data["image_url"] == "https://example.com/image.png"

    @pytest.mark.asyncio
    async def test_get_generation_not_found(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test getting non-existent generation."""
        import uuid

        fake_id = uuid.uuid4()
        response = await async_client.get(
            f"/api/v1/generate/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_generation_wrong_user(  # type: ignore[no-untyped-def]
        self, async_client, auth_headers_user_2, db_session, test_user
    ) -> None:
        """Test getting another user's generation."""
        # Create generation for test_user
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="User 1's prompt",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        # Try to access with user 2's token
        response = await async_client.get(
            f"/api/v1/generate/{generation.id}",
            headers=auth_headers_user_2,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_generation_no_auth(self, async_client, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test getting generation without authentication."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        response = await async_client.get(f"/api/v1/generate/{generation.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_generation_invalid_uuid(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test getting generation with invalid UUID."""
        response = await async_client.get(
            "/api/v1/generate/not-a-uuid",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Get Generation Status Tests ====================


class TestGetGenerationStatus:
    """Test GET /api/v1/generate/{id}/status endpoint."""

    @pytest.mark.asyncio
    async def test_get_status_completed(self, async_client, auth_headers, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test getting status of completed generation."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
            image_url="https://example.com/image.png",
            thumbnail_url="https://example.com/thumb.png",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        response = await async_client.get(
            f"/api/v1/generate/{generation.id}/status",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == GenerationStatus.COMPLETED.value
        assert "message" in data
        assert data["image_url"] == "https://example.com/image.png"
        assert data["thumbnail_url"] == "https://example.com/thumb.png"

    @pytest.mark.asyncio
    async def test_get_status_pending(self, async_client, auth_headers, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test getting status of pending generation."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test",
            status=GenerationStatus.PENDING,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        response = await async_client.get(
            f"/api/v1/generate/{generation.id}/status",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == GenerationStatus.PENDING.value
        assert "message" in data
        assert "image_url" not in data

    @pytest.mark.asyncio
    async def test_get_status_failed(self, async_client, auth_headers, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test getting status of failed generation."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test",
            status=GenerationStatus.FAILED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
            error_message="Something went wrong",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        response = await async_client.get(
            f"/api/v1/generate/{generation.id}/status",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == GenerationStatus.FAILED.value
        assert data["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_get_status_not_found(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test getting status of non-existent generation."""
        import uuid

        fake_id = uuid.uuid4()
        response = await async_client.get(
            f"/api/v1/generate/{fake_id}/status",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ==================== Delete Generation Tests ====================


class TestDeleteGeneration:
    """Test DELETE /api/v1/generate/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_generation_success(self, async_client, auth_headers, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test deleting own generation."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="To be deleted",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)
        gen_id = generation.id

        # Delete
        response = await async_client.delete(
            f"/api/v1/generate/{gen_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

        # Verify deleted
        from sqlalchemy import select

        result = await db_session.execute(
            select(Generation).where(Generation.id == gen_id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_generation_not_found(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test deleting non-existent generation."""
        import uuid

        fake_id = uuid.uuid4()
        response = await async_client.delete(
            f"/api/v1/generate/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_generation_wrong_user(  # type: ignore[no-untyped-def]
        self, async_client, auth_headers_user_2, db_session, test_user
    ) -> None:
        """Test deleting another user's generation."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="User 1's generation",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        # Try to delete with user 2's token
        response = await async_client.delete(
            f"/api/v1/generate/{generation.id}",
            headers=auth_headers_user_2,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify not deleted
        from sqlalchemy import select

        result = await db_session.execute(
            select(Generation).where(Generation.id == generation.id)
        )
        assert result.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_delete_generation_no_auth(self, async_client, db_session, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test deleting generation without authentication."""
        from app.models.generation import Generation, GenerationStatus, ImageProvider

        generation = Generation(
            user_id=test_user.id,
            original_prompt="Test",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add(generation)
        await db_session.commit()
        await db_session.refresh(generation)

        response = await async_client.delete(f"/api/v1/generate/{generation.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
