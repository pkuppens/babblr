"""
Tests for timezone-aware datetime handling throughout the application.

Ensures all timestamps are stored and serialized as timezone-aware UTC datetimes.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Conversation, Message


@pytest.mark.asyncio
async def test_conversation_created_at_is_timezone_aware(db: AsyncSession):
    """Test that conversation created_at is timezone-aware UTC."""
    # Create a conversation
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # Verify created_at is timezone-aware
    assert conv.created_at is not None
    assert conv.created_at.tzinfo is not None
    assert conv.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_conversation_updated_at_is_timezone_aware(db: AsyncSession):
    """Test that conversation updated_at is timezone-aware UTC."""
    # Create a conversation
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # Verify updated_at is timezone-aware
    assert conv.updated_at is not None
    assert conv.updated_at.tzinfo is not None
    assert conv.updated_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_message_created_at_is_timezone_aware(db: AsyncSession):
    """Test that message created_at is timezone-aware UTC."""
    # Create a conversation first
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # Create a message
    msg = Message(conversation_id=conv.id, role="user", content="Hola, ¿cómo estás?")
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # Verify created_at is timezone-aware
    assert msg.created_at is not None
    assert msg.created_at.tzinfo is not None
    assert msg.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_datetime_serialization_includes_timezone(db: AsyncSession):
    """Test that datetime serialization includes timezone information."""
    # Create a conversation
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # Get the created_at as ISO format string
    iso_string = conv.created_at.isoformat()

    # Verify it includes timezone info (either 'Z' or +HH:MM)
    assert iso_string.endswith("Z") or ("+" in iso_string or iso_string.count("-") > 2), (
        f"ISO string missing timezone: {iso_string}"
    )


@pytest.mark.asyncio
async def test_datetime_roundtrip_preserves_utc(db: AsyncSession):
    """Test that datetime values survive database roundtrip as UTC."""
    # Create a conversation and record the exact time
    before = datetime.now(timezone.utc)
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    after = datetime.now(timezone.utc)

    # Verify created_at is within expected range and timezone-aware
    assert before <= conv.created_at <= after
    assert conv.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_multiple_datetimes_are_independent(db: AsyncSession):
    """Test that multiple datetime fields on same model are independent."""
    # Create a conversation
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # Both should be timezone-aware UTC
    assert conv.created_at.tzinfo == timezone.utc
    assert conv.updated_at.tzinfo == timezone.utc

    # They should be equal for a newly created record
    assert conv.created_at == conv.updated_at


@pytest.mark.asyncio
async def test_datetime_offset_is_zero(db: AsyncSession):
    """Test that UTC offset is exactly zero (no timezone bias)."""
    # Create a conversation
    conv = Conversation(language="es", difficulty_level="A1")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    # UTC offset should be zero
    assert conv.created_at.utcoffset().total_seconds() == 0
    assert conv.updated_at.utcoffset().total_seconds() == 0


def test_datetime_formats_correctly_for_json():
    """Test that datetime formats correctly for JSON serialization.

    This tests the frontend's expectation that datetime strings either:
    1. End with 'Z' (indicate UTC)
    2. Have +/-HH:MM offset indicator
    """
    # Create a timezone-aware UTC datetime
    dt = datetime(2026, 1, 22, 13, 3, 0, tzinfo=timezone.utc)

    # Convert to ISO format (what Pydantic does)
    iso_str = dt.isoformat()

    # Should end with 'Z' or have timezone offset
    assert iso_str.endswith("Z") or ("+" in iso_str or iso_str.count("-") > 2), (
        f"ISO format missing timezone indicator: {iso_str}"
    )

    # Parse it back - Python should understand the timezone
    parsed = datetime.fromisoformat(iso_str)
    assert parsed.tzinfo is not None
    assert parsed == dt


def test_naive_datetime_detection():
    """Test that naive datetimes (problematic format) can be detected."""
    # Create a naive datetime (the problematic case)
    naive_dt = datetime(2026, 1, 22, 13, 3, 0)

    # This is what was causing the problem
    iso_str = naive_dt.isoformat()

    # Verify it lacks timezone info
    assert not iso_str.endswith("Z")
    assert "+" not in iso_str

    # This is the case the frontend migration handles
    assert not naive_dt.isoformat().endswith("Z")


def test_frontend_datetime_normalization_logic():
    """Test the frontend's datetime normalization logic that adds 'Z' when missing."""
    # Simulate what frontend does with naive datetime from old backend
    naive_iso = "2026-01-22T13:03:00"

    # Frontend should add 'Z' if missing and looks like valid ISO datetime
    import re

    if not naive_iso.endswith("Z") and re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", naive_iso):
        normalized = naive_iso + "Z"
    else:
        normalized = naive_iso

    # Verify it's now parseable as UTC
    assert normalized.endswith("Z")
    parsed = datetime.fromisoformat(normalized)
    assert parsed.tzinfo == timezone.utc
    assert parsed.year == 2026
    assert parsed.month == 1
    assert parsed.day == 22
    assert parsed.hour == 13
