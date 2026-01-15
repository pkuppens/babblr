"""Vocabulary lesson endpoints for structured vocabulary practice."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.models import Lesson, LessonItem, LessonProgress
from app.models.schemas import (
    LessonProgressCreate,
    LessonProgressResponse,
    LessonResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("/lessons", response_model=List[LessonResponse])
async def list_lessons(
    language: str = Query(..., description="Target language code (e.g., 'es', 'it', 'de')"),
    level: Optional[str] = Query(None, description="CEFR level filter (A1, A2, B1, B2, C1, C2)"),
    db: AsyncSession = Depends(get_db),
):
    """List vocabulary lessons for a given language and optional level.

    Returns lessons ordered by order_index, filtered by language and level.
    Only returns active lessons.
    """
    try:
        # Build query
        query = select(Lesson).where(
            Lesson.language == language,
            Lesson.lesson_type == "vocabulary",
            Lesson.is_active == True,  # noqa: E712
        )

        # Apply level filter if provided
        if level:
            query = query.where(Lesson.difficulty_level == level.upper())

        # Order by order_index, then by created_at
        query = query.order_by(Lesson.order_index, Lesson.created_at)

        result = await db.execute(query)
        lessons = result.scalars().all()

        logger.info(
            f"Found {len(lessons)} vocabulary lessons for language={language}, level={level}"
        )

        return list(lessons)

    except Exception as e:
        logger.error(f"Error listing vocabulary lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list lessons: {str(e)}")


@router.get("/lessons/{lesson_id}", response_model=dict)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific vocabulary lesson with all its items.

    Returns the lesson metadata along with all lesson items (words, phrases, etc.)
    ordered by their order_index.
    """
    try:
        # Get lesson
        result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")

        if lesson.lesson_type != "vocabulary":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400, detail=f"Lesson {lesson_id} is not a vocabulary lesson"
            )

        if not lesson.is_active:  # type: ignore[comparison-overlap]
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} is not active")

        # Get lesson items
        items_result = await db.execute(
            select(LessonItem)
            .where(LessonItem.lesson_id == lesson_id)
            .order_by(LessonItem.order_index)
        )
        items = items_result.scalars().all()

        # Build response with lesson and items
        lesson_data = {
            "id": lesson.id,
            "language": lesson.language,
            "lesson_type": lesson.lesson_type,
            "title": lesson.title,
            "description": lesson.description,
            "difficulty_level": lesson.difficulty_level,
            "order_index": lesson.order_index,
            "is_active": lesson.is_active,
            "created_at": lesson.created_at,
            "items": [
                {
                    "id": item.id,
                    "item_type": item.item_type,
                    "content": item.content,
                    "item_metadata": item.item_metadata,
                    "order_index": item.order_index,
                    "created_at": item.created_at,
                }
                for item in items
            ],
        }

        logger.info(f"Retrieved lesson {lesson_id} with {len(items)} items")

        return lesson_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lesson {lesson_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get lesson: {str(e)}")


@router.post("/progress", response_model=LessonProgressResponse)
async def create_progress(
    progress: LessonProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create or update lesson progress for a user/device.

    If progress already exists for this lesson_id and language, it will be updated.
    Otherwise, a new progress record is created.
    """
    try:
        # Validate lesson exists
        result = await db.execute(select(Lesson).where(Lesson.id == progress.lesson_id))
        lesson = result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {progress.lesson_id} not found")

        if lesson.lesson_type != "vocabulary":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400,
                detail=f"Lesson {progress.lesson_id} is not a vocabulary lesson",
            )

        # Validate status
        valid_statuses = ["not_started", "in_progress", "completed"]
        if progress.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{progress.status}'. Must be one of: {valid_statuses}",
            )

        # Check if progress already exists (for this lesson_id and language)
        # Note: In a multi-user system, you'd also filter by user_id/device_id
        existing_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.lesson_id == progress.lesson_id,
                LessonProgress.language == progress.language,
            )
        )
        existing = existing_result.scalar_one_or_none()

        now = datetime.utcnow()

        if existing:
            # Update existing progress
            existing.status = progress.status  # type: ignore[assignment]
            existing.completion_percentage = progress.completion_percentage  # type: ignore[assignment]
            existing.last_accessed_at = now  # type: ignore[assignment]

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
                f"Updated progress for lesson {progress.lesson_id}, language {progress.language}: "
                f"status={progress.status}, completion={progress.completion_percentage}%"
            )

            return existing
        else:
            # Create new progress
            new_progress = LessonProgress(
                lesson_id=progress.lesson_id,
                language=progress.language,
                status=progress.status,
                completion_percentage=progress.completion_percentage,
                started_at=now if progress.status == "in_progress" else None,
                completed_at=now if progress.status == "completed" else None,
                last_accessed_at=now,
            )

            db.add(new_progress)
            await db.commit()
            await db.refresh(new_progress)

            logger.info(
                f"Created progress for lesson {progress.lesson_id}, language {progress.language}: "
                f"status={progress.status}, completion={progress.completion_percentage}%"
            )

            return new_progress

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")


@router.put("/progress/{progress_id}", response_model=LessonProgressResponse)
async def update_progress(
    progress_id: int,
    progress: LessonProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing lesson progress by ID.

    This endpoint allows updating progress by its ID rather than lesson_id/language.
    """
    try:
        # Get existing progress
        result = await db.execute(select(LessonProgress).where(LessonProgress.id == progress_id))
        existing = result.scalar_one_or_none()

        if not existing:
            raise HTTPException(status_code=404, detail=f"Progress {progress_id} not found")

        # Validate lesson exists
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == progress.lesson_id))
        lesson = lesson_result.scalar_one_or_none()

        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {progress.lesson_id} not found")

        if lesson.lesson_type != "vocabulary":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400,
                detail=f"Lesson {progress.lesson_id} is not a vocabulary lesson",
            )

        # Validate status
        valid_statuses = ["not_started", "in_progress", "completed"]
        if progress.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{progress.status}'. Must be one of: {valid_statuses}",
            )

        # Update progress
        now = datetime.utcnow()
        existing.lesson_id = progress.lesson_id  # type: ignore[assignment]
        existing.language = progress.language  # type: ignore[assignment]
        existing.status = progress.status  # type: ignore[assignment]
        existing.completion_percentage = progress.completion_percentage  # type: ignore[assignment]
        existing.last_accessed_at = now  # type: ignore[assignment]

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
            f"Updated progress {progress_id} for lesson {progress.lesson_id}: "
            f"status={progress.status}, completion={progress.completion_percentage}%"
        )

        return existing

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress {progress_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")
