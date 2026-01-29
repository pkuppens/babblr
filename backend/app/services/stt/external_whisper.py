"""External Whisper STT service via HTTP API.

This implementation calls an external Whisper microservice over HTTP.
Useful for production scale where Whisper runs on dedicated GPU servers.
"""

import logging
from pathlib import Path
from typing import Optional

import httpx

from app.services.stt.base import (
    STTError,
    STTTimeoutError,
    STTUnavailableError,
    TranscriptionResult,
)

logger = logging.getLogger(__name__)


class ExternalWhisperService:
    """External Whisper STT service via HTTP API.

    This implementation calls an external Whisper microservice over HTTP.
    Useful for production scale where Whisper runs on dedicated GPU servers.
    """

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
        base_url: str,
        timeout: float = 300.0,
        device: str = "auto",
    ):
        """Initialize external Whisper service.

        Args:
            base_url: Base URL of Whisper webservice (e.g., "http://whisper-service:9000")
            timeout: Request timeout in seconds
            device: Device preference ("auto", "cuda", "cpu") - used for info only
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.device = device
        self._client: Optional[httpx.AsyncClient] = None
        self._cuda_info_cache: Optional[dict] = None

    @property
    def name(self) -> str:
        return "external_whisper"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> TranscriptionResult:
        """Transcribe audio file using external Whisper service.

        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'es', 'en')
            timeout: Optional timeout override

        Returns:
            TranscriptionResult with transcribed text

        Raises:
            STTUnavailableError: If service is unavailable
            STTTimeoutError: If request times out
        """
        client = await self._get_client()
        effective_timeout = timeout or self.timeout

        try:
            # Read audio file
            with open(audio_path, "rb") as f:
                audio_data = f.read()

            # Prepare request
            files = {"audio_file": audio_data}
            data = {}
            if language:
                data["language"] = language

            # Call external service
            response = await client.post(
                "/asr",
                files=files,
                data=data,
                timeout=effective_timeout,
            )
            response.raise_for_status()

            result_data = response.json()

            return TranscriptionResult(
                text=result_data.get("text", ""),
                language=result_data.get("language"),
                confidence=result_data.get("confidence", self.DEFAULT_CONFIDENCE),
                duration=result_data.get("duration"),
            )
        except httpx.TimeoutException:
            raise STTTimeoutError(f"External Whisper service timed out after {effective_timeout}s")
        except httpx.HTTPStatusError as e:
            raise STTUnavailableError(f"External Whisper service error: {e}")
        except Exception as e:
            raise STTError(f"Transcription failed: {e}") from e

    async def health_check(self) -> bool:
        """Check if external Whisper service is available."""
        try:
            client = await self._get_client()
            response = await client.get("/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"External Whisper health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("External Whisper HTTP client closed")

    def get_available_models(self) -> list[str]:
        """Return list of available models."""
        return self.AVAILABLE_MODELS.copy()

    async def warmup(self) -> None:
        """Warmup external service (no-op, service is always ready)."""
        # External service doesn't need warmup
        pass

    def get_cuda_info(self) -> dict:
        """Get CUDA availability from external Whisper service.

        Returns basic CUDA info based on device configuration.
        For detailed CUDA info from the whisper container, use the async
        _fetch_cuda_info() method or call GET /stt/cuda endpoint.

        Returns:
            Dictionary with CUDA status based on device configuration
        """
        # Return cached info if available
        if self._cuda_info_cache is not None:
            return self._cuda_info_cache

        # Return basic info based on device setting
        # The /stt/cuda endpoint will call _fetch_cuda_info() for detailed info
        info = {
            "available": self.device == "cuda",
            "device": self.device,
            "device_name": None,
            "memory_total_gb": None,
            "memory_free_gb": None,
            "source": "config",
            "note": "For detailed CUDA info from whisper container, use GET /stt/cuda endpoint",
        }
        self._cuda_info_cache = info
        return info

    async def _fetch_cuda_info(self) -> dict:
        """Fetch CUDA info from whisper container API.

        Returns:
            Dictionary with CUDA status and device info
        """
        client = await self._get_client()

        # Try common endpoints for info
        endpoints_to_try = ["/info", "/status", "/health"]
        for endpoint in endpoints_to_try:
            try:
                response = await client.get(endpoint, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    # Extract CUDA info from response
                    # The whisper webservice may return device info in various formats
                    device_info = data.get("device", data.get("cuda", {}))
                    if isinstance(device_info, dict):
                        cuda_available = device_info.get("available", False) or device_info.get(
                            "cuda_available", False
                        )
                        return {
                            "available": cuda_available,
                            "device": device_info.get("device", self.device),
                            "device_name": device_info.get("device_name"),
                            "memory_total_gb": device_info.get("memory_total_gb"),
                            "memory_free_gb": device_info.get("memory_free_gb"),
                            "source": f"api_{endpoint}",
                        }
            except Exception:
                continue

        # If no endpoint provides info, return basic info
        return {
            "available": self.device == "cuda",
            "device": self.device,
            "device_name": None,
            "memory_total_gb": None,
            "memory_free_gb": None,
            "source": "config",
        }
