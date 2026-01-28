"""
Claude Service - Anthropic Claude API integration for prompt enhancement.
"""

import logging
from typing import Any

from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude API."""

    def __init__(self):
        if not settings.has_claude:
            logger.warning("Claude API key not configured")
            self.client = None
        else:
            self.client = Anthropic(api_key=settings.anthropic_api_key)

        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature

    @property
    def is_available(self) -> bool:
        """Check if Claude service is available."""
        return self.client is not None

    async def enhance_prompt(
        self,
        prompt: str,
        style: str | None = None,
        negative_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Enhance a user's prompt for better image generation.

        Args:
            prompt: User's original prompt
            style: Optional style preset
            negative_prompt: Optional negative prompt

        Returns:
            Dictionary with enhanced_prompt and style_suggestions
        """
        if not self.is_available:
            logger.warning("Claude not available, returning original prompt")
            return {
                "enhanced_prompt": prompt,
                "style_suggestions": None,
            }

        system_prompt = """You are an expert at creating detailed, evocative prompts for AI image generation.

Your task is to enhance the user's prompt to create better, more detailed images. Follow these guidelines:

1. Add specific visual details (lighting, colors, textures, atmosphere)
2. Include artistic style references if appropriate
3. Add composition and perspective details
4. Keep the core intent of the original prompt
5. Make it vivid and descriptive but not overly long (aim for 100-200 words)
6. If a style is specified, incorporate it naturally

Respond in JSON format:
{
    "enhanced_prompt": "Your enhanced prompt here",
    "style_suggestions": ["style1", "style2", "style3"]
}

Only respond with the JSON, no other text."""

        user_message = f"Original prompt: {prompt}"
        if style:
            user_message += f"\nStyle: {style}"
        if negative_prompt:
            user_message += f"\nAvoid: {negative_prompt}"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            # Parse the response
            content = response.content[0].text

            # Try to parse as JSON
            import json

            try:
                result = json.loads(content)
                return {
                    "enhanced_prompt": result.get("enhanced_prompt", prompt),
                    "style_suggestions": result.get("style_suggestions"),
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw response as enhanced prompt
                logger.warning("Failed to parse Claude response as JSON")
                return {
                    "enhanced_prompt": content.strip(),
                    "style_suggestions": None,
                }

        except RateLimitError as e:
            logger.error(f"Claude rate limit exceeded: {e}")
            raise ValueError("Rate limit exceeded. Please try again later.")

        except APIConnectionError as e:
            logger.error(f"Claude connection error: {e}")
            raise ValueError("Failed to connect to AI service. Please try again.")

        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise ValueError(f"AI service error: {str(e)}")

    async def chat(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Chat with Claude for prompt assistance.

        Args:
            message: User's message
            conversation_history: Previous messages in the conversation

        Returns:
            Dictionary with message and optional suggested_prompt
        """
        if not self.is_available:
            return {
                "message": "AI assistant is not configured. Please provide your prompt directly.",
                "suggested_prompt": None,
            }

        system_prompt = """You are a helpful AI assistant specializing in creating prompts for AI image generation.

Help users refine their ideas into effective image generation prompts. You can:
- Ask clarifying questions about their vision
- Suggest improvements to their prompts
- Recommend styles and artistic directions
- Provide complete, ready-to-use prompts

When you have enough information, include a "SUGGESTED PROMPT:" section with a complete prompt they can use.

Be friendly, creative, and helpful."""

        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.8,  # Slightly more creative for chat
                system=system_prompt,
                messages=messages,
            )

            content = response.content[0].text

            # Extract suggested prompt if present
            suggested_prompt = None
            if "SUGGESTED PROMPT:" in content:
                parts = content.split("SUGGESTED PROMPT:")
                suggested_prompt = parts[1].strip().split("\n")[0].strip()

            return {
                "message": content,
                "suggested_prompt": suggested_prompt,
            }

        except RateLimitError:
            return {
                "message": "I'm receiving too many requests right now. Please try again in a moment.",
                "suggested_prompt": None,
            }

        except (APIConnectionError, APIError) as e:
            logger.error(f"Claude error in chat: {e}")
            return {
                "message": "I'm having trouble connecting right now. Please try again.",
                "suggested_prompt": None,
            }


# Singleton instance
_claude_service: ClaudeService | None = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
