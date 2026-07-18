"""
Mock LLM provider for testing.

This provider returns simple, rule-based Spanish responses tuned for A1 students
so the backend can be exercised without external LLM access. It attempts to
produce short, clear Spanish replies appropriate for beginners.
"""

import re
from typing import AsyncIterator, Optional

from app.services.llm.base import LLMResponse, StreamChunk


class MockProvider:
    """Rule-based mock provider for interactive tests.

    Behavior:
    - Examines the last user message and returns a short Spanish reply.
    - Replies are deliberately simple (A1-friendly): short sentences, present
      tense, basic vocabulary.
    - Always reports model name "mock-v1" and health_check returns True.
    """

    def __init__(
        self,
        default_response: str = "Hola. ¿Cómo te llamas?",
        model_name: str = "mock-v1",
    ):
        self.default_response = default_response
        self._model = model_name

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return self._model

    def _reply_for_spanish_a1(self, user_text: str) -> str:
        text = user_text.lower().strip()

        # Greeting
        if re.search(r"\bhola\b|\bhi\b|\bhello\b|\bhey\b", text):
            return "Hola. ¿Cómo estás?"

        # Student gives name in Spanish: "me llamo ..." or "soy ..."
        m = re.search(
            r"me llamo\s+([A-Za-zÀ-ÖØ-öø-ÿ\-']+)|soy\s+([A-Za-zÀ-ÖØ-öø-ÿ\-']+)|my name is\s+([A-Za-z\-']+)",
            text,
        )
        if m:
            name = next(g for g in m.groups() if g) or ""
            name_clean = name.capitalize() if name else ""
            return f"Mucho gusto, {name_clean}. ¿De dónde eres?"

        # Student asks "How are you?" in Spanish
        if re.search(r"cómo estás|como estas|how are you", text):
            return "Bien, gracias. ¿Y tú?"

        # Student answers they are from a place
        m2 = re.search(r"de\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\-']+)|from\s+([A-Za-z\s\-']+)", text)
        if m2:
            place = next(g for g in m2.groups() if g) or ""
            place_clean = place.strip().capitalize()
            return f"¡Qué bien! {place_clean} es un buen lugar. ¿Qué te gusta hacer?"

        # Student says they like something
        if re.search(r"me gusta|i like|gustar", text):
            return "¡Genial! ¿Cuándo lo haces?"

        # Short fallback questions/directives
        if text.endswith("?"):
            return "Buena pregunta. ¿Puedes decir más?"

        # Default simple prompt to keep conversation going
        return self.default_response

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        # Try to extract last user message
        last_user: Optional[str] = None
        for msg in reversed(messages or []):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break

        reply = self.default_response
        if last_user:
            # Very small heuristic: if system_prompt mentions A1 or beginner prefer simple Spanish
            if "A1" in (system_prompt or "") or "beginner" in (system_prompt or "").lower():
                reply = self._reply_for_spanish_a1(last_user)
            else:
                # Still use A1 style by default for safety in tests
                reply = self._reply_for_spanish_a1(last_user)

        return LLMResponse(
            content=reply, model=self._model, tokens_used=len(reply.split()), finish_reason="stop"
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        # Stream the reply word-by-word
        response = await self.generate(messages, system_prompt, max_tokens, temperature)
        words = response.content.split()
        for i, w in enumerate(words):
            is_last = i == len(words) - 1
            yield StreamChunk(content=w + (" " if not is_last else ""), done=False)

        yield StreamChunk(content="", done=True, tokens_used=len(words))

    async def health_check(self) -> bool:
        return True
