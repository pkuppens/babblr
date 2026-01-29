"""
Whisper STT Service for speech-to-text transcription.

This service provides an abstraction layer for speech-to-text functionality,
currently implemented using OpenAI Whisper. The interface design allows for
future replacement with other STT implementations (e.g., cloud-based services).
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
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
        self, audio_path: str, language: Optional[str] = None, timeout: int = 30
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language hint (e.g., 'es' for Spanish)
            timeout: Timeout in seconds for transcription

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

    # Available Whisper models (including newer variants)
    # Note: large-v2, large-v3, and turbo are newer models with improved accuracy/speed
    AVAILABLE_MODELS = [
        "tiny",
        "base",
        "small",
        "medium",
        "large",
        "large-v2",  # Improved version of large
        "large-v3",  # Latest and most accurate (recommended for best quality)
        "turbo",  # Optimized for speed with good accuracy
    ]

    # Default confidence when no segments available
    DEFAULT_CONFIDENCE = 0.9

    def __init__(self, model_size: str = "base", device: str = "auto"):
        """
        Initialize Whisper service.

        Args:
            model_size: Model to use (tiny, base, small, medium, large, large-v2, large-v3, turbo)
            device: Device to use ("auto", "cuda", or "cpu")
        """
        self.model = None
        self.model_size = model_size
        self.device = self._determine_device(device)
        self._load_model(model_size)

    @property
    def name(self) -> str:
        """Name of the STT service implementation."""
        return f"whisper_{self.device}"

    def is_model_cached(self, model_size: str) -> bool:
        """
        Check if a Whisper model is already cached (downloaded).

        Args:
            model_size: Model to check

        Returns:
            True if model is cached, False otherwise
        """
        if not WHISPER_AVAILABLE or whisper is None:
            return False

        try:
            # Check if model file exists in whisper cache
            from pathlib import Path

            # Whisper stores models in ~/.cache/whisper/ by default
            cache_dir = Path.home() / ".cache" / "whisper"
            model_file = cache_dir / f"{model_size}.pt"

            return model_file.exists()
        except Exception:
            return False

    def _load_model(self, model_size: str) -> bool:
        """
        Load a Whisper model.

        Args:
            model_size: Model to load

        Returns:
            True if model loaded successfully, False otherwise
        """
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            return False

        try:
            is_cached = self.is_model_cached(model_size)
            action = "Loading" if is_cached else "Downloading and loading"
            logger.info("%s Whisper model: %s on device: %s", action, model_size, self.device)
            start_time = time.time()

            # Load model (this will automatically download if not cached)
            assert whisper is not None
            self.model = whisper.load_model(model_size, device=self.device)
            self.model_size = model_size

            load_time = time.time() - start_time
            logger.info("Whisper model loaded successfully in %.2f seconds", load_time)
            return True

        except Exception as e:
            logger.error("Failed to load Whisper model: %s", str(e), exc_info=True)
            self.model = None
            return False

    def switch_model(self, new_model_size: str) -> bool:
        """
        Switch to a different Whisper model without restarting the service.

        Args:
            new_model_size: New model to use

        Returns:
            True if switch was successful, False otherwise
        """
        if new_model_size not in self.AVAILABLE_MODELS:
            logger.error(
                "Invalid model size: %s. Available: %s", new_model_size, self.AVAILABLE_MODELS
            )
            return False

        if new_model_size == self.model_size and self.model is not None:
            logger.info("Model %s is already loaded", new_model_size)
            return True

        logger.info("Switching Whisper model from %s to %s", self.model_size, new_model_size)

        # Unload current model to free memory
        if self.model is not None:
            del self.model
            self.model = None
            # Force garbage collection to free GPU memory if using CUDA
            if self.device == "cuda" and torch is not None:
                torch.cuda.empty_cache()

        # Load new model
        return self._load_model(new_model_size)

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
        self, audio_path: str, language: Optional[str] = None, timeout: Optional[float] = None
    ):
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language hint (e.g., 'es' or 'spanish')
            timeout: Optional timeout in seconds (default: 30.0)

        Returns:
            TranscriptionResult with text, language, confidence, and duration

        Raises:
            Exception: If Whisper is not available or transcription fails
            asyncio.TimeoutError: If transcription takes longer than timeout
        """
        if not WHISPER_AVAILABLE or self.model is None:
            from app.services.stt.base import STTError

            raise STTError(
                "Whisper is not installed or failed to load. "
                "Install with: pip install openai-whisper"
            )

        from app.services.stt.base import STTError, STTTimeoutError

        try:
            start_time = time.time()
            effective_timeout = timeout or 30.0

            # Run transcription with timeout
            result = await asyncio.wait_for(
                self._transcribe_async(audio_path, language), timeout=effective_timeout
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
            effective_timeout = timeout or 30.0
            logger.error("Transcription timed out after %.1f seconds", effective_timeout)
            raise STTTimeoutError(f"Transcription timed out after {effective_timeout}s")
        except (STTTimeoutError, STTError):
            raise
        except Exception as e:
            raise STTError(f"Transcription failed: {e}") from e

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
        # Whisper returns a dict with "text" as a string
        text = str(result.get("text", "")).strip()  # type: ignore[union-attr]
        detected_language = str(result.get("language", "unknown"))  # type: ignore[union-attr]

        # Calculate average confidence from segments
        segments = result.get("segments", [])  # type: ignore[union-attr]
        if segments:
            # Whisper provides "no_speech_prob" per segment; confidence = 1 - no_speech_prob
            confidences = [
                1.0 - (seg.get("no_speech_prob", 0.0) if isinstance(seg, dict) else 0.0)
                for seg in segments
            ]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = self.DEFAULT_CONFIDENCE  # Default if no segments

        # Get audio duration from segments
        if segments:
            last_segment = segments[-1]
            duration = last_segment.get("end", 0.0) if isinstance(last_segment, dict) else 0.0
        else:
            duration = 0.0

        from app.services.stt.base import TranscriptionResult

        return TranscriptionResult(
            text=text,
            language=detected_language,
            confidence=avg_confidence,
            duration=duration,
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
        return self.AVAILABLE_MODELS.copy()

    def get_cuda_info(self) -> Dict[str, Any]:
        """
        Get CUDA availability and device information.

        Returns:
            Dictionary with CUDA status, device name, and memory info
        """
        if not WHISPER_AVAILABLE or torch is None:
            return {
                "available": False,
                "device": "unknown",
                "device_name": None,
                "memory_total_gb": None,
                "memory_free_gb": None,
            }

        cuda_available = torch.cuda.is_available()
        info = {
            "available": cuda_available,
            "device": self.device,
        }

        if cuda_available:
            try:
                device_name = torch.cuda.get_device_name(0)
                memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
                memory_free = memory_total - memory_allocated

                info.update(
                    {
                        "device_name": device_name,
                        "memory_total_gb": round(memory_total, 2),
                        "memory_allocated_gb": round(memory_allocated, 2),
                        "memory_free_gb": round(memory_free, 2),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to get CUDA device info: {e}")
                info["device_name"] = "unknown"
        else:
            info.update(
                {
                    "device_name": None,
                    "memory_total_gb": None,
                    "memory_free_gb": None,
                }
            )

        return info

    async def health_check(self) -> bool:
        """Check if Whisper service is available."""
        try:
            if not WHISPER_AVAILABLE or self.model is None:
                return False
            return True
        except Exception as e:
            logger.error(f"Whisper health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close resources and clean up model."""
        if self.model is not None:
            # Unload model to free memory
            del self.model
            self.model = None
            # Force garbage collection to free GPU memory if using CUDA
            if self.device == "cuda" and torch is not None:
                torch.cuda.empty_cache()
            logger.info("WhisperService closed and resources cleaned up")

    async def warmup(self) -> None:
        """Warmup service (model is already loaded in __init__)."""
        # Model is already loaded during initialization, so this is a no-op
        logger.debug("WhisperService warmup: model already loaded")


class WhisperWebservice(STTService):
    """Use a remote Whisper ASR webservice over HTTP.

    This adapter sends audio to a Whisper ASR webservice container (e.g. the
    openai-whisper-asr-webservice image) and parses the response. It supports
    basic transcription with language hints and JSON output.
    """

    def __init__(self, base_url: str, model_size: str, device: str, timeout: int = 300):
        """Initialize the remote webservice client.

        Args:
            base_url: Base URL of the Whisper webservice (e.g., http://babblr-whisper:9000).
            model_size: The configured model name for display (e.g., "base", "large-v3").
            device: Device label reported to the UI ("cuda", "cpu", or "auto").
            timeout: Request timeout in seconds for remote transcription.
        """
        self.base_url = base_url.rstrip("/")
        self.model_size = model_size
        self.device = device
        self.timeout = timeout

    def _map_language_code(self, language: Optional[str]) -> Optional[str]:
        """Map full language names to Whisper language codes.

        Args:
            language: Language name or code.

        Returns:
            Language code (e.g., "es") or None if not provided.
        """
        if not language:
            return None

        language_lower = language.lower()
        if language_lower in WhisperService.SUPPORTED_LANGUAGES.values():
            return language_lower
        return WhisperService.SUPPORTED_LANGUAGES.get(language_lower, language_lower)

    async def transcribe(
        self, audio_path: str, language: Optional[str] = None, timeout: int = 30
    ) -> TranscriptionResult:
        """Transcribe audio by calling a remote Whisper ASR webservice.

        Args:
            audio_path: Path to the audio file.
            language: Optional language hint (e.g., "es" or "spanish").
            timeout: Timeout in seconds for the HTTP request.

        Returns:
            TranscriptionResult with text, language, confidence, and duration.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            RuntimeError: If the remote service returns an error response.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        language_code = self._map_language_code(language)
        params: dict[str, Any] = {"task": "transcribe", "output": "json"}
        if language_code:
            params["language"] = language_code

        effective_timeout = max(timeout, self.timeout)
        file_name = Path(audio_path).name

        try:
            async with httpx.AsyncClient(timeout=effective_timeout) as client:
                with open(audio_path, "rb") as audio_file:
                    files = {"audio_file": (file_name, audio_file, "application/octet-stream")}
                    response = await client.post(f"{self.base_url}/asr", params=params, files=files)
                    response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Whisper webservice request failed: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            try:
                payload = json.loads(response.text)
            except json.JSONDecodeError:
                payload = None

        if isinstance(payload, dict):
            text = str(payload.get("text", "")).strip()
            detected_language = str(payload.get("language", language_code or "unknown"))
        else:
            text = response.text.strip()
            detected_language = language_code or "unknown"

        return TranscriptionResult(
            text=text,
            language=detected_language,
            confidence=WhisperService.DEFAULT_CONFIDENCE,
            duration=0.0,
            metadata={"remote": True, "provider": "whisper_webservice"},
        )

    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        return list(WhisperService.SUPPORTED_LANGUAGES.values())

    def get_available_models(self) -> List[str]:
        """Return list of available models."""
        return WhisperService.AVAILABLE_MODELS.copy()

    def is_model_cached(self, model_size: str) -> bool:
        """Return False for remote model cache checks.

        Args:
            model_size: Model to check.

        Returns:
            False because cache is managed by the remote service.
        """
        return False

    def switch_model(self, new_model_size: str) -> bool:
        """Return False because model switching is external.

        Args:
            new_model_size: New model to use.

        Returns:
            False since the remote service must be restarted with ASR_MODEL.
        """
        return False

    def get_cuda_info(self) -> Dict[str, Any]:
        """Return CUDA status as reported by configuration.

        Returns:
            Dictionary with CUDA status and basic device info.
        """
        available = self.device == "cuda"
        return {
            "available": available,
            "device": self.device,
            "device_name": None,
            "memory_total_gb": None,
            "memory_free_gb": None,
        }


# Initialize the service with configuration
def create_whisper_service() -> STTService:
    """Create and initialize the STT service with configuration.

    Returns:
        STTService instance (local Whisper or remote webservice).
    """
    from app.config import settings

    if settings.stt_provider.lower() == "whisper_webservice":
        return WhisperWebservice(
            base_url=settings.stt_webservice_url,
            model_size=settings.whisper_model,
            device=settings.stt_webservice_device,
            timeout=settings.stt_webservice_timeout,
        )

    return WhisperService(model_size=settings.whisper_model, device=settings.whisper_device)


# Create a singleton instance
whisper_service = create_whisper_service()
