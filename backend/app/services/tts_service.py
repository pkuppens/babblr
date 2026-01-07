"""Provide text-to-speech functionality and supported locale metadata.

This service uses `edge-tts` when available (free, Microsoft Edge voices).
It also exposes a stable list of supported locales so the API and health
endpoints can communicate capability clearly.
"""

from __future__ import annotations

import importlib.util
import logging
import re
from pathlib import Path
from typing import Optional

from app.services.language_catalog import list_locales

logger = logging.getLogger(__name__)


def sanitize_tts_text(text: str) -> str:
    """Sanitize text for text-to-speech output.

    This function removes Markdown formatting tokens (like `**bold**` and list
    bullets) that some TTS engines read aloud (for example, "asterisk").
    It keeps readable words and normal punctuation so the spoken output sounds natural.

    Args:
        text (str): Input text that may contain Markdown or lightweight formatting.

    Returns:
        str: A cleaned string suitable for speech synthesis.

    Raises:
        TypeError: If `text` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    value = text.replace("\r\n", "\n")

    # Remove fenced code blocks entirely (they are usually not useful for TTS).
    value = re.sub(r"```[\s\S]*?```", " ", value)

    # Inline code: keep the content, drop the backticks.
    value = re.sub(r"`([^`]+)`", r"\1", value)

    # Images: keep alt text.
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)

    # Links: keep link text.
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)

    # Headings and blockquotes.
    value = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", value)
    value = re.sub(r"(?m)^\s{0,3}>\s?", "", value)

    # Bullet markers at the start of a line.
    value = re.sub(r"(?m)^\s*([*+\-]|•)\s+", "", value)

    # Common Markdown emphasis / strike tokens.
    value = value.replace("**", "")
    value = value.replace("__", "")
    value = value.replace("~~", "")

    # Remove leftover Markdown punctuation that is commonly read aloud.
    value = re.sub(r"[*_`]", "", value)

    # Tables (best-effort): remove pipes used as separators.
    value = value.replace("|", " ")

    # Normalize whitespace.
    value = re.sub(r"\s+", " ", value).strip()

    return value


class TTSService:
    """Service for text-to-speech using system TTS (for MVP, using free options)."""

    def __init__(self):
        self.output_dir = Path("audio_output")
        self.output_dir.mkdir(exist_ok=True)

        # Voices are keyed by locale so we can support variants like en-GB vs en-US.
        # The list is intentionally small and aligned with `language_catalog.py`.
        self._voice_by_locale: dict[str, str] = {
            "en-US": "en-US-GuyNeural",
            "en-GB": "en-GB-RyanNeural",
            "es-ES": "es-ES-AlvaroNeural",
            "es-MX": "es-MX-JorgeNeural",
            "it-IT": "it-IT-DiegoNeural",
            "de-DE": "de-DE-ConradNeural",
            "fr-FR": "fr-FR-HenriNeural",
            "nl-NL": "nl-NL-MaartenNeural",
            "pt-BR": "pt-BR-AntonioNeural",
            "pt-PT": "pt-PT-DuarteNeural",
        }

    def is_edge_tts_available(self) -> bool:
        """Check whether edge-tts is available without importing it eagerly.

        Args:
            None

        Returns:
            bool: True when `edge_tts` can be imported, else False.
        """
        return importlib.util.find_spec("edge_tts") is not None

    def get_supported_locales(self) -> list[str]:
        """Return supported TTS locales for Babblr.

        Args:
            None

        Returns:
            list[str]: Supported locales (e.g., ["en-GB", "en-US", "es-ES", ...]).
        """
        # Keep this aligned with `language_catalog` while ensuring we have a voice.
        locales = [loc for loc in list_locales(tts_only=True) if loc in self._voice_by_locale]
        return sorted(locales)

    def resolve_voice(self, locale_or_language: str) -> str:
        """Resolve an input locale/language into an Edge TTS voice name.

        Args:
            locale_or_language (str): Locale like "en-GB" or a language name like "english".

        Returns:
            str: Edge TTS voice name.
        """
        if not locale_or_language:
            return self._voice_by_locale["en-US"]

        value = locale_or_language.strip().replace("_", "-")
        if not value:
            return self._voice_by_locale["en-US"]

        # First: exact locale match.
        for locale, voice in self._voice_by_locale.items():
            if locale.lower() == value.lower():
                return voice

        # Second: language name / ISO-639-1 fallback.
        name_map = {
            "english": "en-US",
            "en": "en-US",
            "spanish": "es-ES",
            "es": "es-ES",
            "italian": "it-IT",
            "it": "it-IT",
            "german": "de-DE",
            "de": "de-DE",
            "french": "fr-FR",
            "fr": "fr-FR",
            "dutch": "nl-NL",
            "nl": "nl-NL",
            "portuguese": "pt-BR",
            "pt": "pt-BR",
        }
        default_locale = name_map.get(value.lower(), "en-US")
        return self._voice_by_locale.get(default_locale, self._voice_by_locale["en-US"])

    async def synthesize_speech(self, text: str, language: str) -> Optional[str]:
        """
        Convert text to speech and return file path.

        For MVP, we'll use a simple approach. In production, consider:
        - Google Cloud TTS (free tier: 1M chars/month)
        - Amazon Polly (free tier: 5M chars/month first year)
        - Edge TTS (free, Microsoft Edge's TTS)

        Args:
            text: Text to convert to speech
            language: Language code

        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            sanitized_text = sanitize_tts_text(text)
            if not sanitized_text:
                return None

            # For MVP, we'll create a placeholder response
            # In production, integrate with a TTS API

            # Create a unique filename using hash
            text_hash = str(hash(sanitized_text))[-8:]
            output_path = self.output_dir / f"tts_{text_hash}.mp3"

            try:
                import edge_tts

                # For MVP: If edge-tts is available, use it (it's free).
                # Otherwise, return None and the frontend can handle it.
                voice = self.resolve_voice(language)

                # Use edge-tts
                communicate = edge_tts.Communicate(sanitized_text, voice)

                await communicate.save(str(output_path))

                return str(output_path)
            except ImportError:
                logger.warning("edge-tts not installed. TTS functionality disabled.")
                return None

        except Exception as e:
            logger.exception("TTS error: %s", str(e))
            return None


# Create a singleton instance
tts_service = TTSService()
