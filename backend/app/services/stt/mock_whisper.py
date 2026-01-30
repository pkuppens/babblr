"""Mock STT service for testing.

Returns predictable results without actual transcription.
"""

import logging
from pathlib import Path
from typing import Optional

from app.services.stt.base import TranscriptionResult

logger = logging.getLogger(__name__)


class MockSTTService:
    """Mock STT service for testing.

    Returns predictable results without actual transcription.
    """

    def __init__(self, default_text: str = "Mock transcription"):
        """Initialize mock STT service.

        Args:
            default_text: Default text to return for transcriptions
        """
        self.default_text = default_text
        self._call_count = 0

    @property
    def name(self) -> str:
        return "mock"

    async def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> TranscriptionResult:
        """Return mock transcription result."""
        self._call_count += 1
        return TranscriptionResult(
            text=f"{self.default_text} (call #{self._call_count})",
            language=language or "en",
            confidence=0.95,
            duration=5.0,
        )

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        """No resources to close."""
        pass

    def get_available_models(self) -> list[str]:
        """Return list of available models."""
        return ["mock"]

    def get_supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        return ["es", "it", "de", "fr", "nl", "en"]

    async def warmup(self) -> None:
        """Warmup mock service (no-op)."""
        pass
