"""
Mock LLM provider for testing.

This provider returns predictable responses without making any API calls,
making it ideal for unit tests and development without API access.
"""

from typing import AsyncIterator

from app.services.llm.base import LLMResponse, StreamChunk


class MockProvider:
    """Mock LLM provider for testing purposes.

    Returns configurable responses without making external API calls.

    Example:
        provider = MockProvider(default_response="Hello!")
        response = await provider.generate(messages, system_prompt)
        assert response.content == "Hello!"
    """

    def __init__(
        self,
        default_response: str = "This is a mock response from the language tutor.",
        model_name: str = "mock-v1",
    ):
        """Initialize the mock provider.

        Args:
            default_response: The response to return from generate().
            model_name: The model name to report.
        """
        self.default_response = default_response
        self._model = model_name

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "mock"

    @property
    def model(self) -> str:
        """Current model name."""
        return self._model

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a mock response.

        Args:
            messages: Conversation history (ignored in mock).
            system_prompt: System prompt (ignored in mock).
            max_tokens: Maximum tokens (ignored in mock).
            temperature: Temperature (ignored in mock).

        Returns:
            LLMResponse with the default_response.
        """
        return LLMResponse(
            content=self.default_response,
            model=self._model,
            tokens_used=len(self.default_response.split()),
            finish_reason="stop",
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming mock response.

        Splits the default response into word chunks.

        Yields:
            StreamChunk objects, one per word, with final chunk marked done=True.
        """
        words = self.default_response.split()
        for i, word in enumerate(words):
            is_last = i == len(words) - 1
            yield StreamChunk(
                content=word + (" " if not is_last else ""),
                done=False,
            )

        # Final chunk
        yield StreamChunk(
            content="",
            done=True,
            tokens_used=len(words),
        )

    async def health_check(self) -> bool:
        """Mock health check always returns True."""
        return True
