"""Factory for creating STT service instances.

Creates appropriate STT implementation based on configuration.
Supports swapping implementations for testing and different environments.
"""

import logging
from typing import Optional

from app.config import settings
from app.services.stt.base import STTService
from app.services.stt.external_whisper import ExternalWhisperService
from app.services.stt.mock_whisper import MockSTTService
from app.services.whisper_service import WhisperService

logger = logging.getLogger(__name__)


class STTServiceFactory:
    """Factory for creating STT service instances.

    Creates appropriate STT implementation based on configuration.
    Supports swapping implementations for testing and different environments.
    """

    _instance: Optional[STTService] = None

    @classmethod
    def create(cls, provider: Optional[str] = None) -> STTService:
        """Create STT service instance.

        Args:
            provider: Provider name override (None = use settings.stt_provider)

        Returns:
            STT service instance

        Raises:
            ValueError: If provider not supported
        """
        provider = provider or settings.stt_provider

        if provider == "local" or provider.lower() == "whisper":
            logger.info("Creating WhisperService (stable ThreadPoolExecutor implementation)")
            return WhisperService(
                model_size=settings.whisper_model,
                device=settings.whisper_device,
            )
        elif provider == "external" or provider.lower() == "whisper_webservice":
            logger.info("Creating ExternalWhisper service")
            return ExternalWhisperService(
                base_url=settings.stt_webservice_url,
                timeout=float(settings.stt_webservice_timeout),
                device=settings.stt_webservice_device,
            )
        elif provider == "mock":
            logger.info("Creating MockSTT service (testing)")
            return MockSTTService()
        else:
            raise ValueError(f"Unsupported STT provider: {provider}")

    @classmethod
    def get_instance(cls) -> STTService:
        """Get singleton instance (for backward compatibility during migration).

        Note: This method will be deprecated. Use create() with dependency injection instead.
        """
        if cls._instance is None:
            cls._instance = cls.create()
        return cls._instance

    @classmethod
    def clear_instance(cls) -> None:
        """Clear singleton instance (for testing)."""
        if cls._instance and hasattr(cls._instance, "close"):
            # Close resources if service supports it
            import asyncio

            try:
                asyncio.run(cls._instance.close())
            except Exception as e:
                logger.warning(f"Error closing STT service: {e}")
        cls._instance = None
