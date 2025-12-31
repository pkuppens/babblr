import whisper
import tempfile
import os
from typing import Tuple


class WhisperService:
    """Service for speech-to-text using OpenAI Whisper."""
    
    def __init__(self):
        # Load the base model (good balance between speed and accuracy)
        # For production, you might want to make this configurable
        self.model = whisper.load_model("base")
    
    async def transcribe_audio(self, audio_file_path: str, language: str = None) -> Tuple[str, dict]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code (e.g., 'es' for Spanish)
        
        Returns:
            Tuple of (transcribed_text, result_dict)
        """
        try:
            # Whisper transcribe is CPU-bound, but for simplicity we'll run it directly
            # In production, consider using a task queue
            options = {}
            if language:
                options['language'] = self._map_language_code(language)
            
            result = self.model.transcribe(audio_file_path, **options)
            return result['text'].strip(), result
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _map_language_code(self, language: str) -> str:
        """Map full language names to Whisper language codes."""
        language_map = {
            'spanish': 'es',
            'italian': 'it',
            'german': 'de',
            'french': 'fr',
            'dutch': 'nl',
            'english': 'en'
        }
        return language_map.get(language.lower(), language.lower())


# Create a singleton instance
whisper_service = WhisperService()
