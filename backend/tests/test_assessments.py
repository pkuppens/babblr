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


class TestScoringService:
    """Test assessment scoring service."""

    def test_calculate_scores_basic(self):
        """Should calculate overall and per-skill scores."""
        from app.services.scoring_service import calculate_scores

        questions = [
            {"id": 1, "skill_category": "grammar", "correct_answer": "a", "points": 1},
            {"id": 2, "skill_category": "grammar", "correct_answer": "b", "points": 1},
            {"id": 3, "skill_category": "vocabulary", "correct_answer": "c", "points": 1},
            {"id": 4, "skill_category": "vocabulary", "correct_answer": "d", "points": 1},
        ]
        answers = {1: "a", 2: "b", 3: "c", 4: "wrong"}  # 3/4 correct

        result = calculate_scores(questions, answers)

        assert result["overall"]["score"] == 75.0
        assert result["overall"]["correct"] == 3
        assert result["overall"]["total"] == 4
        assert result["grammar"]["score"] == 100.0  # 2/2
        assert result["vocabulary"]["score"] == 50.0  # 1/2

    def test_calculate_scores_empty_answers(self):
        """Should handle empty/missing answers."""
        from app.services.scoring_service import calculate_scores

        questions = [
            {"id": 1, "skill_category": "grammar", "correct_answer": "a", "points": 1},
        ]
        answers = {}  # No answers

        result = calculate_scores(questions, answers)
        assert result["overall"]["score"] == 0.0
        assert result["overall"]["correct"] == 0

    def test_determine_cefr_level_ranges(self):
        """Should map scores to correct CEFR levels."""
        from app.services.scoring_service import determine_cefr_level

        assert determine_cefr_level(10) == "A1"
        assert determine_cefr_level(30) == "A2"
        assert determine_cefr_level(50) == "B1"
        assert determine_cefr_level(70) == "B2"
        assert determine_cefr_level(85) == "C1"
        assert determine_cefr_level(95) == "C2"

    def test_determine_cefr_level_boundary_cases(self):
        """Should handle boundary scores correctly."""
        from app.services.scoring_service import determine_cefr_level

        assert determine_cefr_level(0) == "A1"
        assert determine_cefr_level(20) == "A1"
        assert determine_cefr_level(21) == "A2"
        assert determine_cefr_level(100) == "C2"

    def test_generate_practice_recommendations(self):
        """Should generate recommendations for weak areas."""
        from app.services.scoring_service import generate_practice_recommendations

        skill_scores = {
            "grammar": {"score": 80.0, "total": 10, "correct": 8},
            "vocabulary": {"score": 50.0, "total": 10, "correct": 5},
            "listening": {"score": 30.0, "total": 5, "correct": 1},
        }

        recommendations = generate_practice_recommendations(skill_scores)

        assert len(recommendations) >= 1
        # Should recommend focusing on listening (lowest)
        assert any("listening" in r.lower() for r in recommendations)

    def test_generate_no_recommendations_for_high_scores(self):
        """Should generate congratulatory message for high scores."""
        from app.services.scoring_service import generate_practice_recommendations

        skill_scores = {
            "grammar": {"score": 90.0, "total": 10, "correct": 9},
            "vocabulary": {"score": 85.0, "total": 10, "correct": 8},
        }

        recommendations = generate_practice_recommendations(skill_scores)
        # May have congratulatory message or be empty
        assert isinstance(recommendations, list)


class TestAssessmentSeedService:
    """Test assessment seed data service."""

    @pytest.mark.asyncio
    async def test_seed_creates_assessment(self, db):
        """Seed should create assessment with questions."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")

        assessment = await get_seeded_assessment(db, language="es")
        assert assessment is not None
        assert assessment.language == "es"
        assert assessment.assessment_type == "cefr_placement"
        assert len(assessment.assessment_questions) >= 15  # At least 15 questions

    @pytest.mark.asyncio
    async def test_seed_includes_all_skill_categories(self, db):
        """Seed should include questions for all skill categories."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        skill_categories = {q.skill_category for q in assessment.assessment_questions}
        assert "grammar" in skill_categories
        assert "vocabulary" in skill_categories

    @pytest.mark.asyncio
    async def test_seed_is_idempotent(self, db):
        """Running seed twice should not create duplicates."""
        from app.services.assessment_seed import get_all_assessments, seed_assessment_data

        await seed_assessment_data(db, language="es")
        await seed_assessment_data(db, language="es")

        assessments = await get_all_assessments(db, language="es")
        assert len(assessments) == 1  # Only one assessment

    @pytest.mark.asyncio
    async def test_questions_have_valid_structure(self, db):
        """Questions should have valid options and answers."""
        import json

        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        for question in assessment.assessment_questions:
            if question.question_type == "multiple_choice":
                options = json.loads(question.options)
                assert len(options) >= 2
                assert question.correct_answer in options


class TestListAssessmentsEndpoint:
    """Test GET /assessments endpoint."""

    def test_list_assessments_returns_empty_for_no_assessments(self, client):
        """Should return empty list when no assessments exist."""
        response = client.get("/assessments?language=es")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_assessments_returns_assessments_for_language(self, client, db):
        """Should return assessments for specified language."""
        from app.services.assessment_seed import seed_assessment_data

        await seed_assessment_data(db, language="es")

        response = client.get("/assessments?language=es")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["language"] == "es"
        assert "skill_categories" in data[0]
        assert "question_count" in data[0]

    def test_list_assessments_requires_language(self, client):
        """Should require language parameter."""
        response = client.get("/assessments")
        assert response.status_code == 422  # Validation error

    def test_list_assessments_validates_language(self, client):
        """Should validate language code."""
        response = client.get("/assessments?language=invalid")
        assert response.status_code == 400


class TestGetAssessmentEndpoint:
    """Test GET /assessments/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_assessment_returns_details(self, client, db):
        """Should return assessment with questions."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.get(f"/assessments/{assessment.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == assessment.id
        assert data["title"] is not None
        assert "questions" in data
        assert len(data["questions"]) > 0

    @pytest.mark.asyncio
    async def test_get_assessment_questions_ordered(self, client, db):
        """Questions should be ordered by order_index."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.get(f"/assessments/{assessment.id}")
        data = response.json()

        order_indices = [q["order_index"] for q in data["questions"]]
        assert order_indices == sorted(order_indices)

    @pytest.mark.asyncio
    async def test_get_assessment_excludes_correct_answers(self, client, db):
        """Should NOT include correct_answer in questions."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.get(f"/assessments/{assessment.id}")
        data = response.json()

        for question in data["questions"]:
            assert "correct_answer" not in question

    def test_get_assessment_not_found(self, client):
        """Should return 404 for non-existent assessment."""
        response = client.get("/assessments/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSubmitAttemptEndpoint:
    """Test POST /assessments/{id}/attempts endpoint."""

    @pytest.mark.asyncio
    async def test_submit_attempt_returns_results(self, client, db):
        """Should score answers and return results."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        # Get correct answers for some questions
        correct_answers = {str(q.id): q.correct_answer for q in assessment.assessment_questions[:5]}

        response = client.post(
            f"/assessments/{assessment.id}/attempts", json={"answers": correct_answers}
        )

        assert response.status_code == 200
        data = response.json()

        assert "score" in data
        assert "recommended_level" in data
        assert "skill_scores" in data
        assert data["correct_answers"] >= 5  # At least our correct ones

    @pytest.mark.asyncio
    async def test_submit_attempt_calculates_skill_breakdown(self, client, db):
        """Should return per-skill score breakdown."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.post(
            f"/assessments/{assessment.id}/attempts",
            json={"answers": {}},  # All wrong
        )

        data = response.json()
        skill_scores = data["skill_scores"]

        # Should have at least grammar and vocabulary
        skill_names = [s["skill"] for s in skill_scores]
        assert "grammar" in skill_names or "vocabulary" in skill_names

    @pytest.mark.asyncio
    async def test_submit_attempt_returns_practice_recommendations(self, client, db):
        """Should include practice recommendations."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.post(
            f"/assessments/{assessment.id}/attempts",
            json={"answers": {}},  # All wrong - should trigger recommendations
        )

        data = response.json()
        assert "practice_recommendations" in data
        assert isinstance(data["practice_recommendations"], list)

    @pytest.mark.asyncio
    async def test_submit_attempt_validates_question_ids(self, client, db):
        """Should reject invalid question IDs."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        response = client.post(
            f"/assessments/{assessment.id}/attempts", json={"answers": {"99999": "invalid"}}
        )

        assert response.status_code == 400
        assert "invalid question" in response.json()["detail"].lower()

    def test_submit_attempt_not_found(self, client):
        """Should return 404 for non-existent assessment."""
        response = client.post("/assessments/99999/attempts", json={"answers": {}})
        assert response.status_code == 404


class TestListAttemptsEndpoint:
    """Test GET /assessments/attempts endpoint."""

    @pytest.mark.asyncio
    async def test_list_attempts_returns_history(self, client, db):
        """Should return user's attempt history."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        # Submit two attempts
        for _ in range(2):
            client.post(f"/assessments/{assessment.id}/attempts", json={"answers": {}})

        response = client.get("/assessments/attempts?language=es")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert all(a["language"] == "es" for a in data)

    @pytest.mark.asyncio
    async def test_list_attempts_includes_assessment_title(self, client, db):
        """Should include assessment title in response."""
        from app.services.assessment_seed import get_seeded_assessment, seed_assessment_data

        await seed_assessment_data(db, language="es")
        assessment = await get_seeded_assessment(db, language="es")

        client.post(f"/assessments/{assessment.id}/attempts", json={"answers": {}})

        response = client.get("/assessments/attempts?language=es")
        data = response.json()

        assert data[0]["assessment_title"] is not None


class TestUserLevelEndpoints:
    """Test user level endpoints."""

    def test_update_level_creates_new_record(self, client):
        """Should create new level record if none exists."""
        response = client.put(
            "/user-levels/es", json={"cefr_level": "B1", "proficiency_score": 72.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es"
        assert data["cefr_level"] == "B1"
        assert data["proficiency_score"] == 72.0

    def test_update_level_updates_existing(self, client):
        """Should update existing level record."""
        # Create initial level
        client.put("/user-levels/es", json={"cefr_level": "A1", "proficiency_score": 30.0})

        # Update
        response = client.put(
            "/user-levels/es", json={"cefr_level": "B1", "proficiency_score": 72.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cefr_level"] == "B1"
        assert data["proficiency_score"] == 72.0

    def test_update_level_validates_cefr(self, client):
        """Should validate CEFR level."""
        response = client.put(
            "/user-levels/es", json={"cefr_level": "X1", "proficiency_score": 50.0}
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_update_level_validates_score_range(self, client):
        """Should validate proficiency score range."""
        response = client.put(
            "/user-levels/es", json={"cefr_level": "B1", "proficiency_score": 150.0}
        )

        assert response.status_code == 422  # Pydantic validation

    def test_get_user_level(self, client):
        """Should return user level for language."""
        client.put("/user-levels/es", json={"cefr_level": "B1", "proficiency_score": 72.0})

        response = client.get("/user-levels/es")
        assert response.status_code == 200
        assert response.json()["cefr_level"] == "B1"

    def test_get_user_level_not_found(self, client):
        """Should return 404 if no level exists."""
        response = client.get("/user-levels/xx")
        assert response.status_code == 404
