"""
Integration tests for Google Gemini provider with LangChain.

These tests require a valid GOOGLE_API_KEY in the environment.
They make actual API calls to Google's Gemini service.

Run with: pytest tests/test_gemini_integration.py -v
Skip if no API key: pytest tests/test_gemini_integration.py -v -k "not integration"
"""

import pytest

from app.config import settings


def has_valid_gemini_key() -> bool:
    """Check if a valid Gemini API key is configured."""
    key = getattr(settings, "google_api_key", "")
    return bool(key) and key.startswith("AI")


# Skip all tests in this module if no valid API key
pytestmark = pytest.mark.skipif(
    not has_valid_gemini_key(),
    reason="No valid GOOGLE_API_KEY configured (must start with 'AI')",
)


class TestLangChainGeminiIntegration:
    """Integration tests for LangChain with Gemini."""

    @pytest.mark.asyncio
    async def test_langchain_chat_google_generative_ai(self):
        """Test direct LangChain ChatGoogleGenerativeAI invocation."""
        from langchain_core.messages import HumanMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            max_output_tokens=50,
            temperature=0.7,
        )

        response = await llm.ainvoke([HumanMessage(content="Say hello in Spanish.")])

        assert response is not None
        assert response.content is not None
        # Response metadata should contain model info
        assert "model_name" in response.response_metadata or response.response_metadata

    @pytest.mark.asyncio
    async def test_langchain_streaming(self):
        """Test LangChain streaming with Gemini."""
        from langchain_core.messages import HumanMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            max_output_tokens=50,
            temperature=0.7,
            streaming=True,
        )

        chunks = []
        async for chunk in llm.astream([HumanMessage(content="Count to 3.")]):
            chunks.append(chunk)

        assert len(chunks) > 0, "Should receive at least one chunk"


class TestGeminiProviderIntegration:
    """Integration tests for GeminiProvider wrapper."""

    @pytest.mark.asyncio
    async def test_gemini_provider_generate(self):
        """Test GeminiProvider.generate() method."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("gemini")

        assert provider.name == "gemini"
        assert provider.model == settings.gemini_model

        response = await provider.generate(
            messages=[{"role": "user", "content": "What is 2 + 2?"}],
            system_prompt="You are a helpful assistant. Answer briefly.",
            max_tokens=50,
            temperature=0.3,
        )

        assert response is not None
        assert response.content is not None
        assert response.model == settings.gemini_model

    @pytest.mark.asyncio
    async def test_gemini_provider_stream(self):
        """Test GeminiProvider.generate_stream() method."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("gemini")

        chunks = []
        async for chunk in provider.generate_stream(
            messages=[{"role": "user", "content": "Say hi."}],
            system_prompt="Be brief.",
            max_tokens=20,
            temperature=0.5,
        ):
            chunks.append(chunk)

        assert len(chunks) > 0, "Should receive at least one chunk"
        # Last chunk should have done=True
        assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_gemini_provider_health_check(self):
        """Test GeminiProvider.health_check() method."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("gemini")

        is_healthy = await provider.health_check()
        assert is_healthy is True


class TestConversationServiceGeminiIntegration:
    """Integration tests for ConversationService with Gemini."""

    @pytest.mark.asyncio
    async def test_conversation_service_generate_response(self):
        """Test ConversationService.generate_response() with Gemini."""
        from app.services.conversation_service import ConversationService

        service = ConversationService(provider_name="gemini")

        response, vocabulary = await service.generate_response(
            user_message="Hola, como estas?",
            language="Spanish",
            difficulty_level="beginner",
            conversation_history=[],
        )

        assert response is not None
        assert isinstance(response, str)
        assert isinstance(vocabulary, list)

    @pytest.mark.asyncio
    async def test_conversation_service_correct_text(self):
        """Test ConversationService.correct_text() with Gemini."""
        from app.services.conversation_service import ConversationService

        service = ConversationService(provider_name="gemini")

        # Test with intentional error
        corrected, corrections = await service.correct_text(
            text="Yo soy bueno",  # Should be "Yo estoy bien"
            language="Spanish",
            difficulty_level="beginner",
        )

        assert corrected is not None
        assert isinstance(corrected, str)
        assert isinstance(corrections, list)


class TestGeminiConfiguration:
    """Tests for Gemini configuration."""

    def test_gemini_settings_configured(self):
        """Verify Gemini settings are properly configured."""
        assert settings.google_api_key, "GOOGLE_API_KEY should be set"
        assert settings.google_api_key.startswith("AI"), "Key should start with 'AI'"
        assert settings.gemini_model, "GEMINI_MODEL should be set"

    def test_gemini_registered_in_factory(self):
        """Verify Gemini is registered in ProviderFactory."""
        from app.services.llm.factory import ProviderFactory

        providers = ProviderFactory.list_providers()
        assert "gemini" in providers, "Gemini should be a registered provider"
