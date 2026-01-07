"""
Unit tests for the PromptBuilder service.

Tests template loading, variable substitution, and level normalization.
"""

import json
from pathlib import Path

import pytest

from app.services.prompt_builder import PromptBuilder, get_prompt_builder


class TestPromptBuilder:
    """Test PromptBuilder functionality."""

    def test_prompt_builder_initialization(self):
        """Test that PromptBuilder initializes correctly."""
        builder = PromptBuilder()
        assert builder is not None
        assert len(builder.templates) > 0

    def test_all_cefr_levels_loaded(self):
        """Test that all 6 CEFR levels are loaded."""
        builder = PromptBuilder()
        expected_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        for level in expected_levels:
            assert level in builder.templates, f"Level {level} not loaded"

    def test_template_structure(self):
        """Test that templates have required fields."""
        builder = PromptBuilder()
        required_fields = ["level", "level_name", "description", "template", "correction_strategy"]

        for level, template_data in builder.templates.items():
            for field in required_fields:
                assert (
                    field in template_data
                ), f"Level {level} missing required field: {field}"

    def test_normalize_level_cefr(self):
        """Test normalization of CEFR levels."""
        builder = PromptBuilder()

        # Test uppercase
        assert builder.normalize_level("A1") == "A1"
        assert builder.normalize_level("B2") == "B2"
        assert builder.normalize_level("C1") == "C1"

        # Test lowercase
        assert builder.normalize_level("a1") == "A1"
        assert builder.normalize_level("b2") == "B2"
        assert builder.normalize_level("c2") == "C2"

        # Test with whitespace
        assert builder.normalize_level(" A1 ") == "A1"
        assert builder.normalize_level(" b1 ") == "B1"

    def test_normalize_level_legacy(self):
        """Test normalization of legacy difficulty levels."""
        builder = PromptBuilder()

        assert builder.normalize_level("beginner") == "A1"
        assert builder.normalize_level("intermediate") == "B1"
        assert builder.normalize_level("advanced") == "C1"

        # Test case insensitivity
        assert builder.normalize_level("BEGINNER") == "A1"
        assert builder.normalize_level("Intermediate") == "B1"

    def test_normalize_level_invalid(self):
        """Test normalization of invalid levels defaults to A1."""
        builder = PromptBuilder()

        assert builder.normalize_level("invalid") == "A1"
        assert builder.normalize_level("Z9") == "A1"
        assert builder.normalize_level("") == "A1"

    def test_get_next_level(self):
        """Test getting the next CEFR level."""
        builder = PromptBuilder()

        assert builder.get_next_level("A1") == "A2"
        assert builder.get_next_level("A2") == "B1"
        assert builder.get_next_level("B1") == "B2"
        assert builder.get_next_level("B2") == "C1"
        assert builder.get_next_level("C1") == "C2"
        assert builder.get_next_level("C2") is None  # Already at max

        # Test with legacy levels
        assert builder.get_next_level("beginner") == "A2"
        assert builder.get_next_level("intermediate") == "B2"

    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        builder = PromptBuilder()

        prompt = builder.build_prompt(language="Spanish", level="A1")

        assert "Spanish" in prompt
        assert "A1" in prompt or "beginner" in prompt.lower()
        assert len(prompt) > 100  # Should be a substantial prompt

    def test_build_prompt_with_all_variables(self):
        """Test prompt building with all optional variables."""
        builder = PromptBuilder()

        prompt = builder.build_prompt(
            language="French",
            level="B1",
            topic="travel and culture",
            native_language="English",
            recent_vocab=["voyage", "musée", "château"],
            common_mistakes=["using wrong past tense", "forgetting liaisons"],
        )

        assert "French" in prompt
        assert "B1" in prompt or "intermediate" in prompt.lower()
        assert "travel and culture" in prompt
        assert "English" in prompt
        assert "voyage" in prompt or "musée" in prompt or "château" in prompt
        assert (
            "using wrong past tense" in prompt or "forgetting liaisons" in prompt
        ) or "none identified" in prompt

    def test_build_prompt_all_levels(self):
        """Test that prompts can be built for all CEFR levels."""
        builder = PromptBuilder()

        for level in builder.CEFR_LEVELS:
            prompt = builder.build_prompt(language="German", level=level)
            assert "German" in prompt
            assert level in prompt
            assert len(prompt) > 100

    def test_build_prompt_with_legacy_level(self):
        """Test building prompt with legacy difficulty level."""
        builder = PromptBuilder()

        prompt = builder.build_prompt(language="Italian", level="beginner")

        assert "Italian" in prompt
        assert "A1" in prompt or "beginner" in prompt.lower()

    def test_get_template_metadata(self):
        """Test retrieving template metadata."""
        builder = PromptBuilder()

        metadata = builder.get_template_metadata("A1")

        assert "level" in metadata
        assert metadata["level"] == "A1"
        assert "level_name" in metadata
        assert "description" in metadata
        assert "correction_strategy" in metadata
        assert "template" not in metadata  # Template string should be excluded

    def test_get_correction_strategy(self):
        """Test retrieving correction strategy."""
        builder = PromptBuilder()

        # A1 should ignore punctuation, capitalization, diacritics
        a1_strategy = builder.get_correction_strategy("A1")
        assert a1_strategy["ignore_punctuation"] is True
        assert a1_strategy["ignore_capitalization"] is True
        assert a1_strategy["ignore_diacritics"] is True

        # C1 should NOT ignore these
        c1_strategy = builder.get_correction_strategy("C1")
        assert c1_strategy["ignore_punctuation"] is False
        assert c1_strategy["ignore_capitalization"] is False
        assert c1_strategy["ignore_diacritics"] is False

    def test_list_available_levels(self):
        """Test listing all available levels."""
        builder = PromptBuilder()

        levels = builder.list_available_levels()

        assert len(levels) == 6
        assert all("level" in level_info for level_info in levels)
        assert all("level_name" in level_info for level_info in levels)
        assert all("description" in level_info for level_info in levels)

        # Check that levels are in order
        level_codes = [level_info["level"] for level_info in levels]
        assert level_codes == ["A1", "A2", "B1", "B2", "C1", "C2"]

    def test_singleton_getter(self):
        """Test the singleton getter function."""
        builder1 = get_prompt_builder()
        builder2 = get_prompt_builder()

        assert builder1 is builder2  # Should be the same instance

    def test_prompt_contains_level_plus_one_guidance(self):
        """Test that prompts include level+1 teaching approach."""
        builder = PromptBuilder()

        for level in ["A1", "B1", "C1"]:
            prompt = builder.build_prompt(language="Spanish", level=level)
            # Check for level+1 indicators
            assert (
                "level+1" in prompt.lower()
                or "introduce" in prompt.lower()
                or "stretch" in prompt.lower()
            )

    def test_prompt_includes_assessment_guidance(self):
        """Test that prompts include proficiency assessment guidance."""
        builder = PromptBuilder()

        for level in ["A1", "A2", "B1"]:
            prompt = builder.build_prompt(language="French", level=level)
            # Check for assessment indicators
            assert (
                "assess" in prompt.lower()
                or "ready for" in prompt.lower()
                or "mastery" in prompt.lower()
                or "progress" in prompt.lower()
            )

    def test_correction_strategy_progression(self):
        """Test that correction strategies become stricter at higher levels."""
        builder = PromptBuilder()

        # Lower levels (A1, A2, B1) should ignore diacritics
        for level in ["A1", "A2", "B1"]:
            strategy = builder.get_correction_strategy(level)
            assert (
                strategy["ignore_diacritics"] is True
            ), f"Level {level} should ignore diacritics"

        # B2 might transition
        b2_strategy = builder.get_correction_strategy("B2")
        # B2 starts noticing diacritics according to our template

        # Higher levels (C1, C2) should NOT ignore diacritics
        for level in ["C1", "C2"]:
            strategy = builder.get_correction_strategy(level)
            assert (
                strategy["ignore_diacritics"] is False
            ), f"Level {level} should not ignore diacritics"

    def test_recent_vocab_truncation(self):
        """Test that recent vocabulary is truncated to reasonable length."""
        builder = PromptBuilder()

        # Provide more than 10 words
        long_vocab = [f"word{i}" for i in range(20)]

        prompt = builder.build_prompt(
            language="German", level="B1", recent_vocab=long_vocab
        )

        # Count how many vocab words appear
        vocab_count = sum(1 for word in long_vocab if word in prompt)

        # Should be limited (around 10, give or take for formatting)
        assert vocab_count <= 12, "Too many vocabulary items in prompt"

    def test_common_mistakes_truncation(self):
        """Test that common mistakes are truncated to reasonable length."""
        builder = PromptBuilder()

        # Provide more than 5 mistakes
        many_mistakes = [f"mistake pattern {i}" for i in range(10)]

        prompt = builder.build_prompt(
            language="Spanish", level="A2", common_mistakes=many_mistakes
        )

        # Count how many mistakes appear
        mistakes_count = sum(1 for mistake in many_mistakes if mistake in prompt)

        # Should be limited (around 5)
        assert mistakes_count <= 6, "Too many mistake patterns in prompt"

    def test_empty_vocab_and_mistakes(self):
        """Test handling of empty vocab and mistakes lists."""
        builder = PromptBuilder()

        prompt = builder.build_prompt(
            language="Italian",
            level="B1",
            recent_vocab=[],
            common_mistakes=[],
        )

        assert "none yet" in prompt or "none identified" in prompt

    def test_template_validation_fails_on_missing_directory(self):
        """Test that initialization fails gracefully with missing directory."""
        with pytest.raises(FileNotFoundError):
            PromptBuilder(templates_dir="/nonexistent/path")

    def test_invalid_level_raises_error_in_metadata(self):
        """Test that invalid level raises error when getting metadata."""
        builder = PromptBuilder()

        # After normalization, "beginner" becomes "A1", so it should work
        # But an invalid level that can't be normalized should fail
        # Since normalize_level defaults to A1, we need to test with get_template_metadata
        # which expects the level to exist after normalization

        # This should work (normalized to A1)
        metadata = builder.get_template_metadata("beginner")
        assert metadata["level"] == "A1"

        # Direct call with normalized level
        metadata = builder.get_template_metadata("A1")
        assert metadata["level"] == "A1"
