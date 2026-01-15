"""Tests for list lessons endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import Lesson, LessonProgress


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_list_lessons_empty(async_client: AsyncClient, db: AsyncSession):
    """Test listing lessons when none exist."""
    response = await async_client.get("/lessons?language=es")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_lessons_with_data(async_client: AsyncClient, db: AsyncSession):
    """Test listing lessons with existing data."""
    # Create a grammar lesson
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Present Tense",
        oneliner="Learn present tense conjugation",
        subject="present_ar_verbs",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.get("/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Present Tense"
    assert data[0]["oneliner"] == "Learn present tense conjugation"
    assert data[0]["lesson_type"] == "grammar"
    assert data[0]["subject"] == "present_ar_verbs"
    assert data[0]["difficulty_level"] == "A1"


@pytest.mark.asyncio
async def test_list_lessons_filter_by_level(async_client: AsyncClient, db: AsyncSession):
    """Test filtering lessons by CEFR level."""
    lesson_a1 = Lesson(
        language="es",
        lesson_type="grammar",
        title="A1 Grammar",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    lesson_a2 = Lesson(
        language="es",
        lesson_type="grammar",
        title="A2 Grammar",
        difficulty_level="A2",
        order_index=1,
        is_active=True,
    )
    db.add(lesson_a1)
    db.add(lesson_a2)
    await db.commit()

    response = await async_client.get("/lessons?language=es&level=A1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["difficulty_level"] == "A1"


@pytest.mark.asyncio
async def test_list_lessons_filter_by_type(async_client: AsyncClient, db: AsyncSession):
    """Test filtering lessons by type."""
    grammar_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Grammar Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    vocab_lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Vocabulary Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(grammar_lesson)
    db.add(vocab_lesson)
    await db.commit()

    response = await async_client.get("/lessons?language=es&type=grammar")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["lesson_type"] == "grammar"


@pytest.mark.asyncio
async def test_list_lessons_with_progress(async_client: AsyncClient, db: AsyncSession):
    """Test listing lessons with user progress."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create progress
    progress = LessonProgress(
        lesson_id=lesson.id,
        language="es",
        status="completed",
        completion_percentage=100.0,
        mastery_score=0.85,
    )
    db.add(progress)
    await db.commit()

    response = await async_client.get("/lessons?language=es&user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is True
    assert data[0]["mastery_score"] == 0.85


@pytest.mark.asyncio
async def test_list_lessons_invalid_level(async_client: AsyncClient, db: AsyncSession):
    """Test that invalid CEFR level returns 400 error."""
    response = await async_client.get("/lessons?language=es&level=INVALID")
    assert response.status_code == 400
    assert "Invalid CEFR level" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_lessons_invalid_type(async_client: AsyncClient, db: AsyncSession):
    """Test that invalid lesson type returns 400 error."""
    response = await async_client.get("/lessons?language=es&type=invalid_type")
    assert response.status_code == 400
    assert "Invalid lesson type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_lessons_missing_language(async_client: AsyncClient, db: AsyncSession):
    """Test that language parameter is required."""
    response = await async_client.get("/lessons")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_lessons_only_active(async_client: AsyncClient, db: AsyncSession):
    """Test that only active lessons are returned."""
    active_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Active Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    inactive_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Inactive Lesson",
        difficulty_level="A1",
        order_index=2,
        is_active=False,
    )
    db.add(active_lesson)
    db.add(inactive_lesson)
    await db.commit()

    response = await async_client.get("/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active Lesson"


@pytest.mark.asyncio
async def test_list_lessons_ordering(async_client: AsyncClient, db: AsyncSession):
    """Test that lessons are ordered by order_index."""
    lesson1 = Lesson(
        language="es",
        lesson_type="grammar",
        title="Second",
        difficulty_level="A1",
        order_index=2,
        is_active=True,
    )
    lesson2 = Lesson(
        language="es",
        lesson_type="grammar",
        title="First",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson1)
    db.add(lesson2)
    await db.commit()

    response = await async_client.get("/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "First"
    assert data[1]["title"] == "Second"
