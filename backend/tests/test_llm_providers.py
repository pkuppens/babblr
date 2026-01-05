"""
Test-Driven Development tests for LLM Provider architecture.

These tests define the expected behavior BEFORE implementation.
Run with: uv run pytest backend/tests/test_llm_providers.py -v

Phase 1: RED - All tests should FAIL initially
Phase 2: GREEN - Implement until tests pass
Phase 3: REFACTOR - Clean up while keeping tests green
"""

from unittest.mock import AsyncMock, patch

import pytest

# =============================================================================
# SECTION 1: Protocol & Base Types Tests
# =============================================================================


class TestLLMResponseDataclass:
    """Test LLMResponse dataclass structure."""

    def test_llm_response_import(self):
        """LLMResponse should be importable from base module."""
        from app.services.llm.base import LLMResponse

        assert LLMResponse is not None

    def test_llm_response_required_fields(self):
        """LLMResponse must have content and model fields."""
        from app.services.llm.base import LLMResponse

        response = LLMResponse(content="Hello", model="test-model")
        assert response.content == "Hello"
        assert response.model == "test-model"

    def test_llm_response_optional_fields(self):
        """LLMResponse should have optional tokens_used and finish_reason."""
        from app.services.llm.base import LLMResponse

        response = LLMResponse(
            content="Hello",
            model="test-model",
            tokens_used=42,
            finish_reason="stop",
        )
        assert response.tokens_used == 42
        assert response.finish_reason == "stop"

    def test_llm_response_defaults(self):
        """LLMResponse optional fields should have sensible defaults."""
        from app.services.llm.base import LLMResponse

        response = LLMResponse(content="Hello", model="test-model")
        assert response.tokens_used is None
        assert response.finish_reason == ""


class TestStreamChunkDataclass:
    """Test StreamChunk dataclass structure."""

    def test_stream_chunk_import(self):
        """StreamChunk should be importable from base module."""
        from app.services.llm.base import StreamChunk

        assert StreamChunk is not None

    def test_stream_chunk_content(self):
        """StreamChunk must have content field."""
        from app.services.llm.base import StreamChunk

        chunk = StreamChunk(content="Hello")
        assert chunk.content == "Hello"

    def test_stream_chunk_done_flag(self):
        """StreamChunk should have done flag with default False."""
        from app.services.llm.base import StreamChunk

        chunk = StreamChunk(content="Hello")
        assert chunk.done is False

        final_chunk = StreamChunk(content="", done=True, tokens_used=100)
        assert final_chunk.done is True
        assert final_chunk.tokens_used == 100


class TestLLMProviderProtocol:
    """Test LLMProvider protocol definition."""

    def test_protocol_import(self):
        """LLMProvider protocol should be importable."""
        from app.services.llm.base import LLMProvider

        assert LLMProvider is not None

    def test_protocol_has_name_property(self):
        """LLMProvider must define name property."""
        from app.services.llm.base import LLMProvider

        assert hasattr(LLMProvider, "name")

    def test_protocol_has_model_property(self):
        """LLMProvider must define model property."""
        from app.services.llm.base import LLMProvider

        assert hasattr(LLMProvider, "model")

    def test_protocol_has_generate_method(self):
        """LLMProvider must define generate async method."""
        from app.services.llm.base import LLMProvider

        assert hasattr(LLMProvider, "generate")

    def test_protocol_has_generate_stream_method(self):
        """LLMProvider must define generate_stream async method."""
        from app.services.llm.base import LLMProvider

        assert hasattr(LLMProvider, "generate_stream")

    def test_protocol_has_health_check_method(self):
        """LLMProvider must define health_check async method."""
        from app.services.llm.base import LLMProvider

        assert hasattr(LLMProvider, "health_check")


# =============================================================================
# SECTION 2: Exception Tests
# =============================================================================


class TestLLMExceptions:
    """Test custom LLM exceptions."""

    def test_llm_error_import(self):
        """LLMError base exception should be importable."""
        from app.services.llm.exceptions import LLMError

        assert LLMError is not None
        assert issubclass(LLMError, Exception)

    def test_rate_limit_error(self):
        """RateLimitError should be a subclass of LLMError."""
        from app.services.llm.exceptions import LLMError, RateLimitError

        assert issubclass(RateLimitError, LLMError)

        error = RateLimitError("Rate limit exceeded", retry_after=30)
        assert "Rate limit" in str(error)
        assert error.retry_after == 30

    def test_provider_unavailable_error(self):
        """ProviderUnavailableError should be a subclass of LLMError."""
        from app.services.llm.exceptions import LLMError, ProviderUnavailableError

        assert issubclass(ProviderUnavailableError, LLMError)

        error = ProviderUnavailableError("ollama", "Connection refused")
        assert error.provider == "ollama"

    def test_authentication_error(self):
        """LLMAuthenticationError should be a subclass of LLMError."""
        from app.services.llm.exceptions import LLMAuthenticationError, LLMError

        assert issubclass(LLMAuthenticationError, LLMError)


# =============================================================================
# SECTION 3: Mock Provider Tests
# =============================================================================


class TestMockProvider:
    """Test MockProvider implementation for testing purposes."""

    def test_mock_provider_import(self):
        """MockProvider should be importable."""
        from app.services.llm.providers.mock import MockProvider

        assert MockProvider is not None

    def test_mock_provider_implements_protocol(self):
        """MockProvider must implement LLMProvider protocol."""
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        # Check it has all required attributes/methods
        assert hasattr(provider, "name")
        assert hasattr(provider, "model")
        assert hasattr(provider, "generate")
        assert hasattr(provider, "generate_stream")
        assert hasattr(provider, "health_check")

    def test_mock_provider_name(self):
        """MockProvider should have name 'mock'."""
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        assert provider.name == "mock"

    def test_mock_provider_model(self):
        """MockProvider should have a model name."""
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        assert provider.model == "mock-v1"

    @pytest.mark.asyncio
    async def test_mock_provider_generate(self):
        """MockProvider.generate should return a valid LLMResponse."""
        from app.services.llm.base import LLMResponse
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        response = await provider.generate(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a helpful assistant.",
        )

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert response.model == "mock-v1"

    @pytest.mark.asyncio
    async def test_mock_provider_generate_stream(self):
        """MockProvider.generate_stream should yield StreamChunks."""
        from app.services.llm.base import StreamChunk
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        chunks = []
        async for chunk in provider.generate_stream(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a helpful assistant.",
        ):
            chunks.append(chunk)
            assert isinstance(chunk, StreamChunk)

        assert len(chunks) > 0
        assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_mock_provider_health_check(self):
        """MockProvider.health_check should return True."""
        from app.services.llm.providers.mock import MockProvider

        provider = MockProvider()
        result = await provider.health_check()
        assert result is True

    def test_mock_provider_configurable_response(self):
        """MockProvider should support configurable responses for testing."""
        from app.services.llm.providers.mock import MockProvider

        custom_response = "This is a custom test response"
        provider = MockProvider(default_response=custom_response)
        assert provider.default_response == custom_response


# =============================================================================
# SECTION 4: Provider Factory Tests
# =============================================================================


class TestProviderFactory:
    """Test ProviderFactory for runtime provider selection."""

    def test_factory_import(self):
        """ProviderFactory should be importable."""
        from app.services.llm.factory import ProviderFactory

        assert ProviderFactory is not None

    def test_get_provider_returns_provider(self):
        """get_provider should return a valid LLMProvider."""
        from app.services.llm.factory import ProviderFactory

        # Clear cache first
        ProviderFactory.clear_cache()

        provider = ProviderFactory.get_provider("mock")
        assert hasattr(provider, "name")
        assert hasattr(provider, "generate")

    def test_get_provider_caches_instances(self):
        """get_provider should cache and reuse provider instances."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()

        provider1 = ProviderFactory.get_provider("mock")
        provider2 = ProviderFactory.get_provider("mock")

        assert provider1 is provider2  # Same instance

    def test_get_provider_different_providers(self):
        """get_provider should return different instances for different names."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()

        mock_provider = ProviderFactory.get_provider("mock")
        assert mock_provider.name == "mock"

    def test_get_provider_unknown_raises_error(self):
        """get_provider should raise error for unknown provider."""
        from app.services.llm.exceptions import ProviderUnavailableError
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()

        with pytest.raises((ValueError, ProviderUnavailableError)):
            ProviderFactory.get_provider("unknown_provider_xyz")

    def test_clear_cache(self):
        """clear_cache should remove all cached providers."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider1 = ProviderFactory.get_provider("mock")

        ProviderFactory.clear_cache()
        provider2 = ProviderFactory.get_provider("mock")

        assert provider1 is not provider2  # Different instances after cache clear

    def test_get_default_provider(self):
        """get_provider with no args should return default provider."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()

        # Should use settings.llm_provider as default
        provider = ProviderFactory.get_provider()
        assert provider is not None

    def test_list_available_providers(self):
        """Factory should list available providers."""
        from app.services.llm.factory import ProviderFactory

        providers = ProviderFactory.list_providers()
        assert isinstance(providers, list)
        assert "mock" in providers


# =============================================================================
# SECTION 5: Ollama Provider Tests
# =============================================================================


class TestOllamaProvider:
    """Test OllamaProvider implementation."""

    def test_ollama_provider_import(self):
        """OllamaProvider should be importable."""
        from app.services.llm.providers.ollama import OllamaProvider

        assert OllamaProvider is not None

    def test_ollama_provider_implements_protocol(self):
        """OllamaProvider must implement LLMProvider protocol."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        assert hasattr(provider, "name")
        assert hasattr(provider, "model")
        assert hasattr(provider, "generate")
        assert hasattr(provider, "generate_stream")
        assert hasattr(provider, "health_check")

    def test_ollama_provider_name(self):
        """OllamaProvider should have name 'ollama'."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        assert provider.name == "ollama"

    def test_ollama_provider_configurable_model(self):
        """OllamaProvider should accept model configuration."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider(model="llama3.2:3b")
        assert provider.model == "llama3.2:3b"

    def test_ollama_provider_configurable_base_url(self):
        """OllamaProvider should accept base_url configuration."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider(base_url="http://custom:11434")
        assert provider.base_url == "http://custom:11434"

    @pytest.mark.asyncio
    async def test_ollama_provider_generate_returns_response(self):
        """OllamaProvider.generate should return LLMResponse."""
        from app.services.llm.base import LLMResponse
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Mock the HTTP call
        with patch.object(provider, "_call_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = {
                "message": {"content": "Hola, estoy bien!"},
                "model": "llama3.2:latest",
                "eval_count": 15,
            }

            response = await provider.generate(
                messages=[{"role": "user", "content": "Hola"}],
                system_prompt="You are a Spanish tutor.",
            )

            assert isinstance(response, LLMResponse)
            assert response.content == "Hola, estoy bien!"
            assert response.model == "llama3.2:latest"

    @pytest.mark.asyncio
    async def test_ollama_provider_health_check_success(self):
        """OllamaProvider.health_check returns True when Ollama is running."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        with patch.object(provider, "_check_connection", new_callable=AsyncMock) as mock:
            mock.return_value = True
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_ollama_provider_health_check_failure(self):
        """OllamaProvider.health_check returns False when Ollama is down."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        with patch.object(provider, "_check_connection", new_callable=AsyncMock) as mock:
            mock.return_value = False
            result = await provider.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_ollama_provider_builds_tutor_prompt(self):
        """OllamaProvider should build appropriate language tutor prompts."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # The system prompt for language tutoring should be well-structured
        system_prompt = provider.build_tutor_prompt(
            language="Spanish", level="A2", topic="greetings"
        )

        assert "Spanish" in system_prompt
        assert "A2" in system_prompt or "beginner" in system_prompt.lower()


# =============================================================================
# SECTION 6: Claude Provider Tests (Refactored)
# =============================================================================


class TestClaudeProvider:
    """Test ClaudeProvider implementation (refactored from ClaudeService)."""

    def test_claude_provider_import(self):
        """ClaudeProvider should be importable."""
        from app.services.llm.providers.claude import ClaudeProvider

        assert ClaudeProvider is not None

    def test_claude_provider_implements_protocol(self):
        """ClaudeProvider must implement LLMProvider protocol."""
        from app.services.llm.providers.claude import ClaudeProvider

        provider = ClaudeProvider(api_key="test-key")
        assert hasattr(provider, "name")
        assert hasattr(provider, "model")
        assert hasattr(provider, "generate")
        assert hasattr(provider, "generate_stream")
        assert hasattr(provider, "health_check")

    def test_claude_provider_name(self):
        """ClaudeProvider should have name 'claude'."""
        from app.services.llm.providers.claude import ClaudeProvider

        provider = ClaudeProvider(api_key="test-key")
        assert provider.name == "claude"

    def test_claude_provider_requires_api_key(self):
        """ClaudeProvider should require API key."""
        from app.services.llm.exceptions import LLMAuthenticationError
        from app.services.llm.providers.claude import ClaudeProvider

        # Should raise if no API key provided and none in settings
        with pytest.raises((ValueError, LLMAuthenticationError)):
            ClaudeProvider(api_key="")


# =============================================================================
# SECTION 7: Integration Tests (with Mock)
# =============================================================================


class TestProviderIntegration:
    """Integration tests using MockProvider."""

    @pytest.mark.asyncio
    async def test_full_generate_flow(self):
        """Test complete generate flow through factory."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("mock")

        response = await provider.generate(
            messages=[
                {"role": "user", "content": "Hola, ¿cómo estás?"},
            ],
            system_prompt="You are a Spanish language tutor.",
            max_tokens=100,
            temperature=0.7,
        )

        assert response.content is not None
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_conversation_context(self):
        """Test that conversation history is passed correctly."""
        from app.services.llm.factory import ProviderFactory

        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("mock")

        # Simulate multi-turn conversation
        messages = [
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "¡Hola! ¿Cómo estás?"},
            {"role": "user", "content": "Muy bien, gracias"},
        ]

        response = await provider.generate(
            messages=messages,
            system_prompt="You are a Spanish tutor.",
        )

        assert response.content is not None


# =============================================================================
# SECTION 8: Configuration Tests
# =============================================================================


class TestLLMConfiguration:
    """Test LLM configuration settings."""

    def test_config_has_llm_provider(self):
        """Settings should have llm_provider field."""
        from app.config import settings

        assert hasattr(settings, "llm_provider")

    def test_config_has_ollama_settings(self):
        """Settings should have Ollama configuration."""
        from app.config import settings

        assert hasattr(settings, "ollama_base_url")
        assert hasattr(settings, "ollama_model")

    def test_config_has_llm_common_settings(self):
        """Settings should have common LLM settings."""
        from app.config import settings

        assert hasattr(settings, "llm_max_tokens")
        assert hasattr(settings, "llm_temperature")
        assert hasattr(settings, "llm_timeout")

    def test_config_has_retry_settings(self):
        """Settings should have retry configuration."""
        from app.config import settings

        assert hasattr(settings, "llm_retry_attempts")
        assert hasattr(settings, "llm_retry_base_delay")


# =============================================================================
# SECTION 9: Ollama Integration Tests (Optional - requires Ollama running)
# =============================================================================


@pytest.mark.integration
class TestOllamaIntegration:
    """Integration tests with real Ollama instance."""

    @pytest.mark.asyncio
    async def test_ollama_real_health_check(self):
        """Test real health check with Ollama."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        result = await provider.health_check()
        # This will pass if Ollama is running, skip info if not
        if not result:
            pytest.skip("Ollama not available")
        assert result is True

    @pytest.mark.asyncio
    async def test_ollama_real_generate(self):
        """Test real generation with Ollama."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Check health first
        if not await provider.health_check():
            pytest.skip("Ollama not available")

        response = await provider.generate(
            messages=[{"role": "user", "content": "Say 'hello' in Spanish"}],
            system_prompt="You are a helpful assistant. Respond briefly.",
            max_tokens=50,
        )

        assert response.content is not None
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_ollama_real_stream(self):
        """Test real streaming with Ollama."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        if not await provider.health_check():
            pytest.skip("Ollama not available")

        chunks = []
        async for chunk in provider.generate_stream(
            messages=[{"role": "user", "content": "Count to 3 in Spanish"}],
            system_prompt="You are a helpful assistant. Respond briefly.",
            max_tokens=50,
        ):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert chunks[-1].done is True

    @pytest.mark.asyncio
    async def test_ollama_language_tutor_prompt(self):
        """Test Ollama with language tutor system prompt."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        if not await provider.health_check():
            pytest.skip("Ollama not available")

        system_prompt = provider.build_tutor_prompt(
            language="Spanish", level="A1", topic="greetings"
        )

        response = await provider.generate(
            messages=[{"role": "user", "content": "Hola!"}],
            system_prompt=system_prompt,
            max_tokens=100,
        )

        # Response should be in Spanish (for a Spanish tutor)
        assert response.content is not None
        assert len(response.content) > 0
