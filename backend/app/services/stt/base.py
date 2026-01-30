"""Base protocol and exceptions for STT services.

This module defines the STTService protocol that all STT implementations
must follow, along with exception classes for error handling.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol


@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription.

    Attributes:
        text: Transcribed text
        language: Detected or specified language code (e.g., 'es', 'en')
        confidence: Confidence score (0.0-1.0), None if not available
        duration: Audio duration in seconds, None if not available
    """

    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[float] = None


class STTService(Protocol):
    """Protocol for speech-to-text services.

    All STT implementations (local Whisper, external service, mock) must
    implement this protocol to be usable through the STTServiceFactory.
    """

    @property
    def name(self) -> str:
        """Name of the STT service implementation."""
        ...  # Protocol method - ellipsis required for abstract method definition

    async def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> TranscriptionResult:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'es', 'en')
            timeout: Optional timeout in seconds

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            STTError: If transcription fails
        """
        ...  # Protocol method - ellipsis required for abstract method definition

    async def health_check(self) -> bool:
        """Check if STT service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        ...  # Protocol method - ellipsis required for abstract method definition

    async def close(self) -> None:
        """Close resources (HTTP clients, process pools, etc.)."""
        ...  # Protocol method - ellipsis required for abstract method definition


class STTError(Exception):
    """Base exception for STT service errors."""

    pass


class STTTimeoutError(STTError):
    """Raised when transcription times out."""

    pass


class STTUnavailableError(STTError):
    """Raised when STT service is unavailable."""

    pass
