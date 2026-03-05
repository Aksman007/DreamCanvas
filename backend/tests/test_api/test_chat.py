"""
Tests for chat API endpoints.

Endpoints tested:
    - POST /api/v1/chat
    - POST /api/v1/chat/enhance
"""

from unittest.mock import patch

import pytest
from fastapi import status


# ==================== Chat Tests ====================
class TestChat:
    """Test POST /api/v1/chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_success(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test successful chat with Claude."""
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Help me create a prompt for a sunset scene"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    @pytest.mark.asyncio
    async def test_chat_with_conversation_history(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test chat with conversation history."""
        history = [
            {"role": "user", "content": "I want to create an image"},
            {"role": "assistant", "content": "I can help you with that!"},
        ]

        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Make it colorful", "conversation_history": history},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_chat_suggested_prompt(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test that chat can return suggested prompts."""
        # Mock will return a response with "SUGGESTED PROMPT:" in it
        with patch("app.services.claude_service.ClaudeService.chat") as mock:
            mock.return_value = {
                "message": "Here's an idea:\n\nSUGGESTED PROMPT: A vibrant sunset over mountains",
                "suggested_prompt": "A vibrant sunset over mountains",
            }

            response = await async_client.post(
                "/api/v1/chat",
                headers=auth_headers,
                json={"message": "Suggest a sunset prompt"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "suggested_prompt" in data

    @pytest.mark.asyncio
    async def test_chat_no_auth(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test chat without authentication."""
        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Hello"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test chat with empty message."""
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": ""},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_chat_missing_message(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test chat without message field."""
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_chat_claude_unavailable(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test chat when Claude is unavailable."""
        with patch("app.services.claude_service.ClaudeService.is_available", False):
            response = await async_client.post(
                "/api/v1/chat",
                headers=auth_headers,
                json={"message": "Hello"},
            )

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    @pytest.mark.asyncio
    async def test_chat_invalid_conversation_history(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test chat with malformed conversation history."""
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Hello", "conversation_history": "not-a-list"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Enhance Prompt Tests ====================


class TestEnhancePrompt:
    """Test POST /api/v1/chat/enhance endpoint."""

    @pytest.mark.asyncio
    async def test_enhance_prompt_success(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test successful prompt enhancement."""
        response = await async_client.post(
            "/api/v1/chat/enhance?prompt=a sunset",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "original_prompt" in data
        assert "enhanced_prompt" in data
        assert data["original_prompt"] == "a sunset"
        assert isinstance(data["enhanced_prompt"], str)

    @pytest.mark.asyncio
    async def test_enhance_prompt_with_style(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing prompt with style parameter."""
        response = await async_client.post(
            "/api/v1/chat/enhance?prompt=a cat&style=vivid",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["original_prompt"] == "a cat"
        assert "enhanced_prompt" in data

    @pytest.mark.asyncio
    async def test_enhance_prompt_with_negative(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing prompt with negative prompt."""
        response = await async_client.post(
            "/api/v1/chat/enhance?prompt=a city&negative_prompt=people,cars",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["original_prompt"] == "a city"

    @pytest.mark.asyncio
    async def test_enhance_prompt_style_suggestions(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test that enhancement returns style suggestions."""
        # Mock to return style suggestions
        with patch("app.services.claude_service.ClaudeService.enhance_prompt") as mock:
            mock.return_value = {
                "enhanced_prompt": "A vibrant, colorful sunset",
                "style_suggestions": ["landscape", "nature", "warm colors"],
            }

            response = await async_client.post(
                "/api/v1/chat/enhance?prompt=sunset",
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "style_suggestions" in data
            assert isinstance(data["style_suggestions"], list)

    @pytest.mark.asyncio
    async def test_enhance_prompt_no_auth(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing prompt without authentication."""
        response = await async_client.post("/api/v1/chat/enhance?prompt=test")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_enhance_prompt_empty(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing with empty prompt."""
        response = await async_client.post(
            "/api/v1/chat/enhance?prompt=",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_enhance_prompt_missing(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing without prompt parameter."""
        response = await async_client.post(
            "/api/v1/chat/enhance",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_enhance_prompt_too_long(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing with prompt exceeding max length."""
        long_prompt = "x" * 4001  # Max is 4000

        response = await async_client.post(
            f"/api/v1/chat/enhance?prompt={long_prompt}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_enhance_prompt_claude_unavailable(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test enhancement when Claude is unavailable."""
        with patch("app.services.claude_service.ClaudeService.is_available", False):
            response = await async_client.post(
                "/api/v1/chat/enhance?prompt=test",
                headers=auth_headers,
            )

            # Should return original prompt when unavailable
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["enhanced_prompt"] == data["original_prompt"]

    @pytest.mark.asyncio
    async def test_enhance_prompt_special_characters(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing prompt with special characters."""
        prompt = "A cat & dog (best friends) at 50% opacity!"

        response = await async_client.post(
            f"/api/v1/chat/enhance?prompt={prompt}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "enhanced_prompt" in data

    @pytest.mark.asyncio
    async def test_enhance_prompt_unicode(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test enhancing prompt with unicode characters."""
        prompt = "Un caf\u00e9 avec du th\u00e9 \U0001f375"

        response = await async_client.post(
            f"/api/v1/chat/enhance?prompt={prompt}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "enhanced_prompt" in data

    @pytest.mark.asyncio
    async def test_enhance_prompt_idempotent(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test that enhancing same prompt multiple times works."""
        prompt = "a sunset"

        # Enhance twice
        response1 = await async_client.post(
            f"/api/v1/chat/enhance?prompt={prompt}",
            headers=auth_headers,
        )
        response2 = await async_client.post(
            f"/api/v1/chat/enhance?prompt={prompt}",
            headers=auth_headers,
        )

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_enhance_prompt_all_parameters(self, async_client, auth_headers, mock_claude_api) -> None:  # type: ignore[no-untyped-def]
        """Test enhancement with all parameters."""
        response = await async_client.post(
            "/api/v1/chat/enhance?prompt=mountain&style=photorealistic&negative_prompt=people",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["original_prompt"] == "mountain"
        assert "enhanced_prompt" in data
