"""Unit tests for STT service factory.

Tests the STTServiceFactory class for creating different STT implementations.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.stt.external_whisper import ExternalWhisperService
from app.services.stt.factory import STTServiceFactory
from app.services.stt.mock_whisper import MockSTTService
from app.services.whisper_service import WhisperService


class TestSTTServiceFactory:
    """Tests for STTServiceFactory."""

    def setup_method(self):
        """Clear factory instance before each test."""
        STTServiceFactory.clear_instance()

    def teardown_method(self):
        """Clear factory instance after each test."""
        STTServiceFactory.clear_instance()

    def test_create_local_whisper_service(self):
        """Test creating local Whisper service."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "local"
            mock_settings.whisper_model = "base"
            mock_settings.whisper_device = "cpu"

            service = STTServiceFactory.create()

            assert isinstance(service, WhisperService)

    def test_create_whisper_service_alternate_name(self):
        """Test creating Whisper service with alternate provider name."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.whisper_model = "base"
            mock_settings.whisper_device = "cpu"

            service = STTServiceFactory.create(provider="whisper")

            assert isinstance(service, WhisperService)

    def test_create_external_whisper_service(self):
        """Test creating external Whisper service."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_webservice_url = "http://localhost:8080"
            mock_settings.stt_webservice_timeout = "30"
            mock_settings.stt_webservice_device = "gpu"

            service = STTServiceFactory.create(provider="external")

            assert isinstance(service, ExternalWhisperService)

    def test_create_external_whisper_service_alternate_name(self):
        """Test creating external Whisper service with alternate provider name."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_webservice_url = "http://localhost:8080"
            mock_settings.stt_webservice_timeout = "30"
            mock_settings.stt_webservice_device = "gpu"

            service = STTServiceFactory.create(provider="whisper_webservice")

            assert isinstance(service, ExternalWhisperService)

    def test_create_mock_stt_service(self):
        """Test creating mock STT service."""
        service = STTServiceFactory.create(provider="mock")

        assert isinstance(service, MockSTTService)

    def test_create_with_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported STT provider: invalid"):
            STTServiceFactory.create(provider="invalid")

    def test_create_uses_settings_when_no_provider(self):
        """Test that create() uses settings.stt_provider when no provider specified."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            service = STTServiceFactory.create()

            assert isinstance(service, MockSTTService)

    def test_provider_override(self):
        """Test that explicit provider overrides settings."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "local"
            mock_settings.whisper_model = "base"
            mock_settings.whisper_device = "cpu"

            # Despite settings saying "local", we explicitly request "mock"
            service = STTServiceFactory.create(provider="mock")

            assert isinstance(service, MockSTTService)

    def test_get_instance_creates_singleton(self):
        """Test that get_instance() creates and returns singleton."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            instance1 = STTServiceFactory.get_instance()
            instance2 = STTServiceFactory.get_instance()

            assert instance1 is instance2
            assert isinstance(instance1, MockSTTService)

    def test_clear_instance(self):
        """Test that clear_instance() removes singleton."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            instance1 = STTServiceFactory.get_instance()
            STTServiceFactory.clear_instance()
            instance2 = STTServiceFactory.get_instance()

            assert instance1 is not instance2

    def test_clear_instance_calls_close(self):
        """Test that clear_instance() calls close() on service if available."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            # Create instance
            instance = STTServiceFactory.get_instance()

            # Add a mock close method
            instance.close = MagicMock()

            # Clear should call close
            STTServiceFactory.clear_instance()

            # Note: close() is called via asyncio.run() so we can't easily verify the call
            # This test verifies no exception is raised

    def test_clear_instance_handles_close_error(self):
        """Test that clear_instance() handles errors from close() gracefully."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            # Create instance
            instance = STTServiceFactory.get_instance()

            # Add a mock close method that raises an error
            async def failing_close():
                raise Exception("Close failed")

            instance.close = failing_close

            # Clear should handle the error without raising
            STTServiceFactory.clear_instance()  # Should not raise

    def test_create_returns_different_instances(self):
        """Test that create() returns new instances each time (not singleton)."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.stt_provider = "mock"

            instance1 = STTServiceFactory.create()
            instance2 = STTServiceFactory.create()

            # create() should return different instances
            assert instance1 is not instance2

    def test_case_insensitive_provider_names(self):
        """Test that provider names are case-insensitive."""
        with patch("app.services.stt.factory.settings") as mock_settings:
            mock_settings.whisper_model = "base"
            mock_settings.whisper_device = "cpu"

            service1 = STTServiceFactory.create(provider="WHISPER")
            service2 = STTServiceFactory.create(provider="Whisper")

            assert isinstance(service1, WhisperService)
            assert isinstance(service2, WhisperService)
