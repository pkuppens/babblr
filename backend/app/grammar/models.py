"""Pydantic models for grammar lessons.

These models represent grammar lesson data structures for API responses
and validation. They are separate from SQLAlchemy database models.
"""

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field

from app.models.cefr import CEFRLevel


class Exercise(BaseModel):
    """An exercise in a grammar lesson."""

    id: str = Field(..., description="Unique exercise identifier")
    type: str = Field(
        ..., description="Exercise type: 'multiple_choice', 'fill_in_blank', 'word_order', etc."
    )
    question: str = Field(..., description="Exercise question or prompt")
    options: Optional[list[str]] = Field(
        None, description="Answer options for multiple choice exercises"
    )
    correct_answer: Union[str, int, list] = Field(
        ...,
        description="Correct answer (string for fill-in, int index for multiple choice, list for word order)",
    )
    explanation: str = Field(..., description="Feedback explanation shown after answer submission")

    model_config = {"json_schema_extra": {"examples": []}}


class GrammarLesson(BaseModel):
    """A grammar lesson with content."""

    id: str = Field(..., description="Unique lesson identifier")
    title: str = Field(..., description="Lesson title")
    language: str = Field(..., description="Target language code (e.g., 'es', 'it')")
    level: CEFRLevel = Field(..., description="CEFR proficiency level")
    explanation: str = Field(..., description="Text explanation of the grammar rule")
    examples: list[str] = Field(
        ..., description="List of example sentences demonstrating the grammar rule"
    )
    exercises: list[Exercise] = Field(..., description="List of exercises for practice")
    topic_id: Optional[str] = Field(
        None, description="Link to vocabulary topic if grammar uses topic vocabulary"
    )

    model_config = {"json_schema_extra": {"examples": []}}


class LessonProgress(BaseModel):
    """User's progress on a specific lesson."""

    user_id: str = Field(..., description="User or device identifier")
    lesson_id: str = Field(..., description="Reference to grammar lesson")
    completed: bool = Field(default=False, description="Whether lesson is completed")
    mastery_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Mastery score from 0.0 (no mastery) to 1.0 (full mastery)",
    )
    last_reviewed: Optional[datetime] = Field(
        None, description="Timestamp of last review or practice session"
    )
    next_review: Optional[datetime] = Field(
        None, description="Scheduled next review date for spaced repetition"
    )

    model_config = {"json_schema_extra": {"examples": []}}


class TopicVocabularyProgress(BaseModel):
    """Progress on vocabulary used in grammar lessons for a topic."""

    user_id: str = Field(..., description="User or device identifier")
    topic_id: str = Field(..., description="Reference to vocabulary topic")
    language: str = Field(..., description="Target language code")
    vocabulary_mastery: dict[str, float] = Field(
        ...,
        description="Dictionary mapping vocabulary words to mastery scores (0.0-1.0)",
    )

    model_config = {"json_schema_extra": {"examples": []}}
