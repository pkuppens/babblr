"""
Tests for Progress Dashboard functionality.

This module contains tests for:
- Progress summary Pydantic schemas
- Progress service (vocabulary, grammar, assessment stats)
- Progress API endpoint

Following TDD approach: tests are written first, then implementation.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError


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
        from datetime import datetime, timedelta

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
        now = datetime.utcnow()
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


class TestProgressEndpoint:
    """Test GET /progress/summary endpoint."""

    pass  # Tests to be added in A1
