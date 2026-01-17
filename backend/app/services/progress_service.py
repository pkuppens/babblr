"""
Progress service for aggregating learning progress data.

Provides functions to get vocabulary, grammar, and assessment progress stats.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Lesson, LessonProgress
from app.models.schemas import GrammarProgress, VocabularyProgress

logger = logging.getLogger(__name__)


async def get_vocabulary_progress(
    db: AsyncSession,
    language: str,
) -> VocabularyProgress:
    """
    Get vocabulary lesson progress stats for a language.

    Args:
        db: Database session
        language: Target language code

    Returns:
        VocabularyProgress with completed/in_progress/total counts and last_activity
    """
    # Get total vocabulary lessons for this language
    total_result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.language == language,
            Lesson.lesson_type == "vocabulary",
            Lesson.is_active == True,  # noqa: E712
        )
    )
    total = total_result.scalar() or 0

    # Get completed count
    completed_result = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            LessonProgress.status == "completed",
            Lesson.lesson_type == "vocabulary",
        )
    )
    completed = completed_result.scalar() or 0

    # Get in_progress count
    in_progress_result = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            LessonProgress.status == "in_progress",
            Lesson.lesson_type == "vocabulary",
        )
    )
    in_progress = in_progress_result.scalar() or 0

    # Get most recent activity
    last_activity_result = await db.execute(
        select(func.max(LessonProgress.last_accessed_at))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            Lesson.lesson_type == "vocabulary",
        )
    )
    last_activity = last_activity_result.scalar()

    logger.debug(
        f"Vocabulary progress for {language}: {completed} completed, "
        f"{in_progress} in progress, {total} total"
    )

    return VocabularyProgress(
        completed=completed,
        in_progress=in_progress,
        total=total,
        last_activity=last_activity,
    )


async def get_grammar_progress(
    db: AsyncSession,
    language: str,
) -> GrammarProgress:
    """
    Get grammar lesson progress stats for a language.

    Args:
        db: Database session
        language: Target language code

    Returns:
        GrammarProgress with completed/in_progress/total counts and last_activity
    """
    # Get total grammar lessons for this language
    total_result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.language == language,
            Lesson.lesson_type == "grammar",
            Lesson.is_active == True,  # noqa: E712
        )
    )
    total = total_result.scalar() or 0

    # Get completed count
    completed_result = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            LessonProgress.status == "completed",
            Lesson.lesson_type == "grammar",
        )
    )
    completed = completed_result.scalar() or 0

    # Get in_progress count
    in_progress_result = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            LessonProgress.status == "in_progress",
            Lesson.lesson_type == "grammar",
        )
    )
    in_progress = in_progress_result.scalar() or 0

    # Get most recent activity
    last_activity_result = await db.execute(
        select(func.max(LessonProgress.last_accessed_at))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .where(
            LessonProgress.language == language,
            Lesson.lesson_type == "grammar",
        )
    )
    last_activity = last_activity_result.scalar()

    logger.debug(
        f"Grammar progress for {language}: {completed} completed, "
        f"{in_progress} in progress, {total} total"
    )

    return GrammarProgress(
        completed=completed,
        in_progress=in_progress,
        total=total,
        last_activity=last_activity,
    )
