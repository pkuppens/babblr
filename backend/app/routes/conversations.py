from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.models import Conversation, Message, VocabularyItem
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
    VocabularyItemResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conversation session."""
    new_conversation = Conversation(
        language=conversation.language, difficulty_level=conversation.difficulty_level
    )
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific conversation."""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all conversations."""
    result = await db.execute(
        select(Conversation).offset(skip).limit(limit).order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get all messages in a conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages


@router.get("/{conversation_id}/vocabulary", response_model=List[VocabularyItemResponse])
async def get_conversation_vocabulary(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get vocabulary items from a conversation."""
    result = await db.execute(
        select(VocabularyItem).where(VocabularyItem.conversation_id == conversation_id)
    )
    vocabulary = result.scalars().all()
    return vocabulary


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a conversation and all its messages."""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation deleted successfully"}
