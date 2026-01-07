"""
Google Gemini LLM provider.

This provider connects to the Google Gemini API and supports
both synchronous and streaming responses.
"""

import logging
from typing import AsyncIterator

from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.llm.base import LLMResponse, StreamChunk
from app.services.llm.exceptions import (
    LLMAuthenticationError,
    LLMError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Google Gemini LLM provider.

    Connects to the Google Gemini API for language model inference.

    Example:
        provider = GeminiProvider(api_key="...")
        response = await provider.generate(
            messages=[{"role": "user", "content": "Hola!"}],
            system_prompt="You are a Spanish tutor.",
        )
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Gemini provider.

        Args:
            api_key: Google API key. If empty, will check settings.
            model: Model name to use.

        Raises:
            LLMAuthenticationError: If no API key is provided.
        """
        if not api_key:
            # Try to get from settings
            from app.config import settings

            api_key = getattr(settings, "google_api_key", "")

        if not api_key:
            raise LLMAuthenticationError(
                "Google API key is required. Set GOOGLE_API_KEY in environment."
            )

        self._api_key = api_key
        self._model = model
        self._client = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
        )

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "gemini"

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
        """Generate a complete response from Gemini.

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
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

            # Convert messages to LangChain format
            lc_messages = []
            if system_prompt:
                lc_messages.append(SystemMessage(content=system_prompt))

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    lc_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))

            # Create a new client with the specified parameters
            client = ChatGoogleGenerativeAI(
                model=self._model,
                google_api_key=self._api_key,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            response = await client.ainvoke(lc_messages)

            content = response.content if isinstance(response.content, str) else ""
            tokens_used = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens_used = response.usage_metadata.get(
                    "input_tokens", 0
                ) + response.usage_metadata.get("output_tokens", 0)

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=tokens_used,
                finish_reason="stop",
            )

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Gemini error: {e}")

            if "api key" in error_str or "authentication" in error_str or "invalid" in error_str:
                raise LLMAuthenticationError(f"Invalid Google API key: {e}")
            if "rate" in error_str and "limit" in error_str:
                raise RateLimitError(str(e), retry_after=60)
            if "quota" in error_str:
                raise RateLimitError(str(e), retry_after=60)

            raise LLMError(f"Gemini API error: {e}")

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response from Gemini.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Yields:
            StreamChunk objects with partial content.
        """
        try:
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

            # Convert messages to LangChain format
            lc_messages = []
            if system_prompt:
                lc_messages.append(SystemMessage(content=system_prompt))

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    lc_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))

            # Create a new client with the specified parameters
            client = ChatGoogleGenerativeAI(
                model=self._model,
                google_api_key=self._api_key,
                max_output_tokens=max_tokens,
                temperature=temperature,
                streaming=True,
            )

            async for chunk in client.astream(lc_messages):
                content = chunk.content if isinstance(chunk.content, str) else ""
                yield StreamChunk(content=content, done=False)

            yield StreamChunk(content="", done=True, tokens_used=None)

        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Gemini streaming error: {e}")

            if "api key" in error_str or "authentication" in error_str or "invalid" in error_str:
                raise LLMAuthenticationError(f"Invalid Google API key: {e}")
            if "rate" in error_str and "limit" in error_str:
                raise RateLimitError(str(e), retry_after=60)
            if "quota" in error_str:
                raise RateLimitError(str(e), retry_after=60)

            raise LLMError(f"Gemini streaming error: {e}")

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible.

        Makes a minimal API call to verify connectivity.

        Returns:
            True if API is accessible, False otherwise.
        """
        try:
            from langchain_core.messages import HumanMessage

            client = ChatGoogleGenerativeAI(
                model=self._model,
                google_api_key=self._api_key,
                max_output_tokens=10,
            )
            await client.ainvoke([HumanMessage(content="hi")])
            return True
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False
