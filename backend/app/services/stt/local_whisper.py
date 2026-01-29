"""Local Whisper STT service using ProcessPoolExecutor for parallelism.

This implementation uses ProcessPoolExecutor instead of ThreadPoolExecutor
to bypass the GIL and enable true parallelism on multi-core systems.

Model Caching:
- Service instance is created once at startup (via FastAPI lifespan)
- Each worker process loads the model once (first transcription)
- Model is cached per process and reused for all subsequent transcriptions
- This is critical for short recordings (5-10s) where model loading (5-10s)
  would otherwise be longer than transcription time (1-2s)
"""

import asyncio
import logging
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from app.services.stt.base import STTError, STTTimeoutError, TranscriptionResult

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

# Process-local model cache (each worker process has its own cache)
# Key: (model_size, device), Value: loaded model
_process_model_cache: dict[tuple[str, str], Any] = {}


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
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Audio loading timed out")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg failed to load audio: {e.stderr.decode('utf-8', errors='ignore')}"
        )

    # Convert raw PCM bytes to numpy array
    audio_int16 = np.frombuffer(result.stdout, dtype=np.int16)
    # Convert to float32 and normalize to [-1, 1]
    audio_float32 = audio_int16.astype(np.float32) / 32768.0

    return audio_float32


def _detect_device(device_preference: str = "auto") -> str:
    """Detect available device (CUDA, MPS, CPU).

    Args:
        device_preference: "auto", "cuda", "mps", or "cpu"

    Returns:
        Device string for Whisper ("cuda", "mps", or "cpu")
    """
    if not WHISPER_AVAILABLE or torch is None:
        return "cpu"

    if device_preference == "cpu":
        return "cpu"

    if device_preference == "cuda" and torch.cuda.is_available():
        return "cuda"

    if device_preference == "mps" and torch.backends.mps.is_available():
        return "mps"

    # Auto-detect
    if torch.cuda.is_available():
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
        return "cuda"

    if torch.backends.mps.is_available():
        logger.info("Apple Silicon GPU (MPS) detected")
        return "mps"

    logger.info("No GPU detected, using CPU")
    return "cpu"


def _get_cached_model(model_size: str, device: str) -> Any:
    """Get cached Whisper model or load if not cached (per-process cache).

    Each ProcessPoolExecutor worker process maintains its own cache.
    This avoids reloading the model for every transcription, which is critical
    for short recordings (5-10 seconds) where model loading (5-10s) would be
    longer than transcription time (1-2s).

    Args:
        model_size: Whisper model size (e.g., "base", "small")
        device: Device string ("cuda", "mps", "cpu")

    Returns:
        Loaded Whisper model (cached per process)
    """
    if not WHISPER_AVAILABLE or whisper is None:
        raise RuntimeError("Whisper not available. Install with: pip install openai-whisper")

    cache_key = (model_size, device)

    if cache_key not in _process_model_cache:
        logger.info(
            f"Loading Whisper model '{model_size}' on device '{device}' (first load in this process)"
        )
        start_time = time.time()
        _process_model_cache[cache_key] = whisper.load_model(model_size, device=device)
        load_time = time.time() - start_time
        logger.info(f"Whisper model loaded successfully in {load_time:.2f} seconds")
    else:
        logger.debug(f"Using cached Whisper model '{model_size}' on device '{device}'")

    return _process_model_cache[cache_key]


def _map_language_code(language: Optional[str]) -> Optional[str]:
    """Map language name to Whisper language code.

    Args:
        language: Language name or code (e.g., "spanish", "es")

    Returns:
        Language code (e.g., "es") or None
    """
    if not language:
        return None

    supported_languages = {
        "spanish": "es",
        "italian": "it",
        "german": "de",
        "french": "fr",
        "dutch": "nl",
        "english": "en",
    }

    language_lower = language.lower()
    if language_lower in supported_languages.values():
        return language_lower
    return supported_languages.get(language_lower, language_lower)


def _transcribe_in_process(
    model_size: str,
    device: str,
    audio_path: str,
    language_code: Optional[str],
) -> Dict[str, Any]:
    """Transcribe audio in separate process (bypasses GIL).

    This function runs in a worker process, so it can utilize multiple CPU cores.
    The model is cached per process to avoid reloading overhead for short recordings.

    Args:
        model_size: Whisper model size
        device: Device string
        audio_path: Path to audio file
        language_code: Optional language code

    Returns:
        Dictionary with transcription result
    """
    # Get cached model (loaded once per process, reused for all transcriptions)
    model = _get_cached_model(model_size, device)

    # Load audio
    audio = _load_audio(audio_path)

    # Transcribe
    options: Dict[str, Any] = {}
    if language_code:
        options["language"] = language_code

    # On CPU, fp16 is not supported - use fp32 to avoid warnings
    if device == "cpu":
        options["fp16"] = False

    result = model.transcribe(audio, **options)

    # Extract information
    text = str(result.get("text", "")).strip()
    detected_language = str(result.get("language", "unknown"))

    # Calculate average confidence from segments
    segments = result.get("segments", [])
    default_confidence = 0.9
    if segments:
        # Whisper provides "no_speech_prob" per segment; confidence = 1 - no_speech_prob
        confidences = [
            1.0 - (seg.get("no_speech_prob", 0.0) if isinstance(seg, dict) else 0.0)
            for seg in segments
        ]
        avg_confidence = sum(confidences) / len(confidences)
    else:
        avg_confidence = default_confidence

    # Get audio duration from segments
    if segments:
        last_segment = segments[-1]
        duration = last_segment.get("end", 0.0) if isinstance(last_segment, dict) else 0.0
    else:
        duration = 0.0

    return {
        "text": text,
        "language": detected_language,
        "confidence": avg_confidence,
        "duration": duration,
    }


def _warmup_model_in_process(model_size: str, device: str) -> None:
    """Warmup function to pre-load model in a worker process.

    This function is called during service initialization to pre-load the model
    in each worker process, ensuring the first transcription is fast.

    Args:
        model_size: Whisper model size
        device: Device string
    """
    try:
        _get_cached_model(model_size, device)
        logger.info(f"Warmed up model '{model_size}' on device '{device}' in worker process")
    except Exception as e:
        logger.warning(f"Failed to warmup model in worker process: {e}")


class LocalWhisperService:
    """Local Whisper STT service using ProcessPoolExecutor for parallelism.

    This implementation uses ProcessPoolExecutor instead of ThreadPoolExecutor
    to bypass the GIL and enable true parallelism on multi-core systems.

    Model Caching:
    - Service instance is created once at startup (via FastAPI lifespan)
    - Each worker process loads the model once (first transcription)
    - Model is cached per process and reused for all subsequent transcriptions
    - This is critical for short recordings (5-10s) where model loading (5-10s)
      would otherwise be longer than transcription time (1-2s)
    """

    # Available Whisper models
    AVAILABLE_MODELS = [
        "tiny",
        "base",
        "small",
        "medium",
        "large",
        "large-v2",
        "large-v3",
        "turbo",
    ]

    DEFAULT_CONFIDENCE = 0.9

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        max_workers: Optional[int] = None,
    ):
        """Initialize local Whisper service.

        The service instance is created once at application startup and reused
        for all transcription requests. Each worker process will load the model
        on first use and cache it for subsequent requests.

        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device preference ("auto", "cuda", "mps", "cpu")
            max_workers: Maximum number of worker processes (default: min(CPU count, 4))
        """
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper not available. Install with: pip install openai-whisper")

        self.model_size = model_size
        self.device = _detect_device(device)

        # Create process pool (bypasses GIL)
        # Use CPU count or max 4 to avoid memory issues (each process loads model)
        if max_workers is None:
            max_workers = min(os.cpu_count() or 1, 4)

        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        self._warmed_up = False

        logger.info(
            f"Initialized LocalWhisper with {max_workers} worker processes, "
            f"model={model_size}, device={self.device}. "
            f"Models will be cached per process after first load."
        )

    @property
    def name(self) -> str:
        return f"local_whisper_{self.device}"

    async def warmup(self) -> None:
        """Pre-load models in all worker processes for optimal first-call performance.

        This method submits warmup tasks to all worker processes to pre-load
        the model, ensuring the first transcription is fast (1-2s) instead of
        slow (5-10s model load + 1-2s transcription).

        This is critical for short recordings where users expect near real-time conversion.
        """
        if self._warmed_up:
            logger.debug("Service already warmed up")
            return

        logger.info(
            f"Warming up Whisper model '{self.model_size}' on device '{self.device}' in all worker processes..."
        )
        start_time = time.time()

        # Submit warmup tasks to all workers
        futures = []
        for _ in range(self._executor._max_workers):  # type: ignore[attr-defined]
            future = self._executor.submit(_warmup_model_in_process, self.model_size, self.device)
            futures.append(future)

        # Wait for all warmups to complete
        try:
            for future in futures:
                future.result(timeout=60)  # 60s timeout per worker
            warmup_time = time.time() - start_time
            self._warmed_up = True
            logger.info(
                f"Warmup complete in {warmup_time:.2f} seconds. All worker processes ready."
            )
        except Exception as e:
            logger.warning(f"Warmup completed with errors (some workers may not be ready): {e}")
            # Don't fail initialization if warmup fails - workers will load on first use

    async def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> TranscriptionResult:
        """Transcribe audio file using local Whisper.

        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'es', 'en')
            timeout: Optional timeout in seconds (default: 300s)

        Returns:
            TranscriptionResult with transcribed text

        Raises:
            STTTimeoutError: If transcription times out
            STTError: If transcription fails
        """
        audio_path_str = str(audio_path)
        language_code = _map_language_code(language) if language else None

        timeout = timeout or 300.0  # Default 5 minutes

        try:
            loop = asyncio.get_event_loop()
            # Run in separate process (true parallelism, bypasses GIL)
            result_dict = await asyncio.wait_for(
                loop.run_in_executor(
                    self._executor,
                    _transcribe_in_process,
                    self.model_size,
                    self.device,
                    audio_path_str,
                    language_code,
                ),
                timeout=timeout,
            )
            return TranscriptionResult(
                text=result_dict["text"],
                language=result_dict["language"],
                confidence=result_dict["confidence"],
                duration=result_dict["duration"],
            )
        except asyncio.TimeoutError:
            raise STTTimeoutError(f"Transcription timed out after {timeout}s")
        except Exception as e:
            raise STTError(f"Transcription failed: {e}") from e

    async def health_check(self) -> bool:
        """Check if Whisper service is available."""
        try:
            # Try to load model (quick check)
            if not WHISPER_AVAILABLE or whisper is None:
                return False
            # Just check if we can import and detect device
            return True
        except Exception as e:
            logger.error(f"Whisper health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close process pool and clean up resources."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)
            logger.info("LocalWhisper process pool shut down")

    def get_available_models(self) -> list[str]:
        """Return list of available Whisper models."""
        return self.AVAILABLE_MODELS.copy()

    def is_model_cached(self, model_size: str) -> bool:
        """Check if a Whisper model is already cached (downloaded).

        Args:
            model_size: Model to check

        Returns:
            True if model is cached, False otherwise
        """
        if not WHISPER_AVAILABLE or whisper is None:
            return False

        try:
            # Check if model file exists in whisper cache
            cache_dir = Path.home() / ".cache" / "whisper"
            model_file = cache_dir / f"{model_size}.pt"
            return model_file.exists()
        except Exception:
            return False

    def get_supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        return ["es", "it", "de", "fr", "nl", "en"]

    def get_cuda_info(self) -> dict[str, Any]:
        """Get CUDA availability and device information.

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
        info: dict[str, Any] = {
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
