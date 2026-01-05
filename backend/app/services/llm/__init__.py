"""
LLM Provider abstraction layer for Babblr.

This module provides a unified interface for multiple LLM backends
(Ollama, Claude, Gemini, etc.) with runtime provider switching.

Usage:
    from app.services.llm import ProviderFactory, LLMResponse

    provider = ProviderFactory.get_provider("ollama")
    response = await provider.generate(
        messages=[{"role": "user", "content": "Hola!"}],
        system_prompt="You are a Spanish tutor.",
    )
"""

from app.services.llm.base import LLMProvider, LLMResponse, StreamChunk
from app.services.llm.exceptions import (
    LLMAuthenticationError,
    LLMError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.services.llm.factory import ProviderFactory

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "StreamChunk",
    "LLMError",
    "RateLimitError",
    "ProviderUnavailableError",
    "LLMAuthenticationError",
    "ProviderFactory",
]
