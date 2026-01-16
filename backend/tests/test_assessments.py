"""
Tests for CEFR Assessment functionality.

This module contains tests for:
- Assessment data models and schemas
- Assessment seed data service
- Scoring service with CEFR level determination
- Assessment API endpoints

Following TDD approach: tests are written first, then implementation.
"""

import pytest
from pydantic import ValidationError


class TestAssessmentSchemas:
    """Test Pydantic schemas for assessment data."""

    def test_skill_category_enum_valid_values(self):
        """SkillCategory enum should accept valid skill categories."""
        from app.models.schemas import SkillCategory

        assert SkillCategory.GRAMMAR.value == "grammar"
        assert SkillCategory.VOCABULARY.value == "vocabulary"
        assert SkillCategory.LISTENING.value == "listening"

    def test_skill_score_validation_valid(self):
        """SkillScore should accept valid data."""
        from app.models.schemas import SkillScore

        score = SkillScore(skill="grammar", score=80.0, total=10, correct=8)
        assert score.skill == "grammar"
        assert score.score == 80.0
        assert score.total == 10
        assert score.correct == 8

    def test_skill_score_validation_score_range(self):
        """SkillScore should validate score is 0-100."""
        from app.models.schemas import SkillScore

        # Valid score at boundaries
        score_min = SkillScore(skill="grammar", score=0.0, total=10, correct=0)
        assert score_min.score == 0.0

        score_max = SkillScore(skill="grammar", score=100.0, total=10, correct=10)
        assert score_max.score == 100.0

        # Invalid score over 100
        with pytest.raises(ValidationError):
            SkillScore(skill="grammar", score=150.0, total=10, correct=15)

        # Invalid negative score
        with pytest.raises(ValidationError):
            SkillScore(skill="grammar", score=-10.0, total=10, correct=0)

    def test_skill_score_correct_not_greater_than_total(self):
        """SkillScore should validate correct <= total."""
        from app.models.schemas import SkillScore

        # Valid: correct equals total
        score = SkillScore(skill="grammar", score=100.0, total=10, correct=10)
        assert score.correct == 10

        # Invalid: correct > total
        with pytest.raises(ValidationError):
            SkillScore(skill="grammar", score=100.0, total=10, correct=15)

    def test_assessment_question_response_with_skill_category(self):
        """AssessmentQuestionResponse should include skill_category."""
        from app.models.schemas import AssessmentQuestionResponse

        data = {
            "id": 1,
            "assessment_id": 1,
            "question_type": "multiple_choice",
            "skill_category": "grammar",
            "question_text": "Choose the correct verb form",
            "options": ["hablo", "hablas", "habla", "hablamos"],
            "points": 1,
            "order_index": 0,
        }
        response = AssessmentQuestionResponse(**data)
        assert response.skill_category == "grammar"
        assert response.options == ["hablo", "hablas", "habla", "hablamos"]

    def test_assessment_response_with_skill_categories(self):
        """AssessmentResponse should include skill_categories and question_count."""
        from app.models.schemas import AssessmentListResponse

        data = {
            "id": 1,
            "language": "es",
            "assessment_type": "cefr_placement",
            "title": "Spanish Placement Test",
            "description": "Test your Spanish level",
            "difficulty_level": "mixed",
            "duration_minutes": 30,
            "skill_categories": ["grammar", "vocabulary", "listening"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "question_count": 25,
        }
        response = AssessmentListResponse(**data)
        assert response.skill_categories == ["grammar", "vocabulary", "listening"]
        assert response.question_count == 25

    def test_attempt_result_response_with_skill_breakdown(self):
        """AttemptResultResponse should include skill-level breakdown."""
        from app.models.schemas import AttemptResultResponse

        data = {
            "id": 1,
            "assessment_id": 1,
            "language": "es",
            "score": 72.0,
            "recommended_level": "B1",
            "skill_scores": [
                {"skill": "grammar", "score": 80.0, "total": 10, "correct": 8},
                {"skill": "vocabulary", "score": 70.0, "total": 10, "correct": 7},
                {"skill": "listening", "score": 60.0, "total": 5, "correct": 3},
            ],
            "total_questions": 25,
            "correct_answers": 18,
            "started_at": "2024-01-01T10:00:00Z",
            "completed_at": "2024-01-01T10:30:00Z",
            "practice_recommendations": ["Focus on listening comprehension"],
        }
        response = AttemptResultResponse(**data)
        assert response.recommended_level == "B1"
        assert len(response.skill_scores) == 3
        assert response.skill_scores[0].skill == "grammar"
        assert response.practice_recommendations == ["Focus on listening comprehension"]

    def test_attempt_create_schema(self):
        """AttemptCreate should accept answers dict."""
        from app.models.schemas import AttemptCreate

        data = {
            "answers": {"1": "hablo", "2": "es", "3": "house"},
        }
        attempt = AttemptCreate(**data)
        assert attempt.answers == {"1": "hablo", "2": "es", "3": "house"}

    def test_user_level_update_schema(self):
        """UserLevelUpdate should validate CEFR level and score range."""
        from app.models.schemas import UserLevelUpdate

        # Valid data
        update = UserLevelUpdate(cefr_level="B1", proficiency_score=72.0)
        assert update.cefr_level == "B1"
        assert update.proficiency_score == 72.0

        # Invalid score (over 100)
        with pytest.raises(ValidationError):
            UserLevelUpdate(cefr_level="B1", proficiency_score=150.0)

        # Invalid score (negative)
        with pytest.raises(ValidationError):
            UserLevelUpdate(cefr_level="B1", proficiency_score=-10.0)


class TestAssessmentModels:
    """Test SQLAlchemy models for assessments."""

    def test_assessment_question_has_skill_category_column(self):
        """AssessmentQuestion model should have skill_category column."""
        from app.models.models import AssessmentQuestion

        # Check the column exists
        assert hasattr(AssessmentQuestion, "skill_category")

    def test_assessment_attempt_has_recommended_level_column(self):
        """AssessmentAttempt model should have recommended_level column."""
        from app.models.models import AssessmentAttempt

        assert hasattr(AssessmentAttempt, "recommended_level")

    def test_assessment_attempt_has_skill_scores_json_column(self):
        """AssessmentAttempt model should have skill_scores_json column."""
        from app.models.models import AssessmentAttempt

        assert hasattr(AssessmentAttempt, "skill_scores_json")
