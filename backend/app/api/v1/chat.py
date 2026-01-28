"""
Chat Router - Claude chat for prompt assistance.

Endpoints:
    POST /chat - Chat with Claude for prompt help
    POST /chat/enhance - Enhance a prompt without generating
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser
from app.schemas.generation import ChatRequest, ChatResponse, PromptEnhanceResponse
from app.services.claude_service import get_claude_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with AI",
    description="Chat with Claude AI for prompt assistance.",
    responses={
        200: {"description": "Chat response"},
        503: {"description": "AI service unavailable"},
    },
)
async def chat_with_claude(
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    """
    Chat with Claude AI for prompt assistance.

    Use this to:
    - Get help crafting effective prompts
    - Refine your ideas
    - Get style suggestions

    **Parameters:**
    - `message`: Your message or question
    - `conversation_history`: Previous messages for context (optional)

    **Requires Authentication**
    """
    claude = get_claude_service()

    if not claude.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI chat service is not available",
        )

    result = await claude.chat(
        message=request.message,
        conversation_history=request.conversation_history,
    )

    return ChatResponse(
        message=result["message"],
        suggested_prompt=result.get("suggested_prompt"),
    )


@router.post(
    "/enhance",
    response_model=PromptEnhanceResponse,
    summary="Enhance a prompt",
    description="Use Claude to enhance a prompt without generating an image.",
    responses={
        200: {"description": "Enhanced prompt"},
        503: {"description": "AI service unavailable"},
    },
)
async def enhance_prompt(
    current_user: CurrentUser,
    prompt: str = Query(..., min_length=1, max_length=4000, description="Prompt to enhance"),
    style: str | None = Query(default=None, description="Style preset"),
    negative_prompt: str | None = Query(default=None, description="Things to avoid"),
) -> PromptEnhanceResponse:
    """
    Enhance a prompt using Claude AI.

    This endpoint lets you preview how Claude will enhance your prompt
    before generating an image.

    **Parameters:**
    - `prompt`: Your original prompt (query parameter)
    - `style`: Optional style preset
    - `negative_prompt`: Optional things to avoid

    **Requires Authentication**
    """
    claude = get_claude_service()

    if not claude.is_available:
        return PromptEnhanceResponse(
            original_prompt=prompt,
            enhanced_prompt=prompt,
            style_suggestions=None,
        )

    result = await claude.enhance_prompt(
        prompt=prompt,
        style=style,
        negative_prompt=negative_prompt,
    )

    return PromptEnhanceResponse(
        original_prompt=prompt,
        enhanced_prompt=result["enhanced_prompt"],
        style_suggestions=result.get("style_suggestions"),
    )
