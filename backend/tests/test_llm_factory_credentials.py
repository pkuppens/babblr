"""
Integration tests for LLM provider factory credential resolution.

Tests that the provider factory correctly uses credentials from environment variables.
"""

import pytest

from app.config import settings
from app.services.llm import ProviderFactory


@pytest.fixture(autouse=True)
def clear_provider_cache():
    """Clear provider cache before and after each test."""
    ProviderFactory.clear_cache()
    yield
    ProviderFactory.clear_cache()


class TestLLMProviderFactoryCredentials:
    """Test suite for LLM provider factory credential integration."""

    def test_claude_provider_uses_env_credential(self):
        """Test that Claude provider uses credential from environment variables."""
        settings.anthropic_api_key = "test-anthropic-key-not-a-real-key-12345"

        # Get Claude provider
        provider = ProviderFactory.get_provider("claude")

        # Provider should use the credential from env
        assert provider is not None
        assert hasattr(provider, "_api_key")
        assert provider._api_key == "test-anthropic-key-not-a-real-key-12345"

    def test_gemini_provider_uses_env_credential(self):
        """Test that Gemini provider uses credential from environment variables."""
        settings.google_api_key = "test-google-key-not-a-real-key-12345"

        # Get Gemini provider
        provider = ProviderFactory.get_provider("gemini")

        # Provider should use the credential from env
        assert provider is not None
        assert hasattr(provider, "_api_key")
        assert provider._api_key == "test-google-key-not-a-real-key-12345"

    def test_claude_provider_raises_error_when_no_credential(self):
        """Test that Claude provider raises error when no credential available."""
        settings.anthropic_api_key = ""

        # Get Claude provider should raise LLMAuthenticationError
        from app.services.llm.exceptions import LLMAuthenticationError

        with pytest.raises(LLMAuthenticationError):
            ProviderFactory.get_provider("claude")

    def test_gemini_provider_raises_error_when_no_credential(self):
        """Test that Gemini provider raises error when no credential available."""
        settings.google_api_key = ""

        # Get Gemini provider should raise LLMAuthenticationError
        from app.services.llm.exceptions import LLMAuthenticationError

        with pytest.raises(LLMAuthenticationError):
            ProviderFactory.get_provider("gemini")

    def test_ollama_provider_doesnt_need_credential(self):
        """Test that Ollama provider works without any credential."""
        # Get Ollama provider
        provider = ProviderFactory.get_provider("ollama")

        # Ollama should work without API key
        assert provider is not None
        # Ollama provider doesn't have api_key attribute
