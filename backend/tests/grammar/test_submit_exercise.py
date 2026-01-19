"""Tests for submit exercise endpoint (Issue 4)."""

import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import Lesson, LessonItem, LessonProgress


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_submit_exercise_multiple_choice_correct(async_client: AsyncClient, db: AsyncSession):
    """Test submitting correct multiple choice answer."""
    # Create lesson and exercise
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "multiple_choice",
                "question": "Choose the correct form",
                "options": ["hablo", "hablas", "habla"],
                "correct_answer": 0,
                "explanation": "First person singular",
            }
        ),
        order_index=1,
    )
    db.add(exercise_item)
    await db.commit()
    await db.refresh(exercise_item)

    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": 0},
        params={"user_id": "test_user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["correct_answer"] == 0
    assert "Correcto" in data["explanation"] or "Correct" in data["explanation"]
    assert data["mastery_delta"] > 0


@pytest.mark.asyncio
async def test_submit_exercise_multiple_choice_incorrect(
    async_client: AsyncClient, db: AsyncSession
):
    """Test submitting incorrect multiple choice answer."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "multiple_choice",
                "question": "Choose the correct form",
                "options": ["hablo", "hablas", "habla"],
                "correct_answer": 0,
                "explanation": "First person singular",
            }
        ),
        order_index=1,
    )
    db.add(exercise_item)
    await db.commit()
    await db.refresh(exercise_item)

    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["correct_answer"] == 0
    assert "First person singular" in data["explanation"]
    assert data["mastery_delta"] < 0


@pytest.mark.asyncio
async def test_submit_exercise_fill_in_blank_correct(async_client: AsyncClient, db: AsyncSession):
    """Test submitting correct fill-in-blank answer."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "fill_in_blank",
                "question": "Complete: Yo ___ español.",
                "correct_answer": "hablo",
                "explanation": "'Hablo' is the correct first person form",
            }
        ),
        order_index=1,
    )
    db.add(exercise_item)
    await db.commit()
    await db.refresh(exercise_item)

    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": "hablo"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["correct_answer"] == "hablo"


@pytest.mark.asyncio
async def test_submit_exercise_fill_in_blank_case_insensitive(
    async_client: AsyncClient, db: AsyncSession
):
    """Test that fill-in-blank is case-insensitive."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "fill_in_blank",
                "question": "Complete: Yo ___ español.",
                "correct_answer": "hablo",
                "explanation": "Test",
            }
        ),
        order_index=1,
    )
    db.add(exercise_item)
    await db.commit()
    await db.refresh(exercise_item)

    # Test uppercase
    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": "HABLO"},
    )
    assert response.status_code == 200
    assert response.json()["is_correct"] is True

    # Test with spaces
    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": "  hablo  "},
    )
    assert response.status_code == 200
    assert response.json()["is_correct"] is True


@pytest.mark.asyncio
async def test_submit_exercise_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test submitting answer for non-existent exercise."""
    response = await async_client.post(
        "/grammar/exercises/999/submit",
        json={"answer": "test"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_submit_exercise_updates_progress(async_client: AsyncClient, db: AsyncSession):
    """Test that submitting exercise updates user progress."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content=json.dumps(
            {
                "type": "multiple_choice",
                "question": "Test",
                "options": ["a", "b"],
                "correct_answer": 0,
                "explanation": "Test",
            }
        ),
        order_index=1,
    )
    db.add(exercise_item)
    await db.commit()
    await db.refresh(exercise_item)

    user_id = "test_user_123"

    # Submit correct answer
    response = await async_client.post(
        f"/grammar/exercises/{exercise_item.id}/submit",
        json={"answer": 0},
        params={"user_id": user_id},
    )
    assert response.status_code == 200

    # Check progress was created/updated
    from sqlalchemy import select

    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.lesson_id == lesson.id,
            LessonProgress.language == "es",
        )
    )
    progress = progress_result.scalar_one_or_none()
    assert progress is not None
    assert progress.mastery_score is not None  # type: ignore[attr-defined]
    assert progress.mastery_score > 0  # type: ignore[attr-defined]
