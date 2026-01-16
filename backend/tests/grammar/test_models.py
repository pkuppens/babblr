"""Unit tests for grammar lesson Pydantic models."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.grammar.models import (
    Exercise,
    GrammarLesson,
    LessonProgress,
    TopicVocabularyProgress,
)
from app.models.cefr import CEFRLevel


class TestExercise:
    """Tests for Exercise model."""

    def test_exercise_multiple_choice(self):
        """Test creating a multiple choice exercise."""
        exercise = Exercise(
            id="ex1",
            type="multiple_choice",
            question="Choose the correct form",
            options=["hablo", "hablas", "habla"],
            correct_answer=0,
            explanation="'Hablo' is the first person singular form.",
        )
        assert exercise.id == "ex1"
        assert exercise.type == "multiple_choice"
        assert exercise.options == ["hablo", "hablas", "habla"]
        assert exercise.correct_answer == 0
        assert exercise.explanation == "'Hablo' is the first person singular form."

    def test_exercise_fill_in_blank(self):
        """Test creating a fill-in-blank exercise."""
        exercise = Exercise(
            id="ex2",
            type="fill_in_blank",
            question="Complete: Yo ___ español.",
            correct_answer="hablo",
            explanation="'Hablo' is the correct first person form.",
        )
        assert exercise.type == "fill_in_blank"
        assert exercise.options is None
        assert exercise.correct_answer == "hablo"

    def test_exercise_serialization(self):
        """Test that exercise can be serialized to JSON."""
        exercise = Exercise(
            id="ex1",
            type="multiple_choice",
            question="Test question",
            options=["a", "b", "c"],
            correct_answer=0,
            explanation="Test explanation",
        )
        json_data = exercise.model_dump()
        assert json_data["id"] == "ex1"
        assert json_data["type"] == "multiple_choice"
        assert isinstance(json_data, dict)


class TestGrammarLesson:
    """Tests for GrammarLesson model."""

    def test_grammar_lesson_creation(self):
        """Test creating a grammar lesson with all fields."""
        exercise = Exercise(
            id="ex1",
            type="multiple_choice",
            question="Test question",
            correct_answer=0,
            explanation="Test explanation",
        )
        lesson = GrammarLesson(
            id="lesson1",
            title="Present Tense",
            language="es",
            level=CEFRLevel.A1,
            explanation="The present tense is used for current actions.",
            examples=["Yo hablo español.", "Tú hablas inglés."],
            exercises=[exercise],
            topic_id="shopping",
        )
        assert lesson.id == "lesson1"
        assert lesson.title == "Present Tense"
        assert lesson.language == "es"
        assert lesson.level == CEFRLevel.A1
        assert len(lesson.examples) == 2
        assert len(lesson.exercises) == 1
        assert lesson.topic_id == "shopping"

    def test_grammar_lesson_without_topic(self):
        """Test creating a grammar lesson without topic link."""
        lesson = GrammarLesson(
            id="lesson2",
            title="Ser vs Estar",
            language="es",
            level=CEFRLevel.A1,
            explanation="Ser and estar both mean 'to be'.",
            examples=["Soy estudiante.", "Estoy en casa."],
            exercises=[],
        )
        assert lesson.topic_id is None

    def test_grammar_lesson_serialization(self):
        """Test that grammar lesson can be serialized to JSON."""
        lesson = GrammarLesson(
            id="lesson1",
            title="Test Lesson",
            language="es",
            level=CEFRLevel.A1,
            explanation="Test explanation",
            examples=["Example 1"],
            exercises=[],
        )
        json_data = lesson.model_dump()
        assert json_data["id"] == "lesson1"
        assert json_data["level"] == "A1"
        assert isinstance(json_data["examples"], list)
        assert isinstance(json_data["exercises"], list)

    def test_grammar_lesson_cefr_level_validation(self):
        """Test that CEFR level must be valid."""
        with pytest.raises(ValidationError):
            GrammarLesson(
                id="lesson1",
                title="Test",
                language="es",
                level="INVALID",  # type: ignore[arg-type]
                explanation="Test",
                examples=[],
                exercises=[],
            )


class TestLessonProgress:
    """Tests for LessonProgress model."""

    def test_lesson_progress_creation(self):
        """Test creating lesson progress with all fields."""
        now = datetime.now()
        next_review = now + timedelta(days=7)
        progress = LessonProgress(
            user_id="user123",
            lesson_id="lesson1",
            completed=True,
            mastery_score=0.85,
            last_reviewed=now,
            next_review=next_review,
        )
        assert progress.user_id == "user123"
        assert progress.lesson_id == "lesson1"
        assert progress.completed is True
        assert progress.mastery_score == 0.85
        assert progress.last_reviewed == now
        assert progress.next_review == next_review

    def test_lesson_progress_defaults(self):
        """Test lesson progress with default values."""
        progress = LessonProgress(user_id="user123", lesson_id="lesson1")
        assert progress.completed is False
        assert progress.mastery_score == 0.0
        assert progress.last_reviewed is None
        assert progress.next_review is None

    def test_lesson_progress_mastery_score_validation(self):
        """Test that mastery score must be between 0.0 and 1.0."""
        # Valid scores
        progress1 = LessonProgress(user_id="user1", lesson_id="lesson1", mastery_score=0.0)
        assert progress1.mastery_score == 0.0

        progress2 = LessonProgress(user_id="user2", lesson_id="lesson1", mastery_score=1.0)
        assert progress2.mastery_score == 1.0

        # Invalid scores
        with pytest.raises(ValidationError):
            LessonProgress(user_id="user3", lesson_id="lesson1", mastery_score=-0.1)

        with pytest.raises(ValidationError):
            LessonProgress(user_id="user4", lesson_id="lesson1", mastery_score=1.1)

    def test_lesson_progress_serialization(self):
        """Test that lesson progress can be serialized to JSON."""
        now = datetime.now()
        progress = LessonProgress(
            user_id="user123",
            lesson_id="lesson1",
            completed=True,
            mastery_score=0.75,
            last_reviewed=now,
        )
        json_data = progress.model_dump()
        assert json_data["user_id"] == "user123"
        assert json_data["completed"] is True
        assert json_data["mastery_score"] == 0.75
        assert "last_reviewed" in json_data


class TestTopicVocabularyProgress:
    """Tests for TopicVocabularyProgress model."""

    def test_topic_vocabulary_progress_creation(self):
        """Test creating topic vocabulary progress."""
        progress = TopicVocabularyProgress(
            user_id="user123",
            topic_id="shopping",
            language="es",
            vocabulary_mastery={
                "comprar": 0.9,
                "vender": 0.7,
                "pagar": 0.85,
            },
        )
        assert progress.user_id == "user123"
        assert progress.topic_id == "shopping"
        assert progress.language == "es"
        assert len(progress.vocabulary_mastery) == 3
        assert progress.vocabulary_mastery["comprar"] == 0.9

    def test_topic_vocabulary_progress_empty(self):
        """Test topic vocabulary progress with empty mastery dict."""
        progress = TopicVocabularyProgress(
            user_id="user123",
            topic_id="shopping",
            language="es",
            vocabulary_mastery={},
        )
        assert len(progress.vocabulary_mastery) == 0

    def test_topic_vocabulary_progress_serialization(self):
        """Test that topic vocabulary progress can be serialized to JSON."""
        progress = TopicVocabularyProgress(
            user_id="user123",
            topic_id="shopping",
            language="es",
            vocabulary_mastery={"word1": 0.8, "word2": 0.6},
        )
        json_data = progress.model_dump()
        assert json_data["user_id"] == "user123"
        assert isinstance(json_data["vocabulary_mastery"], dict)
        assert json_data["vocabulary_mastery"]["word1"] == 0.8
