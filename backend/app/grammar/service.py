"""Service layer for grammar lesson operations."""

import json
import logging
from typing import Optional, Union

from app.grammar.models import Exercise
from app.models.models import LessonItem

logger = logging.getLogger(__name__)


def validate_exercise_answer(exercise: Exercise, user_answer: Union[str, int, list]) -> bool:
    """Validate exercise answer based on exercise type.

    Args:
        exercise: Exercise model with type and correct_answer
        user_answer: User's answer (type depends on exercise type)

    Returns:
        True if answer is correct, False otherwise
    """
    if exercise.type == "multiple_choice":
        # Multiple choice: compare int indices
        if isinstance(user_answer, int):
            return user_answer == exercise.correct_answer
        # Try to convert string to int
        try:
            return int(user_answer) == exercise.correct_answer
        except (ValueError, TypeError):
            return False

    elif exercise.type == "fill_in_blank":
        # Fill-in-blank: case-insensitive string comparison
        if isinstance(exercise.correct_answer, str) and isinstance(user_answer, str):
            return user_answer.lower().strip() == exercise.correct_answer.lower().strip()
        return False

    elif exercise.type == "word_order":
        # Word order: list comparison
        if isinstance(user_answer, list) and isinstance(exercise.correct_answer, list):
            return user_answer == exercise.correct_answer
        return False

    else:
        logger.warning(f"Unknown exercise type: {exercise.type}")
        return False


def parse_exercise_from_item(item: LessonItem) -> Optional[Exercise]:
    """Parse Exercise model from LessonItem.

    Args:
        item: LessonItem with item_type="exercise" and JSON content

    Returns:
        Exercise model or None if parsing fails
    """
    if item.item_type != "exercise":  # type: ignore[comparison-overlap]
        return None

    try:
        content = json.loads(str(item.content))  # type: ignore[arg-type]
        return Exercise(
            id=str(item.id),
            type=content.get("type", "multiple_choice"),
            question=content.get("question", ""),
            options=content.get("options"),
            correct_answer=content.get("correct_answer", ""),
            explanation=content.get("explanation", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse exercise from item {item.id}: {e}")
        return None
