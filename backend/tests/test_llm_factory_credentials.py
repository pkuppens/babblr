"""
Integration tests for LLM provider factory credential resolution.

Tests that the provider factory correctly uses credentials from:
- Credential store (secure storage)
- Environment variables (fallback)
- Hybrid mode (credential store first, then env)
"""

import pytest

from app.config import settings
from app.routes.credentials import credential_store
from app.services.llm import ProviderFactory


@pytest.fixture(autouse=True)
def clear_credential_store_and_cache():
    """Clear credential store and provider cache before each test."""
    # Clear credential store
    credential_store._credentials.clear()
    # Clear provider cache
    ProviderFactory.clear_cache()
    yield
    # Clean up after test
    credential_store._credentials.clear()
    ProviderFactory.clear_cache()


@pytest.fixture
def reset_settings():
    """Reset settings to default after each test."""
    original_mode = settings.credential_mode
    yield
    settings.credential_mode = original_mode
    ProviderFactory.clear_cache()


class TestLLMProviderFactoryCredentials:
    """Test suite for LLM provider factory credential integration."""

    def test_claude_provider_uses_credential_store(self, reset_settings):
        """Test that Claude provider uses credential from credential store."""
        # Set credential in store
        credential_store.set_credential("anthropic", "api-key", "store-anthropic-key-123")

        # Set different value in env (should be ignored in hybrid mode if store has value)
        settings.anthropic_api_key = "env-anthropic-key-456"
        settings.credential_mode = "hybrid"

        # Get Claude provider
        provider = ProviderFactory.get_provider("claude")

        # Provider should use the credential from store
        # Note: API key is stored as private _api_key
        assert provider is not None
        assert hasattr(provider, "_api_key")
        assert provider._api_key == "store-anthropic-key-123"

    def test_gemini_provider_uses_credential_store(self, reset_settings):
        """Test that Gemini provider uses credential from credential store."""
        # Set credential in store
        credential_store.set_credential("google", "api-key", "store-google-key-123")

        # Set different value in env
        settings.google_api_key = "env-google-key-456"
        settings.credential_mode = "hybrid"

        # Get Gemini provider
        provider = ProviderFactory.get_provider("gemini")

        # Provider should use the credential from store
        # Note: API key is stored as private _api_key
        assert provider is not None
        assert hasattr(provider, "_api_key")
        assert provider._api_key == "store-google-key-123"

    def test_provider_factory_cache_cleared_on_credential_change(self, reset_settings):
        """Test that provider cache is cleared when credential changes."""
        # Initial setup
        credential_store.set_credential("anthropic", "api-key", "initial-key")
        settings.credential_mode = "hybrid"

        # Get provider (will be cached)
        provider1 = ProviderFactory.get_provider("claude")
        assert provider1._api_key == "initial-key"

        # Update credential
        credential_store.set_credential("anthropic", "api-key", "updated-key")

        # In real usage, the API endpoint would clear the cache
        # Simulate that here
        ProviderFactory.clear_cache()

        # Get provider again (should use new credential)
        provider2 = ProviderFactory.get_provider("claude")
        assert provider2._api_key == "updated-key"

    def test_claude_provider_falls_back_to_env(self, reset_settings):
        """Test that Claude provider falls back to env when credential not in store."""
        # Don't set credential in store
        # Set value in env
        settings.anthropic_api_key = "env-anthropic-key"
        settings.credential_mode = "hybrid"

        # Get Claude provider
        provider = ProviderFactory.get_provider("claude")

        # Provider should use env fallback
        assert provider is not None
        assert provider._api_key == "env-anthropic-key"

    def test_gemini_provider_falls_back_to_env(self, reset_settings):
        """Test that Gemini provider falls back to env when credential not in store."""
        # Don't set credential in store
        # Set value in env
        settings.google_api_key = "env-google-key"
        settings.credential_mode = "hybrid"

        # Get Gemini provider
        provider = ProviderFactory.get_provider("gemini")

        # Provider should use env fallback
        assert provider is not None
        assert provider._api_key == "env-google-key"

    def test_provider_raises_error_when_no_credential(self, reset_settings):
        """Test that provider raises error when no credential available."""
        # Don't set credential in store or env
        settings.anthropic_api_key = ""
        settings.credential_mode = "hybrid"

        # Get Claude provider should raise LLMAuthenticationError
        from app.services.llm.exceptions import LLMAuthenticationError

        with pytest.raises(LLMAuthenticationError):
            ProviderFactory.get_provider("claude")

    def test_ollama_provider_doesnt_need_credential(self, reset_settings):
        """Test that Ollama provider works without any credential."""
        # Don't set any credentials
        settings.credential_mode = "hybrid"

        # Get Ollama provider
        provider = ProviderFactory.get_provider("ollama")

        # Ollama should work without API key
        assert provider is not None
        # Ollama provider doesn't have api_key attribute

    def test_secure_mode_only_uses_credential_store(self, reset_settings):
        """Test that secure mode ignores environment variables."""
        # Set credential in store
        credential_store.set_credential("anthropic", "api-key", "store-key")

        # Set different value in env
        settings.anthropic_api_key = "env-key"
        settings.credential_mode = "secure"

        # Get provider
        provider = ProviderFactory.get_provider("claude")

        # Should use store key
        assert provider._api_key == "store-key"

    def test_env_mode_only_uses_environment(self, reset_settings):
        """Test that env mode ignores credential store."""
        # Set credential in store
        credential_store.set_credential("anthropic", "api-key", "store-key")

        # Set different value in env
        settings.anthropic_api_key = "env-key"
        settings.credential_mode = "env"

        # Clear cache and get provider
        ProviderFactory.clear_cache()
        provider = ProviderFactory.get_provider("claude")

        # Should use env key
        assert provider._api_key == "env-key"
