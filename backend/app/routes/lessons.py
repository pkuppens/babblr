"""General lessons endpoint for listing lessons across all types (grammar, vocabulary, listening)."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.cefr import CEFRLevel
from app.models.models import Lesson, LessonProgress
from app.models.schemas import LessonSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_model=List[LessonSummary])
async def list_lessons(
    language: str = Query(..., description="Target language code (e.g., 'es', 'it', 'de')"),
    level: Optional[str] = Query(None, description="CEFR level filter (A1, A2, B1, B2, C1, C2)"),
    type: Optional[str] = Query(
        None, description="Lesson type filter: 'grammar', 'vocabulary', 'listening'"
    ),
    user_id: Optional[str] = Query(None, description="User ID for progress tracking"),
    db: AsyncSession = Depends(get_db),
):
    """List lessons for a given language, optionally filtered by level and type.

    Returns lessons with user progress if user_id is provided.
    Only returns active lessons, ordered by order_index.
    """
    try:
        # Build base query
        query = select(Lesson).where(
            Lesson.language == language,
            Lesson.is_active == True,  # noqa: E712
        )

        # Apply level filter if provided
        if level:
            level_upper = level.upper()
            valid_levels = [cefr_level.value for cefr_level in CEFRLevel]
            if level_upper not in valid_levels:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid CEFR level '{level}'. Must be one of: A1, A2, B1, B2, C1, C2",
                )
            query = query.where(Lesson.difficulty_level == level_upper)

        # Apply type filter if provided
        if type:
            valid_types = ["grammar", "vocabulary", "listening"]
            if type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid lesson type '{type}'. Must be one of: {', '.join(valid_types)}",
                )
            query = query.where(Lesson.lesson_type == type)

        # Order by order_index, then by created_at
        query = query.order_by(Lesson.order_index, Lesson.created_at)

        result = await db.execute(query)
        lessons = result.scalars().all()

        # Get user progress if user_id provided
        progress_map = {}
        if user_id:
            lesson_ids = [lesson.id for lesson in lessons]
            if lesson_ids:
                progress_result = await db.execute(
                    select(LessonProgress).where(
                        LessonProgress.lesson_id.in_(lesson_ids),
                        LessonProgress.language == language,
                    )
                )
                progress_records = progress_result.scalars().all()
                for progress in progress_records:
                    progress_map[progress.lesson_id] = {  # type: ignore[attr-defined]
                        "completed": progress.status == "completed",  # type: ignore[comparison-overlap]
                        "mastery_score": progress.mastery_score or 0.0,  # type: ignore[attr-defined]
                        "last_accessed_at": progress.last_accessed_at,  # type: ignore[attr-defined]
                    }

        # Build response
        summaries = []
        for lesson in lessons:
            progress = progress_map.get(lesson.id, {})  # type: ignore[attr-defined]
            summaries.append(
                LessonSummary(
                    id=lesson.id,  # type: ignore[attr-defined]
                    title=lesson.title,  # type: ignore[attr-defined]
                    oneliner=lesson.oneliner,  # type: ignore[attr-defined]
                    lesson_type=lesson.lesson_type,  # type: ignore[attr-defined]
                    subject=lesson.subject,  # type: ignore[attr-defined]
                    difficulty_level=lesson.difficulty_level,  # type: ignore[attr-defined]
                    completed=progress.get("completed", False),
                    mastery_score=progress.get("mastery_score", 0.0),
                    last_accessed_at=progress.get("last_accessed_at"),
                )
            )

        logger.info(
            f"Found {len(summaries)} lessons for language={language}, level={level}, type={type}"
        )

        return summaries

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list lessons: {str(e)}")
