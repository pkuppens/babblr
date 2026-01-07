"""
Service for building adaptive system prompts based on CEFR levels.

This module provides:
- Loading of CEFR-level prompt templates
- Variable substitution for personalized prompts
- Level+1 teaching approach
- Adaptive correction strategies per level
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Build customized system prompts for language tutoring based on CEFR levels."""

    # CEFR level hierarchy for validation and progression
    CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    # Mapping of old difficulty levels to CEFR for backwards compatibility
    DIFFICULTY_TO_CEFR = {
        "beginner": "A1",
        "intermediate": "B1",
        "advanced": "C1",
    }

    def __init__(self, templates_dir: str | Path | None = None):
        """
        Initialize the PromptBuilder with templates.

        Args:
            templates_dir: Directory containing prompt template JSON files.
                          Defaults to backend/templates/prompts/
        """
        if templates_dir is None:
            # Default to templates/prompts relative to this file
            backend_dir = Path(__file__).parent.parent.parent
            templates_dir = backend_dir / "templates" / "prompts"

        self.templates_dir = Path(templates_dir)
        self.templates: dict[str, dict[str, Any]] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all CEFR level templates from JSON files."""
        if not self.templates_dir.exists():
            logger.error(f"Templates directory not found: {self.templates_dir}")
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        for level in self.CEFR_LEVELS:
            template_file = self.templates_dir / f"{level.lower()}.json"
            if not template_file.exists():
                logger.warning(f"Template file not found: {template_file}")
                continue

            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    self.templates[level] = template_data
                    logger.info(f"Loaded template for level {level}")
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
                raise

        if not self.templates:
            raise ValueError("No templates loaded. Check templates directory and files.")

        logger.info(f"Successfully loaded {len(self.templates)} CEFR level templates")

    def normalize_level(self, level: str) -> str:
        """
        Normalize difficulty level to CEFR format.

        Converts old difficulty levels (beginner/intermediate/advanced) to CEFR.
        Also handles case-insensitive CEFR levels.

        Args:
            level: User's proficiency level (CEFR or old format)

        Returns:
            Normalized CEFR level (A1, A2, B1, B2, C1, C2)
        """
        level_upper = level.upper().strip()

        # Direct CEFR level
        if level_upper in self.CEFR_LEVELS:
            return level_upper

        # Legacy difficulty level
        level_lower = level.lower().strip()
        if level_lower in self.DIFFICULTY_TO_CEFR:
            cefr_level = self.DIFFICULTY_TO_CEFR[level_lower]
            logger.info(f"Converted legacy level '{level}' to CEFR '{cefr_level}'")
            return cefr_level

        # Default to A1 if unrecognized
        logger.warning(f"Unrecognized level '{level}', defaulting to A1")
        return "A1"

    def get_next_level(self, current_level: str) -> str | None:
        """
        Get the next CEFR level for progression suggestions.

        Args:
            current_level: Current CEFR level

        Returns:
            Next CEFR level, or None if already at C2
        """
        normalized = self.normalize_level(current_level)
        try:
            current_index = self.CEFR_LEVELS.index(normalized)
            if current_index < len(self.CEFR_LEVELS) - 1:
                return self.CEFR_LEVELS[current_index + 1]
        except ValueError:
            pass
        return None

    def build_prompt(
        self,
        language: str,
        level: str,
        topic: str = "general conversation",
        native_language: str | None = None,
        recent_vocab: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> str:
        """
        Build a complete system prompt for the language tutor.

        Args:
            language: Target language for learning (e.g., "Spanish", "French")
            level: User's CEFR proficiency level (A1-C2) or legacy (beginner/intermediate/advanced)
            topic: Current conversation topic
            native_language: User's native language for explanations (defaults to settings value)
            recent_vocab: List of recently learned vocabulary words
            common_mistakes: List of common mistakes to address

        Returns:
            Complete system prompt string with all variables substituted
        """
        # Normalize level to CEFR
        cefr_level = self.normalize_level(level)

        # Get template for this level
        if cefr_level not in self.templates:
            logger.error(f"No template found for level {cefr_level}")
            raise ValueError(f"No template found for level {cefr_level}")

        template_data = self.templates[cefr_level]
        template_str = template_data.get("template", "")

        if not template_str:
            logger.error(f"Template for level {cefr_level} has no 'template' field")
            raise ValueError(f"Invalid template for level {cefr_level}")

        # Use native language from settings if not provided
        if native_language is None:
            native_language = settings.user_native_language

        # Prepare vocabulary list string
        vocab_str = ""
        if recent_vocab and len(recent_vocab) > 0:
            vocab_str = ", ".join(recent_vocab[:10])  # Limit to 10 words
        else:
            vocab_str = "none yet"

        # Prepare common mistakes string
        mistakes_str = ""
        if common_mistakes and len(common_mistakes) > 0:
            mistakes_str = ", ".join(common_mistakes[:5])  # Limit to 5 patterns
        else:
            mistakes_str = "none identified yet"

        # Substitute variables in template
        prompt = template_str.format(
            language=language,
            level=cefr_level,
            topic=topic,
            native_language=native_language,
            recent_vocab=vocab_str,
            common_mistakes=mistakes_str,
        )

        logger.debug(f"Built prompt for {language} at {cefr_level} level")
        return prompt

    def get_template_metadata(self, level: str) -> dict[str, Any]:
        """
        Get metadata for a specific CEFR level template.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Dictionary with template metadata (description, correction_strategy, etc.)
        """
        cefr_level = self.normalize_level(level)

        if cefr_level not in self.templates:
            raise ValueError(f"No template found for level {cefr_level}")

        # Return all metadata except the template string itself
        metadata = {k: v for k, v in self.templates[cefr_level].items() if k != "template"}
        return metadata

    def get_correction_strategy(self, level: str) -> dict[str, Any]:
        """
        Get the correction strategy for a specific CEFR level.

        This helps determine what errors to ignore and what to focus on.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Dictionary with correction strategy details
        """
        metadata = self.get_template_metadata(level)
        return metadata.get("correction_strategy", {})

    def list_available_levels(self) -> list[dict[str, str]]:
        """
        List all available CEFR levels with descriptions.

        Returns:
            List of dictionaries with level info (level, level_name, description, playback_speed)
        """
        levels_info = []
        for level in self.CEFR_LEVELS:
            if level in self.templates:
                template = self.templates[level]
                levels_info.append(
                    {
                        "level": level,
                        "level_name": template.get("level_name", ""),
                        "description": template.get("description", ""),
                        "playback_speed": template.get("playback_speed", 1.0),
                    }
                )
        return levels_info

    def get_playback_speed(self, level: str) -> float:
        """
        Get the recommended playback speed for a specific CEFR level.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Playback speed as float (0.75 for A1, incrementing to 1.0 for C2)
        """
        cefr_level = self.normalize_level(level)
        if cefr_level in self.templates:
            return self.templates[cefr_level].get("playback_speed", 1.0)
        return 1.0


# Singleton instance for easy access
_prompt_builder_instance: PromptBuilder | None = None


def get_prompt_builder() -> PromptBuilder:
    """
    Get the singleton PromptBuilder instance.

    Returns:
        PromptBuilder instance
    """
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder()
    return _prompt_builder_instance
