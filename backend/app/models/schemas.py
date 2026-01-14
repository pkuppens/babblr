from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    language: str = Field(..., description="Target language for learning")
    difficulty_level: str = Field(
        default="A1",
        description="Proficiency level: CEFR (A1, A2, B1, B2, C1, C2) or legacy (beginner, intermediate, advanced)",
    )
    topic_id: Optional[str] = Field(
        None, description="Topic identifier from topics.json (e.g., 'restaurant', 'classroom')"
    )


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    language: str
    difficulty_level: str
    topic_id: Optional[str] = None
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
        default="A1",
        description="Proficiency level: CEFR (A1, A2, B1, B2, C1, C2) or legacy (beginner, intermediate, advanced)",
    )


class InitialMessageRequest(BaseModel):
    """Schema for initial message request."""

    conversation_id: int = Field(..., description="ID of the conversation")
    language: str = Field(..., description="Target language (e.g., 'spanish', 'italian')")
    difficulty_level: str = Field(..., description="CEFR difficulty level (A1, A2, B1, B2, C1, C2)")
    topic_id: str = Field(..., description="Topic identifier from topics.json")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    assistant_message: str
    corrections: Optional[List[dict]] = None
    translation: Optional[str] = Field(
        None, description="Translation of the message in the user's native language"
    )


class TTSRequest(BaseModel):
    """Schema for text-to-speech request."""

    text: str
    language: str


# Lesson schemas
class LessonCreate(BaseModel):
    """Schema for creating a new lesson."""

    language: str = Field(..., description="Target language code")
    lesson_type: str = Field(..., description="Type: 'vocabulary' or 'grammar'")
    title: str = Field(..., description="Lesson title")
    description: Optional[str] = None
    difficulty_level: str = Field(default="A1", description="CEFR difficulty level")
    order_index: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Whether lesson is available")


class LessonResponse(BaseModel):
    """Schema for lesson response."""

    id: int
    language: str
    lesson_type: str
    title: str
    description: Optional[str]
    difficulty_level: str
    order_index: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# LessonProgress schemas
class LessonProgressCreate(BaseModel):
    """Schema for creating lesson progress."""

    lesson_id: int = Field(..., description="Reference to lesson")
    language: str = Field(..., description="Target language code")
    status: str = Field(
        default="not_started", description="Status: 'not_started', 'in_progress', 'completed'"
    )
    completion_percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion percentage"
    )
    mastery_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Mastery score (0.0-1.0) for adaptive scheduling"
    )


class LessonProgressResponse(BaseModel):
    """Schema for lesson progress response."""

    id: int
    lesson_id: int
    language: str
    status: str
    completion_percentage: float
    mastery_score: Optional[float] = None
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Assessment schemas
class AssessmentCreate(BaseModel):
    """Schema for creating a new assessment."""

    language: str = Field(..., description="Target language code")
    assessment_type: str = Field(
        ..., description="Type: 'cefr_placement', 'vocabulary', 'grammar', 'comprehensive'"
    )
    title: str = Field(..., description="Assessment title")
    description: Optional[str] = None
    difficulty_level: str = Field(..., description="Target CEFR level")
    duration_minutes: Optional[int] = Field(None, gt=0, description="Estimated duration in minutes")
    is_active: bool = Field(default=True, description="Whether assessment is available")


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""

    id: int
    language: str
    assessment_type: str
    title: str
    description: Optional[str]
    difficulty_level: str
    duration_minutes: Optional[int]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# UserLevel schemas
class UserLevelCreate(BaseModel):
    """Schema for creating user level."""

    language: str = Field(..., description="Target language code")
    cefr_level: str = Field(default="A1", description="Current CEFR level")
    proficiency_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Proficiency score")


class UserLevelResponse(BaseModel):
    """Schema for user level response."""

    id: int
    language: str
    cefr_level: str
    proficiency_score: float
    assessed_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
