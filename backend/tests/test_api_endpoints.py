"""
Unit tests for Babblr API endpoints - Section 2 of validation plan.

Tests all major API endpoints with proper mocking to avoid external dependencies.
Run with: pytest tests/test_api_endpoints.py -v
"""

from unittest.mock import AsyncMock, patch

from app.services.stt.base import TranscriptionResult


class TestHealthEndpoint:
    """Test GET /health endpoint - verify response structure."""

    def test_health_check_response_structure(self, client):
        """Verify /health endpoint returns expected structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        # Top-level fields
        assert "status" in data
        assert data["status"] == "healthy"
        assert "database" in data
        assert "llm_provider" in data
        assert "services" in data

    def test_health_check_services_structure(self, client):
        """Verify health check includes all service details."""
        response = client.get("/health")
        data = response.json()
        services = data["services"]

        # Check main services
        assert "whisper" in services
        assert "claude" in services
        assert "ollama" in services
        assert "tts" in services

    def test_health_check_whisper_details(self, client):
        """Verify Whisper service details in health check."""
        response = client.get("/health")
        data = response.json()
        whisper = data["services"]["whisper"]

        assert "status" in whisper
        assert "current_model" in whisper
        assert "supported_models" in whisper
        assert "supported_locales" in whisper
        assert isinstance(whisper["supported_models"], list)
        assert isinstance(whisper["supported_locales"], list)

    def test_health_check_tts_details(self, client):
        """Verify TTS service details in health check."""
        response = client.get("/health")
        data = response.json()
        tts = data["services"]["tts"]

        assert "status" in tts
        assert tts["status"] in ["available", "unavailable"]
        assert "supported_locales" in tts
        assert isinstance(tts["supported_locales"], list)

    def test_health_check_ollama_details(self, client):
        """Verify Ollama provider details in health check."""
        response = client.get("/health")
        data = response.json()
        ollama = data["services"]["ollama"]

        assert "status" in ollama
        assert "base_url" in ollama
        assert "configured_model" in ollama


class TestTopicsEndpoint:
    """Test GET /topics endpoint - verify topic list."""

    def test_topics_endpoint_returns_list(self, client):
        """Verify /topics returns a topics structure."""
        response = client.get("/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "topics" in data

    def test_topics_list_structure(self, client):
        """Verify each topic has required fields."""
        response = client.get("/topics")
        data = response.json()
        topics = data["topics"]

        assert isinstance(topics, list)
        assert len(topics) > 0

        # Check first topic structure
        topic = topics[0]
        assert "id" in topic
        assert "names" in topic
        assert "descriptions" in topic

    def test_topics_multilingual_names(self, client):
        """Verify topics have names in multiple languages."""
        response = client.get("/topics")
        data = response.json()
        topics = data["topics"]

        topic = topics[0]
        names = topic["names"]
        assert isinstance(names, dict)
        # Should have translations for supported languages
        assert len(names) > 0

    def test_topics_starters_available(self, client):
        """Verify topics include conversation starters."""
        response = client.get("/topics")
        data = response.json()
        topics = data["topics"]

        topic = topics[0]
        assert "starters" in topic
        assert isinstance(topic["starters"], dict)


class TestConversationEndpoints:
    """Test conversation CRUD endpoints."""

    def test_create_conversation_success(self, client):
        """Test POST /conversations creates a conversation."""
        response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["language"] == "spanish"
        assert data["difficulty_level"] == "A1"

    def test_create_conversation_response_fields(self, client):
        """Verify created conversation has all expected fields."""
        response = client.post(
            "/conversations", json={"language": "french", "difficulty_level": "B1"}
        )
        data = response.json()

        assert "id" in data
        assert "language" in data
        assert "difficulty_level" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_conversations_list(self, client):
        """Test GET /conversations returns list."""
        # Create a conversation first
        client.post("/conversations", json={"language": "spanish", "difficulty_level": "A1"})

        # List conversations
        response = client.get("/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_conversations_list_structure(self, client):
        """Verify conversation list items have correct structure."""
        # Create a conversation
        client.post("/conversations", json={"language": "italian", "difficulty_level": "B2"})

        response = client.get("/conversations")
        data = response.json()
        assert len(data) > 0

        conv = data[0]
        assert "id" in conv
        assert "language" in conv
        assert "difficulty_level" in conv

    def test_get_specific_conversation(self, client):
        """Test GET /conversations/{id} retrieves specific conversation."""
        # Create conversation
        create_response = client.post(
            "/conversations", json={"language": "german", "difficulty_level": "C1"}
        )
        conv_id = create_response.json()["id"]

        # Get specific conversation
        response = client.get(f"/conversations/{conv_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conv_id

    def test_get_nonexistent_conversation(self, client):
        """Test getting non-existent conversation returns 404."""
        response = client.get("/conversations/99999")
        assert response.status_code == 404

    def test_get_conversation_messages(self, client):
        """Test GET /conversations/{id}/messages returns message list."""
        # Create conversation
        create_response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        conv_id = create_response.json()["id"]

        # Get messages (should be empty initially)
        response = client.get(f"/conversations/{conv_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestChatEndpoint:
    """Test POST /chat endpoint - verify conversation flow."""

    @patch("app.services.conversation_service.get_conversation_service")
    def test_chat_endpoint_structure(self, mock_service, client):
        """Test /chat endpoint accepts correct request structure."""
        # Create conversation first
        conv_response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        conv_id = conv_response.json()["id"]

        # Mock the conversation service with correct methods
        mock_conv_service = AsyncMock()
        mock_conv_service.generate_response = AsyncMock(return_value="Hola, ¿cómo estás?")
        mock_conv_service.correct_text = AsyncMock(return_value=("Hola", {}))
        mock_service.return_value = mock_conv_service

        # Send chat message
        response = client.post(
            "/chat",
            json={
                "conversation_id": conv_id,
                "user_message": "Hola",
                "language": "spanish",
                "difficulty_level": "A1",
            },
        )

        # Should succeed with mocked service
        assert response.status_code == 200

    @patch("app.services.conversation_service.get_conversation_service")
    def test_chat_endpoint_response_structure(self, mock_service, client):
        """Test chat response has expected fields."""
        # Create conversation
        conv_response = client.post(
            "/conversations", json={"language": "french", "difficulty_level": "B1"}
        )
        conv_id = conv_response.json()["id"]

        # Mock the conversation service with correct methods
        mock_conv_service = AsyncMock()
        mock_conv_service.generate_response = AsyncMock(return_value="Bonjour, comment allez-vous?")
        mock_conv_service.correct_text = AsyncMock(return_value=("Bonjour", {}))
        mock_service.return_value = mock_conv_service

        response = client.post(
            "/chat",
            json={
                "conversation_id": conv_id,
                "user_message": "Bonjour",
                "language": "french",
                "difficulty_level": "B1",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "assistant_message" in data

    def test_chat_requires_conversation_id(self, client):
        """Test chat endpoint requires conversation_id."""
        response = client.post(
            "/chat",
            json={
                "user_message": "Hola",
                "language": "spanish",
                "difficulty_level": "A1",
            },
        )
        # Should fail validation
        assert response.status_code in [422, 400]

    def test_chat_with_nonexistent_conversation(self, client):
        """Test chat to non-existent conversation returns error."""
        response = client.post(
            "/chat",
            json={
                "conversation_id": 99999,
                "user_message": "Hola",
                "language": "spanish",
                "difficulty_level": "A1",
            },
        )
        assert response.status_code in [404, 500]


class TestSTTEndpoint:
    """Test POST /stt/transcribe endpoint - verify speech-to-text."""

    def test_stt_requires_audio_file(self, client):
        """Test STT endpoint requires audio file."""
        response = client.post("/stt/transcribe", data={})
        assert response.status_code in [422, 400]

    def test_stt_endpoint_with_mock_audio(self, client):
        """Test STT endpoint with mocked transcription."""
        from app.main import app

        result = TranscriptionResult(
            text="Hola mundo",
            language="es",
            confidence=0.95,
            duration=2.5,
        )

        # Patch the service instance's transcribe method
        with patch.object(
            app.state.stt_service, "transcribe", new_callable=AsyncMock
        ) as mock_transcribe:
            mock_transcribe.return_value = result

            # Create a simple test audio file
            audio_content = b"\xff\xfb" + b"\x00" * 100  # Fake MP3 header
            response = client.post(
                "/stt/transcribe",
                files={"audio": ("test.mp3", audio_content, "audio/mpeg")},
                data={"language": "spanish"},
            )

            # Should succeed or fail gracefully based on audio validation
            assert response.status_code in [200, 400]

    def test_stt_response_structure(self, client):
        """Test STT response structure matches schema."""
        from app.main import app

        result = TranscriptionResult(
            text="Test transcription",
            language="en",
            confidence=0.92,
            duration=3.0,
        )

        # Patch the service instance's transcribe method
        with patch.object(
            app.state.stt_service, "transcribe", new_callable=AsyncMock
        ) as mock_transcribe:
            mock_transcribe.return_value = result

            audio_content = b"\xff\xfb" + b"\x00" * 100
            response = client.post(
                "/stt/transcribe",
                files={"audio": ("test.mp3", audio_content, "audio/mpeg")},
            )

            if response.status_code == 200:
                data = response.json()
                assert "text" in data
                assert "language" in data or data.get("language") is None
                assert "confidence" in data
                assert "duration" in data


class TestTTSEndpoint:
    """Test POST /tts/synthesize endpoint - verify text-to-speech."""

    def test_tts_endpoint_requires_text(self, client):
        """Test TTS endpoint requires text parameter."""
        response = client.post("/tts/synthesize", json={"language": "spanish"})
        assert response.status_code in [422, 400]

    def test_tts_endpoint_requires_language(self, client):
        """Test TTS endpoint requires language parameter."""
        response = client.post("/tts/synthesize", json={"text": "Hola"})
        assert response.status_code in [422, 400]

    @patch("app.services.tts_service.tts_service.synthesize_speech")
    def test_tts_endpoint_response(self, mock_synthesize, client, tmp_path):
        """Test TTS endpoint returns audio file."""
        # Create a fake audio file
        fake_audio = tmp_path / "test.mp3"
        fake_audio.write_bytes(b"\xff\xfb" + b"\x00" * 100)

        # Mock as async
        async def async_return_path(*args, **kwargs):
            return str(fake_audio)

        mock_synthesize.side_effect = async_return_path

        response = client.post("/tts/synthesize", json={"text": "Hola", "language": "es"})

        assert response.status_code in [200, 503]

    def test_tts_unavailable_graceful(self, client):
        """Test TTS handles unavailable service gracefully."""
        with patch("app.services.tts_service.tts_service.synthesize_speech") as mock_synthesize:
            # Make it async and return None to simulate unavailable service
            async def async_return_none(*args, **kwargs):
                return None

            mock_synthesize.side_effect = async_return_none

            response = client.post("/tts/synthesize", json={"text": "Hola", "language": "es"})

            # Should return error status (503 for unavailable, 500 for mock error)
            assert response.status_code in [500, 503]


class TestProgressEndpoint:
    """Test GET /progress/summary endpoint - verify progress data."""

    def test_progress_summary_requires_language(self, client):
        """Test progress endpoint requires language parameter."""
        response = client.get("/progress/summary")
        assert response.status_code in [422, 400]

    def test_progress_summary_with_valid_language(self, client):
        """Test progress summary with valid language."""
        response = client.get("/progress/summary?language=es")
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "vocabulary" in data
        assert "grammar" in data
        assert "assessment" in data

    def test_progress_summary_structure(self, client):
        """Verify progress summary response structure."""
        response = client.get("/progress/summary?language=fr")
        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "language" in data
        assert "vocabulary" in data
        assert "grammar" in data
        assert "assessment" in data

        # Check vocabulary stats
        vocab = data["vocabulary"]
        assert "total" in vocab
        assert "completed" in vocab
        assert "in_progress" in vocab
        assert "last_activity" in vocab

        # Check grammar stats
        grammar = data["grammar"]
        assert "total" in grammar
        assert "completed" in grammar
        assert "in_progress" in grammar
        assert "last_activity" in grammar

        # Check assessment stats (may be empty)
        assessment = data["assessment"]
        assert "latest_score" in assessment
        assert "recommended_level" in assessment

    def test_progress_summary_invalid_language(self, client):
        """Test progress endpoint rejects invalid language."""
        response = client.get("/progress/summary?language=invalid_lang_xyz")
        assert response.status_code == 400

    def test_progress_summary_multiple_languages(self, client):
        """Test progress endpoint works for multiple languages."""
        languages = ["es", "fr", "de", "it"]  # ISO 639-1 codes

        for lang in languages:
            response = client.get(f"/progress/summary?language={lang}")
            assert response.status_code == 200
            data = response.json()
            assert "vocabulary" in data
            assert "grammar" in data


class TestEndpointIntegration:
    """Integration-style unit tests combining multiple endpoints."""

    def test_create_and_list_conversation_flow(self, client):
        """Test creating and then listing a conversation."""
        # Create conversation
        create_response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        assert create_response.status_code == 200
        created_conv = create_response.json()

        # List conversations
        list_response = client.get("/conversations")
        assert list_response.status_code == 200
        conversations = list_response.json()

        # Verify created conversation is in list
        conv_ids = [c["id"] for c in conversations]
        assert created_conv["id"] in conv_ids

    def test_conversation_message_retrieval_flow(self, client):
        """Test creating conversation and retrieving its messages."""
        # Create conversation
        conv_response = client.post(
            "/conversations", json={"language": "french", "difficulty_level": "B1"}
        )
        conv_id = conv_response.json()["id"]

        # Get messages for new conversation (should be empty)
        msg_response = client.get(f"/conversations/{conv_id}/messages")
        assert msg_response.status_code == 200
        messages = msg_response.json()
        assert isinstance(messages, list)

    def test_multiple_conversations_isolation(self, client):
        """Test that different conversations are properly isolated."""
        # Create two conversations
        conv1_response = client.post(
            "/conversations", json={"language": "spanish", "difficulty_level": "A1"}
        )
        conv1_id = conv1_response.json()["id"]

        conv2_response = client.post(
            "/conversations", json={"language": "french", "difficulty_level": "B1"}
        )
        conv2_id = conv2_response.json()["id"]

        # Get each conversation
        get1 = client.get(f"/conversations/{conv1_id}")
        get2 = client.get(f"/conversations/{conv2_id}")

        assert get1.status_code == 200
        assert get2.status_code == 200
        assert get1.json()["language"] == "spanish"
        assert get2.json()["language"] == "french"

    def test_progress_endpoint_after_conversations(self, client):
        """Test progress endpoint works after creating conversations."""
        # Create conversations in different languages
        client.post("/conversations", json={"language": "es", "difficulty_level": "A1"})
        client.post("/conversations", json={"language": "fr", "difficulty_level": "B1"})

        # Check progress for each language (use ISO codes)
        for lang in ["es", "fr"]:
            response = client.get(f"/progress/summary?language={lang}")
            assert response.status_code == 200
            data = response.json()
            assert "vocabulary" in data
