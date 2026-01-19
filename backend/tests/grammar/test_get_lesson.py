"""Tests for get grammar lesson endpoint (Issue 3)."""

import json

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import GrammarRule, Lesson, LessonItem


@pytest.mark.asyncio
async def test_get_grammar_lesson_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test getting a non-existent grammar lesson."""
    response = await async_client.get("/grammar/lessons/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_grammar_lesson_with_content(async_client: AsyncClient, db: AsyncSession):
    """Test getting a grammar lesson with full content."""
    # Create lesson
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Present Tense",
        description="Learn present tense",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create grammar rule
    rule = GrammarRule(
        lesson_id=lesson.id,
        title="Regular -ar verbs",
        description="Add -o, -as, -a, -amos, -áis, -an to the stem",
        examples='[{"es": "hablo", "en": "I speak"}]',
        difficulty_level="A1",
    )
    db.add(rule)
    await db.commit()

    # Create example item
    example_item = LessonItem(
        lesson_id=lesson.id,
        item_type="example",
        content='{"text": "Yo hablo español"}',
        order_index=1,
    )
    db.add(example_item)
    await db.commit()

    # Create exercise item
    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "multiple_choice",
                "question": "Choose the correct form",
                "options": ["hablo", "hablas", "habla"],
                "correct_answer": 0,
                "explanation": "'Hablo' is first person singular",
            }
        ),
        order_index=2,
    )
    db.add(exercise_item)
    await db.commit()

    response = await async_client.get(f"/grammar/lessons/{lesson.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lesson.id)
    assert data["title"] == "Present Tense"
    assert data["language"] == "es"
    assert data["level"] == "A1"
    assert "explanation" in data
    assert len(data["examples"]) > 0
    assert len(data["exercises"]) > 0
    assert data["exercises"][0]["type"] == "multiple_choice"


@pytest.mark.asyncio
async def test_get_grammar_lesson_wrong_type(async_client: AsyncClient, db: AsyncSession):
    """Test getting a vocabulary lesson via grammar endpoint."""
    vocab_lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Vocab Lesson",
        is_active=True,
    )
    db.add(vocab_lesson)
    await db.commit()
    await db.refresh(vocab_lesson)

    response = await async_client.get(f"/grammar/lessons/{vocab_lesson.id}")
    assert response.status_code == 400
    assert "not a grammar lesson" in response.json()["detail"].lower()
