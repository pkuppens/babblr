"""
Progress API routes for the progress dashboard.

Provides endpoints for retrieving user learning progress summary.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.schemas import ProgressSummary
from app.services.language_catalog import find_variant
from app.services.progress_service import (
    get_assessment_progress,
    get_grammar_progress,
    get_vocabulary_progress,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary", response_model=ProgressSummary)
async def get_progress_summary(
    language: str = Query(..., description="Target language code"),
    db: AsyncSession = Depends(get_db),
) -> ProgressSummary:
    """
    Get progress summary for a specific language.

    Returns vocabulary, grammar, and assessment progress stats for the user
    in the specified target language.

    Args:
        language: Target language code (e.g., 'es', 'fr', 'de')
        db: Database session

    Returns:
        ProgressSummary with vocabulary, grammar, and assessment stats

    Raises:
        HTTPException 400: If language is not supported
    """
    # Validate language
    if find_variant(language) is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}. Please use a valid language code.",
        )

    logger.info(f"Getting progress summary for language: {language}")

    # Get progress stats from each service
    vocabulary = await get_vocabulary_progress(db, language)
    grammar = await get_grammar_progress(db, language)
    assessment = await get_assessment_progress(db, language)

    return ProgressSummary(
        language=language,
        vocabulary=vocabulary,
        grammar=grammar,
        assessment=assessment,
    )
