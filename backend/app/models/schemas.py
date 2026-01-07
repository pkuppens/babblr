from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    language: str = Field(..., description="Target language for learning")
    difficulty_level: str = Field(
        default="beginner",
        description="Proficiency level: CEFR (A1, A2, B1, B2, C1, C2) or legacy (beginner, intermediate, advanced)",
    )


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    language: str
    difficulty_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    conversation_id: int
    role: str = Field(..., description="Role: user or assistant")
    content: str
    audio_path: Optional[str] = None
    corrections: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    conversation_id: int
    role: str
    content: str
    audio_path: Optional[str] = None
    corrections: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TranscriptionRequest(BaseModel):
    """Schema for transcription request."""

    conversation_id: int
    language: str


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""

    text: str
    language: str
    confidence: float
    duration: float
    corrections: Optional[List[dict]] = None


class ChatRequest(BaseModel):
    """Schema for chat request."""

    conversation_id: int
    user_message: str
    language: str
    difficulty_level: str = Field(
        default="beginner",
        description="Proficiency level: CEFR (A1, A2, B1, B2, C1, C2) or legacy (beginner, intermediate, advanced)",
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""

    assistant_message: str
    corrections: Optional[List[dict]] = None
    vocabulary_items: Optional[List[dict]] = None


class VocabularyItemResponse(BaseModel):
    """Schema for vocabulary item response."""

    id: int
    word: str
    translation: str
    context: Optional[str] = None
    difficulty: str
    times_encountered: int
    created_at: datetime
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)


class TTSRequest(BaseModel):
    """Schema for text-to-speech request."""

    text: str
    language: str
