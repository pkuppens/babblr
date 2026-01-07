"""
Whisper STT Service for speech-to-text transcription.

This service provides an abstraction layer for speech-to-text functionality,
currently implemented using OpenAI Whisper. The interface design allows for
future replacement with other STT implementations (e.g., cloud-based services).
"""

import asyncio
import logging
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np

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

# Whisper expects audio at this sample rate
WHISPER_SAMPLE_RATE = 16000


def _get_ffmpeg_exe() -> str:
    """Get the path to ffmpeg executable.

    Uses imageio-ffmpeg's bundled binary, which works cross-platform without
    requiring ffmpeg to be installed system-wide or on PATH.

    Returns:
        Path to the ffmpeg executable.

    Raises:
        RuntimeError: If imageio-ffmpeg is not installed or ffmpeg not found.
    """
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError("imageio-ffmpeg not installed. Install with: pip install imageio-ffmpeg")
    except Exception as e:
        raise RuntimeError(f"Failed to get ffmpeg from imageio-ffmpeg: {e}")


def _load_audio(audio_path: str, sr: int = WHISPER_SAMPLE_RATE) -> np.ndarray:
    """Load audio file and convert to numpy array at the specified sample rate.

    Uses imageio-ffmpeg's bundled ffmpeg binary directly, avoiding the need for
    ffmpeg to be on PATH. This replicates what whisper.load_audio() does internally.

    Args:
        audio_path: Path to the audio file (supports any format ffmpeg can decode).
        sr: Target sample rate (default: 16000 Hz for Whisper).

    Returns:
        Audio as float32 numpy array normalized to [-1, 1].

    Raises:
        RuntimeError: If audio loading fails.
    """
    ffmpeg_exe = _get_ffmpeg_exe()

    # Run ffmpeg to convert audio to 16-bit PCM at target sample rate
    # This is exactly what whisper.load_audio() does, but using our bundled ffmpeg
    cmd = [
        ffmpeg_exe,
        "-nostdin",
        "-threads",
        "0",
        "-i",
        audio_path,
        "-f",
        "s16le",  # 16-bit signed little-endian PCM
        "-ac",
        "1",  # mono
        "-acodec",
        "pcm_s16le",
        "-ar",
        str(sr),
        "-",  # output to stdout
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to load audio '{audio_path}': ffmpeg returned {e.returncode}. "
            f"stderr: {e.stderr.decode(errors='replace')}"
        )

    # Convert to numpy float32 array normalized to [-1, 1]
    audio = np.frombuffer(result.stdout, np.int16).astype(np.float32) / 32768.0
    return audio


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

        try:
            start_time = time.time()

            # Run transcription with timeout
            result = await asyncio.wait_for(
                self._transcribe_async(audio_path, language), timeout=timeout
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

    async def _transcribe_async(
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

        # Load audio using our bundled ffmpeg (avoids PATH dependency)
        audio = _load_audio(audio_path)

        options: Dict[str, Any] = {}
        if language_code:
            options["language"] = language_code

        # On CPU, fp16 is not supported - use fp32 to avoid warnings
        if self.device == "cpu":
            options["fp16"] = False

        # Transcribe (passing numpy array directly, not file path)
        result = self.model.transcribe(audio, **options)

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

        language_lower = language.lower()

        # If it's already a code, return it
        if language_lower in self.SUPPORTED_LANGUAGES.values():
            return language_lower

        # Map from name to code
        return self.SUPPORTED_LANGUAGES.get(language_lower, language_lower)

    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        return list(self.SUPPORTED_LANGUAGES.values())

    def get_available_models(self) -> List[str]:
        """Return list of available Whisper models."""
        return self.AVAILABLE_MODELS


# Initialize the service with configuration
def create_whisper_service() -> WhisperService:
    """Create and initialize Whisper service with configuration."""
    from app.config import settings

    return WhisperService(model_size=settings.whisper_model, device=settings.whisper_device)


# Create a singleton instance
whisper_service = create_whisper_service()
