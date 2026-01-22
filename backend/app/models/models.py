from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


class Conversation(Base):
    """Model for storing conversation sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False)
    difficulty_level = Column(
        String(20), default="A1"
    )  # Supports CEFR (A1-C2) or legacy (beginner/intermediate/advanced)
    topic_id = Column(
        String(100), nullable=True
    )  # Topic identifier from topics.json (e.g., "restaurant", "classroom")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Model for storing individual messages in a conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    audio_path = Column(String(255), nullable=True)  # Path to audio file if applicable
    corrections = Column(Text, nullable=True)  # JSON string of corrections
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Lesson(Base):
    """Model for storing structured lesson content for vocabulary, grammar, and listening."""

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False)
    lesson_type = Column(String(50), nullable=False)  # 'vocabulary', 'grammar', 'listening'
    title = Column(String(200), nullable=False)
    oneliner = Column(String(500), nullable=True)  # Brief one-sentence description for lesson cards
    description = Column(Text, nullable=True)  # Detailed description
    tutor_prompt = Column(Text, nullable=True)  # Extensive LLM prompt for content generation
    subject = Column(
        String(100), nullable=True
    )  # Subject/topic identifier (e.g., "present_ar_verbs", "shopping")
    topic_id = Column(String(100), nullable=True)  # Link to vocabulary topic if applicable
    difficulty_level = Column(String(20), nullable=False, default="A1")
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_accessed_at = Column(
        DateTime, nullable=True
    )  # For gamification streaks and recap decisions

    # Relationships
    lesson_items = relationship("LessonItem", back_populates="lesson", cascade="all, delete-orphan")
    lesson_progress = relationship(
        "LessonProgress", back_populates="lesson", cascade="all, delete-orphan"
    )
    grammar_rules = relationship(
        "GrammarRule", back_populates="lesson", cascade="all, delete-orphan"
    )


class LessonItem(Base):
    """Model for storing individual items (words, phrases, exercises) within a lesson."""

    __tablename__ = "lesson_items"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # 'word', 'phrase', 'exercise', 'example'
    content = Column(Text, nullable=False)
    item_metadata = Column(
        Text, nullable=True
    )  # JSON string (renamed from "metadata" to avoid SQLAlchemy conflict)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="lesson_items")


class LessonProgress(Base):
    """Model for tracking user progress through lessons."""

    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(
        String(20), nullable=False, default="not_started"
    )  # 'not_started', 'in_progress', 'completed'
    completion_percentage = Column(Float, nullable=False, default=0.0)
    mastery_score = Column(Float, nullable=True, default=None)  # 0.0-1.0 for adaptive scheduling
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="lesson_progress")


class GrammarRule(Base):
    """Model for storing grammar rules associated with lessons."""

    __tablename__ = "grammar_rules"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    examples = Column(Text, nullable=True)  # JSON array
    difficulty_level = Column(String(20), nullable=False, default="A1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="grammar_rules")


class Assessment(Base):
    """Model for storing assessment tests for proficiency evaluation."""

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False)
    assessment_type = Column(
        String(50), nullable=False
    )  # 'cefr_placement', 'vocabulary', 'grammar', 'comprehensive'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    assessment_questions = relationship(
        "AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan"
    )
    assessment_attempts = relationship(
        "AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentQuestion(Base):
    """Model for storing questions within an assessment."""

    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_type = Column(
        String(50), nullable=False
    )  # 'multiple_choice', 'fill_blank', 'translation', 'grammar'
    skill_category = Column(
        String(50), nullable=False, default="grammar"
    )  # 'grammar', 'vocabulary', 'listening' - for skill-based scoring
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON array for multiple choice
    points = Column(Integer, nullable=False, default=1)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_questions")


class AssessmentAttempt(Base):
    """Model for storing user attempts at assessments."""

    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    language = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)  # Percentage 0.0-100.0
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    answers_json = Column(Text, nullable=True)  # JSON object
    recommended_level = Column(
        String(20), nullable=True
    )  # Recommended CEFR level based on assessment (A1-C2)
    skill_scores_json = Column(
        Text, nullable=True
    )  # JSON array of {skill, score, total, correct} for skill breakdown

    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_attempts")


class UserLevel(Base):
    """Model for storing user proficiency level per language."""

    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False, unique=True)
    cefr_level = Column(String(20), nullable=False, default="A1")
    proficiency_score = Column(Float, nullable=False, default=0.0)  # 0.0-100.0
    assessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
