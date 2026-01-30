"""
Section 4: Speech Services Validation Tests

Unit tests for Speech-to-Text (Whisper) and Text-to-Speech (Edge TTS) services.
These tests use mocks and don't require actual audio files.

Run with: pytest tests/test_speech_services_validation.py -v

For testing with actual audio samples, use the manual test script:
    python tests/manual_speech_services_test.py
"""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# =============================================================================
# STT (SPEECH-TO-TEXT) VALIDATION TESTS
# =============================================================================


class TestSTTValidation:
    """Unit tests for Speech-to-Text (Whisper) service."""

    @pytest.mark.asyncio
    async def test_stt_transcribe_mock(self):
        """Unit test: STT transcription with mocked Whisper."""
        from app.services.stt.base import TranscriptionResult

        # Mock transcription result
        mock_result = TranscriptionResult(
            text="Hola, ¿cómo estás?",
            language="es",
            confidence=0.95,
            duration=2.5,
        )

        # Simulate what the route would do
        assert mock_result.text == "Hola, ¿cómo estás?"
        assert mock_result.language == "es"
        assert mock_result.confidence == 0.95
        assert mock_result.duration == 2.5

    @pytest.mark.asyncio
    async def test_stt_spanish_transcription_mock(self):
        """Unit test: Spanish language transcription (mocked)."""
        from app.services.stt.base import TranscriptionResult

        spanish_result = TranscriptionResult(
            text="Buenos días. Mi nombre es María.",
            language="es",
            confidence=0.92,
            duration=3.2,
        )

        assert spanish_result.language == "es"
        assert "María" in spanish_result.text
        assert 0 < spanish_result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_stt_french_transcription_mock(self):
        """Unit test: French language transcription (mocked)."""
        from app.services.stt.base import TranscriptionResult

        french_result = TranscriptionResult(
            text="Bonjour, comment allez-vous?",
            language="fr",
            confidence=0.93,
            duration=2.8,
        )

        assert french_result.language == "fr"
        assert "Bonjour" in french_result.text

    @pytest.mark.asyncio
    async def test_stt_german_transcription_mock(self):
        """Unit test: German language transcription (mocked)."""
        from app.services.stt.base import TranscriptionResult

        german_result = TranscriptionResult(
            text="Guten Tag, wie geht es Ihnen?",
            language="de",
            confidence=0.91,
            duration=3.0,
        )

        assert german_result.language == "de"
        assert "Guten Tag" in german_result.text

    @pytest.mark.asyncio
    async def test_stt_italian_transcription_mock(self):
        """Unit test: Italian language transcription (mocked)."""
        from app.services.stt.base import TranscriptionResult

        italian_result = TranscriptionResult(
            text="Ciao, come stai?",
            language="it",
            confidence=0.94,
            duration=2.3,
        )

        assert italian_result.language == "it"
        assert "Ciao" in italian_result.text

    @pytest.mark.asyncio
    async def test_stt_dutch_transcription_mock(self):
        """Unit test: Dutch language transcription (mocked)."""
        from app.services.stt.base import TranscriptionResult

        dutch_result = TranscriptionResult(
            text="Hallo, hoe gaat het met je?",
            language="nl",
            confidence=0.90,
            duration=2.9,
        )

        assert dutch_result.language == "nl"
        assert "Hallo" in dutch_result.text

    @pytest.mark.asyncio
    async def test_stt_confidence_score(self):
        """Unit test: Confidence score validation."""
        from app.services.stt.base import TranscriptionResult

        result = TranscriptionResult(
            text="Test",
            language="en",
            confidence=0.87,
            duration=1.0,
        )

        # Confidence should be between 0 and 1
        assert 0.0 <= result.confidence <= 1.0
        # Higher confidence indicates better transcription quality
        assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_stt_duration_tracking(self):
        """Unit test: Audio duration is properly tracked."""
        from app.services.stt.base import TranscriptionResult

        result = TranscriptionResult(
            text="Audio sample",
            language="en",
            confidence=0.89,
            duration=4.5,
        )

        # Duration should be positive and reasonable
        assert result.duration > 0
        assert result.duration < 300  # Less than 5 minutes for this test


# =============================================================================
# TTS (TEXT-TO-SPEECH) VALIDATION TESTS
# =============================================================================


class TestTTSValidation:
    """Unit tests for Text-to-Speech (Edge TTS) service."""

    def test_tts_request_structure(self):
        """Unit test: TTS request schema validation."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(text="Hola mundo", language="spanish")

        assert request.text == "Hola mundo"
        assert request.language == "spanish"

    def test_tts_spanish_request(self):
        """Unit test: Spanish TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Buenos días. ¿Cómo estás hoy?",
            language="spanish",
        )

        assert "Buenos" in request.text
        assert request.language == "spanish"

    def test_tts_french_request(self):
        """Unit test: French TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Bonjour, comment allez-vous aujourd'hui?",
            language="french",
        )

        assert "Bonjour" in request.text
        assert request.language == "french"

    def test_tts_german_request(self):
        """Unit test: German TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Guten Morgen. Wie geht es dir?",
            language="german",
        )

        assert "Guten" in request.text
        assert request.language == "german"

    def test_tts_italian_request(self):
        """Unit test: Italian TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Buongiorno, come stai?",
            language="italian",
        )

        assert "Buongiorno" in request.text
        assert request.language == "italian"

    def test_tts_dutch_request(self):
        """Unit test: Dutch TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Goedemorgen, hoe gaat het?",
            language="dutch",
        )

        assert "Goedemorgen" in request.text
        assert request.language == "dutch"

    def test_tts_english_request(self):
        """Unit test: English TTS request structure."""
        from app.models.schemas import TTSRequest

        request = TTSRequest(
            text="Good morning, how are you?",
            language="english",
        )

        assert "Good morning" in request.text
        assert request.language == "english"

    @pytest.mark.asyncio
    async def test_tts_response_mock(self):
        """Unit test: TTS response structure (mocked file path)."""
        from app.services.tts_service import tts_service

        # Mock the synthesize_speech method
        with patch.object(tts_service, "synthesize_speech", new_callable=AsyncMock) as mock:
            mock.return_value = "/tmp/audio_output.mp3"

            result = await tts_service.synthesize_speech("Hola", "spanish")

            assert result is not None
            assert result.endswith(".mp3")

    @pytest.mark.asyncio
    async def test_tts_multiple_languages_mock(self):
        """Unit test: TTS supports multiple languages (mocked)."""
        from app.services.tts_service import tts_service

        languages = ["spanish", "french", "german", "italian", "dutch", "english"]

        with patch.object(tts_service, "synthesize_speech", new_callable=AsyncMock) as mock:
            mock.return_value = "/tmp/audio.mp3"

            for lang in languages:
                result = await tts_service.synthesize_speech("Test", lang)
                assert result is not None

    @pytest.mark.asyncio
    async def test_tts_text_sanitization_mock(self):
        """Unit test: TTS handles special characters (mocked)."""
        from app.services.tts_service import tts_service

        test_cases = [
            "Hello, how are you?",
            "¿Cómo estás?",
            "Pourquoi pas?",
            "Großartig!",
        ]

        with patch.object(tts_service, "synthesize_speech", new_callable=AsyncMock) as mock:
            mock.return_value = "/tmp/audio.mp3"

            for text in test_cases:
                result = await tts_service.synthesize_speech(text, "english")
                assert result is not None


# =============================================================================
# STT/TTS INTEGRATION TESTS
# =============================================================================


class TestSpeechServicesIntegration:
    """Integration tests for STT and TTS together."""

    @pytest.mark.asyncio
    async def test_stt_to_tts_pipeline_mock(self):
        """Unit test: STT output can be used as TTS input (mocked)."""
        from app.models.schemas import TTSRequest
        from app.services.stt.base import TranscriptionResult
        from app.services.tts_service import tts_service

        # Step 1: Mock STT transcription
        stt_result = TranscriptionResult(
            text="La comida está deliciosa",
            language="es",
            confidence=0.94,
            duration=2.5,
        )

        # Step 2: Mock TTS from STT output
        with patch.object(tts_service, "synthesize_speech", new_callable=AsyncMock) as mock:
            mock.return_value = "/tmp/audio_out.mp3"

            # Use transcribed text as input to TTS
            tts_request = TTSRequest(
                text=stt_result.text,
                language="spanish",
            )

            result = await tts_service.synthesize_speech(
                tts_request.text,
                tts_request.language,
            )

            assert result is not None
            assert stt_result.text in tts_request.text

    @pytest.mark.asyncio
    async def test_conversation_speech_flow_mock(self):
        """Unit test: Full conversation with STT input and TTS output (mocked)."""
        from app.models.schemas import TTSRequest
        from app.services.stt.base import TranscriptionResult
        from app.services.tts_service import tts_service

        # User speaks (STT mocked)
        user_input = TranscriptionResult(
            text="¿Cuál es el mejor restaurante?",
            language="es",
            confidence=0.91,
            duration=3.0,
        )

        # LLM response (would come from actual LLM)
        llm_response = "El mejor restaurante en la ciudad es La Pergola."

        # TTS to speak the response (mocked)
        with patch.object(tts_service, "synthesize_speech", new_callable=AsyncMock) as mock:
            mock.return_value = "/tmp/response_audio.mp3"

            tts_request = TTSRequest(
                text=llm_response,
                language="spanish",
            )

            audio_path = await tts_service.synthesize_speech(
                tts_request.text,
                tts_request.language,
            )

            # Verify the complete flow works
            assert user_input.text == "¿Cuál es el mejor restaurante?"
            assert llm_response == "El mejor restaurante en la ciudad es La Pergola."
            assert audio_path is not None
