import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.db import get_db
from app.models.models import Conversation, Message
from app.models.schemas import ChatRequest, ChatResponse, InitialMessageRequest
from app.services.conversation_service import get_conversation_service
from app.services.llm.exceptions import LLMAuthenticationError, LLMError, RateLimitError
from app.utils.performance import async_perf_timer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/initial-message", response_model=ChatResponse)
async def generate_initial_message(
    request: InitialMessageRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an initial tutor message to start a conversation based on topic.
    This creates the first message from the tutor without requiring user input.
    """
    try:
        logger.info(
            f"Generating initial message for conversation {request.conversation_id} with topic {request.topic_id}"
        )

        # Verify conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Load topic information
        import json
        from pathlib import Path

        topics_file = Path(__file__).parent.parent / "static" / "topics.json"
        with open(topics_file, "r", encoding="utf-8") as f:
            topics_data = json.load(f)

        topic = None
        for t in topics_data.get("topics", []):
            if t.get("id") == request.topic_id:
                topic = t
                break

        if not topic:
            raise HTTPException(status_code=404, detail=f"Topic '{request.topic_id}' not found")

        # Get topic name and description in the target language
        topic_name = topic.get("names", {}).get(request.language.lower(), request.topic_id)
        topic_description = topic.get("descriptions", {}).get(request.language.lower(), "")

        # Get roleplay context in the target language
        roleplay_context = topic.get("roleplayContext", {}).get(request.language.lower())

        # Get conversation service
        conversation_service = get_conversation_service()

        # Generate initial message (returns message and translation)
        async with async_perf_timer("initial_message.generate_llm", logging.INFO):
            initial_message, translation = await conversation_service.generate_initial_message(
                language=request.language,
                difficulty_level=request.difficulty_level,
                topic=topic_name,
                topic_description=topic_description,
                roleplay_context=roleplay_context,
            )

        # Save assistant message (only the target language message, not translation)
        assistant_message = Message(
            conversation_id=request.conversation_id, role="assistant", content=initial_message
        )
        db.add(assistant_message)

        # Update conversation timestamp (UTC as per ADR-0001)
        conversation.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(assistant_message)  # Refresh to get the saved message with ID

        # Log what was actually saved to verify consistency
        logger.info(
            f"Saved initial assistant message (ID: {assistant_message.id}) for conversation {request.conversation_id}: "
            f"'{initial_message[:100]}...' (truncated)"
        )

        logger.info(
            f"Successfully generated initial message for conversation {request.conversation_id}"
        )

        return ChatResponse(
            assistant_message=initial_message, corrections=None, translation=translation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating initial message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to generate initial message",
                "technical_details": str(e),
            },
        )


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

        # Get conversation history BEFORE saving new user message
        # This ensures we don't include the current message twice (it will be added by generate_response)
        messages_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == request.conversation_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()

        # Convert messages to dict format, ensuring content is string (not Column)
        # Limit to recent messages to reduce LLM latency
        recent_messages = messages[-settings.conversation_max_history:] if len(messages) > settings.conversation_max_history else messages
        conversation_history = [
            {"role": str(msg.role), "content": str(msg.content)} for msg in recent_messages
        ]

        # Get conversation service (uses configured provider, defaults to Ollama)
        conversation_service = get_conversation_service()

        # Get topic information if conversation has a topic
        topic_name = "general conversation"
        roleplay_context = None
        if conversation.topic_id is not None:
            import json
            from pathlib import Path

            topics_file = Path(__file__).parent.parent / "static" / "topics.json"
            try:
                with open(topics_file, "r", encoding="utf-8") as f:
                    topics_data = json.load(f)

                for t in topics_data.get("topics", []):
                    if t.get("id") == conversation.topic_id:
                        topic_name = t.get("names", {}).get(
                            request.language.lower(), conversation.topic_id
                        )
                        roleplay_context = t.get("roleplayContext", {}).get(
                            request.language.lower()
                        )
                        break
            except Exception as e:
                logger.warning(f"Failed to load topic information: {e}")

        # First, correct the user's message if needed (only if below correction threshold)
        corrected_text = request.user_message
        corrections = None

        # Apply corrections if difficulty level is at or below configured threshold
        # "0" = no corrections, "A1" = only A1, "A2" = A1 and A2, etc.
        # CEFR levels in order: A1, A2, B1, B2, C1, C2
        cefr_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        try:
            user_level_index = cefr_order.index(request.difficulty_level)
            max_level_index = cefr_order.index(settings.correction_max_level) if settings.correction_max_level != "0" else -1
            should_correct = settings.correction_max_level != "0" and user_level_index <= max_level_index
        except ValueError:
            # If level not found, default to correcting
            should_correct = settings.correction_max_level != "0"

        if should_correct:
            async with async_perf_timer("chat.correct_text", logging.INFO):
                corrected_text, corrections = await conversation_service.correct_text(
                    request.user_message, request.language, request.difficulty_level
                )
        else:
            logger.debug(
                f"Skipping correction: difficulty_level={request.difficulty_level}, "
                f"max_level={settings.correction_max_level}"
            )

        # Save user message (with original text) - save BEFORE generating response
        # so it's in the database, but don't include it in conversation_history
        # since generate_response will add it
        async with async_perf_timer("chat.save_user_message", logging.DEBUG):
            user_message = Message(
                conversation_id=request.conversation_id,
                role="user",
                content=request.user_message,
                corrections=json.dumps(corrections) if corrections else None,
            )
            db.add(user_message)
            await db.commit()

        # Log conversation history for debugging
        logger.debug(
            f"Conversation history for {request.conversation_id}: {len(conversation_history)} messages "
            f"(before adding current user message)"
        )

        # Generate AI response with topic context and roleplay persona
        # Pass corrected_text as user_message - generate_response will add it to the history
        async with async_perf_timer("chat.generate_response_llm", logging.INFO):
            assistant_response = await conversation_service.generate_response(
                corrected_text if corrections else request.user_message,
                request.language,
                request.difficulty_level,
                conversation_history,
                topic=topic_name,
                roleplay_context=roleplay_context,
            )

        # Save assistant message
        assistant_message = Message(
            conversation_id=request.conversation_id, role="assistant", content=assistant_response
        )
        db.add(assistant_message)

        # Update conversation timestamp (UTC as per ADR-0001)
        conversation.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(assistant_message)  # Refresh to get the saved message with ID

        # Log what was actually saved to verify consistency
        logger.info(
            f"Saved assistant message (ID: {assistant_message.id}) for conversation {request.conversation_id}: "
            f"'{assistant_response[:100]}...' (truncated)"
        )

        logger.info(f"Successfully processed chat for conversation {request.conversation_id}")

        return ChatResponse(
            assistant_message=assistant_response,
            corrections=corrections,
            translation=None,  # Regular chat responses don't include translation
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
