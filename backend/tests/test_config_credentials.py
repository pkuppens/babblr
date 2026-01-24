"""
Tests for credential resolution logic in config module.

Tests the get_api_key_for_provider function which handles API key retrieval
from environment variables.
"""

from app.config import get_api_key_for_provider, settings


class TestGetAPIKeyForProvider:
    """Test suite for get_api_key_for_provider function."""

    def test_get_api_key_for_anthropic(self):
        """Test getting API key for Anthropic provider."""
        settings.anthropic_api_key = "anthropic-test-key"

        result = get_api_key_for_provider("anthropic")

        assert result == "anthropic-test-key"

    def test_get_api_key_for_google(self):
        """Test getting API key for Google provider."""
        settings.google_api_key = "google-test-key"

        result = get_api_key_for_provider("google")

        assert result == "google-test-key"

    def test_get_api_key_for_openai(self):
        """Test getting API key for OpenAI provider."""
        settings.openai_api_key = "openai-test-key"

        result = get_api_key_for_provider("openai")

        assert result == "openai-test-key"

    def test_get_api_key_for_ollama(self):
        """Test getting API key for Ollama provider (should return None, no key needed)."""
        result = get_api_key_for_provider("ollama")

        # Ollama doesn't use API keys
        assert result is None

    def test_get_api_key_empty_string_treated_as_none(self):
        """Test that empty string API keys are treated as None."""
        settings.anthropic_api_key = ""

        result = get_api_key_for_provider("anthropic")

        assert result is None

    def test_get_api_key_for_unknown_provider(self):
        """Test getting API key for unknown provider returns None."""
        result = get_api_key_for_provider("unknown-provider")

        assert result is None
