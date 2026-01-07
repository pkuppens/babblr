"""
STT (Speech-to-Text) API routes.

This module provides endpoints for speech-to-text transcription,
language support information, and model availability.
"""

import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.db import get_db
from app.models.models import Conversation
from app.models.schemas import TranscriptionResponse
from app.services.language_catalog import LANGUAGE_VARIANTS, list_locales
from app.services.whisper_service import whisper_service

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TRANSCRIPTION_TIMEOUT = 30  # seconds

router = APIRouter(prefix="/stt", tags=["speech-to-text"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
    conversation_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Transcribe audio file to text using OpenAI Whisper.

    This endpoint receives an audio file and transcribes it to text.
    Supports multiple audio formats (webm, wav, mp3, etc.).

    Args:
        audio_file: Uploaded audio file
        language: Optional language hint (e.g., 'spanish', 'es')

    Returns:
        TranscriptionResponse with text, language, confidence, and duration

    Raises:
        HTTPException: 400 for invalid file, 500 for transcription errors
    """
    logger.info(
        "Received transcription request: filename=%s, content_type=%s, language=%s",
        audio.filename,
        audio.content_type,
        language,
    )

    # Validate file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    temp_file = None

    try:
        # If a conversation_id is provided, validate it exists so clients can keep
        # conversation-scoped workflows without using the legacy /speech routes.
        if conversation_id is not None:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

        # Create temp file
        suffix = os.path.splitext(audio.filename)[1] or ".webm"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        # Write uploaded content
        content = await audio.read()
        logger.debug("Audio file size: %d bytes", len(content))

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        temp_file.write(content)
        temp_file.close()

        # Save file in development mode (for debugging/testing)
        if settings.babblr_dev_mode:
            await _save_audio_file(temp_file.name, audio.filename)

        logger.info("Starting transcription...")

        # Transcribe with timeout
        result = await whisper_service.transcribe(
            temp_file.name, language=language, timeout=DEFAULT_TRANSCRIPTION_TIMEOUT
        )

        logger.info(
            "Transcription successful: language=%s, confidence=%.2f, duration=%.2fs",
            result.language,
            result.confidence,
            result.duration,
        )

        return TranscriptionResponse(
            text=result.text,
            language=result.language,
            confidence=result.confidence,
            duration=result.duration,
            corrections=None,  # Corrections handled separately by chat endpoint
        )

    except Exception as e:
        logger.error("Transcription failed: %s", str(e), exc_info=True)

        # Provide more specific error messages
        error_msg = str(e)
        if "timed out" in error_msg.lower():
            raise HTTPException(
                status_code=408,
                detail="Transcription timed out. Please try with a shorter audio file.",
            )
        elif "not installed" in error_msg.lower():
            raise HTTPException(status_code=503, detail="Speech-to-text service not available")
        else:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")

    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
                logger.debug("Cleaned up temporary file: %s", temp_file.name)
            except Exception as e:
                logger.warning("Failed to delete temp file: %s", str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for speech-to-text.

    Returns:
        JSON object with supported languages and their codes
    """
    logger.debug("Getting supported languages")

    supported_locales = list_locales(stt_only=True)

    languages = []
    for variant in LANGUAGE_VARIANTS:
        if variant.locale not in supported_locales:
            continue
        languages.append(
            {
                "locale": variant.locale,
                "iso_639_1": variant.iso_639_1,
                "iso_3166_1": variant.iso_3166_1,
                "name": variant.name,
                "native_name": variant.native_name,
                "stt": {"supported": variant.stt, "whisper_language_code": variant.iso_639_1},
                "tts": {"supported": variant.tts},
            }
        )

    return JSONResponse(
        content={
            "languages": languages,
            "count": len(languages),
        }
    )


@router.get("/models")
async def get_available_models():
    """
    Get list of available Whisper models.

    Returns:
        JSON object with available models and current model
    """
    logger.debug("Getting available Whisper models")

    models = whisper_service.get_available_models()
    current_model = settings.whisper_model

    # Model details
    model_details = {
        "tiny": {
            "name": "tiny",
            "parameters": "39M",
            "vram": "~1GB",
            "speed": "~10x faster",
            "description": "Fastest, least accurate",
        },
        "base": {
            "name": "base",
            "parameters": "74M",
            "vram": "~1GB",
            "speed": "~7x faster",
            "description": "Good balance (default)",
        },
        "small": {
            "name": "small",
            "parameters": "244M",
            "vram": "~2GB",
            "speed": "~4x faster",
            "description": "Better accuracy",
        },
        "medium": {
            "name": "medium",
            "parameters": "769M",
            "vram": "~5GB",
            "speed": "~2x faster",
            "description": "High accuracy",
        },
        "large": {
            "name": "large",
            "parameters": "1550M",
            "vram": "~10GB",
            "speed": "1x (baseline)",
            "description": "Best accuracy, requires GPU",
        },
    }

    return JSONResponse(
        content={
            "models": [model_details.get(model, {"name": model}) for model in models],
            "current_model": current_model,
            "device": whisper_service.device if hasattr(whisper_service, "device") else "unknown",
            "multilingual": True,
            "notes": [
                "Whisper model selection is not language-specific (models are multilingual).",
                "You may pass a language hint as ISO-639-1 (e.g., 'en') or locale (e.g., 'en-GB'); locales map to ISO-639-1.",
            ],
            "count": len(models),
        }
    )


async def _save_audio_file(temp_path: str, original_filename: str) -> str | None:
    """
    Save audio file to storage in development mode.

    Args:
        temp_path: Path to temporary file
        original_filename: Original filename from upload

    Returns:
        Path to saved file, or None if saving failed
    """
    try:
        # Create storage directory if it doesn't exist
        storage_path = Path(settings.babblr_audio_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(original_filename)[1]
        filename = f"audio_{timestamp}{ext}"

        # Save file
        dest_path = storage_path / filename
        shutil.copy2(temp_path, dest_path)

        logger.info("Audio file saved in development mode: %s", dest_path)
        return str(dest_path)

    except Exception as e:
        logger.warning("Failed to save audio file in development mode: %s", str(e))
        return None
