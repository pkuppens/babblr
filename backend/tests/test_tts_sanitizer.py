"""
Unit tests for TTS text sanitization.

These tests ensure that Markdown formatting is removed before speech synthesis,
so TTS engines do not read formatting characters aloud (e.g., "asterisk").
"""

import pytest

from app.services.tts_service import sanitize_tts_text


class TestSanitizeTTSText:
    """Test sanitization of Markdown-like content for TTS."""

    def test_removes_bold_markers_and_bullets(self):
        """Bold markers and bullet prefixes should be removed."""
        raw = "**Estar es**: para describir estados.\n* Una cosa\n- Otra cosa"
        cleaned = sanitize_tts_text(raw)
        assert "*" not in cleaned
        assert "Estar es: para describir estados." in cleaned
        assert "Una cosa" in cleaned
        assert "Otra cosa" in cleaned

    def test_removes_code_fences_and_keeps_surrounding_text(self):
        """Fenced code blocks should be removed fully."""
        raw = "Intro\n```python\nprint('hola')\n```\nOutro"
        cleaned = sanitize_tts_text(raw)
        assert "print" not in cleaned
        assert "Intro" in cleaned
        assert "Outro" in cleaned

    def test_converts_links_and_inline_code(self):
        """Links should keep their label and inline code should keep content."""
        raw = "Read [`estar`](https://example.com) and `ser`."
        cleaned = sanitize_tts_text(raw)
        assert "https://example.com" not in cleaned
        assert "estar" in cleaned
        assert "ser" in cleaned

    def test_rejects_non_string_input(self):
        """Non-string input should raise a TypeError."""
        with pytest.raises(TypeError):
            sanitize_tts_text(None)  # type: ignore[arg-type]
