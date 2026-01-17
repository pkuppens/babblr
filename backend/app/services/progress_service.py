"""
Progress service for aggregating learning progress data.

Provides functions to get vocabulary, grammar, and assessment progress stats.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AssessmentAttempt, Lesson, LessonProgress, UserLevel
from app.models.schemas import AssessmentProgress, GrammarProgress, VocabularyProgress

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


async def get_assessment_progress(
    db: AsyncSession,
    language: str,
) -> AssessmentProgress:
    """
    Get assessment progress stats for a language.

    Args:
        db: Database session
        language: Target language code

    Returns:
        AssessmentProgress with latest_score, recommended_level, and last_attempt
    """
    # Get most recent assessment attempt for this language
    latest_attempt_result = await db.execute(
        select(AssessmentAttempt)
        .where(AssessmentAttempt.language == language)
        .order_by(AssessmentAttempt.completed_at.desc())
        .limit(1)
    )
    latest_attempt = latest_attempt_result.scalar_one_or_none()

    # Get user level for recommended CEFR level
    user_level_result = await db.execute(select(UserLevel).where(UserLevel.language == language))
    user_level = user_level_result.scalar_one_or_none()

    # Extract data from results
    latest_score = latest_attempt.score if latest_attempt else None
    last_attempt = latest_attempt.completed_at if latest_attempt else None
    recommended_level = user_level.cefr_level if user_level else None

    logger.debug(
        f"Assessment progress for {language}: score={latest_score}, "
        f"level={recommended_level}, last_attempt={last_attempt}"
    )

    return AssessmentProgress(
        latest_score=latest_score,
        recommended_level=recommended_level,
        skill_scores=None,  # Skill breakdown to be added when assessment feature is enhanced
        last_attempt=last_attempt,
    )
