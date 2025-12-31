from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.database.db import get_db
from app.models.models import Conversation, Message
from app.models.schemas import ChatRequest, ChatResponse
from app.services.claude_service import claude_service
import tempfile
import os
import json


# Configure timezone (defaults to Europe/Amsterdam, configurable via env)
DEFAULT_TIMEZONE = os.getenv("TIMEZONE", "Europe/Amsterdam")


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process a chat message and get AI tutor response.
    Includes error correction and vocabulary extraction.
    """
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
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    # First, correct the user's message if needed
    corrected_text, corrections = await claude_service.correct_text(
        request.user_message,
        request.language,
        request.difficulty_level
    )
    
    # Save user message (with original text)
    user_message = Message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.user_message,
        corrections=json.dumps(corrections) if corrections else None
    )
    db.add(user_message)
    await db.commit()
    
    # Generate AI response
    assistant_response, vocabulary_items = await claude_service.generate_response(
        corrected_text if corrections else request.user_message,
        request.language,
        request.difficulty_level,
        conversation_history
    )
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=assistant_response
    )
    db.add(assistant_message)
    
    # Update conversation timestamp using configured timezone
    tz = ZoneInfo(DEFAULT_TIMEZONE)
    conversation.updated_at = datetime.now(tz).replace(tzinfo=None)
    
    await db.commit()
    
    return ChatResponse(
        assistant_message=assistant_response,
        corrections=corrections,
        vocabulary_items=vocabulary_items
    )
