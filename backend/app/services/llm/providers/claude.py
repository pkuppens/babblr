"""
Anthropic Claude LLM provider.

This provider connects to the Anthropic Claude API and supports
both synchronous and streaming responses.
"""

import logging
from typing import AsyncIterator

from anthropic import Anthropic, APIError, AuthenticationError

from app.services.llm.base import LLMResponse, StreamChunk
from app.services.llm.exceptions import (
    LLMAuthenticationError,
    LLMError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class ClaudeProvider:
    """Anthropic Claude LLM provider.

    Connects to the Anthropic Claude API for high-quality language model inference.

    Example:
        provider = ClaudeProvider(api_key="sk-...")
        response = await provider.generate(
            messages=[{"role": "user", "content": "Hola!"}],
            system_prompt="You are a Spanish tutor.",
        )
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "claude-sonnet-4-20250514",
    ):
        """Initialize the Claude provider.

        Args:
            api_key: Anthropic API key. If empty, will check settings.
            model: Model name to use.

        Raises:
            LLMAuthenticationError: If no API key is provided.
        """
        if not api_key:
            # Try to get from settings
            from app.config import settings

            api_key = getattr(settings, "anthropic_api_key", "")

        # Check if API key is missing or is the placeholder value
        if not api_key or api_key == "your_anthropic_api_key_here":
            raise LLMAuthenticationError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY in environment."
            )

        self._api_key = api_key
        self._model = model
        self._client = Anthropic(api_key=api_key)

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "claude"

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
        """Generate a complete response from Claude.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            LLMResponse with the generated content.

        Raises:
            LLMAuthenticationError: If API key is invalid.
            RateLimitError: If rate limit is exceeded.
            LLMError: For other API errors.
        """
        try:
            # Claude API is synchronous, but we wrap it for async interface
            response = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )

            content = response.content[0].text if response.content else ""
            tokens_used = None
            if hasattr(response, "usage"):
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=tokens_used,
                finish_reason=response.stop_reason or "stop",
            )

        except AuthenticationError as e:
            logger.error(f"Claude authentication error: {e}")
            raise LLMAuthenticationError(f"Invalid Anthropic API key: {e}")
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), retry_after=60)
            raise LLMError(f"Claude API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected Claude error: {e}")
            raise LLMError(f"Unexpected error: {e}")

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response from Claude.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Yields:
            StreamChunk objects with partial content.
        """
        try:
            with self._client.messages.stream(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield StreamChunk(content=text, done=False)

                # Get final message for token count
                final_message = stream.get_final_message()
                tokens_used = None
                if hasattr(final_message, "usage"):
                    tokens_used = (
                        final_message.usage.input_tokens + final_message.usage.output_tokens
                    )

                yield StreamChunk(content="", done=True, tokens_used=tokens_used)

        except AuthenticationError as e:
            logger.error(f"Claude authentication error: {e}")
            raise LLMAuthenticationError(f"Invalid Anthropic API key: {e}")
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), retry_after=60)
            raise LLMError(f"Claude API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected Claude error: {e}")
            raise LLMError(f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if Claude API is accessible.

        Makes a minimal API call to verify connectivity.

        Returns:
            True if API is accessible, False otherwise.
        """
        try:
            # Make a minimal request to check API access
            self._client.messages.create(
                model=self._model,
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except Exception as e:
            logger.warning(f"Claude health check failed: {e}")
            return False
