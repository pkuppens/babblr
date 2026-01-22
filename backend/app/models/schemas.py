from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    speed: float = 1.0  # Playback speed multiplier (0.5 to 2.0, default 1.0)


# Lesson schemas
class LessonCreate(BaseModel):
    """Schema for creating a new lesson."""

    language: str = Field(..., description="Target language code")
    lesson_type: str = Field(..., description="Type: 'vocabulary', 'grammar', or 'listening'")
    title: str = Field(..., description="Lesson title")
    title_en: Optional[str] = Field(None, description="English title for hover help")
    oneliner: Optional[str] = Field(
        None, description="Brief one-sentence description for lesson cards"
    )
    oneliner_en: Optional[str] = Field(None, description="English oneliner for hover help")
    description: Optional[str] = None
    description_en: Optional[str] = Field(None, description="English description for hover help")
    tutor_prompt: Optional[str] = Field(
        None, description="Extensive LLM prompt for content generation"
    )
    subject: Optional[str] = Field(
        None, description="Subject/topic identifier (e.g., 'present_ar_verbs', 'shopping')"
    )
    topic_id: Optional[str] = Field(None, description="Link to vocabulary topic if applicable")
    difficulty_level: str = Field(default="A1", description="CEFR difficulty level")
    order_index: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Whether lesson is available")


class LessonResponse(BaseModel):
    """Schema for lesson response."""

    id: int
    language: str
    lesson_type: str
    title: str
    title_en: Optional[str]
    oneliner: Optional[str]
    oneliner_en: Optional[str]
    description: Optional[str]
    description_en: Optional[str]
    tutor_prompt: Optional[str]
    subject: Optional[str]
    topic_id: Optional[str]
    difficulty_level: str
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class LessonSummary(BaseModel):
    """Schema for lesson summary in list responses."""

    id: int
    title: str
    title_en: Optional[str] = None
    oneliner: Optional[str]
    oneliner_en: Optional[str] = None
    lesson_type: str
    subject: Optional[str]
    difficulty_level: str
    completed: bool = False
    mastery_score: float = 0.0
    last_accessed_at: Optional[datetime] = None

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


class UserLevelUpdate(BaseModel):
    """Schema for updating user level."""

    cefr_level: str = Field(..., description="CEFR level (A1-C2)")
    proficiency_score: float = Field(..., ge=0.0, le=100.0, description="Score percentage")


# ============================================================================
# CEFR Assessment Schemas
# ============================================================================


class SkillCategory(str, Enum):
    """Valid skill categories for assessments."""

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    LISTENING = "listening"
    # Future: SPEAKING = "speaking"


class SkillScore(BaseModel):
    """Score for a specific skill category."""

    skill: str = Field(..., description="Skill category name")
    score: float = Field(..., ge=0.0, le=100.0, description="Percentage score")
    total: int = Field(..., ge=0, description="Total questions in this category")
    correct: int = Field(..., ge=0, description="Correct answers in this category")

    @model_validator(mode="after")
    def validate_correct_not_greater_than_total(self) -> "SkillScore":
        """Validate that correct answers don't exceed total."""
        if self.correct > self.total:
            raise ValueError("correct cannot be greater than total")
        return self


class AssessmentQuestionResponse(BaseModel):
    """Schema for assessment question response (without correct answer for test-takers)."""

    id: int
    assessment_id: int
    question_type: str
    skill_category: str
    question_text: str
    options: Optional[List[str]] = None
    points: int
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class AssessmentListResponse(BaseModel):
    """Schema for assessment list response - includes skill categories and question count."""

    id: int
    language: str
    assessment_type: str
    title: str
    description: Optional[str]
    difficulty_level: str
    duration_minutes: Optional[int]
    skill_categories: List[str] = Field(
        default_factory=list, description="Skill categories covered by this assessment"
    )
    is_active: bool
    created_at: datetime
    question_count: int = Field(default=0, description="Number of questions")

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetailResponse(AssessmentListResponse):
    """Schema for assessment detail response - includes questions (without answers)."""

    questions: List[AssessmentQuestionResponse] = Field(
        default_factory=list, description="Assessment questions without correct answers"
    )


class AttemptCreate(BaseModel):
    """Schema for submitting assessment answers."""

    answers: Dict[str, str] = Field(..., description="Question ID to selected answer mapping")


class QuestionAnswer(BaseModel):
    """Schema for a question answer in review."""

    question_id: int
    question_text: str
    skill_category: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    options: Optional[List[str]] = None


class AttemptResultResponse(BaseModel):
    """Schema for assessment attempt result with skill breakdown."""

    id: int
    assessment_id: int
    language: str
    score: float = Field(..., ge=0.0, le=100.0)
    recommended_level: str
    skill_scores: List[SkillScore]
    total_questions: int
    correct_answers: int
    started_at: datetime
    completed_at: Optional[datetime]
    practice_recommendations: List[str] = Field(
        default_factory=list, description="Suggested areas to practice"
    )
    question_answers: Optional[List[QuestionAnswer]] = Field(
        default=None, description="Question-by-question answers for review"
    )

    model_config = ConfigDict(from_attributes=True)


class AttemptSummary(BaseModel):
    """Summary of an assessment attempt for history list."""

    id: int
    assessment_id: int
    assessment_title: str
    language: str
    score: float
    recommended_level: Optional[str]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Progress Dashboard Schemas
# ============================================================================


class VocabularyProgress(BaseModel):
    """Schema for vocabulary lesson progress stats."""

    completed: int = Field(..., ge=0, description="Number of completed lessons")
    in_progress: int = Field(..., ge=0, description="Number of in-progress lessons")
    total: int = Field(..., ge=0, description="Total available lessons")
    last_activity: Optional[datetime] = Field(None, description="Most recent activity timestamp")


class GrammarProgress(BaseModel):
    """Schema for grammar lesson progress stats."""

    completed: int = Field(..., ge=0, description="Number of completed lessons")
    in_progress: int = Field(..., ge=0, description="Number of in-progress lessons")
    total: int = Field(..., ge=0, description="Total available lessons")
    last_activity: Optional[datetime] = Field(None, description="Most recent activity timestamp")


class AssessmentProgress(BaseModel):
    """Schema for assessment progress stats."""

    latest_score: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Score from most recent assessment"
    )
    recommended_level: Optional[str] = Field(
        None, description="Recommended CEFR level from assessment"
    )
    skill_scores: Optional[List[SkillScore]] = Field(
        None, description="Per-skill breakdown from latest assessment"
    )
    last_attempt: Optional[datetime] = Field(None, description="When the last assessment was taken")


class ProgressSummary(BaseModel):
    """Schema for complete progress summary response."""

    language: str = Field(..., description="Target language code")
    vocabulary: VocabularyProgress = Field(..., description="Vocabulary lesson progress")
    grammar: GrammarProgress = Field(..., description="Grammar lesson progress")
    assessment: AssessmentProgress = Field(..., description="Assessment progress")
