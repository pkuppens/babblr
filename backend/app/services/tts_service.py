"""Provide text-to-speech functionality and supported locale metadata.

This service uses `edge-tts` when available (free, Microsoft Edge voices).
It also exposes a stable list of supported locales so the API and health
endpoints can communicate capability clearly.
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Optional

from app.services.language_catalog import list_locales

logger = logging.getLogger(__name__)


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
            # For MVP, we'll create a placeholder response
            # In production, integrate with a TTS API

            # Create a unique filename using hash
            text_hash = str(hash(text))[-8:]
            output_path = self.output_dir / f"tts_{text_hash}.mp3"

            try:
                import edge_tts

                # For MVP: If edge-tts is available, use it (it's free).
                # Otherwise, return None and the frontend can handle it.
                voice = self.resolve_voice(language)

                # Use edge-tts
                communicate = edge_tts.Communicate(text, voice)

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
