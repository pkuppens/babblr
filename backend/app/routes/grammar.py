"""Grammar lesson endpoints for structured grammar practice with spaced repetition."""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.grammar.models import GrammarLesson
from app.grammar.schemas import ExerciseResult, SubmitExerciseRequest
from app.grammar.service import parse_exercise_from_item, validate_exercise_answer
from app.models.cefr import CEFRLevel
from app.models.models import GrammarRule, Lesson, LessonItem, LessonProgress
from app.models.schemas import (
    LessonProgressCreate,
    LessonProgressResponse,
    LessonResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grammar", tags=["grammar"])

# Language-specific success messages for correct answers
SUCCESS_MESSAGES = {
    "es": "¡Correcto!",
    "en": "Correct!",
    "it": "Corretto!",
    "fr": "Correct !",
    "de": "Richtig!",
    "nl": "Correct!",
}


def calculate_next_review_date(mastery_score: Optional[float], last_reviewed: datetime) -> datetime:
    """Calculate next review date based on mastery score (simple spaced repetition).

    Higher mastery = longer intervals between reviews.
    Simple algorithm:
    - mastery >= 0.9: 14 days (2 weeks)
    - mastery >= 0.7: 7 days (1 week)
    - mastery >= 0.5: 3 days
    - mastery < 0.5: 1 day (daily)

    Args:
        mastery_score: Mastery score from 0.0 to 1.0 (None if not set)
        last_reviewed: Last review timestamp

    Returns:
        Next review date
    """
    if mastery_score is None:
        mastery_score = 0.5  # Default for new lessons

    # Simple intervals based on mastery
    if mastery_score >= 0.9:
        interval_days = 14  # 2 weeks
    elif mastery_score >= 0.7:
        interval_days = 7  # 1 week
    elif mastery_score >= 0.5:
        interval_days = 3  # 3 days
    else:
        interval_days = 1  # Daily

    return last_reviewed + timedelta(days=interval_days)


@router.get("/lessons", response_model=List[LessonResponse])
async def list_lessons(
    language: str = Query(..., description="Target language code (e.g., 'es', 'it', 'de')"),
    level: Optional[str] = Query(None, description="CEFR level filter (A1, A2, B1, B2, C1, C2)"),
    type: Optional[str] = Query(
        None, description="Lesson type filter: 'new', 'practice', 'test', 'recap'"
    ),
    db: AsyncSession = Depends(get_db),
):
    """List grammar lessons for a given language and optional level/type.

    Returns lessons ordered by order_index, filtered by language, level, and type.
    Only returns active lessons.
    """
    try:
        # Build query
        query = select(Lesson).where(
            Lesson.language == language,
            Lesson.lesson_type == "grammar",
            Lesson.is_active == True,  # noqa: E712
        )

        # Apply level filter if provided
        if level:
            query = query.where(Lesson.difficulty_level == level.upper())

        # Note: Type filtering would require checking lesson items or metadata
        # For v1, we'll return all grammar lessons and filter by type in the response
        # or use a separate metadata field. For now, we'll skip type filtering at DB level.

        # Order by order_index, then by created_at
        query = query.order_by(Lesson.order_index, Lesson.created_at)

        result = await db.execute(query)
        lessons = result.scalars().all()

        # Filter by type if specified (check metadata in lesson items)
        if type:
            filtered_lessons = []
            for lesson in lessons:
                # Check if lesson has metadata indicating its type
                items_result = await db.execute(
                    select(LessonItem).where(
                        LessonItem.lesson_id == lesson.id, LessonItem.item_type == "metadata"
                    )
                )
                metadata_items = items_result.scalars().all()
                lesson_type = None
                for item in metadata_items:
                    try:
                        metadata = json.loads(str(item.content))  # type: ignore[arg-type]
                        lesson_type = metadata.get("lesson_type")
                        break
                    except (json.JSONDecodeError, KeyError):
                        continue

                # If no metadata found, assume "new" for new lessons
                if not lesson_type:
                    # Check if lesson has progress - if completed, it could be a recap candidate
                    progress_result = await db.execute(
                        select(LessonProgress).where(
                            LessonProgress.lesson_id == lesson.id,
                            LessonProgress.language == language,
                        )
                    )
                    progress = progress_result.scalar_one_or_none()
                    if progress and progress.status == "completed":  # type: ignore[truthy-function]
                        lesson_type = "recap"
                    else:
                        lesson_type = "new"

                if lesson_type == type:
                    filtered_lessons.append(lesson)
            lessons = filtered_lessons

        logger.info(
            f"Found {len(lessons)} grammar lessons for language={language}, level={level}, type={type}"
        )

        return list(lessons)

    except Exception as e:
        logger.error(f"Error listing grammar lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list lessons: {str(e)}")


@router.get("/lessons/{lesson_id}", response_model=GrammarLesson)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific grammar lesson with all its content.

    Returns the lesson with explanation, examples, and exercises in GrammarLesson format.
    """
    try:
        # Get lesson
        result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")

        if lesson.lesson_type != "grammar":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400, detail=f"Lesson {lesson_id} is not a grammar lesson"
            )

        if not lesson.is_active:  # type: ignore[comparison-overlap]
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} is not active")

        # Get grammar rules for explanation
        rules_result = await db.execute(
            select(GrammarRule).where(GrammarRule.lesson_id == lesson_id)
        )
        rules = rules_result.scalars().all()

        # Build explanation from rules
        explanation_parts = []
        for rule in rules:
            if rule.description:  # type: ignore[truthy-function]
                explanation_parts.append(rule.description)
        explanation = "\n\n".join(explanation_parts) or (
            lesson.description or ""  # type: ignore[assignment]
        )

        # Get lesson items (examples, exercises)
        items_result = await db.execute(
            select(LessonItem)
            .where(LessonItem.lesson_id == lesson_id)
            .order_by(LessonItem.order_index)
        )
        items = items_result.scalars().all()

        # Process items to extract examples and exercises
        examples = []
        exercises = []
        for item in items:
            if item.item_type == "example":  # type: ignore[comparison-overlap]
                try:
                    example_data = json.loads(str(item.content))  # type: ignore[arg-type]
                    # Extract text for examples list
                    if "text" in example_data:
                        examples.append(example_data["text"])
                    elif isinstance(example_data, str):
                        examples.append(example_data)
                except (json.JSONDecodeError, KeyError):
                    # If content is not JSON, treat as plain text
                    examples.append(str(item.content))
            elif item.item_type == "exercise":  # type: ignore[comparison-overlap]
                exercise = parse_exercise_from_item(item)
                if exercise:
                    exercises.append(exercise)

        # Get CEFR level
        try:
            level = CEFRLevel(lesson.difficulty_level)  # type: ignore[arg-type]
        except ValueError:
            level = CEFRLevel.A1  # Default fallback

        grammar_lesson = GrammarLesson(
            id=str(lesson.id),  # type: ignore[attr-defined]
            title=lesson.title,  # type: ignore[attr-defined]
            language=lesson.language,  # type: ignore[attr-defined]
            level=level,
            explanation=explanation,
            examples=examples,
            exercises=exercises,
            topic_id=lesson.topic_id,  # type: ignore[attr-defined]
        )

        logger.info(
            f"Retrieved grammar lesson {lesson_id} with {len(rules)} rules, "
            f"{len(examples)} examples, {len(exercises)} exercises"
        )

        return grammar_lesson

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting grammar lesson {lesson_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get lesson: {str(e)}")


@router.post("/exercises/{exercise_id}/submit", response_model=ExerciseResult)
async def submit_exercise(
    exercise_id: int,
    request: SubmitExerciseRequest,
    user_id: Optional[str] = Query(None, description="User ID for progress tracking"),
    db: AsyncSession = Depends(get_db),
):
    """Submit an exercise answer and get feedback.

    Validates the answer and updates user progress if user_id is provided.
    """
    try:
        # Get exercise from lesson items
        result = await db.execute(
            select(LessonItem).where(
                LessonItem.id == exercise_id, LessonItem.item_type == "exercise"
            )
        )
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail=f"Exercise {exercise_id} not found")

        # Parse exercise
        exercise = parse_exercise_from_item(item)
        if not exercise:
            raise HTTPException(
                status_code=400, detail=f"Exercise {exercise_id} could not be parsed"
            )

        # Validate answer
        is_correct = validate_exercise_answer(exercise, request.answer)

        # Get lesson to determine language for feedback message
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == item.lesson_id))
        lesson = lesson_result.scalar_one_or_none()

        # Get language-aware success message
        lesson_language: str = str(lesson.language) if lesson else "en"
        success_message = SUCCESS_MESSAGES.get(lesson_language, SUCCESS_MESSAGES["en"])

        # Update progress if user_id provided
        if user_id and lesson:
            # Get or create progress
            progress_result = await db.execute(
                select(LessonProgress).where(
                    LessonProgress.lesson_id == lesson.id,  # type: ignore[attr-defined]
                    LessonProgress.language == lesson.language,  # type: ignore[attr-defined]
                )
            )
            progress = progress_result.scalar_one_or_none()

            now = datetime.now(timezone.utc)
            mastery_delta = 0.05 if is_correct else -0.02

            if progress:
                # Update existing progress
                current_mastery = progress.mastery_score or 0.0  # type: ignore[attr-defined]
                new_mastery = max(0.0, min(1.0, current_mastery + mastery_delta))
                progress.mastery_score = new_mastery  # type: ignore[assignment]
                progress.last_accessed_at = now  # type: ignore[assignment]
            else:
                # Create new progress
                new_progress = LessonProgress(
                    lesson_id=lesson.id,  # type: ignore[attr-defined]
                    language=lesson.language,  # type: ignore[attr-defined]
                    status="in_progress",
                    completion_percentage=0.0,
                    mastery_score=max(0.0, min(1.0, mastery_delta)),
                    started_at=now,
                    last_accessed_at=now,
                )
                db.add(new_progress)

            await db.commit()

        # Build response
        return ExerciseResult(
            is_correct=is_correct,
            correct_answer=exercise.correct_answer,
            explanation=exercise.explanation if not is_correct else success_message,
            mastery_delta=0.05 if is_correct else -0.02,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting exercise {exercise_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit exercise: {str(e)}")


@router.post("/progress", response_model=LessonProgressResponse)
async def create_progress(
    progress: LessonProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create or update grammar lesson progress for a user/device.

    If progress already exists for this lesson_id and language, it will be updated.
    Otherwise, a new progress record is created.
    Tracks mastery score for adaptive spaced repetition scheduling.
    """
    try:
        # Validate lesson exists
        result = await db.execute(select(Lesson).where(Lesson.id == progress.lesson_id))
        lesson = result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {progress.lesson_id} not found")

        if lesson.lesson_type != "grammar":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400,
                detail=f"Lesson {progress.lesson_id} is not a grammar lesson",
            )

        # Validate status
        valid_statuses = ["not_started", "in_progress", "completed"]
        if progress.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{progress.status}'. Must be one of: {valid_statuses}",
            )

        # Check if progress already exists
        existing_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.lesson_id == progress.lesson_id,
                LessonProgress.language == progress.language,
            )
        )
        existing = existing_result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            # Update existing progress
            existing.status = progress.status  # type: ignore[assignment]
            existing.completion_percentage = progress.completion_percentage  # type: ignore[assignment]
            existing.last_accessed_at = now  # type: ignore[assignment]

            # Update mastery score if provided
            if progress.mastery_score is not None:
                existing.mastery_score = progress.mastery_score  # type: ignore[assignment]

            # Update started_at if transitioning from not_started
            if existing.status == "in_progress" and existing.started_at is None:  # type: ignore[comparison-overlap]
                existing.started_at = now  # type: ignore[assignment]

            # Update completed_at if status is completed
            if existing.status == "completed":  # type: ignore[comparison-overlap]
                existing.completed_at = now  # type: ignore[assignment]
            elif existing.status != "completed" and existing.completed_at is not None:  # type: ignore[comparison-overlap]
                # Reset completed_at if status changed from completed
                existing.completed_at = None  # type: ignore[assignment]

            await db.commit()
            await db.refresh(existing)

            logger.info(
                f"Updated grammar progress for lesson {progress.lesson_id}, language {progress.language}: "
                f"status={progress.status}, completion={progress.completion_percentage}%, "
                f"mastery={progress.mastery_score}"
            )

            return existing
        else:
            # Create new progress
            new_progress = LessonProgress(
                lesson_id=progress.lesson_id,
                language=progress.language,
                status=progress.status,
                completion_percentage=progress.completion_percentage,
                mastery_score=progress.mastery_score,
                started_at=now if progress.status == "in_progress" else None,
                completed_at=now if progress.status == "completed" else None,
                last_accessed_at=now,
            )

            db.add(new_progress)
            await db.commit()
            await db.refresh(new_progress)

            logger.info(
                f"Created grammar progress for lesson {progress.lesson_id}, language {progress.language}: "
                f"status={progress.status}, completion={progress.completion_percentage}%, "
                f"mastery={progress.mastery_score}"
            )

            return new_progress

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating grammar progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")


@router.get("/recaps", response_model=List[LessonResponse])
async def get_recaps(
    language: str = Query(..., description="Target language code"),
    level: Optional[str] = Query(None, description="CEFR level filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get grammar lessons due for review based on spaced repetition.

    Returns lessons that are due for recap based on:
    - Last reviewed date
    - Mastery score (adaptive intervals)
    - Completion status (only completed lessons are eligible for recaps)

    Higher mastery scores result in longer intervals between reviews.
    """
    try:
        now = datetime.now(timezone.utc)

        # Get all completed grammar lessons for this language/level
        query = (
            select(Lesson, LessonProgress)
            .join(
                LessonProgress,
                and_(
                    LessonProgress.lesson_id == Lesson.id,
                    LessonProgress.language == language,
                    LessonProgress.status == "completed",
                ),
            )
            .where(
                Lesson.language == language,
                Lesson.lesson_type == "grammar",
                Lesson.is_active == True,  # noqa: E712
            )
        )

        if level:
            query = query.where(Lesson.difficulty_level == level.upper())

        result = await db.execute(query)
        rows = result.all()

        # Filter lessons that are due for review
        due_lessons = []
        for lesson, progress in rows:
            # Handle case where mastery_score column might not exist yet (defensive)
            mastery = getattr(progress, "mastery_score", None)  # type: ignore[attr-defined]
            last_reviewed = progress.last_accessed_at  # type: ignore[attr-defined]

            if last_reviewed:
                next_review_date = calculate_next_review_date(mastery, last_reviewed)
                if now >= next_review_date:
                    due_lessons.append(lesson)

        # Order by how overdue they are (most overdue first)
        due_lessons_with_dates = []
        for lesson in due_lessons:
            progress_result = await db.execute(
                select(LessonProgress).where(
                    LessonProgress.lesson_id == lesson.id,
                    LessonProgress.language == language,
                )
            )
            progress = progress_result.scalar_one_or_none()
            if progress and progress.last_accessed_at:  # type: ignore[truthy-function]
                # Handle case where mastery_score column might not exist yet (defensive)
                mastery = getattr(progress, "mastery_score", None)  # type: ignore[attr-defined]
                next_review = calculate_next_review_date(mastery, progress.last_accessed_at)  # type: ignore[arg-type]
                days_overdue = (now - next_review).days
                due_lessons_with_dates.append((days_overdue, lesson))

        # Sort by days overdue (descending)
        due_lessons_with_dates.sort(key=lambda x: x[0], reverse=True)
        due_lessons = [lesson for _, lesson in due_lessons_with_dates]

        logger.info(
            f"Found {len(due_lessons)} grammar lessons due for recap "
            f"for language={language}, level={level}"
        )

        return due_lessons

    except Exception as e:
        logger.error(f"Error getting grammar recaps: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recaps: {str(e)}")
