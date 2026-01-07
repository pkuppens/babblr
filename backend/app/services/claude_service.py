import json
import logging
from typing import Dict, List, Tuple

from anthropic import Anthropic, APIError, AuthenticationError

from app.config import settings
from app.services.prompt_builder import get_prompt_builder

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for AI conversation using Anthropic Claude."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self._prompt_builder = get_prompt_builder()

    async def correct_text(
        self, text: str, language: str, difficulty_level: str
    ) -> Tuple[str, List[Dict]]:
        """
        Analyze user's text for errors and provide corrections.

        Args:
            text: User's input text
            language: Target language
            difficulty_level: User's proficiency level

        Returns:
            Tuple of (corrected_text, list_of_corrections)
        """
        # Get correction strategy for this level
        correction_strategy = self._prompt_builder.get_correction_strategy(difficulty_level)

        # Build correction guidance based on strategy
        ignore_list = []
        if correction_strategy.get("ignore_punctuation"):
            ignore_list.append("punctuation errors")
        if correction_strategy.get("ignore_capitalization"):
            ignore_list.append("capitalization mistakes")
        if correction_strategy.get("ignore_diacritics"):
            ignore_list.append("missing or incorrect diacritical marks (accents)")

        focus_list = correction_strategy.get("focus_on", [])

        guidance_parts = []
        if ignore_list:
            guidance_parts.append(f"IGNORE: {', '.join(ignore_list)}")
        if focus_list:
            focus_str = ", ".join(focus_list).replace("_", " ")
            guidance_parts.append(f"FOCUS ON: {focus_str}")

        correction_guidance = "\n".join(guidance_parts)

        # Normalize level for display
        normalized_level = self._prompt_builder.normalize_level(difficulty_level)

        prompt = f"""You are a language tutor teaching {language}. A {normalized_level} level student said:

"{text}"

Analyze this for errors based on the following correction strategy for {normalized_level} level:
{correction_guidance}

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

        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
            )

            result = json.loads(response.content[0].text)
            return result.get("corrected_text", text), result.get("corrections", [])
        except AuthenticationError as e:
            logger.error(f"Authentication error in correct_text: {e}")
            # Don't fail the request - just skip corrections
            return text, []
        except APIError as e:
            logger.error(f"API error in correct_text: {e}")
            return text, []
        except Exception as e:
            logger.error(f"Unexpected error in correct_text: {e}")
            return text, []
            return text, []

    async def generate_response(
        self,
        user_message: str,
        language: str,
        difficulty_level: str,
        conversation_history: List[Dict[str, str]] | None = None,
    ) -> Tuple[str, List[Dict]]:
        """
        Generate a conversational response from the AI tutor.

        Args:
            user_message: User's message
            language: Target language
            difficulty_level: User's proficiency level
            conversation_history: Previous messages in the conversation

        Returns:
            Tuple of (assistant_response, vocabulary_items)
        """
        if conversation_history is None:
            conversation_history = []

        # Build system prompt
        system_prompt = self._build_system_prompt(language, difficulty_level)

        # Build messages
        messages = []
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=2048, system=system_prompt, messages=messages
            )

            assistant_message = response.content[0].text

            # Extract vocabulary items (simple extraction for MVP)
            vocabulary_items = self._extract_vocabulary(assistant_message, language)

            return assistant_message, vocabulary_items
        except AuthenticationError as e:
            logger.error(f"Authentication error in generate_response: {e}")
            raise
        except APIError as e:
            logger.error(f"API error in generate_response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_response: {e}")
            raise

    def _build_system_prompt(
        self,
        language: str,
        difficulty_level: str,
        topic: str = "general conversation",
        recent_vocab: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> str:
        """Build system prompt using PromptBuilder.

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
            native_language=None,  # Will use settings.user_native_language by default
            recent_vocab=recent_vocab,
            common_mistakes=common_mistakes,
        )

    def _extract_vocabulary(self, text: str, language: str) -> List[Dict]:
        """
        Extract potentially new vocabulary from the assistant's message.
        This is a simple implementation - could be enhanced with NLP.
        """
        # For MVP, return empty list. In production, you'd use language-specific
        # analysis to identify uncommon words worth learning
        return []


# Create a singleton instance
claude_service = ClaudeService()
