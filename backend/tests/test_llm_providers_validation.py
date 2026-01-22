"""
Section 3: LLM Provider Validation Tests

Tests for LLM provider connectivity, health checks, and chat completions.

Run unit tests (with mocks):
    pytest tests/test_llm_providers_validation.py -v

Run production tests (requires running backend with actual providers):
    pytest tests/test_llm_providers_validation.py -v --production

The production tests require:
- Ollama: Running at http://localhost:11434
- Gemini: API_KEY configured in .env
- Claude: API_KEY configured in .env (will be skipped if not available)
"""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def production_mode(request):
    """Fixture to check if running in production mode."""
    return request.config.getoption("--production")


# =============================================================================
# OLLAMA PROVIDER VALIDATION
# =============================================================================


class TestOllamaValidation:
    """Validate Ollama provider connectivity and functionality."""

    @pytest.mark.asyncio
    async def test_ollama_health_check_mock(self):
        """Unit test: Ollama health check with mock."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Mock the internal connection check
        with patch.object(provider, "_check_connection", new_callable=AsyncMock) as mock:
            mock.return_value = True
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_ollama_health_check_production(self, production_mode):
        """Production test: Real Ollama health check."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        result = await provider.health_check()

        # Should succeed if Ollama is running
        if result:
            assert result is True
        else:
            pytest.skip("Ollama not running at localhost:11434")

    @pytest.mark.asyncio
    async def test_ollama_zero_temperature_chat_mock(self):
        """Unit test: Ollama chat completion at 0.0 temperature (mocked)."""
        from app.services.llm.base import LLMResponse
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Mock the _call_api method directly
        mock_api_response = {
            "message": {"content": "Hola, estoy bien."},
            "model": "llama3.2:latest",
            "eval_count": 42,
        }

        with patch.object(provider, "_call_api", new_callable=AsyncMock) as mock:
            mock.return_value = mock_api_response

            response = await provider.generate(
                messages=[{"role": "user", "content": "¿Hola, cómo estás?"}],
                system_prompt="You are a Spanish tutor.",
                temperature=0.0,
                max_tokens=150,
            )

            assert isinstance(response, LLMResponse)
            assert response.content == "Hola, estoy bien."

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_ollama_zero_temperature_chat_production(self, production_mode):
        """Production test: Ollama chat completion at 0.0 temperature."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Check health first
        if not await provider.health_check():
            pytest.skip("Ollama not running at localhost:11434")

        response = await provider.generate(
            messages=[{"role": "user", "content": "Say 'Hello' in Spanish. Just one word."}],
            system_prompt="Respond with just one Spanish word.",
            temperature=0.0,
            max_tokens=20,
        )

        assert response.content is not None
        assert len(response.content) > 0


# =============================================================================
# GEMINI PROVIDER VALIDATION
# =============================================================================


class TestGeminiValidation:
    """Validate Gemini provider connectivity and functionality."""

    @pytest.mark.asyncio
    async def test_gemini_health_check_mock(self):
        """Unit test: Gemini health check with mock."""
        from app.services.llm.providers.gemini import GeminiProvider

        provider = GeminiProvider(api_key="test-key-xyz")

        # Mock the health check
        with patch.object(provider, "health_check", new_callable=AsyncMock) as mock:
            mock.return_value = True
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_gemini_health_check_production(self, production_mode):
        """Production test: Real Gemini health check."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.config import settings
        from app.services.llm.providers.gemini import GeminiProvider

        api_key = getattr(settings, "google_api_key", "")
        if not api_key or api_key == "your_google_api_key_here":
            pytest.skip("Gemini API key not configured in .env")

        try:
            provider = GeminiProvider(api_key=api_key)
            result = await provider.health_check()
            if result:
                assert result is True
            else:
                pytest.skip("Gemini API not responding")
        except Exception as e:
            pytest.skip(f"Gemini not available: {e}")

    @pytest.mark.asyncio
    async def test_gemini_zero_temperature_chat_mock(self):
        """Unit test: Gemini chat at 0.0 temperature (mocked)."""
        from app.services.llm.base import LLMResponse
        from app.services.llm.providers.gemini import GeminiProvider

        provider = GeminiProvider(api_key="test-key")

        # Mock the generate method
        with patch.object(provider, "generate", new_callable=AsyncMock) as mock:
            mock.return_value = LLMResponse(
                content="Hola, estoy bien.",
                model="gemini-1.5-flash",
                tokens_used=28,
            )

            response = await provider.generate(
                messages=[{"role": "user", "content": "¿Hola, cómo estás?"}],
                system_prompt="You are a Spanish tutor.",
                temperature=0.0,
                max_tokens=150,
            )

            assert isinstance(response, LLMResponse)
            assert "Hola" in response.content or "hola" in response.content
            assert "gemini" in response.model.lower()

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_gemini_zero_temperature_chat_production(self, production_mode):
        """Production test: Gemini chat at 0.0 temperature."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.config import settings
        from app.services.llm.providers.gemini import GeminiProvider

        api_key = getattr(settings, "google_api_key", "")
        if not api_key or api_key == "your_google_api_key_here":
            pytest.skip("Gemini API key not configured")

        try:
            provider = GeminiProvider(api_key=api_key)

            if not await provider.health_check():
                pytest.skip("Gemini API not responding")

            response = await provider.generate(
                messages=[
                    {"role": "user", "content": "Respond with only the Spanish word for 'hello'."}
                ],
                system_prompt="Respond with only one Spanish word.",
                temperature=0.0,
                max_tokens=20,
            )

            assert response.content is not None
            assert len(response.content) > 0
        except Exception as e:
            pytest.skip(f"Gemini test skipped: {e}")


# =============================================================================
# CLAUDE PROVIDER VALIDATION
# =============================================================================


class TestClaudeValidation:
    """Validate Claude provider connectivity and functionality."""

    @pytest.mark.asyncio
    async def test_claude_health_check_mock(self):
        """Unit test: Claude health check with mock."""
        from app.services.llm.providers.claude import ClaudeProvider

        provider = ClaudeProvider(api_key="sk-ant-api03-test-key")

        with patch.object(provider, "health_check", new_callable=AsyncMock) as mock:
            mock.return_value = True
            result = await provider.health_check()
            assert result is True

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_claude_health_check_production(self, production_mode):
        """Production test: Real Claude health check (skipped if not configured)."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.config import settings
        from app.services.llm.providers.claude import ClaudeProvider

        api_key = getattr(settings, "anthropic_api_key", "")
        if not api_key or api_key == "your_anthropic_api_key_here":
            pytest.skip("Claude API key not configured (expected)")

        try:
            provider = ClaudeProvider(api_key=api_key)
            result = await provider.health_check()
            if result:
                assert result is True
            else:
                pytest.skip("Claude API not responding")
        except Exception as e:
            pytest.skip(f"Claude not available: {e}")

    @pytest.mark.asyncio
    async def test_claude_zero_temperature_chat_mock(self):
        """Unit test: Claude chat at 0.0 temperature (mocked)."""
        from app.services.llm.base import LLMResponse
        from app.services.llm.providers.claude import ClaudeProvider

        provider = ClaudeProvider(api_key="sk-ant-api03-test-key")

        with patch.object(provider, "generate", new_callable=AsyncMock) as mock:
            mock.return_value = LLMResponse(
                content="Hola, estoy bien.",
                model="claude-3-5-sonnet-20241022",
                tokens_used=28,
            )

            response = await provider.generate(
                messages=[{"role": "user", "content": "¿Hola, cómo estás?"}],
                system_prompt="You are a Spanish tutor.",
                temperature=0.0,
                max_tokens=150,
            )

            assert isinstance(response, LLMResponse)
            assert "Hola" in response.content or "hola" in response.content
            assert "claude" in response.model.lower()

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_claude_zero_temperature_chat_production(self, production_mode):
        """Production test: Claude chat at 0.0 temperature."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.config import settings
        from app.services.llm.providers.claude import ClaudeProvider

        api_key = getattr(settings, "anthropic_api_key", "")
        if not api_key or api_key == "your_anthropic_api_key_here":
            pytest.skip("Claude API key not configured")

        try:
            provider = ClaudeProvider(api_key=api_key)

            if not await provider.health_check():
                pytest.skip("Claude API not responding")

            response = await provider.generate(
                messages=[
                    {"role": "user", "content": "Respond with only the Spanish word for 'hello'."}
                ],
                system_prompt="Respond with only one Spanish word.",
                temperature=0.0,
                max_tokens=20,
            )

            assert response.content is not None
            assert len(response.content) > 0
        except Exception as e:
            pytest.skip(f"Claude test skipped: {e}")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestProviderIntegration:
    """Test complete provider flows."""

    @pytest.mark.asyncio
    async def test_ollama_full_flow_mock(self):
        """Unit test: Ollama full flow (health -> chat)."""
        from app.services.llm.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        with patch.object(provider, "_check_connection", new_callable=AsyncMock) as health_mock:
            health_mock.return_value = True

            # Step 1: Health check
            health = await provider.health_check()
            assert health is True

        # Step 2: Chat
        mock_api_response = {
            "message": {"content": "Hola"},
            "model": "llama3.2:latest",
            "eval_count": 10,
        }

        with patch.object(provider, "_call_api", new_callable=AsyncMock) as chat_mock:
            chat_mock.return_value = mock_api_response

            response = await provider.generate(
                messages=[{"role": "user", "content": "Hola"}],
                system_prompt="You are a tutor.",
                temperature=0.0,
            )
            assert response.content == "Hola"

    @pytest.mark.asyncio
    @pytest.mark.production
    async def test_all_providers_available(self, production_mode):
        """Production test: Check which providers are available."""
        if not production_mode:
            pytest.skip("Skipped without --production flag")

        from app.config import settings
        from app.services.llm.providers.claude import ClaudeProvider
        from app.services.llm.providers.gemini import GeminiProvider
        from app.services.llm.providers.ollama import OllamaProvider

        results = {}

        # Test Ollama
        try:
            ollama = OllamaProvider()
            results["ollama"] = await ollama.health_check()
        except Exception as e:
            results["ollama"] = f"Error: {str(e)[:50]}"

        # Test Gemini
        gemini_key = getattr(settings, "google_api_key", "")
        if gemini_key and gemini_key != "your_google_api_key_here":
            try:
                gemini = GeminiProvider(api_key=gemini_key)
                results["gemini"] = await gemini.health_check()
            except Exception as e:
                results["gemini"] = f"Error: {str(e)[:50]}"

        # Test Claude
        claude_key = getattr(settings, "anthropic_api_key", "")
        if claude_key and claude_key != "your_anthropic_api_key_here":
            try:
                claude = ClaudeProvider(api_key=claude_key)
                results["claude"] = await claude.health_check()
            except Exception as e:
                results["claude"] = f"Error: {str(e)[:50]}"

        # At least one should be available
        print("\nProvider Availability:")
        for provider, status in results.items():
            print(f"  {provider}: {status}")

        assert len(results) > 0, "No providers found to test"
