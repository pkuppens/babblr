"""Integration test for POST /chat/initial-message endpoint with actual HTTP calls.

This test makes real HTTP requests to verify the endpoint works correctly.
"""

import logging

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Conversation, Message

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_initial_message_endpoint_with_payload(async_client: AsyncClient, db: AsyncSession):
    """Test the initial message endpoint with a real payload.

    This test makes real HTTP requests that require Ollama to be running,
    so it must be marked as an integration test.
    """
    # Create a conversation
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="restaurant",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    # Make the actual HTTP request
    payload = {
        "conversation_id": conversation.id,
        "language": "spanish",
        "difficulty_level": "A1",
        "topic_id": "restaurant",
    }

    response = await async_client.post("/chat/initial-message", json=payload)

    # Debug: Log response if it fails
    if response.status_code != 200:
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")
        logger.debug(f"Request payload: {payload}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "assistant_message" in data
    assert len(data["assistant_message"]) > 0

    # Verify message was saved
    result = await db.execute(select(Message).where(Message.conversation_id == conversation.id))
    messages = result.scalars().all()
    assert len(messages) == 1
    assert messages[0].role == "assistant"
    assert messages[0].content == data["assistant_message"]


@pytest.mark.asyncio
async def test_initial_message_validation_errors(async_client: AsyncClient):
    """Test that validation errors are returned correctly."""
    # Missing conversation_id
    response = await async_client.post(
        "/chat/initial-message",
        json={
            "language": "spanish",
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )
    assert response.status_code == 422
    errors = response.json()
    assert "detail" in errors

    # Missing language
    response = await async_client.post(
        "/chat/initial-message",
        json={
            "conversation_id": 1,
            "difficulty_level": "A1",
            "topic_id": "restaurant",
        },
    )
    assert response.status_code == 422

    # Missing topic_id
    response = await async_client.post(
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
async def test_initial_message_restaurant_topic(async_client: AsyncClient, db: AsyncSession):
    """Test initial message for restaurant topic returns relevant content."""
    conversation = Conversation(
        language="spanish",
        difficulty_level="A1",
        topic_id="restaurant",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    response = await async_client.post(
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

    # Check for restaurant-related keywords
    restaurant_keywords = ["restaurante", "mesa", "comida", "menú", "pedir", "waiter", "order"]
    assert any(keyword in message for keyword in restaurant_keywords), (
        f"Message should contain restaurant keywords. Got: {data['assistant_message']}"
    )
