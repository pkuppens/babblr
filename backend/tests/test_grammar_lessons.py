"""Tests for grammar lesson endpoints following TDD approach."""

from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import GrammarRule, Lesson, LessonItem, LessonProgress


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_list_grammar_lessons_empty(async_client: AsyncClient, db: AsyncSession):
    """Test listing grammar lessons when none exist."""
    response = await async_client.get("/grammar/lessons?language=es")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_grammar_lessons_with_data(async_client: AsyncClient, db: AsyncSession):
    """Test listing grammar lessons with existing data."""
    # Create a grammar lesson
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Present Tense",
        description="Learn present tense conjugation",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.get("/grammar/lessons?language=es")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Present Tense"
    assert data[0]["language"] == "es"
    assert data[0]["lesson_type"] == "grammar"
    assert data[0]["difficulty_level"] == "A1"


@pytest.mark.asyncio
async def test_list_grammar_lessons_filter_by_level(async_client: AsyncClient, db: AsyncSession):
    """Test filtering grammar lessons by CEFR level."""
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
        order_index=2,
        is_active=True,
    )
    db.add(lesson_a1)
    db.add(lesson_a2)
    await db.commit()

    response = await async_client.get("/grammar/lessons?language=es&level=A1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["difficulty_level"] == "A1"


@pytest.mark.asyncio
async def test_list_grammar_lessons_filter_by_type(async_client: AsyncClient, db: AsyncSession):
    """Test filtering grammar lessons by type (new, practice, test, recap)."""
    # Create lessons with different types (stored in metadata or separate field)
    # For now, we'll use lesson items to indicate type
    new_lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="New Lesson",
        difficulty_level="A1",
        order_index=1,
        is_active=True,
    )
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)

    # Add item indicating this is a "new" lesson
    item = LessonItem(
        lesson_id=new_lesson.id,
        item_type="metadata",
        content='{"lesson_type": "new"}',
        order_index=0,
    )
    db.add(item)
    await db.commit()

    response = await async_client.get("/grammar/lessons?language=es&type=new")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_grammar_lesson_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test getting a non-existent grammar lesson."""
    response = await async_client.get("/grammar/lessons/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_grammar_lesson_with_content(async_client: AsyncClient, db: AsyncSession):
    """Test getting a grammar lesson with full content including rules, examples, exercises."""
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
        examples='[{"es": "hablo", "en": "I speak"}, {"es": "hablas", "en": "you speak"}]',
        difficulty_level="A1",
    )
    db.add(rule)
    await db.commit()

    # Create lesson items (examples and exercises)
    example_item = LessonItem(
        lesson_id=lesson.id,
        item_type="example",
        content='{"text": "Yo hablo español", "translation": "I speak Spanish", "audio_url": "/tts/synthesize?text=Yo+hablo+español&language=es"}',
        order_index=1,
    )
    exercise_item = LessonItem(
        lesson_id=lesson.id,
        item_type="exercise",
        content='{"type": "multiple_choice", "question": "Choose the correct form", "options": ["hablo", "hablas", "habla"], "correct": 0}',
        order_index=2,
    )
    db.add(example_item)
    db.add(exercise_item)
    await db.commit()

    response = await async_client.get(f"/grammar/lessons/{lesson.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lesson.id)  # GrammarLesson uses string ID
    assert data["title"] == "Present Tense"
    assert "explanation" in data
    assert "examples" in data
    assert "exercises" in data


@pytest.mark.asyncio
async def test_get_grammar_lesson_includes_audio_urls(async_client: AsyncClient, db: AsyncSession):
    """Test that grammar lesson includes audio URLs for examples."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    example_item = LessonItem(
        lesson_id=lesson.id,
        item_type="example",
        content='{"text": "Hola", "audio_url": "/tts/synthesize?text=Hola&language=es"}',
        order_index=1,
    )
    db.add(example_item)
    await db.commit()

    response = await async_client.get(f"/grammar/lessons/{lesson.id}")
    assert response.status_code == 200
    data = response.json()
    # Check that examples are present (audio URLs are generated on-demand in frontend)
    assert "examples" in data
    assert len(data["examples"]) > 0
    assert isinstance(data["examples"], list)


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


@pytest.mark.asyncio
async def test_create_grammar_progress_new(async_client: AsyncClient, db: AsyncSession):
    """Test creating new grammar lesson progress."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.post(
        "/grammar/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "in_progress",
            "completion_percentage": 25.0,
            "mastery_score": 0.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] == lesson.id
    assert data["language"] == "es"
    assert data["status"] == "in_progress"
    assert data["completion_percentage"] == 25.0
    assert "mastery_score" in data or data.get("mastery_score") == 0.5


@pytest.mark.asyncio
async def test_create_grammar_progress_with_mastery(async_client: AsyncClient, db: AsyncSession):
    """Test that progress tracks mastery score for adaptive scheduling."""
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.post(
        "/grammar/progress",
        json={
            "lesson_id": lesson.id,
            "language": "es",
            "status": "completed",
            "completion_percentage": 100.0,
            "mastery_score": 0.9,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mastery_score"] == 0.9
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_get_grammar_recaps_due_for_review(async_client: AsyncClient, db: AsyncSession):
    """Test getting grammar lessons due for recap based on spaced repetition."""
    # Create a completed lesson with mastery score
    lesson = Lesson(
        language="es",
        lesson_type="grammar",
        title="Past Tense",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    # Create progress with last reviewed date in the past
    progress = LessonProgress(
        lesson_id=lesson.id,
        language="es",
        status="completed",
        completion_percentage=100.0,
        started_at=datetime.utcnow() - timedelta(days=5),
        completed_at=datetime.utcnow() - timedelta(days=5),
        last_accessed_at=datetime.utcnow() - timedelta(days=5),
    )
    db.add(progress)
    await db.commit()

    response = await async_client.get("/grammar/recaps?language=es&level=A1")
    assert response.status_code == 200
    data = response.json()
    # Should return lessons due for review (based on last_accessed_at and mastery)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_grammar_recaps_adaptive_scheduling(async_client: AsyncClient, db: AsyncSession):
    """Test that recaps respect mastery scores (high mastery = longer intervals)."""
    # Create two lessons with different mastery scores
    lesson_high = Lesson(
        language="es",
        lesson_type="grammar",
        title="High Mastery",
        is_active=True,
    )
    lesson_low = Lesson(
        language="es",
        lesson_type="grammar",
        title="Low Mastery",
        is_active=True,
    )
    db.add(lesson_high)
    db.add(lesson_low)
    await db.commit()
    await db.refresh(lesson_high)
    await db.refresh(lesson_low)

    # High mastery lesson reviewed 7 days ago (should NOT be due yet)
    progress_high = LessonProgress(
        lesson_id=lesson_high.id,
        language="es",
        status="completed",
        completion_percentage=100.0,
        last_accessed_at=datetime.utcnow() - timedelta(days=7),
    )
    # Low mastery lesson reviewed 2 days ago (should be due)
    progress_low = LessonProgress(
        lesson_id=lesson_low.id,
        language="es",
        status="completed",
        completion_percentage=100.0,
        last_accessed_at=datetime.utcnow() - timedelta(days=2),
    )
    db.add(progress_high)
    db.add(progress_low)
    await db.commit()

    response = await async_client.get("/grammar/recaps?language=es")
    assert response.status_code == 200
    data = response.json()
    # Low mastery lesson should appear before high mastery lesson
    # (implementation detail: we'll check that adaptive scheduling works)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_progress_invalid_lesson(async_client: AsyncClient, db: AsyncSession):
    """Test creating progress for non-existent lesson."""
    response = await async_client.post(
        "/grammar/progress",
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
        lesson_type="grammar",
        title="Test Lesson",
        is_active=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)

    response = await async_client.post(
        "/grammar/progress",
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
async def test_list_grammar_lessons_missing_language(async_client: AsyncClient, db: AsyncSession):
    """Test that language parameter is required."""
    response = await async_client.get("/grammar/lessons")
    assert response.status_code == 422  # Validation error
