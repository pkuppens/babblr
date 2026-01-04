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
        assert hasattr(settings, "host")
        assert hasattr(settings, "port")
        assert hasattr(settings, "claude_model")
        assert hasattr(settings, "whisper_model")

    def test_config_defaults(self):
        """Test configuration defaults."""
        from app.config import settings

        assert settings.host == "127.0.0.1"
        assert settings.port == 8000
        assert settings.claude_model == "claude-3-5-sonnet-20241022"
        assert settings.whisper_model == "base"


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
