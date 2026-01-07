"""
LangChain-based conversation service for language tutoring.

This module provides:
- Prompt management with LangChain ChatPromptTemplate
- Conversation memory with Summary Buffer (summarizes older messages)
- Provider-agnostic design (defaults to Ollama)
- Basic input/output guardrails
"""

import json
import logging
import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.config import settings
from app.services.prompt_builder import get_prompt_builder

logger = logging.getLogger(__name__)


# Prompt templates for the language tutor
TUTOR_SYSTEM_PROMPT = """You are a friendly and encouraging {language} language tutor. You're having a natural conversation with a {difficulty_level} student.

Guidelines:
- Respond ONLY in {language} (except for brief clarifications if absolutely needed)
- {difficulty_guidance}
- Keep responses conversational and natural, not like a textbook
- Adapt to the student's interests and previous messages
- If they make mistakes, gently incorporate corrections in your response naturally
- Ask engaging questions to keep the conversation flowing
- Focus on practical, everyday language use

Remember: Your goal is immersive, natural conversation - not explicit grammar lessons."""

DIFFICULTY_GUIDANCE = {
    "beginner": "Use simple sentences, basic vocabulary, and present tense mostly. Be very patient and encouraging.",
    "intermediate": "Use varied sentence structures and introduce more complex grammar. Encourage natural expression.",
    "advanced": "Use sophisticated vocabulary and complex structures. Challenge the student with nuanced language.",
}

CORRECTION_PROMPT = """You are a language tutor teaching {language}. A {difficulty_level} student said:

"{text}"

Analyze this for grammatical errors, vocabulary issues, or unnatural phrasing.
Respond with a JSON object containing:
1. "corrected_text": The corrected version (or original if perfect)
2. "corrections": Array of corrections, each with "original", "corrected", "explanation", and "type" (grammar/vocabulary/style)

Keep explanations brief and encouraging. If the text is perfect, return an empty corrections array.

Response format:
{{
  "corrected_text": "...",
  "corrections": [
    {{"original": "...", "corrected": "...", "explanation": "...", "type": "grammar"}}
  ]
}}"""


class ConversationMemory:
    """Manages conversation memory with summary buffer strategy.

    Keeps recent messages verbatim and summarizes older messages
    to maintain context while controlling token usage.
    """

    def __init__(self, max_token_limit: int = 2000):
        """Initialize conversation memory.

        Args:
            max_token_limit: Maximum estimated tokens before summarizing.
        """
        self.max_token_limit = max_token_limit
        self._messages: list[dict[str, str]] = []
        self._summary: str = ""

    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory.

        Args:
            role: Message role ('user' or 'assistant').
            content: Message content.
        """
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        """Get all messages including any summary context."""
        return self._messages.copy()

    def get_langchain_messages(self, system_prompt: str = "") -> list:
        """Get messages in LangChain format.

        Args:
            system_prompt: Optional system prompt to prepend.

        Returns:
            List of LangChain message objects.
        """
        lc_messages = []

        if system_prompt:
            lc_messages.append(SystemMessage(content=system_prompt))

        # Add summary context if available
        if self._summary:
            lc_messages.append(
                SystemMessage(content=f"Previous conversation summary: {self._summary}")
            )

        # Add recent messages
        for msg in self._messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        return lc_messages

    def load_from_history(self, history: list[dict[str, str]]) -> None:
        """Load messages from conversation history.

        Args:
            history: List of message dicts with 'role' and 'content'.
        """
        # Keep only recent messages to control context size
        # A simple heuristic: ~4 chars per token, keep last N messages
        recent_count = 10  # Keep last 10 messages
        self._messages = history[-recent_count:] if len(history) > recent_count else history.copy()

        # If there were older messages, note that context was truncated
        if len(history) > recent_count:
            self._summary = f"[Earlier conversation with {len(history) - recent_count} messages truncated for context]"

    def clear(self) -> None:
        """Clear all memory."""
        self._messages.clear()
        self._summary = ""


class InputGuardrails:
    """Basic input validation and sanitization."""

    # Patterns that might indicate prompt injection attempts
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?above",
        r"you\s+are\s+now\s+a",
        r"pretend\s+you\s+are",
        r"act\s+as\s+if",
    ]

    @classmethod
    def validate(cls, text: str) -> tuple[bool, str]:
        """Validate user input.

        Args:
            text: User input text.

        Returns:
            Tuple of (is_valid, cleaned_text or error_message).
        """
        if not text or not text.strip():
            return False, "Input cannot be empty"

        # Check length
        if len(text) > 10000:
            return False, "Input too long (max 10000 characters)"

        # Check for suspicious patterns (basic prompt injection detection)
        text_lower = text.lower()
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"Suspicious input pattern detected: {pattern}")
                # Don't block, just log - could be legitimate language learning
                break

        return True, text.strip()


class OutputGuardrails:
    """Basic output validation."""

    @classmethod
    def validate_json_response(cls, response: str) -> tuple[bool, Any]:
        """Validate and parse JSON response.

        Args:
            response: Raw response text.

        Returns:
            Tuple of (is_valid, parsed_data or error_message).
        """
        try:
            # Try to extract JSON from response
            # Sometimes LLMs wrap JSON in markdown code blocks
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
            if json_match:
                response = json_match.group(1)

            data = json.loads(response.strip())
            return True, data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return False, str(e)


class ConversationService:
    """LangChain-based conversation service for language tutoring.

    Provides prompt management, memory handling, and guardrails
    while supporting multiple LLM providers.
    """

    def __init__(self, provider_name: str | None = None):
        """Initialize the conversation service.

        Args:
            provider_name: LLM provider to use. Defaults to settings.llm_provider (Ollama).
        """
        from app.services.llm.factory import ProviderFactory

        self.provider_name = provider_name or settings.llm_provider
        self._provider = ProviderFactory.get_provider(self.provider_name)
        self._memory = ConversationMemory(max_token_limit=settings.conversation_max_token_limit)
        self._prompt_builder = get_prompt_builder()

        logger.info(f"ConversationService initialized with provider: {self.provider_name}")

    def _build_system_prompt(
        self,
        language: str,
        difficulty_level: str,
        topic: str = "general conversation",
        recent_vocab: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> str:
        """Build system prompt for the tutor using PromptBuilder.

        Args:
            language: Target language.
            difficulty_level: Student's proficiency level (CEFR or legacy).
            topic: Current conversation topic.
            recent_vocab: Recently learned vocabulary.
            common_mistakes: Common mistakes to address.

        Returns:
            Formatted system prompt.
        """
        return self._prompt_builder.build_prompt(
            language=language,
            level=difficulty_level,
            topic=topic,
            native_language="English",  # TODO: Make this configurable per user
            recent_vocab=recent_vocab,
            common_mistakes=common_mistakes,
        )

    async def correct_text(
        self, text: str, language: str, difficulty_level: str
    ) -> tuple[str, list[dict]]:
        """Analyze and correct user's text.

        Args:
            text: User's input text.
            language: Target language.
            difficulty_level: User's proficiency level.

        Returns:
            Tuple of (corrected_text, list_of_corrections).
        """
        # Validate input
        is_valid, result = InputGuardrails.validate(text)
        if not is_valid:
            logger.warning(f"Input validation failed: {result}")
            return text, []

        prompt = CORRECTION_PROMPT.format(
            language=language,
            difficulty_level=difficulty_level,
            text=text,
        )

        try:
            response = await self._provider.generate(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="",
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for more consistent corrections
            )

            # Validate and parse JSON response
            is_valid, parsed = OutputGuardrails.validate_json_response(response.content)
            if is_valid and isinstance(parsed, dict):
                return parsed.get("corrected_text", text), parsed.get("corrections", [])

            logger.warning("Failed to parse correction response, returning original text")
            return text, []

        except Exception as e:
            logger.error(f"Error in correct_text: {e}")
            return text, []

    async def generate_response(
        self,
        user_message: str,
        language: str,
        difficulty_level: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[dict]]:
        """Generate a conversational response from the AI tutor.

        Args:
            user_message: User's message.
            language: Target language.
            difficulty_level: User's proficiency level.
            conversation_history: Previous messages in the conversation.

        Returns:
            Tuple of (assistant_response, vocabulary_items).
        """
        # Validate input
        is_valid, result = InputGuardrails.validate(user_message)
        if not is_valid:
            raise ValueError(f"Invalid input: {result}")

        # Load conversation history into memory
        if conversation_history:
            self._memory.load_from_history(conversation_history)

        # Build system prompt
        system_prompt = self._build_system_prompt(language, difficulty_level)

        # Build messages for the provider
        messages = self._memory.get_messages()
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self._provider.generate(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            )

            assistant_message = response.content

            # Add to memory for future context
            self._memory.add_message("user", user_message)
            self._memory.add_message("assistant", assistant_message)

            # Extract vocabulary (placeholder - could be enhanced with NLP)
            vocabulary_items = self._extract_vocabulary(assistant_message, language)

            return assistant_message, vocabulary_items

        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            raise

    def _extract_vocabulary(self, text: str, language: str) -> list[dict]:
        """Extract potentially new vocabulary from text.

        Args:
            text: Text to analyze.
            language: Target language.

        Returns:
            List of vocabulary items (empty for now - can be enhanced).
        """
        # Placeholder for vocabulary extraction
        # Could be enhanced with NLP, word frequency analysis, etc.
        return []

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self._memory.clear()

    @property
    def provider(self):
        """Get the current LLM provider."""
        return self._provider


def get_conversation_service(provider_name: str | None = None) -> ConversationService:
    """Factory function to get a conversation service instance.

    Args:
        provider_name: Optional provider name override.

    Returns:
        ConversationService instance.
    """
    return ConversationService(provider_name=provider_name)
