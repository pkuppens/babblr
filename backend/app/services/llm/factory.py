"""
Provider factory for runtime LLM provider selection.

The factory maintains a cache of provider instances for efficiency
and supports runtime switching between providers.
"""

from typing import TYPE_CHECKING

from app.config import settings
from app.services.llm.exceptions import ProviderUnavailableError

if TYPE_CHECKING:
    from app.services.llm.base import LLMProvider


class ProviderFactory:
    """Factory for creating and caching LLM provider instances.

    Supports runtime provider selection with singleton caching for efficiency.

    Example:
        # Get default provider (from settings)
        provider = ProviderFactory.get_provider()

        # Get specific provider
        ollama = ProviderFactory.get_provider("ollama")

        # Clear cache (useful for testing)
        ProviderFactory.clear_cache()
    """

    _instances: dict[str, "LLMProvider"] = {}
    _providers: dict[str, type] = {}

    @classmethod
    def _register_default_providers(cls) -> None:
        """Register default providers if not already registered."""
        if cls._providers:
            return

        # Import providers
        from app.services.llm.providers.mock import MockProvider

        cls._providers["mock"] = MockProvider

        # Try to import optional providers
        try:
            from app.services.llm.providers.ollama import OllamaProvider

            cls._providers["ollama"] = OllamaProvider
        except ImportError:
            pass

        try:
            from app.services.llm.providers.claude import ClaudeProvider

            cls._providers["claude"] = ClaudeProvider
        except ImportError:
            pass

        try:
            from app.services.llm.providers.gemini import GeminiProvider

            cls._providers["gemini"] = GeminiProvider
        except ImportError:
            pass

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """Register a provider class.

        Args:
            name: Provider identifier (e.g., "ollama", "claude").
            provider_class: The provider class to register.
        """
        cls._providers[name] = provider_class

    @classmethod
    def get_provider(cls, name: str | None = None) -> "LLMProvider":
        """Get a provider instance by name.

        Uses cached instances when available for efficiency.

        Args:
            name: Provider name. If None, uses settings.llm_provider.

        Returns:
            An LLMProvider instance.

        Raises:
            ProviderUnavailableError: If the provider is not registered.
        """
        cls._register_default_providers()

        if name is None:
            name = getattr(settings, "llm_provider", "mock")

        if name in cls._instances:
            return cls._instances[name]

        provider = cls._create_provider(name)
        cls._instances[name] = provider
        return provider

    @classmethod
    def _create_provider(cls, name: str) -> "LLMProvider":
        """Create a new provider instance.

        Args:
            name: Provider name.

        Returns:
            A new LLMProvider instance.

        Raises:
            ProviderUnavailableError: If the provider is not registered.
        """
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys()) or "none"
            raise ProviderUnavailableError(
                name, f"Not registered. Available providers: {available}"
            )

        provider_class = cls._providers[name]

        # Handle provider-specific initialization
        if name == "claude":
            api_key = getattr(settings, "anthropic_api_key", "")
            model = getattr(settings, "anthropic_model", "claude-sonnet-4-20250514")
            return provider_class(api_key=api_key, model=model)
        elif name == "ollama":
            base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            model = getattr(settings, "ollama_model", "llama3.2:latest")
            return provider_class(base_url=base_url, model=model)
        elif name == "gemini":
            api_key = getattr(settings, "google_api_key", "")
            model = getattr(settings, "gemini_model", "gemini-2.0-flash")
            return provider_class(api_key=api_key, model=model)
        else:
            return provider_class()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached provider instances.

        Useful for testing or when reconfiguring providers.
        """
        cls._instances.clear()

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names.

        Returns:
            List of provider names.
        """
        cls._register_default_providers()
        return list(cls._providers.keys())
