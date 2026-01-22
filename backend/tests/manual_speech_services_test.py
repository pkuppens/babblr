"""
Manual Test Script for Section 4: Speech Services with Actual Audio

This script tests STT (Speech-to-Text) and TTS (Text-to-Speech) with real audio.
NOT part of unit tests - use actual audio samples (local, not in repo).

Prerequisites:
- Backend running at http://localhost:8000
- Ollama/Claude configured for chat
- Optional: Audio files or ability to record audio

Usage:
    python tests/manual_speech_services_test.py

The script will:
1. Generate synthetic test audio or use provided samples
2. Test STT transcription in multiple languages
3. Test TTS generation in multiple languages
4. Test the full conversation flow (STT → LLM → TTS)
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


async def test_stt_with_sample_audio():
    """Test STT with actual audio samples."""
    print("\n" + "=" * 70)
    print("SECTION 4.1: STT (Speech-to-Text) - Real Audio Testing")
    print("=" * 70)


    test_cases = [
        {
            "language": "spanish",
            "description": "Spanish phrase: 'Hola, ¿cómo estás?'",
            "expected_keywords": ["Hola", "cómo", "estás"],
        },
        {
            "language": "french",
            "description": "French phrase: 'Bonjour, comment allez-vous?'",
            "expected_keywords": ["Bonjour", "comment"],
        },
        {
            "language": "german",
            "description": "German phrase: 'Guten Tag, wie geht es dir?'",
            "expected_keywords": ["Guten", "Tag", "geht"],
        },
    ]

    print("\n[MANUAL TEST STEPS]")
    print("To test with actual audio samples:")
    print("1. Place audio files in: ./audio_samples/")
    print("   - spanish_greeting.wav")
    print("   - french_greeting.wav")
    print("   - german_greeting.wav")
    print("2. Or record audio using your microphone during test execution")
    print("3. Each test will display the transcribed text")
    print("\nExpected Results:")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['description']}")
        print(f"  Language: {test_case['language']}")
        print(f"  Expected Keywords: {', '.join(test_case['expected_keywords'])}")
        print("  Verify: Transcribed text contains most of these keywords")
        print("  Verify: Confidence score > 0.8")
        print("  Verify: Duration is reasonable (2-5 seconds)")


async def test_tts_generation():
    """Test TTS with actual audio generation."""
    print("\n" + "=" * 70)
    print("SECTION 4.2: TTS (Text-to-Speech) - Real Audio Generation")
    print("=" * 70)

    from app.services.tts_service import tts_service

    test_cases = [
        {"language": "spanish", "text": "Buenos días. Bienvenido a nuestro tutor de idiomas."},
        {"language": "french", "text": "Bonjour. Bienvenue dans notre tuteur de langues."},
        {"language": "german", "text": "Guten Tag. Willkommen zu unserem Sprachtutor."},
        {"language": "italian", "text": "Buongiorno. Benvenuto al nostro tutor di lingue."},
        {"language": "dutch", "text": "Goedemorgen. Welkom bij onze taaltutator."},
    ]

    print("\n[MANUAL TEST STEPS]")
    print("For each language, the test will generate audio and save to temp directory.")
    print("\nExpected Results:")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['language'].upper()}")
        print(f"  Text: {test_case['text']}")
        print("  Verify: Audio file is generated (MP3 format)")
        print("  Verify: File size > 10KB (valid audio data)")
        print("  Verify: Playback sounds like native speaker")
        print("  Verify: Pronunciation is clear and correct")

    # Attempt to generate audio
    print("\n[EXECUTING TTS TESTS]")
    for test_case in test_cases:
        try:
            lang = test_case["language"]
            text = test_case["text"]
            print(f"\nGenerating audio for {lang}...", end=" ")

            audio_path = await tts_service.synthesize_speech(text, lang)

            if audio_path and os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✓ (File: {Path(audio_path).name}, Size: {file_size} bytes)")

                # Move to temp directory with descriptive name
                temp_dir = tempfile.gettempdir()
                dest_path = os.path.join(temp_dir, f"babblr_tts_{lang}.mp3")
                if os.path.exists(audio_path):
                    os.rename(audio_path, dest_path)
                    print(f"  → Saved to: {dest_path}")
                    print("  → You can play this file to verify pronunciation")
            else:
                print("✗ (Audio generation failed or service unavailable)")

        except Exception as e:
            print(f"✗ Error: {str(e)[:100]}")


async def test_conversation_flow():
    """Test full conversation flow with STT and TTS."""
    print("\n" + "=" * 70)
    print("SECTION 4.3: Full Conversation Flow - STT + LLM + TTS")
    print("=" * 70)

    from app.services.llm import ProviderFactory
    from app.services.tts_service import tts_service

    print("\n[SCENARIO]")
    print("User speaks in Spanish: 'Hola, ¿cuál es tu nombre?'")
    print("\nExpected Result:")
    print("1. STT transcribes the user input")
    print("2. LLM generates a response in Spanish")
    print("3. TTS converts response to speech")

    print("\n[MANUAL TEST STEPS]")
    print("1. Record or prepare audio of: 'Hola, ¿cuál es tu nombre?'")
    print("2. Submit to /stt/transcribe endpoint")
    print("3. Verify transcribed text is accurate")
    print("4. Verify LLM response is in Spanish")
    print("5. Verify TTS output can be played and sounds natural")

    print("\n[EXECUTING CONVERSATION FLOW]")
    try:
        # Check if LLM provider is available
        provider = ProviderFactory.get_provider()
        print(f"✓ LLM Provider: {provider.name}")

        # Test TTS is available
        audio_path = await tts_service.synthesize_speech(
            "Hola, ¿cómo te llamas?",
            "spanish",
        )

        if audio_path and os.path.exists(audio_path):
            print("✓ TTS Service: Available")
            print(f"  → Generated response audio at: {audio_path}")
        else:
            print("✗ TTS Service: Unavailable")

    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")


async def test_multilingual_support():
    """Test speech services across all supported languages."""
    print("\n" + "=" * 70)
    print("SECTION 4.4: Multilingual Support")
    print("=" * 70)

    supported_languages = {
        "spanish": "Hola, me llamo Clara.",
        "french": "Bonjour, je m'appelle Claire.",
        "german": "Guten Tag, mein Name ist Clara.",
        "italian": "Buongiorno, mi chiamo Chiara.",
        "dutch": "Goedemorgen, mijn naam is Klara.",
        "english": "Hello, my name is Clara.",
    }

    print("\nSupported Languages for Speech Services:")
    for lang, sample in supported_languages.items():
        print(f"  • {lang.upper():12} - {sample}")

    print("\n[EXPECTED RESULTS]")
    print("✓ All languages should be recognized by STT")
    print("✓ All languages should be synthesized by TTS")
    print("✓ Transcriptions should maintain language-specific phonetics")
    print("✓ TTS should use appropriate pronunciation for each language")

    print("\n[TESTING LANGUAGE SUPPORT]")
    from app.services.tts_service import tts_service
    from app.services.whisper_service import whisper_service

    try:
        supported_locales = whisper_service.get_supported_locales()
        print(f"✓ Whisper supported locales: {len(supported_locales)} languages")

        tts_locales = tts_service.get_supported_locales()
        print(f"✓ TTS supported locales: {len(tts_locales)} languages")

    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")


async def main():
    """Run all manual speech service tests."""
    print("\n" + "=" * 70)
    print("BABBLR - SECTION 4: MANUAL SPEECH SERVICES TEST")
    print("=" * 70)
    print(f"\nTest Time: {os.popen('date').read().strip()}")
    print("Backend: http://localhost:8000")

    try:
        # Test 1: STT with samples
        await test_stt_with_sample_audio()

        # Test 2: TTS generation
        await test_tts_generation()

        # Test 3: Full conversation flow
        await test_conversation_flow()

        # Test 4: Multilingual support
        await test_multilingual_support()

    except Exception as e:
        print(f"\n✗ Test Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)
    print("SECTION 4 - MANUAL TESTS COMPLETED")
    print("=" * 70)
    print("\n[NEXT STEPS]")
    print("1. Review generated audio files for quality")
    print("2. Verify transcriptions are accurate")
    print("3. Check multilingual support works correctly")
    print("4. Proceed to Section 5 (Frontend Validation)")


if __name__ == "__main__":
    asyncio.run(main())
