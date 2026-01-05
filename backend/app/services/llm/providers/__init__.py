"""
LLM Provider implementations.

Each provider implements the LLMProvider protocol from base.py.
"""

from app.services.llm.providers.mock import MockProvider

# Lazy imports to avoid loading heavy dependencies
__all__ = ["MockProvider"]


def get_ollama_provider():
    """Lazy import for OllamaProvider."""
    from app.services.llm.providers.ollama import OllamaProvider

    return OllamaProvider


def get_claude_provider():
    """Lazy import for ClaudeProvider."""
    from app.services.llm.providers.claude import ClaudeProvider

    return ClaudeProvider
