import json
import logging
from typing import Dict, List, Tuple

from anthropic import Anthropic, APIError, AuthenticationError

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for AI conversation using Anthropic Claude."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

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
        prompt = f"""You are a language tutor teaching {language}. A {difficulty_level} student said:

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

    async def generate_response(
        self,
        user_message: str,
        language: str,
        difficulty_level: str,
        conversation_history: List[Dict[str, str]] = None,
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
            logger.error(
                f"Authentication error: Invalid Anthropic API key. "
                f"Please check your ANTHROPIC_API_KEY in .env file. Original error: {e}"
            )
            raise
        except APIError as e:
            logger.error(f"API error in generate_response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_response: {e}")
            raise

    def _build_system_prompt(self, language: str, difficulty_level: str) -> str:
        """Build system prompt based on language and difficulty."""
        difficulty_guidance = {
            "beginner": "Use simple sentences, basic vocabulary, and present tense mostly. Be very patient and encouraging.",
            "intermediate": "Use varied sentence structures and introduce more complex grammar. Encourage natural expression.",
            "advanced": "Use sophisticated vocabulary and complex structures. Challenge the student with nuanced language.",
        }

        return f"""You are a friendly and encouraging {language} language tutor. You're having a natural conversation with a {difficulty_level} student.

Guidelines:
- Respond ONLY in {language} (except for brief clarifications if absolutely needed)
- {difficulty_guidance.get(difficulty_level, difficulty_guidance["beginner"])}
- Keep responses conversational and natural, not like a textbook
- Adapt to the student's interests and previous messages
- If they make mistakes, gently incorporate corrections in your response naturally
- Ask engaging questions to keep the conversation flowing
- Focus on practical, everyday language use

Remember: Your goal is immersive, natural conversation - not explicit grammar lessons."""

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
