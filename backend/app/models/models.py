from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


class Conversation(Base):
    """Model for storing conversation sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    vocabulary_items = relationship(
        "VocabularyItem", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """Model for storing individual messages in a conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    audio_path = Column(String(255), nullable=True)  # Path to audio file if applicable
    corrections = Column(Text, nullable=True)  # JSON string of corrections
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class VocabularyItem(Base):
    """Model for storing vocabulary items learned during conversations."""

    __tablename__ = "vocabulary_items"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    word = Column(String(100), nullable=False)
    translation = Column(String(100), nullable=False)
    context = Column(Text, nullable=True)  # Sentence where it was used
    difficulty = Column(String(20), default="beginner")
    times_encountered = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="vocabulary_items")
