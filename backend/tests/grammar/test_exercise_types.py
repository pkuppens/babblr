"""Tests for multiple exercise types (Issue 6)."""

from app.grammar.models import Exercise
from app.grammar.service import validate_exercise_answer


def test_validate_multiple_choice_correct():
    """Test validating correct multiple choice answer."""
    exercise = Exercise(
        id="ex1",
        type="multiple_choice",
        question="Choose the correct form",
        options=["hablo", "hablas", "habla"],
        correct_answer=0,
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, 0) is True
    assert validate_exercise_answer(exercise, 1) is False


def test_validate_multiple_choice_string_int():
    """Test that string "0" can be converted to int for multiple choice."""
    exercise = Exercise(
        id="ex1",
        type="multiple_choice",
        question="Test",
        options=["a", "b"],
        correct_answer=0,
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, "0") is True
    assert validate_exercise_answer(exercise, "1") is False


def test_validate_fill_in_blank_correct():
    """Test validating correct fill-in-blank answer."""
    exercise = Exercise(
        id="ex2",
        type="fill_in_blank",
        question="Complete: Yo ___ español.",
        correct_answer="hablo",
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, "hablo") is True
    assert validate_exercise_answer(exercise, "hablas") is False


def test_validate_fill_in_blank_case_insensitive():
    """Test that fill-in-blank is case-insensitive."""
    exercise = Exercise(
        id="ex2",
        type="fill_in_blank",
        question="Test",
        correct_answer="hablo",
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, "HABLO") is True
    assert validate_exercise_answer(exercise, "Hablo") is True
    assert validate_exercise_answer(exercise, "hablo") is True


def test_validate_fill_in_blank_strips_whitespace():
    """Test that fill-in-blank strips whitespace."""
    exercise = Exercise(
        id="ex2",
        type="fill_in_blank",
        question="Test",
        correct_answer="hablo",
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, "  hablo  ") is True
    assert validate_exercise_answer(exercise, "hablo ") is True
    assert validate_exercise_answer(exercise, " hablo") is True


def test_validate_word_order_correct():
    """Test validating correct word order answer."""
    exercise = Exercise(
        id="ex3",
        type="word_order",
        question="Arrange the words",
        correct_answer=["¿", "Dónde", "vives", "?"],
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, ["¿", "Dónde", "vives", "?"]) is True
    assert validate_exercise_answer(exercise, ["Dónde", "¿", "vives", "?"]) is False


def test_validate_unknown_type():
    """Test that unknown exercise type returns False."""
    exercise = Exercise(
        id="ex4",
        type="unknown_type",
        question="Test",
        correct_answer="test",
        explanation="Test",
    )
    assert validate_exercise_answer(exercise, "test") is False
