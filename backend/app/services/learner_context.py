"""Collect learner history (recent vocabulary, common mistakes) for the tutor prompt."""

import json
import logging
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Conversation, Lesson, LessonItem, LessonProgress, Message

logger = logging.getLogger(__name__)

MAX_VOCAB = 10
MAX_MISTAKES = 5
_MESSAGE_SCAN_LIMIT = 100
_VOCAB_SCAN_LIMIT = 50


async def get_recent_vocab(db: AsyncSession, language: str, limit: int = MAX_VOCAB) -> list[str]:
    """Return words from vocabulary lessons that the learner opened, newest first."""
    result = await db.execute(
        select(LessonItem.content)
        .join(Lesson, Lesson.id == LessonItem.lesson_id)
        .join(LessonProgress, LessonProgress.lesson_id == Lesson.id)
        .where(
            Lesson.lesson_type == "vocabulary",
            LessonItem.item_type == "word",
            func.lower(LessonProgress.language) == language.lower(),
        )
        .order_by(LessonProgress.last_accessed_at.desc(), LessonItem.order_index)
        .limit(_VOCAB_SCAN_LIMIT)
    )
    words: list[str] = []
    for (content,) in result.all():
        word = (content or "").strip()
        if word and word not in words:
            words.append(word)
        if len(words) >= limit:
            break
    return words


async def get_common_mistakes(
    db: AsyncSession, language: str, limit: int = MAX_MISTAKES
) -> list[str]:
    """Return the most frequent correction explanations from recent user messages."""
    result = await db.execute(
        select(Message.corrections)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(
            Message.role == "user",
            Message.corrections.is_not(None),
            func.lower(Conversation.language) == language.lower(),
        )
        .order_by(Message.id.desc())
        .limit(_MESSAGE_SCAN_LIMIT)
    )
    counts: Counter[str] = Counter()
    for (raw,) in result.all():
        try:
            corrections = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        if not isinstance(corrections, list):
            continue
        for item in corrections:
            if not isinstance(item, dict):
                continue
            label = str(item.get("explanation") or "").strip()
            if not label and item.get("original") and item.get("corrected"):
                label = f"{item['original']} -> {item['corrected']}"
            if label:
                counts[label] += 1
    return [label for label, _ in counts.most_common(limit)]


async def get_learner_context(
    db: AsyncSession, language: str
) -> tuple[list[str] | None, list[str] | None]:
    """Return (recent_vocab, common_mistakes). Empty results become None.

    Failures never block a chat turn: the tutor then gets the plain prompt.
    """
    try:
        vocab = await get_recent_vocab(db, language)
        mistakes = await get_common_mistakes(db, language)
    except Exception as e:
        logger.warning(f"Could not load learner context: {e}")
        return None, None
    return vocab or None, mistakes or None
