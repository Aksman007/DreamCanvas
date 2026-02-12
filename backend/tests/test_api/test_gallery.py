"""
Tests for gallery API endpoints.

Endpoints tested:
    - GET /api/v1/gallery
"""

import pytest
from fastapi import status

from app.models.generation import GenerationStatus


# ==================== List Generations Tests ====================


class TestListGenerations:
    """Test GET /api/v1/gallery endpoint."""

    @pytest.mark.asyncio
    async def test_list_generations_success(self, async_client, auth_headers, db_session, test_user):
        """Test listing user's generations."""
        # Create some generations
        from app.models.generation import Generation, ImageProvider

        for i in range(3):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                status=GenerationStatus.COMPLETED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        await db_session.commit()

        response = await async_client.get("/api/v1/gallery", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data

        # Check items
        assert len(data["items"]) == 3
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_list_generations_empty(self, async_client, auth_headers):
        """Test listing when user has no generations."""
        response = await async_client.get("/api/v1/gallery", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_generations_pagination(self, async_client, auth_headers, db_session, test_user):
        """Test pagination of generations."""
        # Create 25 generations
        from app.models.generation import Generation, ImageProvider

        for i in range(25):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                status=GenerationStatus.COMPLETED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        await db_session.commit()

        # Get first page (default page_size=20)
        response1 = await async_client.get("/api/v1/gallery?page=1", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["items"]) == 20
        assert data1["total"] == 25
        assert data1["page"] == 1
        assert data1["pages"] == 2

        # Get second page
        response2 = await async_client.get("/api/v1/gallery?page=2", headers=auth_headers)
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert len(data2["items"]) == 5
        assert data2["total"] == 25
        assert data2["page"] == 2

    @pytest.mark.asyncio
    async def test_list_generations_custom_page_size(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test custom page size."""
        # Create 15 generations
        from app.models.generation import Generation, ImageProvider

        for i in range(15):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                status=GenerationStatus.COMPLETED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        await db_session.commit()

        response = await async_client.get("/api/v1/gallery?page_size=5", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 5
        assert data["page_size"] == 5
        assert data["total"] == 15
        assert data["pages"] == 3

    @pytest.mark.asyncio
    async def test_list_generations_max_page_size(self, async_client, auth_headers):
        """Test that page size is limited to maximum."""
        response = await async_client.get("/api/v1/gallery?page_size=200", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Max page size should be 100
        assert data["page_size"] == 100

    @pytest.mark.asyncio
    async def test_list_generations_filter_by_status(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test filtering by status."""
        # Create generations with different statuses
        from app.models.generation import Generation, ImageProvider

        statuses = [
            GenerationStatus.COMPLETED,
            GenerationStatus.COMPLETED,
            GenerationStatus.FAILED,
            GenerationStatus.PENDING,
        ]

        for i, status_val in enumerate(statuses):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                status=status_val,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        await db_session.commit()

        # Filter for completed only
        response = await async_client.get(
            f"/api/v1/gallery?status={GenerationStatus.COMPLETED.value}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert all(item["status"] == GenerationStatus.COMPLETED.value for item in data["items"])

    @pytest.mark.asyncio
    async def test_list_generations_filter_pending(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test filtering for pending generations."""
        from app.models.generation import Generation, ImageProvider

        # Create mix of statuses
        gen1 = Generation(
            user_id=test_user.id,
            original_prompt="Completed",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        gen2 = Generation(
            user_id=test_user.id,
            original_prompt="Pending",
            status=GenerationStatus.PENDING,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add_all([gen1, gen2])
        await db_session.commit()

        # Filter for pending
        response = await async_client.get(
            f"/api/v1/gallery?status={GenerationStatus.PENDING.value}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == GenerationStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_list_generations_ordering(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test that generations are ordered by created_at desc (newest first)."""
        import asyncio
        from app.models.generation import Generation, ImageProvider

        # Create generations with small delay
        for i in range(3):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                status=GenerationStatus.COMPLETED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
            await db_session.commit()
            await db_session.refresh(gen)
            await asyncio.sleep(0.01)  # Small delay to ensure different timestamps

        response = await async_client.get("/api/v1/gallery", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be in reverse order (newest first)
        assert data["items"][0]["original_prompt"] == "Prompt 2"
        assert data["items"][1]["original_prompt"] == "Prompt 1"
        assert data["items"][2]["original_prompt"] == "Prompt 0"

    @pytest.mark.asyncio
    async def test_list_generations_no_auth(self, async_client):
        """Test listing generations without authentication."""
        response = await async_client.get("/api/v1/gallery")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_list_generations_only_own(
        self, async_client, auth_headers, auth_headers_user_2, db_session, test_user, test_user_2
    ):
        """Test that users only see their own generations."""
        from app.models.generation import Generation, ImageProvider

        # Create generations for user 1
        gen1 = Generation(
            user_id=test_user.id,
            original_prompt="User 1's generation",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        # Create generation for user 2
        gen2 = Generation(
            user_id=test_user_2.id,
            original_prompt="User 2's generation",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
        )
        db_session.add_all([gen1, gen2])
        await db_session.commit()

        # User 1 should only see their generation
        response1 = await async_client.get("/api/v1/gallery", headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["items"]) == 1
        assert data1["items"][0]["original_prompt"] == "User 1's generation"

        # User 2 should only see their generation
        response2 = await async_client.get("/api/v1/gallery", headers=auth_headers_user_2)
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert len(data2["items"]) == 1
        assert data2["items"][0]["original_prompt"] == "User 2's generation"

    @pytest.mark.asyncio
    async def test_list_generations_invalid_page(self, async_client, auth_headers):
        """Test with invalid page number."""
        response = await async_client.get("/api/v1/gallery?page=0", headers=auth_headers)

        # Should default to page 1
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_generations_invalid_page_size(self, async_client, auth_headers):
        """Test with invalid page size."""
        response = await async_client.get("/api/v1/gallery?page_size=0", headers=auth_headers)

        # Should default to minimum page size (1)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page_size"] >= 1

    @pytest.mark.asyncio
    async def test_list_generations_invalid_status(self, async_client, auth_headers):
        """Test filtering with invalid status."""
        response = await async_client.get("/api/v1/gallery?status=invalid_status", headers=auth_headers)

        # Should return 422 for invalid enum value
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_list_generations_combined_filters(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test combining pagination and filtering."""
        from app.models.generation import Generation, ImageProvider

        # Create 10 completed and 5 failed
        for i in range(10):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Completed {i}",
                status=GenerationStatus.COMPLETED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        for i in range(5):
            gen = Generation(
                user_id=test_user.id,
                original_prompt=f"Failed {i}",
                status=GenerationStatus.FAILED,
                provider=ImageProvider.DALLE,
                model="dall-e-3",
            )
            db_session.add(gen)
        await db_session.commit()

        # Get completed with page size 5
        response = await async_client.get(
            f"/api/v1/gallery?status={GenerationStatus.COMPLETED.value}&page_size=5",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["items"]) == 5
        assert data["total"] == 10
        assert data["pages"] == 2

    @pytest.mark.asyncio
    async def test_list_generations_response_structure(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test that response includes all expected fields."""
        from app.models.generation import Generation, ImageProvider

        gen = Generation(
            user_id=test_user.id,
            original_prompt="Test prompt",
            enhanced_prompt="Enhanced test prompt",
            status=GenerationStatus.COMPLETED,
            provider=ImageProvider.DALLE,
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            style="vivid",
            image_url="https://example.com/image.png",
            thumbnail_url="https://example.com/thumb.png",
        )
        db_session.add(gen)
        await db_session.commit()

        response = await async_client.get("/api/v1/gallery", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        item = data["items"][0]
        assert "id" in item
        assert "original_prompt" in item
        assert "enhanced_prompt" in item
        assert "status" in item
        assert "provider" in item
        assert "model" in item
        assert "size" in item
        assert "quality" in item
        assert "style" in item
        assert "image_url" in item
        assert "thumbnail_url" in item
        assert "created_at" in item
        assert "updated_at" in item
