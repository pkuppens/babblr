"""
Manual live API check for the Babblr backend.

This script performs a small set of real HTTP requests against a running Babblr backend.
It is intentionally **not** a pytest test module, so it does not run during unit tests.

Usage:
    - Start the backend in one terminal (see `backend/tests/README.md`)
    - Run this script in another terminal:
        python backend/tests/manual_api_check.py

Notes:
    - Set `BABBLR_BASE_URL` to override the target server (default: http://localhost:8000).
    - The chat endpoint may require `ANTHROPIC_API_KEY` configured in `backend/.env`.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any

import httpx

# Configure logging for standalone script output
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:8000"


def _truncate(text: str, max_len: int = 250) -> str:
    """Return a shortened version of a string for safe console output.

    This helper prevents accidental dumping of large response bodies to the terminal.

    Args:
        text (str): The input text to truncate.
        max_len (int, optional): Maximum length to keep. Must be positive.

    Returns:
        str: The original string if it is short enough, otherwise a truncated version.

    Raises:
        ValueError: If `max_len` is not a positive integer.
    """
    if max_len <= 0:
        raise ValueError("max_len must be a positive integer")
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}..."


def _print_fail(title: str, message: str) -> None:
    """Log a failure message in a consistent, readable format.

    Args:
        title (str): Short label of the step that failed.
        message (str): Human-readable explanation of the failure.
    """
    logger.info(f"[FAIL] {title}: {_truncate(message)}")


def _print_ok(title: str, message: str) -> None:
    """Log a success message in a consistent, readable format.

    Args:
        title (str): Short label of the step that succeeded.
        message (str): Human-readable success message.
    """
    logger.info(f"[ OK ] {title}: {_truncate(message)}")


def test_health_check(client: httpx.Client) -> bool:
    """Check if the backend health endpoint responds.

    This call verifies the backend is reachable and returns a JSON payload.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.

    Returns:
        bool: True if the endpoint responds with HTTP 200 and expected JSON, else False.
    """
    logger.info("Testing health check...")
    try:
        response = client.get("/health")
    except Exception as exc:
        _print_fail("Health", f"Request failed: {exc}")
        return False

    if response.status_code != 200:
        _print_fail("Health", f"Unexpected status code: {response.status_code}")
        return False

    try:
        data = response.json()
    except Exception as exc:
        _print_fail("Health", f"Could not parse JSON response: {exc}")
        return False

    status = data.get("status", "<missing>")
    services = data.get("services", {})
    _print_ok("Health", f"Backend is healthy (status={status})")
    logger.info(f"   Services: {services}")
    return True


def test_create_conversation(client: httpx.Client) -> dict[str, Any] | None:
    """Create a new conversation via the API.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.

    Returns:
        dict[str, Any] | None: The created conversation object on success, otherwise None.
    """
    logger.info("\nTesting conversation creation...")
    try:
        response = client.post(
            "/conversations",
            json={"language": "spanish", "difficulty_level": "beginner"},
        )
    except Exception as exc:
        _print_fail("Create conversation", f"Request failed: {exc}")
        return None

    if response.status_code != 200:
        _print_fail("Create conversation", f"Unexpected status code: {response.status_code}")
        return None

    try:
        conversation = response.json()
    except Exception as exc:
        _print_fail("Create conversation", f"Could not parse JSON response: {exc}")
        return None

    conversation_id = conversation.get("id")
    _print_ok("Create conversation", f"Created conversation id={conversation_id}")
    logger.info(f"   Language: {conversation.get('language')}")
    logger.info(f"   Difficulty: {conversation.get('difficulty_level')}")
    return conversation


def test_chat(client: httpx.Client, conversation_id: int) -> bool:
    """Send a chat message and validate basic response structure.

    This endpoint may require an API key to be configured on the backend.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.
        conversation_id (int): The conversation ID to send the message to.

    Returns:
        bool: True if a plausible response is received, else False.
    """
    logger.info("\nTesting chat endpoint...")
    try:
        response = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "user_message": "Hola, ¿cómo estás?",
                "language": "spanish",
                "difficulty_level": "beginner",
            },
        )
    except Exception as exc:
        _print_fail("Chat", f"Request failed: {exc}")
        return False

    if response.status_code != 200:
        # Do not print response bodies to avoid leaking unexpected content to logs.
        _print_fail("Chat", f"Unexpected status code: {response.status_code}")
        return False

    try:
        chat_response = response.json()
    except Exception as exc:
        _print_fail("Chat", f"Could not parse JSON response: {exc}")
        return False

    assistant_msg = str(chat_response.get("assistant_message", ""))
    _print_ok("Chat", "Response received")
    logger.info(f"   Assistant (preview): {_truncate(assistant_msg, max_len=100)}")
    corrections = chat_response.get("corrections")
    if corrections:
        logger.info(f"   Corrections: {len(corrections)}")
    return True


def test_get_messages(client: httpx.Client, conversation_id: int) -> bool:
    """Fetch the messages for a conversation.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.
        conversation_id (int): The conversation ID to fetch messages for.

    Returns:
        bool: True if messages are returned as a list, else False.
    """
    logger.info("\nTesting message retrieval...")
    try:
        response = client.get(f"/conversations/{conversation_id}/messages")
    except Exception as exc:
        _print_fail("Get messages", f"Request failed: {exc}")
        return False

    if response.status_code != 200:
        _print_fail("Get messages", f"Unexpected status code: {response.status_code}")
        return False

    try:
        messages = response.json()
    except Exception as exc:
        _print_fail("Get messages", f"Could not parse JSON response: {exc}")
        return False

    if not isinstance(messages, list):
        _print_fail("Get messages", "Expected a list of messages")
        return False

    _print_ok("Get messages", f"Retrieved {len(messages)} message(s)")
    for msg in messages[:5]:
        role = msg.get("role", "<missing>")
        content = str(msg.get("content", ""))
        logger.info(f"   {role}: {_truncate(content, max_len=50)}")
    if len(messages) > 5:
        logger.info("   ... (more messages omitted)")
    return True


def test_list_conversations(client: httpx.Client) -> bool:
    """List all conversations from the API.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.

    Returns:
        bool: True if the endpoint returns a JSON list, else False.
    """
    logger.info("\nTesting conversation list...")
    try:
        response = client.get("/conversations")
    except Exception as exc:
        _print_fail("List conversations", f"Request failed: {exc}")
        return False

    if response.status_code != 200:
        _print_fail("List conversations", f"Unexpected status code: {response.status_code}")
        return False

    try:
        conversations = response.json()
    except Exception as exc:
        _print_fail("List conversations", f"Could not parse JSON response: {exc}")
        return False

    if not isinstance(conversations, list):
        _print_fail("List conversations", "Expected a list")
        return False

    _print_ok("List conversations", f"Found {len(conversations)} conversation(s)")
    return True


def test_tts(client: httpx.Client) -> bool:
    """Try to generate TTS audio (optional feature).

    The backend may return HTTP 503 when TTS is not available.

    Args:
        client (httpx.Client): An HTTP client configured with the backend base URL.

    Returns:
        bool: True if the check is non-fatal (success or expected not-available), else False.
    """
    logger.info("\nTesting text-to-speech...")
    try:
        response = client.post("/tts/synthesize", json={"text": "Hola", "language": "spanish"})
    except Exception as exc:
        _print_fail("TTS", f"Request failed: {exc}")
        return True  # Non-critical

    if response.status_code == 503:
        _print_ok("TTS", "Not available (backend returned 503)")
        return True

    if response.status_code != 200:
        _print_fail("TTS", f"Unexpected status code: {response.status_code}")
        return True  # Non-critical

    _print_ok("TTS", f"Generated audio ({len(response.content)} bytes)")
    return True


def main() -> None:
    """Run a manual end-to-end check against a running backend.

    This script is meant for quick local validation. It exits with a non-zero status code
    when the backend is not reachable or core endpoints fail.
    """
    base_url = os.getenv("BABBLR_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL

    logger.info("=" * 60)
    logger.info("Babblr Backend Live API Check")
    logger.info("=" * 60)
    logger.info(f"\nTarget: {base_url}")
    logger.info("Make sure the backend is running first.\n")

    time.sleep(0.5)

    timeout = httpx.Timeout(5.0)
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        if not test_health_check(client):
            logger.info("\nBackend is not responding. Make sure it is running.")
            sys.exit(1)

        conversation = test_create_conversation(client)
        if not conversation or "id" not in conversation:
            logger.info("\nCould not create a conversation.")
            sys.exit(1)

        conversation_id = int(conversation["id"])

        if not test_chat(client, conversation_id):
            logger.info("\nChat test failed. Check if ANTHROPIC_API_KEY is set in backend/.env.")

        test_get_messages(client, conversation_id)
        test_list_conversations(client)
        test_tts(client)

    logger.info("\n" + "=" * 60)
    logger.info("Live API check completed.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
