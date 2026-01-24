"""
Tests for credential resolution logic in config module.

Tests the get_api_key_for_provider function which handles:
- Credential mode configuration (secure, env, hybrid)
- Fallback logic between credential store and environment variables
"""

import os
from unittest.mock import patch

import pytest

from app.config import get_api_key_for_provider, settings
from app.routes.credentials import credential_store


@pytest.fixture(autouse=True)
def clear_credential_store():
    """Clear the credential store before and after each test."""
    # Clear before test
    credential_store._credentials.clear()
    yield
    # Clear after test
    credential_store._credentials.clear()


@pytest.fixture
def reset_settings():
    """Reset settings to default after each test."""
    yield
    # Reset to default after test
    settings.credential_mode = "hybrid"


class TestGetAPIKeyForProvider:
    """Test suite for get_api_key_for_provider function."""

    def test_get_api_key_secure_mode(self, reset_settings):
        """Test that secure mode only uses credential store."""
        # Set secure mode
        settings.credential_mode = "secure"

        # Store credential in credential_store
        credential_store.set_credential("anthropic", "api-key", "store-key-123")

        # Set env variable (should be ignored)
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key-456"}):
            settings.anthropic_api_key = "env-key-456"

            result = get_api_key_for_provider("anthropic")

            # Should use credential store, not env
            assert result == "store-key-123"

    def test_get_api_key_secure_mode_no_credential(self, reset_settings):
        """Test that secure mode returns None when credential not in store."""
        # Set secure mode
        settings.credential_mode = "secure"

        # Set env variable (should be ignored)
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key-456"}):
            settings.anthropic_api_key = "env-key-456"

            result = get_api_key_for_provider("anthropic")

            # Should return None (env is ignored in secure mode)
            assert result is None

    def test_get_api_key_env_mode(self, reset_settings):
        """Test that env mode only uses environment variables."""
        # Set env mode
        settings.credential_mode = "env"

        # Store credential in credential_store (should be ignored)
        credential_store.set_credential("anthropic", "api-key", "store-key-123")

        # Set env variable
        settings.anthropic_api_key = "env-key-456"

        result = get_api_key_for_provider("anthropic")

        # Should use env, not credential store
        assert result == "env-key-456"

    def test_get_api_key_hybrid_mode_store_first(self, reset_settings):
        """Test that hybrid mode tries credential store first."""
        # Set hybrid mode (default)
        settings.credential_mode = "hybrid"

        # Store credential in credential_store
        credential_store.set_credential("anthropic", "api-key", "store-key-123")

        # Set env variable with different value
        settings.anthropic_api_key = "env-key-456"

        result = get_api_key_for_provider("anthropic")

        # Should use credential store (takes precedence)
        assert result == "store-key-123"

    def test_get_api_key_hybrid_mode_env_fallback(self, reset_settings):
        """Test that hybrid mode falls back to env when credential not in store."""
        # Set hybrid mode (default)
        settings.credential_mode = "hybrid"

        # Don't store in credential_store

        # Set env variable
        settings.anthropic_api_key = "env-key-456"

        result = get_api_key_for_provider("anthropic")

        # Should fall back to env
        assert result == "env-key-456"

    def test_get_api_key_for_anthropic(self, reset_settings):
        """Test getting API key for Anthropic provider."""
        settings.credential_mode = "env"
        settings.anthropic_api_key = "anthropic-test-key"

        result = get_api_key_for_provider("anthropic")

        assert result == "anthropic-test-key"

    def test_get_api_key_for_google(self, reset_settings):
        """Test getting API key for Google provider."""
        settings.credential_mode = "env"
        settings.google_api_key = "google-test-key"

        result = get_api_key_for_provider("google")

        assert result == "google-test-key"

    def test_get_api_key_for_openai(self, reset_settings):
        """Test getting API key for OpenAI provider."""
        settings.credential_mode = "env"
        settings.openai_api_key = "openai-test-key"

        result = get_api_key_for_provider("openai")

        assert result == "openai-test-key"

    def test_get_api_key_for_ollama(self, reset_settings):
        """Test getting API key for Ollama provider (should return None, no key needed)."""
        settings.credential_mode = "env"

        result = get_api_key_for_provider("ollama")

        # Ollama doesn't use API keys
        assert result is None

    def test_get_api_key_empty_string_treated_as_none(self, reset_settings):
        """Test that empty string API keys are treated as None."""
        settings.credential_mode = "env"
        settings.anthropic_api_key = ""

        result = get_api_key_for_provider("anthropic")

        assert result is None

    def test_get_api_key_credential_store_takes_precedence_in_hybrid(self, reset_settings):
        """Test that credential store takes precedence over env in hybrid mode."""
        settings.credential_mode = "hybrid"

        # Set both
        credential_store.set_credential("google", "api-key", "store-google-key")
        settings.google_api_key = "env-google-key"

        result = get_api_key_for_provider("google")

        # Credential store should win
        assert result == "store-google-key"

    def test_get_api_key_for_unknown_provider(self, reset_settings):
        """Test getting API key for unknown provider returns None."""
        settings.credential_mode = "env"

        result = get_api_key_for_provider("unknown-provider")

        assert result is None
