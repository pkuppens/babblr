import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from anthropic import APIError, AuthenticationError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.db import get_db
from app.models.models import Conversation, Message
from app.models.schemas import ChatRequest, ChatResponse
from app.services.claude_service import claude_service

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

        # First, correct the user's message if needed
        corrected_text, corrections = await claude_service.correct_text(
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
        assistant_response, vocabulary_items = await claude_service.generate_response(
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

        # Update conversation timestamp using configured timezone
        tz = ZoneInfo(settings.timezone)
        conversation.updated_at = datetime.now(tz).replace(tzinfo=None)

        await db.commit()

        logger.info(f"Successfully processed chat for conversation {request.conversation_id}")

        return ChatResponse(
            assistant_message=assistant_response,
            corrections=corrections,
            vocabulary_items=vocabulary_items,
        )

    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication_error",
                "message": "Invalid Anthropic API key configured on the server",
                "technical_details": str(e),
                "fix": "Server admin needs to set valid ANTHROPIC_API_KEY in .env file",
            },
        )
    except APIError as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "api_error",
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
