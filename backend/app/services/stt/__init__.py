"""STT (Speech-to-Text) service implementations.

This module provides a protocol-based STT service architecture with multiple
implementations: local Whisper (CPU/GPU), external Whisper microservice, and mock.
"""

from app.services.stt.base import (
    STTError,
    STTService,
    STTTimeoutError,
    STTUnavailableError,
    TranscriptionResult,
)
from app.services.stt.factory import STTServiceFactory

__all__ = [
    "STTService",
    "STTError",
    "STTTimeoutError",
    "STTUnavailableError",
    "TranscriptionResult",
    "STTServiceFactory",
]
