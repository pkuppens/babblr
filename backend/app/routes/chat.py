import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.db import get_db
from app.models.models import Conversation, Message
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation_service import get_conversation_service
from app.services.llm.exceptions import LLMAuthenticationError, LLMError, RateLimitError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Process a chat message and get AI tutor response.
    Includes error correction and vocabulary extraction.
    """
    try:
        logger.info(f"Processing chat request for conversation {request.conversation_id}")

        # Verify conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get conversation history
        messages_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == request.conversation_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()

        conversation_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Get conversation service (uses configured provider, defaults to Ollama)
        conversation_service = get_conversation_service()

        # First, correct the user's message if needed
        corrected_text, corrections = await conversation_service.correct_text(
            request.user_message, request.language, request.difficulty_level
        )

        # Save user message (with original text)
        user_message = Message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.user_message,
            corrections=json.dumps(corrections) if corrections else None,
        )
        db.add(user_message)
        await db.commit()

        # Generate AI response
        assistant_response, vocabulary_items = await conversation_service.generate_response(
            corrected_text if corrections else request.user_message,
            request.language,
            request.difficulty_level,
            conversation_history,
        )

        # Save assistant message
        assistant_message = Message(
            conversation_id=request.conversation_id, role="assistant", content=assistant_response
        )
        db.add(assistant_message)

        # Update conversation timestamp using configured timezone.
        #
        # On Windows, `zoneinfo` needs the `tzdata` package to resolve IANA timezone
        # names like "Europe/Amsterdam". If not available (or misconfigured), we
        # fall back to UTC rather than failing the whole chat request.
        try:
            tz = ZoneInfo(settings.babblr_timezone)
        except ZoneInfoNotFoundError:
            logger.warning(
                "Invalid/unavailable timezone '%s'; falling back to UTC. "
                "Tip: on Windows, install the 'tzdata' Python package.",
                settings.babblr_timezone,
            )
            tz = ZoneInfo("UTC")

        conversation.updated_at = datetime.now(tz).replace(tzinfo=None)

        await db.commit()

        logger.info(f"Successfully processed chat for conversation {request.conversation_id}")

        return ChatResponse(
            assistant_message=assistant_response,
            corrections=corrections,
            vocabulary_items=vocabulary_items,
        )

    except LLMAuthenticationError as e:
        # This is *server-to-upstream* authentication (LLM provider), not end-user auth.
        # Return 503 to avoid confusing the UI with a "you are unauthorized" message.
        logger.error("LLM authentication error: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_authentication_error",
                "message": "The AI tutor service is not configured (missing/invalid API key).",
                "technical_details": str(e),
                "fix": f"Set a valid API key for {settings.llm_provider} in backend/.env, or switch LLM_PROVIDER to 'ollama' or 'mock'.",
            },
        )
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_error",
                "message": "AI service rate limit exceeded. Please try again later.",
                "technical_details": str(e),
                "retry_after": getattr(e, "retry_after", 60),
            },
        )
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_error",
                "message": "AI service temporarily unavailable",
                "technical_details": str(e),
            },
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "technical_details": str(e),
            },
        )
