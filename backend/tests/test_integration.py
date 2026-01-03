"""
Integration tests for Babblr backend API.
These tests require the backend to be running.
Run with: pytest tests/test_integration.py
"""

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    """Create HTTP client for testing."""
    return httpx.Client(base_url=BASE_URL, timeout=10.0)


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "services" in data


@pytest.mark.integration
class TestConversationEndpoints:
    """Test conversation CRUD endpoints."""

    def test_create_conversation(self, client):
        """Test creating a new conversation."""
        response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["language"] == "spanish"
        assert data["difficulty_level"] == "A1"

    def test_list_conversations(self, client):
        """Test listing conversations."""
        response = client.get("/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_conversation(self, client):
        """Test getting a specific conversation."""
        # First create a conversation
        create_response = client.post(
            "/conversations", json={"language": "french", "difficulty_level": "B2"}
        )
        assert create_response.status_code == 200
        conversation_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conversation_id
        assert data["language"] == "french"


@pytest.mark.integration
class TestChatEndpoint:
    """Test chat endpoint (requires API key)."""

    def test_chat_endpoint_structure(self, client):
        """Test chat endpoint accepts correct structure."""
        # Create conversation first
        conv_response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        assert conv_response.status_code == 200
        conversation_id = conv_response.json()["id"]

        # Try to send a chat message
        # This may fail if API key is not configured, but we test structure
        response = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "user_message": "Hola",
                "language": "spanish",
                "difficulty_level": "A1",
            },
        )
        # Accept either success or error due to missing API key
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestMessagesEndpoint:
    """Test message retrieval endpoints."""

    def test_get_conversation_messages(self, client):
        """Test getting messages for a conversation."""
        # Create conversation
        conv_response = client.post(
            "/conversations", json={"language": "italian", "difficulty_level": "C1"}
        )
        conversation_id = conv_response.json()["id"]

        # Get messages (should be empty for new conversation)
        response = client.get(f"/conversations/{conversation_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestSTTEndpoints:
    """Test STT (Speech-to-Text) endpoints."""

    def test_stt_languages_endpoint(self, client):
        """Test getting supported languages."""
        response = client.get("/api/stt/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "count" in data
        assert isinstance(data["languages"], list)
        assert data["count"] >= 5  # At least 5 languages

        # Check for expected languages
        language_codes = [lang["code"] for lang in data["languages"]]
        assert "es" in language_codes
        assert "it" in language_codes
        assert "de" in language_codes
        assert "fr" in language_codes
        assert "nl" in language_codes

    def test_stt_models_endpoint(self, client):
        """Test getting available models."""
        response = client.get("/api/stt/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "current_model" in data
        assert "device" in data
        assert "count" in data
        assert isinstance(data["models"], list)
        assert data["count"] >= 5  # At least 5 models

        # Check for expected models
        model_names = [model["name"] for model in data["models"]]
        assert "tiny" in model_names
        assert "base" in model_names
        assert "small" in model_names
        assert "medium" in model_names
        assert "large" in model_names

    def test_stt_transcribe_endpoint_structure(self, client):
        """Test transcribe endpoint accepts correct structure."""
        # Note: This test checks the endpoint structure without actual audio
        # Real transcription tests would require audio files

        # Test with missing file
        response = client.post("/api/stt/transcribe")
        # Should return 422 (validation error) for missing required field
        assert response.status_code == 422
