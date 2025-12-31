from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import TTSRequest
from app.services.tts_service import tts_service
import os


router = APIRouter(prefix="/tts", tags=["text-to-speech"])


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech and return audio file.
    """
    try:
        audio_path = await tts_service.synthesize_speech(
            request.text,
            request.language
        )
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(
                status_code=503, 
                detail="TTS service unavailable. Please install edge-tts or configure alternative TTS."
            )
        
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=os.path.basename(audio_path)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
