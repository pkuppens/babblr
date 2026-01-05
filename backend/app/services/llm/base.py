"""
Base types and protocol for LLM providers.

This module defines the core abstractions that all LLM providers must implement.
"""

from dataclasses import dataclass
from typing import AsyncIterator, Protocol


@dataclass
class LLMResponse:
    """Response from an LLM provider.

    Attributes:
        content: The generated text content.
        model: The model that generated the response.
        tokens_used: Number of tokens used (if available from provider).
        finish_reason: Why generation stopped (e.g., "stop", "length").
    """

    content: str
    model: str
    tokens_used: int | None = None
    finish_reason: str = ""


@dataclass
class StreamChunk:
    """A chunk of streaming response from an LLM provider.

    Attributes:
        content: The text content of this chunk.
        done: Whether this is the final chunk.
        tokens_used: Total tokens used (typically only set on final chunk).
    """

    content: str
    done: bool = False
    tokens_used: int | None = None


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers.

    All LLM providers (Ollama, Claude, Gemini, etc.) must implement this protocol
    to be usable through the ProviderFactory.

    Example:
        class MyProvider:
            @property
            def name(self) -> str:
                return "my_provider"

            @property
            def model(self) -> str:
                return "my-model-v1"

            async def generate(self, messages, system_prompt, **kwargs) -> LLMResponse:
                # Implementation
                ...
    """

    @property
    def name(self) -> str:
        """Provider identifier (e.g., 'claude', 'ollama')."""
        ...

    @property
    def model(self) -> str:
        """Current model name."""
        ...

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a complete response.

        Args:
            messages: Conversation history as list of {"role": "...", "content": "..."}.
            system_prompt: System prompt to set context.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).

        Returns:
            LLMResponse with the generated content.

        Raises:
            LLMError: If generation fails.
        """
        ...

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response.

        Args:
            messages: Conversation history.
            system_prompt: System prompt to set context.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Yields:
            StreamChunk objects with partial content.

        Raises:
            LLMError: If generation fails.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is available and healthy.

        Returns:
            True if provider is available, False otherwise.
        """
        ...
