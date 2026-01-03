"""
Speech-to-text routes for audio transcription.

This module handles audio file uploads and transcription using OpenAI Whisper.
It supports multiple languages and integrates with the conversation system.
"""
import logging
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.models.models import Conversation
from app.models.schemas import TranscriptionResponse
from app.services.whisper_service import whisper_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    conversation_id: int,
    language: str,
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Transcribe audio to text using OpenAI Whisper.

    This endpoint receives an audio file, saves it temporarily, and uses the Whisper
    service to transcribe it to text. The transcription is returned without corrections,
    which are handled separately by the chat endpoint.

    Args:
        conversation_id: ID of the conversation this audio belongs to
        language: Target language code (e.g., 'spanish', 'french')
        audio: Uploaded audio file (WebM, MP4, WAV formats supported)
        db: Database session (injected dependency)

    Returns:
        TranscriptionResponse: Object containing the transcribed text

    Raises:
        HTTPException: 404 if conversation not found
        HTTPException: 500 if transcription fails or file processing errors occur
    """
    logger.info(
        "Received audio transcription request: conversation_id=%s, language=%s, "
        "filename=%s, content_type=%s",
        conversation_id, language, audio.filename, audio.content_type
    )

    # Verify conversation exists
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        logger.warning("Conversation not found: id=%s", conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temp file
        suffix = os.path.splitext(audio.filename)[1] if audio.filename else '.wav'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        # Write uploaded content
        content = await audio.read()
        logger.debug("Audio file size: %s bytes", len(content))
        temp_file.write(content)
        temp_file.close()

        logger.info("Starting transcription for conversation_id=%s", conversation_id)
        # Transcribe
        transcribed_text, result = await whisper_service.transcribe_audio(
            temp_file.name,
            language
        )

        logger.info(
            "Transcription complete: conversation_id=%s, text_length=%s",
            conversation_id, len(transcribed_text)
        )

        return TranscriptionResponse(
            text=transcribed_text,
            corrections=None  # Corrections will be done in chat endpoint
        )

    except Exception as e:
        logger.error(
            "Transcription failed: conversation_id=%s, error=%s",
            conversation_id, str(e), exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            logger.debug("Cleaned up temporary file: %s", temp_file.name)
