"""
Unit tests for Babblr backend.
Run with: pytest tests/
"""

from app.models.schemas import (
    ChatRequest,
    ConversationCreate,
    TranscriptionRequest,
    TTSRequest,
)


class TestSchemas:
    """Test Pydantic schemas validation."""

    def test_conversation_create_valid(self):
        """Test creating a valid conversation."""
        conv = ConversationCreate(language="spanish", difficulty_level="beginner")
        assert conv.language == "spanish"
        assert conv.difficulty_level == "beginner"

    def test_conversation_create_with_cefr(self):
        """Test conversation with CEFR level."""
        conv = ConversationCreate(language="french", difficulty_level="A2")
        assert conv.language == "french"
        assert conv.difficulty_level == "A2"

    def test_chat_request_valid(self):
        """Test creating a valid chat request."""
        chat = ChatRequest(
            conversation_id=1,
            user_message="Bonjour",
            language="french",
            difficulty_level="B1",
        )
        assert chat.conversation_id == 1
        assert chat.user_message == "Bonjour"
        assert chat.language == "french"
        assert chat.difficulty_level == "B1"

    def test_transcription_request(self):
        """Test transcription request schema."""
        req = TranscriptionRequest(conversation_id=1, language="spanish")
        assert req.conversation_id == 1
        assert req.language == "spanish"

    def test_transcription_response(self):
        """Test transcription response schema with new fields."""
        from app.models.schemas import TranscriptionResponse

        resp = TranscriptionResponse(
            text="Hola mundo", language="es", confidence=0.95, duration=2.5
        )
        assert resp.text == "Hola mundo"
        assert resp.language == "es"
        assert resp.confidence == 0.95
        assert resp.duration == 2.5
        assert resp.corrections is None

    def test_tts_request(self):
        """Test TTS request schema."""
        req = TTSRequest(text="Hola mundo", language="spanish")
        assert req.text == "Hola mundo"
        assert req.language == "spanish"


class TestConfig:
    """Test configuration loading."""

    def test_config_imports(self):
        """Test that config module imports correctly."""
        from app.config import settings

        assert settings is not None
        assert hasattr(settings, "babblr_api_host")
        assert hasattr(settings, "babblr_api_port")
        assert hasattr(settings, "anthropic_model")
        assert hasattr(settings, "whisper_model")

    def test_config_defaults(self):
        """Test configuration defaults and types.

        Note: Some values may be overridden by local .env file.
        We test that settings exist with correct types, not specific values
        that depend on the local environment.
        """
        from app.config import settings

        # These should have consistent defaults regardless of .env
        assert settings.babblr_api_host == "127.0.0.1"
        assert settings.babblr_api_port == 8000
        assert settings.whisper_model == "base"
        assert settings.whisper_device == "auto"
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3.2:latest"

        # These exist and have correct types (values may come from .env)
        assert isinstance(settings.babblr_dev_mode, bool)
        assert isinstance(settings.babblr_audio_storage_path, str)
        assert isinstance(settings.llm_provider, str)
        assert isinstance(settings.anthropic_model, str)


class TestModels:
    """Test database models."""

    def test_conversation_model_import(self):
        """Test that Conversation model can be imported."""
        from app.models.models import Conversation

        assert Conversation is not None
        assert hasattr(Conversation, "__tablename__")
        assert Conversation.__tablename__ == "conversations"

    def test_message_model_import(self):
        """Test that Message model can be imported."""
        from app.models.models import Message

        assert Message is not None
        assert hasattr(Message, "__tablename__")
        assert Message.__tablename__ == "messages"

    def test_vocabulary_model_import(self):
        """Test that VocabularyItem model can be imported."""
        from app.models.models import VocabularyItem

        assert VocabularyItem is not None
        assert hasattr(VocabularyItem, "__tablename__")
        assert VocabularyItem.__tablename__ == "vocabulary_items"


class TestWhisperService:
    """Test Whisper service functionality."""

    def test_whisper_service_import(self):
        """Test that WhisperService can be imported."""
        from app.services.whisper_service import WhisperService

        assert WhisperService is not None

    def test_whisper_service_initialization(self):
        """Test WhisperService initialization."""
        from app.services.whisper_service import WhisperService

        service = WhisperService(model_size="base", device="cpu")
        assert service.model_size == "base"
        assert service.device == "cpu"

    def test_supported_languages(self):
        """Test supported languages list."""
        from app.services.whisper_service import whisper_service

        languages = whisper_service.get_supported_languages()
        assert isinstance(languages, list)
        assert "es" in languages  # Spanish
        assert "it" in languages  # Italian
        assert "de" in languages  # German
        assert "fr" in languages  # French
        assert "nl" in languages  # Dutch
        assert "en" in languages  # English

    def test_available_models(self):
        """Test available models list."""
        from app.services.whisper_service import whisper_service

        models = whisper_service.get_available_models()
        assert isinstance(models, list)
        assert "tiny" in models
        assert "base" in models
        assert "small" in models
        assert "medium" in models
        assert "large" in models

    def test_language_code_mapping(self):
        """Test language name to code mapping."""
        from app.services.whisper_service import WhisperService

        service = WhisperService(model_size="base", device="cpu")

        # Test full names
        assert service._map_language_code("spanish") == "es"
        assert service._map_language_code("italian") == "it"
        assert service._map_language_code("german") == "de"
        assert service._map_language_code("french") == "fr"
        assert service._map_language_code("dutch") == "nl"

        # Test codes (should pass through)
        assert service._map_language_code("es") == "es"
        assert service._map_language_code("it") == "it"

        # Test case insensitivity
        assert service._map_language_code("Spanish") == "es"
        assert service._map_language_code("FRENCH") == "fr"
