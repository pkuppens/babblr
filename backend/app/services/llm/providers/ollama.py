"""
Ollama LLM provider for local language model inference.

This provider connects to a local Ollama instance and supports
both synchronous and streaming responses.
"""

import logging
from typing import Any, AsyncIterator

import httpx

from app.services.llm.base import LLMResponse, StreamChunk
from app.services.llm.exceptions import LLMError, ProviderUnavailableError

logger = logging.getLogger(__name__)

# Language tutor system prompt template optimized for Ollama models
TUTOR_PROMPT_TEMPLATE = """You are a friendly and encouraging {language} language tutor helping a {level} level student.

IMPORTANT RULES:
1. Respond ONLY in {language} (the target language being learned)
2. Keep responses concise: 2-4 sentences for beginners (A1-A2), 3-6 for intermediate/advanced
3. Match vocabulary and grammar complexity to the {level} proficiency level
4. If the student makes errors, gently model the correct form in your response
5. Ask one engaging follow-up question to continue the conversation
6. Be encouraging, patient, and supportive

LEVEL GUIDELINES:
- A1 (Beginner): Simple present tense, basic vocabulary (100-500 words), very short sentences
- A2 (Elementary): Past tense, common expressions, simple questions, basic connectors
- B1 (Intermediate): Varied tenses, idioms, natural conversation flow, some complex sentences
- B2 (Upper-Intermediate): Complex grammar, nuanced vocabulary, natural corrections
- C1 (Advanced): Native-like expressions, subtle error correction, sophisticated language
- C2 (Mastery): Peer-level discourse, cultural nuances, near-native fluency

{topic_section}

Remember: Your goal is immersive, natural conversation - not explicit grammar lessons.
Encourage the student and help them build confidence in speaking {language}."""


class OllamaProvider:
    """Ollama LLM provider for local model inference.

    Connects to a local Ollama instance via HTTP API.

    Example:
        provider = OllamaProvider(model="llama3.2:latest")
        response = await provider.generate(
            messages=[{"role": "user", "content": "Hola!"}],
            system_prompt=provider.build_tutor_prompt("Spanish", "A2"),
        )
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:latest",
        timeout: float = 60.0,
    ):
        """Initialize the Ollama provider.

        Args:
            base_url: Ollama API base URL.
            model: Model name to use.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "ollama"

    @property
    def model(self) -> str:
        """Current model name."""
        return self._model

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def _call_api(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Make an API call to Ollama.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            stream: Whether to stream the response.

        Returns:
            API response as a dictionary.

        Raises:
            ProviderUnavailableError: If Ollama is not reachable.
            LLMError: If the API call fails.
        """
        client = await self._get_client()

        # Build the request payload
        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise ProviderUnavailableError(
                "ollama", f"Cannot connect to Ollama at {self.base_url}: {e}"
            )
        except httpx.TimeoutException as e:
            raise LLMError(f"Ollama request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise LLMError(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise LLMError(f"Unexpected error calling Ollama: {e}")

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a complete response from Ollama.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            LLMResponse with the generated content.
        """
        result = await self._call_api(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )

        content = result.get("message", {}).get("content", "")
        model = result.get("model", self._model)
        tokens_used = result.get("eval_count")

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens_used,
            finish_reason="stop",
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response from Ollama.

        Args:
            messages: Conversation history.
            system_prompt: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Yields:
            StreamChunk objects with partial content.
        """
        client = await self._get_client()

        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            async with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue

                    import json

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    content = data.get("message", {}).get("content", "")
                    done = data.get("done", False)

                    if done:
                        yield StreamChunk(
                            content=content,
                            done=True,
                            tokens_used=data.get("eval_count"),
                        )
                    else:
                        yield StreamChunk(content=content, done=False)

        except httpx.ConnectError as e:
            raise ProviderUnavailableError(
                "ollama", f"Cannot connect to Ollama at {self.base_url}: {e}"
            )
        except httpx.TimeoutException as e:
            raise LLMError(f"Ollama stream timed out: {e}")
        except Exception as e:
            raise LLMError(f"Ollama streaming error: {e}")

    async def _check_connection(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models from the local Ollama instance.

        Args:
            None

        Returns:
            list[str]: Model identifiers as returned by Ollama (e.g., "llama3.2:latest").

        Raises:
            ProviderUnavailableError: If Ollama is not reachable.
            LLMError: If Ollama returns an unexpected response.
        """
        client = await self._get_client()
        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
        except httpx.ConnectError as e:
            raise ProviderUnavailableError(
                "ollama", f"Cannot connect to Ollama at {self.base_url}: {e}"
            )
        except httpx.TimeoutException as e:
            raise LLMError(f"Ollama request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise LLMError(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise LLMError(f"Unexpected error calling Ollama: {e}")

        models = data.get("models", [])
        names: list[str] = []
        for item in models:
            name = item.get("name")
            if isinstance(name, str) and name:
                names.append(name)
        return sorted(set(names))

    async def health_check(self) -> bool:
        """Check if Ollama is available and healthy.

        Returns:
            True if Ollama is reachable, False otherwise.
        """
        return await self._check_connection()

    def build_tutor_prompt(
        self,
        language: str,
        level: str,
        topic: str | None = None,
    ) -> str:
        """Build a language tutor system prompt.

        Args:
            language: Target language (e.g., "Spanish", "French").
            level: Proficiency level (e.g., "A1", "B2", "beginner").
            topic: Optional conversation topic.

        Returns:
            Formatted system prompt for language tutoring.
        """
        # Normalize level
        level_mapping = {
            "beginner": "A1",
            "elementary": "A2",
            "intermediate": "B1",
            "upper-intermediate": "B2",
            "advanced": "C1",
            "mastery": "C2",
        }
        normalized_level = level_mapping.get(level.lower(), level.upper())

        topic_section = ""
        if topic:
            topic_section = f"\nCurrent conversation topic: {topic}\nTry to incorporate vocabulary related to this topic naturally."

        return TUTOR_PROMPT_TEMPLATE.format(
            language=language,
            level=normalized_level,
            topic_section=topic_section,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
