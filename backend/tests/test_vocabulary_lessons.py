"""Tests for vocabulary lesson endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import Lesson, LessonItem


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_list_lessons_empty(async_client: AsyncClient, db: AsyncSession):
    """Test listing lessons when none exist."""
    response = await async_client.get("/vocabulary/lessons?language=es")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_lessons_with_data(async_client: AsyncClient, db: AsyncSession):
    """Test listing lessons with existing data."""
    # Create a vocabulary lesson
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        description="A test lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.get("/vocabulary/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Lesson"
    assert data[0]["language"] == "es"
    assert data[0]["lesson_type"] == "vocabulary"
    assert data[0]["difficulty_level"] == "A1"


@pytest.mark.asyncio
async def test_list_lessons_filter_by_level(async_client: AsyncClient, db: AsyncSession):
    """Test filtering lessons by CEFR level."""
    # Create lessons at different levels
    lesson_a1 = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="A1 Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    lesson_a2 = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="A2 Lesson",
        difficulty_level="A2",
        order_index=2,
        is_active=True,
    )
    db.add(lesson_a1)
    db.add(lesson_a2)
    await db.commit()

    # Filter by A1
    response = await async_client.get("/vocabulary/lessons?language=es&level=A1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["difficulty_level"] == "A1"

    # Filter by A2
    response = await async_client.get("/vocabulary/lessons?language=es&level=A2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["difficulty_level"] == "A2"


@pytest.mark.asyncio
async def test_list_lessons_only_active(async_client: AsyncClient, db: AsyncSession):
    """Test that only active lessons are returned."""
    active_lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Active Lesson",
        is_active=True,
        order_index=1,
    )
    inactive_lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Inactive Lesson",
        is_active=False,
        order_index=2,
    )
    db.add(active_lesson)
    db.add(inactive_lesson)
    await db.commit()

    response = await async_client.get("/vocabulary/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active Lesson"


@pytest.mark.asyncio
async def test_list_lessons_only_vocabulary(async_client: AsyncClient, db: AsyncSession):
    """Test that only vocabulary lessons are returned."""
    vocab_lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Vocab Lesson",
        is_active=True,
        order_index=1,
    )
    grammar_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Grammar Lesson",
        is_active=True,
        order_index=2,
    )
    db.add(vocab_lesson)
    db.add(grammar_lesson)
    await db.commit()

    response = await async_client.get("/vocabulary/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Vocab Lesson"


@pytest.mark.asyncio
async def test_get_lesson_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test getting a non-existent lesson."""
    response = await async_client.get("/vocabulary/lessons/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_lesson_with_items(async_client: AsyncClient, db: AsyncSession):
    """Test getting a lesson with its items."""
    # Create lesson
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        description="A test lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create lesson items
    item1 = LessonItem(
        lesson_id=lesson.id,
        item_type="word",
        content="Hola",
        item_metadata='{"translation": "Hello"}',
        order_index=1,
    )
    item2 = LessonItem(
        lesson_id=lesson.id,
        item_type="word",
        content="Adiós",
        item_metadata='{"translation": "Goodbye"}',
        order_index=2,
    )
    db.add(item1)
    db.add(item2)
    await db.commit()

    response = await async_client.get(f"/vocabulary/lessons/{lesson.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lesson.id
    assert data["title"] == "Test Lesson"
    assert len(data["items"]) == 2
    assert data["items"][0]["word"] == "Hola"
    assert data["items"][1]["word"] == "Adiós"
    # Items should be ordered by order_index
    assert data["items"][0]["order_index"] == 1
    assert data["items"][1]["order_index"] == 2


@pytest.mark.asyncio
async def test_get_lesson_wrong_type(async_client: AsyncClient, db: AsyncSession):
    """Test getting a grammar lesson via vocabulary endpoint."""
    grammar_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Grammar Lesson",
        is_active=True,
    )
    db.add(grammar_lesson)
    await db.commit()
    await db.refresh(grammar_lesson)

    response = await async_client.get(f"/vocabulary/lessons/{grammar_lesson.id}")
    assert response.status_code == 400
    assert "not a vocabulary lesson" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_progress_new(async_client: AsyncClient, db: AsyncSession):
    """Test creating new lesson progress."""
    # Create lesson
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create progress
    response = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 25.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] == lesson.id
    assert data["language"] == "es"
    assert data["status"] == "in_progress"
    assert data["completion_percentage"] == 25.0
    assert data["started_at"] is not None
    assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_create_progress_update_existing(async_client: AsyncClient, db: AsyncSession):
    """Test that creating progress updates existing record."""
    # Create lesson
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create initial progress
    response1 = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 25.0,
        },
    )
    assert response1.status_code == 200
    progress_id = response1.json()["id"]

    # Update progress
    response2 = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "completed",
            "completion_percentage": 100.0,
        },
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["id"] == progress_id  # Same record
    assert data["status"] == "completed"
    assert data["completion_percentage"] == 100.0
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_create_progress_invalid_lesson(async_client: AsyncClient, db: AsyncSession):
    """Test creating progress for non-existent lesson."""
    response = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": 999,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 0.0,
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_progress_invalid_status(async_client: AsyncClient, db: AsyncSession):
    """Test creating progress with invalid status."""
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "invalid_status",
            "completion_percentage": 0.0,
        },
    )
    assert response.status_code == 400
    assert "invalid status" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_progress_by_id(async_client: AsyncClient, db: AsyncSession):
    """Test updating progress by ID."""
    # Create lesson
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create progress
    create_response = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 50.0,
        },
    )
    progress_id = create_response.json()["id"]

    # Update progress
    update_response = await async_client.put(
        f"/vocabulary/progress/{progress_id}",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "completed",
            "completion_percentage": 100.0,
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == progress_id
    assert data["status"] == "completed"
    assert data["completion_percentage"] == 100.0


@pytest.mark.asyncio
async def test_update_progress_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test updating non-existent progress."""
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.put(
        "/vocabulary/progress/999",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "completed",
            "completion_percentage": 100.0,
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_lessons_missing_language(async_client: AsyncClient, db: AsyncSession):
    """Test that language parameter is required."""
    response = await async_client.get("/vocabulary/lessons")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_progress_completion_tracking(async_client: AsyncClient, db: AsyncSession):
    """Test that completion timestamps are tracked correctly."""
    lesson = Lesson(
        language="es",
        lesson_type="vocabulary",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Start progress
    response1 = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 50.0,
        },
    )
    data1 = response1.json()
    assert data1["started_at"] is not None
    assert data1["completed_at"] is None

    # Complete progress
    response2 = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "completed",
            "completion_percentage": 100.0,
        },
    )
    data2 = response2.json()
    assert data2["completed_at"] is not None

    # Revert to in_progress
    response3 = await async_client.post(
        "/vocabulary/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 75.0,
        },
    )
    data3 = response3.json()
    assert data3["completed_at"] is None  # Should be reset
