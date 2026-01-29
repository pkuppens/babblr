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

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.db import get_db
from app.dependencies import get_stt_service
from app.models.models import Conversation, Message
from app.models.schemas import TranscriptionResponse
from app.services.language_catalog import LANGUAGE_VARIANTS, list_locales
from app.services.stt import STTError, STTService, STTTimeoutError
from app.services.stt_correction_service import get_stt_correction_service
from app.utils.performance import async_perf_timer

logger = logging.getLogger(__name__)

# Global state for model switching status
_model_switch_status: dict = {"status": "idle", "target_model": None, "error": None}

# Configuration constants
DEFAULT_TRANSCRIPTION_TIMEOUT = 30  # seconds

router = APIRouter(prefix="/stt", tags=["speech-to-text"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
    conversation_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    stt_service: STTService = Depends(get_stt_service),
):
    """
    Transcribe audio file to text using OpenAI Whisper.

    This endpoint receives an audio file and transcribes it to text.
    Supports multiple audio formats (webm, wav, mp3, etc.).

    When conversation_id is provided, the transcription is corrected using
    an LLM with conversation context to fix speech recognition errors
    (homophones, similar-sounding words, etc.).

    Args:
        audio_file: Uploaded audio file
        language: Optional language hint (e.g., 'spanish', 'es')
        conversation_id: Optional conversation ID for context-aware correction

    Returns:
        TranscriptionResponse with text, language, confidence, duration, and corrections

    Raises:
        HTTPException: 400 for invalid file, 500 for transcription errors
    """
    logger.info(
        "Received transcription request: filename=%s, content_type=%s, language=%s, conversation_id=%s",
        audio.filename,
        audio.content_type,
        language,
        conversation_id,
    )

    # Validate file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    temp_file = None
    conversation = None
    conversation_history = []

    try:
        # If a conversation_id is provided, validate it exists and fetch context
        if conversation_id is not None:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Fetch conversation history for STT correction
            messages_result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            messages = messages_result.scalars().all()
            conversation_history = [
                {"role": str(msg.role), "content": str(msg.content)} for msg in messages
            ]

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
        try:
            async with async_perf_timer("stt.transcribe_whisper", logging.INFO):
                result = await stt_service.transcribe(
                    temp_file.name, language=language, timeout=DEFAULT_TRANSCRIPTION_TIMEOUT
                )
        except STTTimeoutError as e:
            raise HTTPException(
                status_code=408,
                detail=f"Transcription timed out: {str(e)}",
            )
        except STTError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}",
            )

        logger.info(
            "Transcription successful: language=%s, confidence=%.2f, duration=%.2fs",
            result.language,
            result.confidence,
            result.duration,
        )

        # Apply STT correction if conversation context is available
        corrections = None
        final_text = result.text

        if conversation is not None and conversation_history:
            stt_correction_service = get_stt_correction_service()
            async with async_perf_timer("stt.correction_llm", logging.INFO):
                correction_result = await stt_correction_service.correct_transcription(
                    stt_text=result.text,
                    conversation_history=conversation_history,
                    language=str(conversation.language),
                    difficulty_level=str(conversation.difficulty_level),
                )

            final_text = correction_result.corrected_text
            if correction_result.corrections:
                corrections = correction_result.corrections

                # Log corrections in dev mode
                if settings.babblr_dev_mode:
                    logger.info(
                        "STT correction applied:\n"
                        "  Original STT: %s\n"
                        "  Corrected: %s\n"
                        "  Corrections: %s",
                        result.text,
                        final_text,
                        corrections,
                    )

        return TranscriptionResponse(
            text=final_text,
            language=result.language,
            confidence=result.confidence,
            duration=result.duration,
            corrections=corrections,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like 404, 408, 500)
        raise
    except Exception as e:
        logger.error("Transcription failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

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
async def get_available_models(stt_service: STTService = Depends(get_stt_service)):
    """
    Get list of available Whisper models.

    Returns:
        JSON object with available models and current model
    """
    logger.debug("Getting available Whisper models")

    models = (
        stt_service.get_available_models() if hasattr(stt_service, "get_available_models") else []
    )
    # Use the actual loaded model, not just the settings value
    current_model = (
        stt_service.model_size if hasattr(stt_service, "model_size") else settings.whisper_model
    )

    # Model details with updated information
    model_details = {
        "tiny": {
            "name": "tiny",
            "parameters": "39M",
            "vram": "~1GB",
            "speed": "~10x faster",
            "description": "Fastest, least accurate",
            "recommended_for": "Quick testing, low-resource systems",
        },
        "base": {
            "name": "base",
            "parameters": "74M",
            "vram": "~1GB",
            "speed": "~7x faster",
            "description": "Good balance (default)",
            "recommended_for": "General use, balanced accuracy/speed",
        },
        "small": {
            "name": "small",
            "parameters": "244M",
            "vram": "~2GB",
            "speed": "~4x faster",
            "description": "Better accuracy",
            "recommended_for": "Better accuracy without heavy resources",
        },
        "medium": {
            "name": "medium",
            "parameters": "769M",
            "vram": "~5GB",
            "speed": "~2x faster",
            "description": "High accuracy",
            "recommended_for": "High accuracy, moderate GPU memory",
        },
        "large": {
            "name": "large",
            "parameters": "1550M",
            "vram": "~10GB",
            "speed": "1x (baseline)",
            "description": "Best accuracy, requires GPU",
            "recommended_for": "Maximum accuracy (legacy)",
        },
        "large-v2": {
            "name": "large-v2",
            "parameters": "1550M",
            "vram": "~10GB",
            "speed": "1x (baseline)",
            "description": "Improved large model",
            "recommended_for": "Better accuracy than large",
        },
        "large-v3": {
            "name": "large-v3",
            "parameters": "1550M",
            "vram": "~10GB",
            "speed": "1x (baseline)",
            "description": "Latest and most accurate (recommended)",
            "recommended_for": "Best accuracy, latest improvements",
        },
        "turbo": {
            "name": "turbo",
            "parameters": "~1500M",
            "vram": "~10GB",
            "speed": "~2x faster than large",
            "description": "Optimized for speed with good accuracy",
            "recommended_for": "Fast transcription with high accuracy",
        },
    }

    # Get CUDA information
    cuda_info = {"available": False, "device": "unknown"}
    if hasattr(stt_service, "get_cuda_info"):
        cuda_info = stt_service.get_cuda_info()
    elif hasattr(stt_service, "device"):
        cuda_info = {"available": stt_service.device != "cpu", "device": stt_service.device}

    return JSONResponse(
        content={
            "models": [model_details.get(model, {"name": model}) for model in models],
            "current_model": current_model,
            "device": stt_service.device if hasattr(stt_service, "device") else "unknown",
            "cuda": cuda_info,
            "multilingual": True,
            "notes": [
                "Whisper model selection is not language-specific (models are multilingual).",
                "You may pass a language hint as ISO-639-1 (e.g., 'en') or locale (e.g., 'en-GB'); locales map to ISO-639-1.",
                "Models are automatically downloaded on first use.",
                "Larger models (large-v3, turbo) require more GPU memory but offer better accuracy.",
            ],
            "count": len(models),
        }
    )


@router.get("/config")
async def get_stt_config(
    include_status: bool = False, stt_service: STTService = Depends(get_stt_service)
):
    """
    Get current STT configuration including CUDA status and available models.

    Returns:
        JSON object with STT configuration
    """
    try:
        logger.debug("Getting STT configuration")

        # Get CUDA information with error handling and timeout protection
        cuda_info = {"available": False, "device": "unknown"}
        try:
            if hasattr(stt_service, "get_cuda_info"):
                # Run CUDA check in executor to avoid blocking
                import asyncio

                loop = asyncio.get_event_loop()
                cuda_info = await asyncio.wait_for(
                    loop.run_in_executor(None, stt_service.get_cuda_info),
                    timeout=2.0,  # 2 second timeout for CUDA detection
                )
        except asyncio.TimeoutError:
            logger.warning("CUDA info check timed out, using defaults")
            cuda_info = {"available": False, "device": "unknown", "timeout": True}
        except Exception as e:
            logger.warning(f"Failed to get CUDA info: {e}")
            cuda_info = {"available": False, "device": "unknown", "error": str(e)}

        # Get available models with error handling
        try:
            models = (
                stt_service.get_available_models()
                if hasattr(stt_service, "get_available_models")
                else []
            )
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            models = ["base"]  # Fallback

        # Use the actual loaded model, not just the settings value
        try:
            current_model = (
                stt_service.model_size
                if hasattr(stt_service, "model_size")
                else settings.whisper_model
            )
        except Exception as e:
            logger.warning(f"Failed to get current model: {e}")
            current_model = settings.whisper_model

        # Get device with error handling
        try:
            device = stt_service.device if hasattr(stt_service, "device") else "unknown"
        except Exception as e:
            logger.warning(f"Failed to get device: {e}")
            device = "unknown"

        response_content = {
            "provider": settings.stt_provider,
            "current_model": current_model,
            "available_models": models,
            "cuda": cuda_info,
            "device": device,
        }

        # Include switch status if requested
        if include_status:
            response_content["switch_status"] = _model_switch_status

        return JSONResponse(content=response_content)
    except Exception as e:
        logger.error(f"Error in get_stt_config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get STT configuration: {str(e)}")


def _switch_model_background(new_model: str):
    """
    Background task to switch the Whisper model.

    Note: Model switching with ProcessPoolExecutor requires restarting workers
    or waiting for natural worker replacement. For now, this updates settings
    and logs a warning that a restart may be needed for full effect.

    Args:
        new_model: Model to switch to
    """
    global _model_switch_status
    try:
        _model_switch_status["status"] = "switching"
        _model_switch_status["target_model"] = new_model
        _model_switch_status["error"] = None

        # Note: With ProcessPoolExecutor, model switching is complex because
        # each worker process has its own cached model. For now, we update settings
        # and note that workers will use the new model on next process restart.
        # A full implementation would require ProcessPoolExecutor recreation.

        # Update settings
        settings.whisper_model = new_model
        _model_switch_status["status"] = "idle"
        _model_switch_status["target_model"] = None
        logger.info(
            f"STT model setting updated to {new_model}. "
            "Note: Existing worker processes will continue using the old model "
            "until they are replaced. Consider restarting the service for immediate effect."
        )
    except Exception as e:
        _model_switch_status["status"] = "idle"
        _model_switch_status["error"] = str(e)
        logger.error(f"Error in background model switch: {e}", exc_info=True)


@router.post("/config/model")
async def update_stt_model(request: dict, background_tasks: BackgroundTasks):
    """
    Update the STT model dynamically (no server restart required).

    This endpoint returns immediately and switches the model in the background.
    Use GET /stt/config/status to check the switch progress.

    Args:
        request: JSON body with "model" key (e.g., {"model": "large-v3"})
        background_tasks: FastAPI background tasks

    Returns:
        JSON object indicating the switch has been initiated
    """
    from pydantic import BaseModel

    class ModelUpdateRequest(BaseModel):
        model: str

    try:
        update_request = ModelUpdateRequest(**request)
        new_model = update_request.model

        # Note: Model validation is done against known models list
        # With ProcessPoolExecutor, full model switching requires worker restart

        # Validate model against known models
        available_models = [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
            "turbo",
        ]
        if new_model not in available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model '{new_model}'. Available models: {', '.join(available_models)}",
            )

        # Check if already switching
        if _model_switch_status["status"] != "idle":
            raise HTTPException(
                status_code=409,
                detail=f"Model switch already in progress. Current status: {_model_switch_status['status']}",
            )

        old_model = settings.whisper_model
        action = "switching"  # Note: With ProcessPoolExecutor, full switch requires worker restart

        # Start background task
        background_tasks.add_task(_switch_model_background, new_model)

        logger.info(
            f"Initiating STT model switch from {old_model} to {new_model} (action: {action})"
        )

        return JSONResponse(
            content={
                "message": f"Model switch initiated from {old_model} to {new_model}",
                "requested_model": new_model,
                "previous_model": old_model,
                "action": action,
                "note": "Model switch is in progress. Use GET /stt/config/status to check progress. The model will be automatically downloaded if not already cached. To persist across server restarts, update WHISPER_MODEL in .env file.",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating STT model switch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initiate model switch: {str(e)}")


@router.get("/config/status")
async def get_stt_switch_status():
    """
    Get the current status of a model switch operation.

    Returns:
        JSON object with switch status
    """
    return JSONResponse(content=_model_switch_status)


@router.get("/cuda")
async def get_cuda_info(stt_service: STTService = Depends(get_stt_service)):
    """
    Get CUDA/GPU availability information for Whisper.

    This endpoint provides detailed CUDA information including:
    - Whether CUDA is available
    - Current device being used
    - GPU device name (if available)
    - GPU memory information (if available)

    For external Whisper services, this queries the whisper container's API
    to get actual CUDA status from the container running Whisper.

    Returns:
        JSON object with CUDA status and device information
    """
    logger.debug("Getting CUDA information")

    try:
        # Get CUDA info with timeout protection
        import asyncio

        cuda_info = {"available": False, "device": "unknown"}

        if hasattr(stt_service, "get_cuda_info"):
            try:
                # For external service with async fetch method, use it directly
                if hasattr(stt_service, "_fetch_cuda_info"):
                    cuda_info = await asyncio.wait_for(stt_service._fetch_cuda_info(), timeout=5.0)
                else:
                    # For local service or external with sync method, run in executor
                    loop = asyncio.get_event_loop()
                    cuda_info = await asyncio.wait_for(
                        loop.run_in_executor(None, stt_service.get_cuda_info),
                        timeout=5.0,
                    )
            except asyncio.TimeoutError:
                logger.warning("CUDA info check timed out, using defaults")
                cuda_info = {"available": False, "device": "unknown", "timeout": True}
            except Exception as e:
                logger.warning(f"Failed to get CUDA info: {e}")
                cuda_info = {"available": False, "device": "unknown", "error": str(e)}
        elif hasattr(stt_service, "device"):
            # Fallback: use device attribute
            device = stt_service.device
            cuda_info = {
                "available": device != "cpu" and device != "unknown",
                "device": device,
                "device_name": None,
                "memory_total_gb": None,
                "memory_free_gb": None,
                "source": "device_attribute",
            }

        # Add provider info
        provider_info = {
            "provider": settings.stt_provider,
            "provider_name": stt_service.name if hasattr(stt_service, "name") else "unknown",
        }

        return JSONResponse(content={**cuda_info, **provider_info})

    except Exception as e:
        logger.error(f"Error getting CUDA info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get CUDA information: {str(e)}")


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
