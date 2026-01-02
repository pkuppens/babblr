from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.models import Conversation, Message
from app.models.schemas import TranscriptionResponse
from app.services.whisper_service import whisper_service
import tempfile
import os
import json


router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    conversation_id: int,
    language: str,
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Transcribe audio to text using Whisper.
    """
    print(f"🎙️ Received audio transcription request:")
    print(f"  - Conversation ID: {conversation_id}")
    print(f"  - Language: {language}")
    print(f"  - Filename: {audio.filename}")
    print(f"  - Content Type: {audio.content_type}")
    
    # Verify conversation exists
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temp file
        suffix = os.path.splitext(audio.filename)[1] if audio.filename else '.wav'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # Write uploaded content
        content = await audio.read()
        print(f"  - Audio size: {len(content)} bytes")
        temp_file.write(content)
        temp_file.close()
        
        print(f"📝 Starting transcription...")
        # Transcribe
        transcribed_text, result = await whisper_service.transcribe_audio(
            temp_file.name,
            language
        )
        
        print(f"✅ Transcription complete: '{transcribed_text}'")
        
        return TranscriptionResponse(
            text=transcribed_text,
            corrections=None  # Corrections will be done in chat endpoint
        )
    
    except Exception as e:
        print(f"❌ Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
