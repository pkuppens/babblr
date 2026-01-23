"""
Tests for Progress Dashboard functionality.

This module contains tests for:
- Progress summary Pydantic schemas
- Progress service (vocabulary, grammar, assessment stats)
- Progress API endpoint

Following TDD approach: tests are written first, then implementation.
"""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


class TestProgressSummarySchemas:
    """Test Pydantic schemas for progress summary data."""

    def test_vocabulary_progress_schema_valid(self):
        """VocabularyProgress should accept valid data."""
        from app.models.schemas import VocabularyProgress

        data = {
            "completed": 5,
            "in_progress": 2,
            "total": 10,
            "last_activity": "2024-01-15T10:30:00Z",
        }
        progress = VocabularyProgress(**data)
        assert progress.completed == 5
        assert progress.in_progress == 2
        assert progress.total == 10
        assert progress.last_activity is not None

    def test_vocabulary_progress_schema_with_no_activity(self):
        """VocabularyProgress should accept null last_activity."""
        from app.models.schemas import VocabularyProgress

        data = {
            "completed": 0,
            "in_progress": 0,
            "total": 10,
            "last_activity": None,
        }
        progress = VocabularyProgress(**data)
        assert progress.last_activity is None

    def test_vocabulary_progress_negative_values_rejected(self):
        """VocabularyProgress should reject negative counts."""
        from app.models.schemas import VocabularyProgress

        with pytest.raises(ValidationError):
            VocabularyProgress(completed=-1, in_progress=0, total=10, last_activity=None)

    def test_grammar_progress_schema_valid(self):
        """GrammarProgress should accept valid data."""
        from app.models.schemas import GrammarProgress

        data = {
            "completed": 3,
            "in_progress": 1,
            "total": 8,
            "last_activity": "2024-01-15T10:30:00Z",
        }
        progress = GrammarProgress(**data)
        assert progress.completed == 3
        assert progress.total == 8

    def test_assessment_progress_schema_valid(self):
        """AssessmentProgress should accept valid data."""
        from app.models.schemas import AssessmentProgress, SkillScore

        skill_scores = [
            SkillScore(skill="grammar", score=80.0, total=10, correct=8),
            SkillScore(skill="vocabulary", score=70.0, total=10, correct=7),
        ]
        data = {
            "latest_score": 75.0,
            "recommended_level": "B1",
            "skill_scores": skill_scores,
            "last_attempt": "2024-01-15T10:30:00Z",
        }
        progress = AssessmentProgress(**data)
        assert progress.latest_score == 75.0
        assert progress.recommended_level == "B1"
        assert len(progress.skill_scores) == 2

    def test_assessment_progress_schema_with_no_attempts(self):
        """AssessmentProgress should accept null values for no attempts."""
        from app.models.schemas import AssessmentProgress

        data = {
            "latest_score": None,
            "recommended_level": None,
            "skill_scores": None,
            "last_attempt": None,
        }
        progress = AssessmentProgress(**data)
        assert progress.latest_score is None
        assert progress.recommended_level is None

    def test_assessment_progress_score_range(self):
        """AssessmentProgress should validate score is 0-100."""
        from app.models.schemas import AssessmentProgress

        with pytest.raises(ValidationError):
            AssessmentProgress(
                latest_score=150.0,  # Invalid
                recommended_level="B1",
                skill_scores=None,
                last_attempt=None,
            )

    def test_progress_summary_schema_valid(self):
        """ProgressSummary should compose all progress types."""
        from app.models.schemas import (
            AssessmentProgress,
            GrammarProgress,
            ProgressSummary,
            VocabularyProgress,
        )

        vocab = VocabularyProgress(completed=5, in_progress=2, total=10, last_activity=None)
        grammar = GrammarProgress(completed=3, in_progress=1, total=8, last_activity=None)
        assessment = AssessmentProgress(
            latest_score=75.0, recommended_level="B1", skill_scores=None, last_attempt=None
        )

        summary = ProgressSummary(
            language="es",
            vocabulary=vocab,
            grammar=grammar,
            assessment=assessment,
        )

        assert summary.language == "es"
        assert summary.vocabulary.completed == 5
        assert summary.grammar.completed == 3
        assert summary.assessment.latest_score == 75.0

    def test_progress_summary_empty_state(self):
        """ProgressSummary should handle empty/zero progress."""
        from app.models.schemas import (
            AssessmentProgress,
            GrammarProgress,
            ProgressSummary,
            VocabularyProgress,
        )

        vocab = VocabularyProgress(completed=0, in_progress=0, total=0, last_activity=None)
        grammar = GrammarProgress(completed=0, in_progress=0, total=0, last_activity=None)
        assessment = AssessmentProgress(
            latest_score=None, recommended_level=None, skill_scores=None, last_attempt=None
        )

        summary = ProgressSummary(
            language="es",
            vocabulary=vocab,
            grammar=grammar,
            assessment=assessment,
        )

        assert summary.vocabulary.total == 0
        assert summary.assessment.latest_score is None


class TestProgressService:
    """Test progress service functions."""

    @pytest.mark.asyncio
    async def test_get_vocabulary_progress_returns_stats(self, db):
        """get_vocabulary_progress should return vocabulary lesson stats."""
        from app.models.models import Lesson, LessonProgress
        from app.services.progress_service import get_vocabulary_progress

        # Create vocabulary lessons
        lesson1 = Lesson(
            language="es",
            lesson_type="vocabulary",
            title="Lesson 1",
            difficulty_level="A1",
            order_index=0,
        )
        lesson2 = Lesson(
            language="es",
            lesson_type="vocabulary",
            title="Lesson 2",
            difficulty_level="A1",
            order_index=1,
        )
        db.add_all([lesson1, lesson2])
        await db.flush()

        # Create progress - one completed, one in progress
        progress1 = LessonProgress(
            lesson_id=lesson1.id,
            language="es",
            status="completed",
            completion_percentage=100.0,
        )
        progress2 = LessonProgress(
            lesson_id=lesson2.id,
            language="es",
            status="in_progress",
            completion_percentage=50.0,
        )
        db.add_all([progress1, progress2])
        await db.commit()

        result = await get_vocabulary_progress(db, "es")

        assert result.completed == 1
        assert result.in_progress == 1
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_get_vocabulary_progress_with_no_data(self, db):
        """get_vocabulary_progress should return zeros when no data exists."""
        from app.services.progress_service import get_vocabulary_progress

        result = await get_vocabulary_progress(db, "es")

        assert result.completed == 0
        assert result.in_progress == 0
        assert result.total == 0
        assert result.last_activity is None

    @pytest.mark.asyncio
    async def test_get_vocabulary_progress_last_activity(self, db):
        """get_vocabulary_progress should return most recent activity timestamp."""

        from app.models.models import Lesson, LessonProgress
        from app.services.progress_service import get_vocabulary_progress

        # Create vocabulary lesson
        lesson = Lesson(
            language="es",
            lesson_type="vocabulary",
            title="Lesson 1",
            difficulty_level="A1",
            order_index=0,
        )
        db.add(lesson)
        await db.flush()

        # Create progress with known timestamp
        now = datetime.now(timezone.utc)
        progress = LessonProgress(
            lesson_id=lesson.id,
            language="es",
            status="in_progress",
            completion_percentage=50.0,
            last_accessed_at=now,
        )
        db.add(progress)
        await db.commit()

        result = await get_vocabulary_progress(db, "es")

        assert result.last_activity is not None
        # Should be close to the time we set (within a few seconds)
        assert abs((result.last_activity - now).total_seconds()) < 5

    @pytest.mark.asyncio
    async def test_get_grammar_progress_returns_stats(self, db):
        """get_grammar_progress should return grammar lesson stats."""
        from app.models.models import Lesson, LessonProgress
        from app.services.progress_service import get_grammar_progress

        # Create grammar lessons
        lesson1 = Lesson(
            language="es",
            lesson_type="grammar",
            title="Grammar 1",
            difficulty_level="A1",
            order_index=0,
        )
        lesson2 = Lesson(
            language="es",
            lesson_type="grammar",
            title="Grammar 2",
            difficulty_level="A1",
            order_index=1,
        )
        db.add_all([lesson1, lesson2])
        await db.flush()

        # Create progress - both completed
        progress1 = LessonProgress(
            lesson_id=lesson1.id,
            language="es",
            status="completed",
            completion_percentage=100.0,
        )
        progress2 = LessonProgress(
            lesson_id=lesson2.id,
            language="es",
            status="completed",
            completion_percentage=100.0,
        )
        db.add_all([progress1, progress2])
        await db.commit()

        result = await get_grammar_progress(db, "es")

        assert result.completed == 2
        assert result.in_progress == 0
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_get_grammar_progress_with_no_data(self, db):
        """get_grammar_progress should return zeros when no data exists."""
        from app.services.progress_service import get_grammar_progress

        result = await get_grammar_progress(db, "fr")

        assert result.completed == 0
        assert result.in_progress == 0
        assert result.total == 0
        assert result.last_activity is None

    @pytest.mark.asyncio
    async def test_get_grammar_progress_last_activity(self, db):
        """get_grammar_progress should return most recent activity timestamp."""

        from app.models.models import Lesson, LessonProgress
        from app.services.progress_service import get_grammar_progress

        # Create grammar lesson
        lesson = Lesson(
            language="es",
            lesson_type="grammar",
            title="Grammar 1",
            difficulty_level="A1",
            order_index=0,
        )
        db.add(lesson)
        await db.flush()

        # Create progress with known timestamp
        now = datetime.now(timezone.utc)
        progress = LessonProgress(
            lesson_id=lesson.id,
            language="es",
            status="completed",
            completion_percentage=100.0,
            last_accessed_at=now,
        )
        db.add(progress)
        await db.commit()

        result = await get_grammar_progress(db, "es")

        assert result.last_activity is not None


class TestAssessmentProgressService:
    """Test assessment progress service functions."""

    @pytest.mark.asyncio
    async def test_get_assessment_progress_returns_latest_attempt(self, db):
        """get_assessment_progress should return latest assessment attempt stats."""
        from datetime import timedelta

        from app.models.models import Assessment, AssessmentAttempt
        from app.services.progress_service import get_assessment_progress

        # Create assessment
        assessment = Assessment(
            language="es",
            assessment_type="cefr_placement",
            title="Placement Test",
            difficulty_level="A1",
        )
        db.add(assessment)
        await db.flush()

        # Create two attempts - second one is more recent and should be returned
        older_attempt = AssessmentAttempt(
            assessment_id=assessment.id,
            language="es",
            score=60.0,
            total_questions=10,
            correct_answers=6,
            completed_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        newer_attempt = AssessmentAttempt(
            assessment_id=assessment.id,
            language="es",
            score=80.0,
            total_questions=10,
            correct_answers=8,
            completed_at=datetime.now(timezone.utc),
        )
        db.add_all([older_attempt, newer_attempt])
        await db.commit()

        result = await get_assessment_progress(db, "es")

        assert result.latest_score == 80.0
        assert result.last_attempt is not None

    @pytest.mark.asyncio
    async def test_get_assessment_progress_with_no_attempts(self, db):
        """get_assessment_progress should return None values when no attempts exist."""
        from app.services.progress_service import get_assessment_progress

        result = await get_assessment_progress(db, "es")

        assert result.latest_score is None
        assert result.recommended_level is None
        assert result.skill_scores is None
        assert result.last_attempt is None

    @pytest.mark.asyncio
    async def test_get_assessment_progress_includes_recommended_level(self, db):
        """get_assessment_progress should include recommended_level from UserLevel."""

        from app.models.models import Assessment, AssessmentAttempt, UserLevel
        from app.services.progress_service import get_assessment_progress

        # Create assessment and attempt
        assessment = Assessment(
            language="es",
            assessment_type="cefr_placement",
            title="Placement Test",
            difficulty_level="A1",
        )
        db.add(assessment)
        await db.flush()

        attempt = AssessmentAttempt(
            assessment_id=assessment.id,
            language="es",
            score=75.0,
            total_questions=10,
            correct_answers=7,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(attempt)

        # Create user level with recommended CEFR level
        user_level = UserLevel(
            language="es",
            cefr_level="B1",
            proficiency_score=75.0,
        )
        db.add(user_level)
        await db.commit()

        result = await get_assessment_progress(db, "es")

        assert result.latest_score == 75.0
        assert result.recommended_level == "B1"


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestProgressEndpoint:
    """Test GET /progress/summary endpoint."""

    @pytest.mark.asyncio
    async def test_progress_summary_returns_200_with_valid_language(
        self, async_client: AsyncClient, db: AsyncSession
    ):
        """GET /progress/summary should return 200 with valid language."""
        response = await async_client.get("/progress/summary?language=es")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es"
        assert "vocabulary" in data
        assert "grammar" in data
        assert "assessment" in data

    @pytest.mark.asyncio
    async def test_progress_summary_empty_stats(self, async_client: AsyncClient, db: AsyncSession):
        """GET /progress/summary should return zeros when no progress exists."""
        response = await async_client.get("/progress/summary?language=fr")
        assert response.status_code == 200
        data = response.json()

        # Vocabulary should be empty
        assert data["vocabulary"]["completed"] == 0
        assert data["vocabulary"]["in_progress"] == 0
        assert data["vocabulary"]["total"] == 0
        assert data["vocabulary"]["last_activity"] is None

        # Grammar should be empty
        assert data["grammar"]["completed"] == 0
        assert data["grammar"]["in_progress"] == 0
        assert data["grammar"]["total"] == 0

        # Assessment should be empty
        assert data["assessment"]["latest_score"] is None
        assert data["assessment"]["recommended_level"] is None

    @pytest.mark.asyncio
    async def test_progress_summary_with_data(self, async_client: AsyncClient, db: AsyncSession):
        """GET /progress/summary should return populated stats when data exists."""
        from app.models.models import Lesson, LessonProgress

        # Create vocabulary lesson with progress
        lesson = Lesson(
            language="es",
            lesson_type="vocabulary",
            title="Test Vocab",
            difficulty_level="A1",
            order_index=0,
        )
        db.add(lesson)
        await db.flush()

        progress = LessonProgress(
            lesson_id=lesson.id,
            language="es",
            status="completed",
            completion_percentage=100.0,
        )
        db.add(progress)
        await db.commit()

        response = await async_client.get("/progress/summary?language=es")
        assert response.status_code == 200
        data = response.json()

        assert data["vocabulary"]["completed"] == 1
        assert data["vocabulary"]["total"] == 1

    @pytest.mark.asyncio
    async def test_progress_summary_requires_language(
        self, async_client: AsyncClient, db: AsyncSession
    ):
        """GET /progress/summary should return 422 without language parameter."""
        response = await async_client.get("/progress/summary")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_progress_summary_validates_language(
        self, async_client: AsyncClient, db: AsyncSession
    ):
        """GET /progress/summary should validate language is supported."""
        response = await async_client.get("/progress/summary?language=xyz")
        assert response.status_code == 400
        data = response.json()
        assert "language" in data["detail"].lower()
