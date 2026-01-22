"""Integration test for POST /chat/initial-message endpoint.

This test verifies that the endpoint:
1. Accepts a conversation_id, language, difficulty_level, and topic_id
2. Returns a useful initial message from the roleplaying tutor
3. Saves the message to the database
4. The message is contextually relevant to the topic
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Conversation, Message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_creates_tutor_message(client: TestClient, db: AsyncSession):
    """Test that initial message endpoint creates a tutor message in the database."""
    # Create a conversation first
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="restaurant",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    # Call the initial message endpoint
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": conversation.id,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "assistant_message" in data
    assert len(data["assistant_message"]) > 0
    assert data["assistant_message"].strip() != ""

    # Verify message was saved to database
    messages_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation.id)
    )
    messages = messages_result.scalars().all()

    assert len(messages) == 1
    message = messages[0]
    assert message.role == "assistant"
    assert len(message.content) > 0
    assert message.content == data["assistant_message"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_restaurant_topic(client: TestClient, db: AsyncSession):
    """Test that initial message for restaurant topic is contextually relevant."""
    # Create conversation with restaurant topic
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="restaurant",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    # Call endpoint
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": conversation.id,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )

    assert response.status_code == 200
    data = response.json()
    message = data["assistant_message"].lower()

    # Verify message is about restaurant context
    # Should mention restaurant-related terms (in Spanish or English)
    restaurant_keywords = [
        "restaurante",
        "mesa",
        "comida",
        "menú",
        "pedir",
        "waiter",
        "order",
        "food",
        "menu",
    ]
    assert any(keyword in message for keyword in restaurant_keywords), (
        f"Message should contain restaurant-related keywords. Got: {data['assistant_message']}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_travel_topic(client: TestClient, db: AsyncSession):
    """Test that initial message for travel topic is contextually relevant."""
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="travel",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": conversation.id,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "travel",
        },
    )

    assert response.status_code == 200
    data = response.json()
    message = data["assistant_message"].lower()

    # Verify message is about travel
    travel_keywords = [
        "viaje",
        "viajar",
        "transporte",
        "avión",
        "tren",
        "autobús",
        "travel",
        "trip",
        "transport",
    ]
    assert any(keyword in message for keyword in travel_keywords), (
        f"Message should contain travel-related keywords. Got: {data['assistant_message']}"
    )


@pytest.mark.asyncio
async def test_initial_message_invalid_conversation(client: TestClient, db: AsyncSession):
    """Test that endpoint returns 404 for non-existent conversation."""
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": 99999,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_initial_message_invalid_topic(client: TestClient, db: AsyncSession):
    """Test that endpoint returns 404 for non-existent topic."""
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id=None,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": conversation.id,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "nonexistent_topic",
        },
    )

    assert response.status_code == 404
    assert "topic" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_initial_message_validates_request_body(client: TestClient, db: AsyncSession):
    """Test that endpoint validates required fields in request body."""
    # Missing conversation_id
    response = client.post(
        "/chat/initial-message",
        json={
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )
    assert response.status_code == 422  # Validation error

    # Missing language
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": 1,
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )
    assert response.status_code == 422

    # Missing topic_id
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": 1,
            "language": "spanish",
            "difficulty_level": "A1",
        },
    )
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_updates_conversation_timestamp(client: TestClient, db: AsyncSession):
    """Test that generating initial message updates conversation timestamp."""
    # Create conversation with old timestamp
    from datetime import datetime, timedelta, timezone

    old_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="restaurant",
        updated_at=old_time,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    original_updated_at = conversation.updated_at

    # Generate initial message
    response = client.post(
        "/chat/initial-message",
        json={
            "conversation_id": conversation.id,
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )

    assert response.status_code == 200

    # Refresh conversation and verify timestamp was updated
    await db.refresh(conversation)
    assert conversation.updated_at > original_updated_at


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_different_languages(client: TestClient, db: AsyncSession):
    """Test that initial message works for different languages."""
    languages = ["spanish", "italian", "german", "french", "dutch"]

    for lang in languages:
        conversation = Conversation(
            language=lang,
            difficulty_level="A1",
            topic_id="restaurant",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        response = client.post(
            "/chat/initial-message",
            json={
                "conversation_id": conversation.id,
                "language": lang,
                "difficulty_level": "A1",
                "topic_id": "restaurant",
            },
        )

        assert response.status_code == 200, f"Failed for language: {lang}"
        data = response.json()
        assert len(data["assistant_message"]) > 0, f"Empty message for language: {lang}"

        # Clean up
        await db.delete(conversation)
        await db.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_different_difficulty_levels(client: TestClient, db: AsyncSession):
    """Test that initial message adapts to different difficulty levels."""
    levels = ["A1", "A2", "B1", "B2"]

    for level in levels:
        conversation = Conversation(
            language="spanish",
            difficulty_level=level,
            topic_id="restaurant",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        response = client.post(
            "/chat/initial-message",
            json={
                "conversation_id": conversation.id,
                "language": "spanish",
                "difficulty_level": level,
                "topic_id": "restaurant",
            },
        )

        assert response.status_code == 200, f"Failed for level: {level}"
        data = response.json()
        assert len(data["assistant_message"]) > 0, f"Empty message for level: {level}"

        # Clean up
        await db.delete(conversation)
        await db.commit()
