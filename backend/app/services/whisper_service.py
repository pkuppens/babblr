"""
Whisper STT Service for speech-to-text transcription.

This service provides an abstraction layer for speech-to-text functionality,
currently implemented using OpenAI Whisper. The interface design allows for
future replacement with other STT implementations (e.g., cloud-based services).
"""

import asyncio
import importlib.util
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.services.language_catalog import list_locales, locale_to_iso_639_1

logger = logging.getLogger(__name__)

# Check if Whisper is available
try:
    import torch
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None
    torch = None


def _is_pydub_available() -> bool:
    """Check whether pydub is available without importing it.

    Importing pydub at module import time can emit third-party warnings
    (e.g., ffmpeg discovery warnings) during unit tests. We keep it lazy
    and only import it when audio conversion is actually needed.
    """
    return importlib.util.find_spec("pydub") is not None


class TranscriptionResult:
    """Result of a transcription operation."""

    def __init__(
        self,
        text: str,
        language: str,
        confidence: float,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.text = text
        self.language = language
        self.confidence = confidence
        self.duration = duration
        self.metadata = metadata or {}


class STTService(ABC):
    """Abstract base class for speech-to-text services."""

    @abstractmethod
    async def transcribe(
        self, audio_path: str, language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language hint (e.g., 'es' for Spanish)

        Returns:
            TranscriptionResult with text, language, confidence, and duration
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models."""
        pass


class WhisperService(STTService):
    """Service for speech-to-text using OpenAI Whisper."""

    # Supported languages for Babblr
    SUPPORTED_LANGUAGES = {
        "spanish": "es",
        "italian": "it",
        "german": "de",
        "french": "fr",
        "dutch": "nl",
        "english": "en",
    }

    # Available Whisper models
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    # Default confidence when no segments available
    DEFAULT_CONFIDENCE = 0.9

    def __init__(self, model_size: str = "base", device: str = "auto"):
        """
        Initialize Whisper service.

        Args:
            model_size: Model to use (tiny, base, small, medium, large)
            device: Device to use ("auto", "cuda", or "cpu")
        """
        self.model = None
        self.model_size = model_size
        self.device = self._determine_device(device)

        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            return

        try:
            logger.info("Loading Whisper model: %s on device: %s", model_size, self.device)
            start_time = time.time()

            # Load model
            assert whisper is not None
            self.model = whisper.load_model(model_size, device=self.device)

            load_time = time.time() - start_time
            logger.info("Whisper model loaded successfully in %.2f seconds", load_time)

        except Exception as e:
            logger.error("Failed to load Whisper model: %s", str(e), exc_info=True)
            self.model = None

    def _determine_device(self, device: str) -> str:
        """
        Determine which device to use for Whisper.

        Args:
            device: "auto", "cuda", or "cpu"

        Returns:
            Device string for Whisper
        """
        if not WHISPER_AVAILABLE or torch is None:
            return "cpu"

        if device == "auto":
            if torch.cuda.is_available():
                logger.info("CUDA available, using GPU for Whisper")
                return "cuda"
            else:
                logger.info("CUDA not available, using CPU for Whisper")
                return "cpu"
        else:
            return device

    async def transcribe(
        self, audio_path: str, language: Optional[str] = None, timeout: int = 30
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language hint (e.g., 'es' or 'spanish')
            timeout: Timeout in seconds (default: 30)

        Returns:
            TranscriptionResult with text, language, confidence, and duration

        Raises:
            Exception: If Whisper is not available or transcription fails
            asyncio.TimeoutError: If transcription takes longer than timeout
        """
        if not WHISPER_AVAILABLE or self.model is None:
            raise Exception(
                "Whisper is not installed or failed to load. "
                "Install with: pip install openai-whisper"
            )

        # Convert audio format if needed
        converted_path = await self._convert_audio_format(audio_path)

        try:
            start_time = time.time()

            # Run transcription with timeout
            result = await asyncio.wait_for(
                self._transcribe_sync(converted_path, language), timeout=timeout
            )

            processing_time = time.time() - start_time

            logger.info(
                "Transcription complete - Language: %s, Confidence: %.2f, "
                "Duration: %.2fs, Text length: %d",
                result.language,
                result.confidence,
                processing_time,
                len(result.text),
            )

            return result

        except asyncio.TimeoutError:
            logger.error("Transcription timed out after %d seconds", timeout)
            raise Exception(f"Transcription timed out after {timeout} seconds")

        finally:
            # Clean up converted file if it's different from original
            if converted_path != audio_path and os.path.exists(converted_path):
                os.unlink(converted_path)

    async def _transcribe_sync(
        self, audio_path: str, language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Run Whisper transcription in a thread pool to avoid blocking.

        Args:
            audio_path: Path to the audio file
            language: Optional language hint

        Returns:
            TranscriptionResult
        """
        # Map language name to code if needed
        language_code = self._map_language_code(language) if language else None

        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._do_transcription, audio_path, language_code)

        return result

    def _do_transcription(
        self, audio_path: str, language_code: Optional[str]
    ) -> TranscriptionResult:
        """
        Perform the actual transcription (runs in thread pool).

        Args:
            audio_path: Path to the audio file
            language_code: Optional language code (e.g., 'es')

        Returns:
            TranscriptionResult
        """
        if self.model is None:
            raise RuntimeError("Whisper model is not loaded")

        options = {}
        if language_code:
            options["language"] = language_code

        # Transcribe
        result = self.model.transcribe(audio_path, **options)

        # Extract information
        text = result["text"].strip()
        detected_language = result.get("language", "unknown")

        # Calculate average confidence from segments
        segments = result.get("segments", [])
        if segments:
            # Whisper provides "no_speech_prob" per segment; confidence = 1 - no_speech_prob
            confidences = [1.0 - seg.get("no_speech_prob", 0.0) for seg in segments]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = self.DEFAULT_CONFIDENCE  # Default if no segments

        # Get audio duration from segments
        if segments:
            duration = segments[-1].get("end", 0.0)
        else:
            duration = 0.0

        return TranscriptionResult(
            text=text,
            language=detected_language,
            confidence=avg_confidence,
            duration=duration,
            metadata=result,
        )

    async def _convert_audio_format(self, audio_path: str) -> str:
        """
        Convert audio to a format Whisper can handle if needed.

        Whisper handles most formats, but this provides a fallback
        for problematic formats using pydub.

        Args:
            audio_path: Path to the audio file

        Returns:
            Path to the converted file (or original if no conversion needed)
        """
        # Check file extension
        ext = os.path.splitext(audio_path)[1].lower()

        # Whisper can handle these formats directly
        supported_formats = [".wav", ".mp3", ".m4a", ".ogg", ".flac"]
        if ext in supported_formats:
            return audio_path

        # For other formats, try to convert using pydub
        if not _is_pydub_available():
            logger.warning(
                "pydub not available, cannot convert %s format. Install with: pip install pydub",
                ext,
            )
            return audio_path

        try:
            logger.info("Converting audio format from %s to wav", ext)

            # Run conversion in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output_path = await loop.run_in_executor(None, self._do_audio_conversion, audio_path)

            logger.info("Audio converted successfully to %s", output_path)
            return output_path

        except Exception as e:
            logger.warning("Failed to convert audio format: %s. Using original file.", str(e))
            return audio_path

    def _do_audio_conversion(self, audio_path: str) -> str:
        """
        Perform audio conversion (runs in thread pool).

        Args:
            audio_path: Path to the audio file

        Returns:
            Path to converted file
        """
        try:
            from pydub import AudioSegment
        except ImportError as e:
            raise RuntimeError("pydub is not installed") from e

        # Load audio
        audio = AudioSegment.from_file(audio_path)

        # Export as WAV
        output_path = f"{audio_path}.converted.wav"
        audio.export(output_path, format="wav")

        return output_path

    def _map_language_code(self, language: Optional[str]) -> Optional[str]:
        """
        Map full language names to Whisper language codes.

        Args:
            language: Language name or code

        Returns:
            Language code (e.g., 'es')
        """
        if not language:
            return None

        language_lower = language.lower().strip().replace("_", "-")

        # If it's already a code, return it
        if language_lower in self.SUPPORTED_LANGUAGES.values():
            return language_lower

        # If it's a locale, convert to ISO-639-1
        iso_code = locale_to_iso_639_1(language_lower)
        if iso_code:
            return iso_code

        # Map from name to code
        return self.SUPPORTED_LANGUAGES.get(language_lower, language_lower)

    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        return list(self.SUPPORTED_LANGUAGES.values())

    def get_supported_locales(self) -> List[str]:
        """Return list of supported locales for Babblr STT.

        Babblr exposes locale variants (e.g., "en-GB") to the client, but Whisper
        receives an ISO-639-1 language code (e.g., "en"). This method provides the
        locale variants we explicitly support in our UX.
        """
        return list_locales(stt_only=True)

    def get_available_models(self) -> List[str]:
        """Return list of available Whisper models."""
        return self.AVAILABLE_MODELS

    def get_cuda_info(self) -> Dict[str, Any]:
        """Return CUDA/GPU availability information for Whisper runtime.

        Args:
            None

        Returns:
            dict[str, Any]: CUDA/runtime information for health/status endpoints.
        """
        if not WHISPER_AVAILABLE or torch is None:
            return {
                "torch_available": False,
                "cuda_available": False,
                "device": "cpu",
                "gpu_count": 0,
                "gpu_names": [],
            }

        cuda_available = bool(torch.cuda.is_available())
        gpu_count = int(torch.cuda.device_count()) if cuda_available else 0
        gpu_names: list[str] = []
        if cuda_available:
            for i in range(gpu_count):
                try:
                    gpu_names.append(str(torch.cuda.get_device_name(i)))
                except Exception:
                    gpu_names.append("unknown")

        return {
            "torch_available": True,
            "torch_version": getattr(torch, "__version__", "unknown"),
            "cuda_available": cuda_available,
            "device": self.device,
            "gpu_count": gpu_count,
            "gpu_names": gpu_names,
        }


# Initialize the service with configuration
def create_whisper_service() -> WhisperService:
    """Create and initialize Whisper service with configuration."""
    from app.config import settings

    return WhisperService(model_size=settings.whisper_model, device=settings.whisper_device)


# Create a singleton instance
whisper_service = create_whisper_service()
