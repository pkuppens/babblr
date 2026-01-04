"""
Quick test script to verify the backend API is working.

This script tests the main functionality without needing the frontend.
Run after starting the backend with: ./run-backend.sh

Usage: python examples/test_api.py
"""

import json
import sys
import time

import requests

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test that the API is responding."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Backend is healthy: {data['status']}")
        print(f"   Services: {json.dumps(data['services'], indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_create_conversation():
    """Test creating a new conversation."""
    print("\nTesting conversation creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/conversations",
            json={"language": "spanish", "difficulty_level": "beginner"},
        )
        response.raise_for_status()
        conversation = response.json()
        print(f"✅ Created conversation ID: {conversation['id']}")
        print(f"   Language: {conversation['language']}")
        print(f"   Difficulty: {conversation['difficulty_level']}")
        return conversation
    except Exception as e:
        print(f"❌ Conversation creation failed: {e}")
        return None


def test_chat(conversation_id):
    """Test sending a chat message."""
    print("\nTesting chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "conversation_id": conversation_id,
                "user_message": "Hola, ¿cómo estás?",
                "language": "spanish",
                "difficulty_level": "beginner",
            },
        )
        response.raise_for_status()
        chat_response = response.json()
        print("✅ Chat response received")
        print(f"   Assistant: {chat_response['assistant_message'][:100]}...")
        if chat_response.get("corrections"):
            print(f"   Corrections: {len(chat_response['corrections'])} found")
        return True
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"   Error details: {e.response.text}")
        return False


def test_get_messages(conversation_id):
    """Test getting conversation messages."""
    print("\nTesting message retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages")
        response.raise_for_status()
        messages = response.json()
        print(f"✅ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"   {msg['role']}: {msg['content'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ Message retrieval failed: {e}")
        return False


def test_list_conversations():
    """Test listing all conversations."""
    print("\nTesting conversation list...")
    try:
        response = requests.get(f"{BASE_URL}/conversations")
        response.raise_for_status()
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversation(s)")
        return True
    except Exception as e:
        print(f"❌ Conversation list failed: {e}")
        return False


def test_tts():
    """Test text-to-speech (if available)."""
    print("\nTesting text-to-speech...")
    try:
        response = requests.post(
            f"{BASE_URL}/tts/synthesize", json={"text": "Hola", "language": "spanish"}
        )
        if response.status_code == 503:
            print("⚠️  TTS not available (edge-tts not installed)")
            return True
        response.raise_for_status()
        print(f"✅ TTS generated audio ({len(response.content)} bytes)")
        return True
    except Exception as e:
        print(f"⚠️  TTS test skipped or failed: {e}")
        return True  # Non-critical


def main():
    """Run all tests."""
    print("=" * 60)
    print("Babblr Backend API Test")
    print("=" * 60)
    print("\nMake sure the backend is running: ./run-backend.sh\n")

    time.sleep(1)

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend is not responding. Make sure it's running!")
        print("   Start with: ./run-backend.sh")
        sys.exit(1)

    # Test 2: Create conversation
    conversation = test_create_conversation()
    if not conversation:
        print("\n❌ Could not create conversation")
        sys.exit(1)

    conversation_id = conversation["id"]

    # Test 3: Chat
    if not test_chat(conversation_id):
        print("\n⚠️  Chat test failed. Check if ANTHROPIC_API_KEY is set in backend/.env")

    # Test 4: Get messages
    test_get_messages(conversation_id)

    # Test 5: List conversations
    test_list_conversations()

    # Test 6: TTS (optional)
    test_tts()

    print("\n" + "=" * 60)
    print("✨ API tests completed!")
    print("=" * 60)
    print("\nNotes:")
    print("- Voice recording (Whisper) requires: pip install openai-whisper")
    print("- TTS requires: pip install edge-tts")
    print("- Chat requires: ANTHROPIC_API_KEY in backend/.env")
    print("\nTo test the full app, start the frontend:")
    print("  ./run-frontend.sh")


if __name__ == "__main__":
    main()
