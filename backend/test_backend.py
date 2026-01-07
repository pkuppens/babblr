"""
Quick validation test for the backend API.
Run with: pytest test_backend.py
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.models.schemas import ChatRequest, ConversationCreate


def test_config_loads():
    """Test that configuration loads."""
    assert settings is not None
    assert settings.babblr_api_host == "127.0.0.1"
    assert settings.babblr_api_port == 8000


def test_schemas_validate():
    """Test that Pydantic schemas work."""
    # Test conversation creation
    conv = ConversationCreate(language="spanish", difficulty_level="beginner")
    assert conv.language == "spanish"
    assert conv.difficulty_level == "beginner"

    # Test chat request
    chat = ChatRequest(
        conversation_id=1, user_message="Hola", language="spanish", difficulty_level="beginner"
    )
    assert chat.conversation_id == 1
    assert chat.user_message == "Hola"


def test_imports():
    """Test that all main modules can be imported."""
    from app.database.db import get_db
    from app.main import app
    from app.models.models import Conversation
    from app.services.claude_service import claude_service

    assert app is not None
    assert get_db is not None
    assert Conversation is not None
    assert claude_service is not None


if __name__ == "__main__":
    print("Running basic validation tests...")
    test_config_loads()
    print("✅ Config loads")
    test_schemas_validate()
    print("✅ Schemas validate")
    test_imports()
    print("✅ All imports work")
    print("\n✨ All validation tests passed!")
