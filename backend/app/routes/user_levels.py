"""User level endpoints for CEFR proficiency tracking."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.cefr import CEFRLevel
from app.models.models import UserLevel
from app.models.schemas import UserLevelResponse, UserLevelUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-levels", tags=["user-levels"])

VALID_CEFR_LEVELS = [level.value for level in CEFRLevel]


@router.put("/{language}", response_model=UserLevelResponse)
async def update_user_level(
    language: str,
    level_data: UserLevelUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update user's CEFR level for a language.

    Creates new record if none exists, updates existing otherwise.
    """
    # Validate CEFR level
    if level_data.cefr_level not in VALID_CEFR_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CEFR level '{level_data.cefr_level}'. "
            f"Must be one of: {', '.join(VALID_CEFR_LEVELS)}",
        )

    # Find or create
    result = await db.execute(select(UserLevel).where(UserLevel.language == language))
    user_level = result.scalar()

    now = datetime.now(timezone.utc)
    if user_level:
        await db.execute(
            update(UserLevel)
            .where(UserLevel.id == user_level.id)
            .values(
                cefr_level=level_data.cefr_level,
                proficiency_score=level_data.proficiency_score,
                assessed_at=now,
                updated_at=now,
            )
        )
        await db.commit()
        result = await db.execute(select(UserLevel).where(UserLevel.id == user_level.id))
        user_level = result.scalar_one()
    else:
        user_level = UserLevel(
            language=language,
            cefr_level=level_data.cefr_level,
            proficiency_score=level_data.proficiency_score,
            assessed_at=now,
        )
        db.add(user_level)
        await db.commit()
        await db.refresh(user_level)

    logger.info(f"Updated user level for {language}: {level_data.cefr_level}")

    return user_level


@router.get("/{language}", response_model=UserLevelResponse)
async def get_user_level(
    language: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user's current CEFR level for a language."""
    result = await db.execute(select(UserLevel).where(UserLevel.language == language))
    user_level = result.scalar()

    if not user_level:
        raise HTTPException(status_code=404, detail="User level not found")

    return user_level
