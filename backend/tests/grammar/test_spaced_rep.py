"""Tests for spaced repetition algorithm (Issue 5)."""

from datetime import datetime, timezone

from app.routes.grammar import calculate_next_review_date


def test_calculate_next_review_high_mastery():
    """Test that high mastery (>=0.9) results in 14 day interval."""
    last_reviewed = datetime.now(timezone.utc)
    next_review = calculate_next_review_date(0.95, last_reviewed)
    interval = (next_review - last_reviewed).days
    assert interval == 14


def test_calculate_next_review_medium_high_mastery():
    """Test that medium-high mastery (>=0.7) results in 7 day interval."""
    last_reviewed = datetime.now(timezone.utc)
    next_review = calculate_next_review_date(0.75, last_reviewed)
    interval = (next_review - last_reviewed).days
    assert interval == 7


def test_calculate_next_review_medium_mastery():
    """Test that medium mastery (>=0.5) results in 3 day interval."""
    last_reviewed = datetime.now(timezone.utc)
    next_review = calculate_next_review_date(0.6, last_reviewed)
    interval = (next_review - last_reviewed).days
    assert interval == 3


def test_calculate_next_review_low_mastery():
    """Test that low mastery (<0.5) results in 1 day interval."""
    last_reviewed = datetime.now(timezone.utc)
    next_review = calculate_next_review_date(0.3, last_reviewed)
    interval = (next_review - last_reviewed).days
    assert interval == 1


def test_calculate_next_review_none_mastery():
    """Test that None mastery defaults to 0.5 (3 day interval)."""
    last_reviewed = datetime.now(timezone.utc)
    next_review = calculate_next_review_date(None, last_reviewed)
    interval = (next_review - last_reviewed).days
    assert interval == 3  # Defaults to 0.5, which is >= 0.5 but < 0.7


def test_calculate_next_review_boundary_values():
    """Test boundary values for mastery scores."""
    last_reviewed = datetime.now(timezone.utc)

    # Exactly 0.9
    next_review = calculate_next_review_date(0.9, last_reviewed)
    assert (next_review - last_reviewed).days == 14

    # Exactly 0.7
    next_review = calculate_next_review_date(0.7, last_reviewed)
    assert (next_review - last_reviewed).days == 7

    # Exactly 0.5
    next_review = calculate_next_review_date(0.5, last_reviewed)
    assert (next_review - last_reviewed).days == 3

    # Just below 0.5
    next_review = calculate_next_review_date(0.49, last_reviewed)
    assert (next_review - last_reviewed).days == 1
