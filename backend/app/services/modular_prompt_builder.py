"""
Modular Prompt Builder for language tutoring.

This module provides a modular approach to building system prompts by composing
separate components:
1. Base tutor identity (constant)
2. Language constraints (level-specific, topic-agnostic)
3. Roleplay context (topic-specific)
4. Tutor observer (level-specific correction strategy)
5. Personalization (user-specific context)

The 90% Coverage Principle: Students should recognize ~90% of vocabulary/grammar
from lessons at or below their CEFR level.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class ModularPromptBuilder:
    """
    Build system prompts from modular, reusable components.

    This enables:
    - Separation of level-specific vs topic-specific content
    - Reuse of language constraints across all topics
    - Reuse of tutor observer strategies across all topics
    - Clean composition of prompt parts
    """

    CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    DIFFICULTY_TO_CEFR = {
        "beginner": "A1",
        "intermediate": "B1",
        "advanced": "C1",
    }

    def __init__(self, components_dir: str | Path | None = None):
        """
        Initialize the ModularPromptBuilder.

        Args:
            components_dir: Directory containing prompt component JSON files.
                           Defaults to backend/templates/prompt_components/
        """
        if components_dir is None:
            backend_dir = Path(__file__).parent.parent.parent
            components_dir = backend_dir / "templates" / "prompt_components"

        self.components_dir = Path(components_dir)
        self.base_tutor: dict[str, Any] = {}
        self.level_components: dict[str, dict[str, Any]] = {}
        self._load_components()

    def _load_components(self) -> None:
        """Load all prompt components from JSON files."""
        if not self.components_dir.exists():
            logger.warning(f"Components directory not found: {self.components_dir}")
            return

        # Load base tutor identity
        base_tutor_file = self.components_dir / "base_tutor.json"
        if base_tutor_file.exists():
            try:
                with open(base_tutor_file, "r", encoding="utf-8") as f:
                    self.base_tutor = json.load(f)
                logger.info("Loaded base tutor component")
            except Exception as e:
                logger.error(f"Error loading base tutor: {e}")

        # Load level-specific components
        levels_dir = self.components_dir / "levels"
        if levels_dir.exists():
            for level in self.CEFR_LEVELS:
                level_file = levels_dir / f"{level.lower()}.json"
                if level_file.exists():
                    try:
                        with open(level_file, "r", encoding="utf-8") as f:
                            self.level_components[level] = json.load(f)
                        logger.info(f"Loaded components for level {level}")
                    except Exception as e:
                        logger.error(f"Error loading level {level}: {e}")

        logger.info(f"Loaded {len(self.level_components)} level component sets")

    def normalize_level(self, level: str) -> str:
        """
        Normalize difficulty level to CEFR format.

        Args:
            level: User's proficiency level (CEFR or legacy format)

        Returns:
            Normalized CEFR level (A1-C2)
        """
        level_upper = level.upper().strip()
        if level_upper in self.CEFR_LEVELS:
            return level_upper

        level_lower = level.lower().strip()
        if level_lower in self.DIFFICULTY_TO_CEFR:
            return self.DIFFICULTY_TO_CEFR[level_lower]

        logger.warning(f"Unrecognized level '{level}', defaulting to A1")
        return "A1"

    def build_prompt(
        self,
        language: str,
        level: str,
        topic: str = "general conversation",
        roleplay_context: str | None = None,
        native_language: str | None = None,
        recent_vocab: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> str:
        """
        Build a complete system prompt from modular components.

        Args:
            language: Target language for learning (e.g., "Spanish", "French")
            level: User's CEFR proficiency level (A1-C2)
            topic: Current conversation topic
            roleplay_context: Topic-specific roleplay persona/scenario
            native_language: User's native language for explanations
            recent_vocab: List of recently learned vocabulary words
            common_mistakes: List of common mistakes to address

        Returns:
            Complete composed system prompt
        """
        cefr_level = self.normalize_level(level)

        if native_language is None:
            native_language = settings.user_native_language

        # Build prompt from components
        prompt_parts: list[str] = []

        # 1. Base tutor identity
        base_prompt = self._build_base_tutor(language, cefr_level, native_language)
        if base_prompt:
            prompt_parts.append(base_prompt)

        # 2. Language constraints (level-specific)
        constraints = self._build_language_constraints(cefr_level, language)
        if constraints:
            prompt_parts.append(constraints)

        # 3. Roleplay context (topic-specific, optional)
        if roleplay_context:
            prompt_parts.append(f"**Roleplay Scenario:**\n{roleplay_context}")

        # 4. Topic context (simpler fallback if no roleplay)
        if not roleplay_context and topic != "general conversation":
            prompt_parts.append(f"**Conversation Topic:** {topic}")

        # 5. Tutor observer (level-specific correction strategy)
        observer = self._build_tutor_observer(cefr_level, language)
        if observer:
            prompt_parts.append(observer)

        # 6. Personalization (user-specific)
        personalization = self._build_personalization(recent_vocab, common_mistakes)
        if personalization:
            prompt_parts.append(personalization)

        return "\n\n".join(prompt_parts)

    def _build_base_tutor(self, language: str, level: str, native_language: str) -> str:
        """Build the base tutor identity section."""
        if not self.base_tutor:
            return self._fallback_base_tutor(language, level, native_language)

        template = self.base_tutor.get("template", "")
        if template:
            return template.format(
                language=language,
                level=level,
                native_language=native_language,
            )

        return self._fallback_base_tutor(language, level, native_language)

    def _fallback_base_tutor(self, language: str, level: str, native_language: str) -> str:
        """Fallback base tutor if components not loaded."""
        return f"""You are a friendly and encouraging {language} language tutor.

**Teaching Philosophy:**
- Create a safe space for mistakes - they are valuable learning opportunities
- Use the Level+1 approach: speak mostly at the student's level ({level}) with 5-15% stretch content
- Be conversational and natural, not robotic or overly formal
- Maintain immersion: respond primarily in {language}
- Use the student's native language ({native_language}) only for grammar explanations when essential"""

    def _build_language_constraints(self, level: str, language: str) -> str:
        """Build the language constraints section (level-specific)."""
        if level not in self.level_components:
            return self._fallback_language_constraints(level)

        component = self.level_components[level]
        constraints = component.get("language_constraints", {})
        template = constraints.get("template", "")

        if template:
            return template.format(level=level, language=language)

        return self._fallback_language_constraints(level)

    def _fallback_language_constraints(self, level: str) -> str:
        """Fallback language constraints."""
        constraints_map = {
            "A1": "Use only basic vocabulary (~500 words). Simple present tense. Short sentences (max 10 words).",
            "A2": "Use elementary vocabulary (~1000 words). Present and simple past. Sentences up to 15 words.",
            "B1": "Use intermediate vocabulary (~2500 words). Multiple tenses. Medium sentences (up to 20 words).",
            "B2": "Use upper-intermediate vocabulary (~5000 words). All common tenses. Complex sentences allowed.",
            "C1": "Use advanced vocabulary (~8000 words). Full grammar range. Sophisticated discourse.",
            "C2": "No restrictions. Native-like fluency. Full linguistic range.",
        }
        constraint = constraints_map.get(level, constraints_map["A1"])
        return f"**Language Boundaries for {level} Level:**\n{constraint}"

    def _build_tutor_observer(self, level: str, language: str) -> str:
        """Build the tutor observer section (level-specific correction strategy)."""
        if level not in self.level_components:
            return self._fallback_tutor_observer(level)

        component = self.level_components[level]
        observer = component.get("tutor_observer", {})
        template = observer.get("template", "")

        if template:
            return template.format(level=level, language=language)

        return self._fallback_tutor_observer(level)

    def _fallback_tutor_observer(self, level: str) -> str:
        """Fallback tutor observer strategy."""
        if level in ["A1", "A2"]:
            return """**Error Correction Strategy:**
- IGNORE: punctuation, capitalization, diacritics
- FOCUS: basic grammar, core vocabulary
- Maximum 1 correction per response
- Always encourage and acknowledge effort first"""
        elif level in ["B1", "B2"]:
            return """**Error Correction Strategy:**
- IGNORE: punctuation, capitalization
- FOCUS: tense usage, idiomatic expressions, register
- Maximum 2 corrections per response
- Use natural recasting technique"""
        else:  # C1, C2
            return """**Error Correction Strategy:**
- Minimal corrections - focus on refinement
- FOCUS: precision, style, cultural appropriateness
- Treat as peer-to-peer exchange
- Offer suggestions, not corrections"""

    def _build_personalization(
        self,
        recent_vocab: list[str] | None,
        common_mistakes: list[str] | None,
    ) -> str:
        """Build the personalization section (user-specific)."""
        parts: list[str] = []

        if recent_vocab and len(recent_vocab) > 0:
            vocab_str = ", ".join(recent_vocab[:10])
            parts.append(f"- Recently learned vocabulary to reinforce: {vocab_str}")

        if common_mistakes and len(common_mistakes) > 0:
            mistakes_str = ", ".join(common_mistakes[:5])
            parts.append(f"- Common mistakes to gently address: {mistakes_str}")

        if parts:
            return "**Your Student's Learning Context:**\n" + "\n".join(parts)

        return ""

    def get_level_metadata(self, level: str) -> dict[str, Any]:
        """
        Get metadata for a specific CEFR level.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Dictionary with level metadata
        """
        cefr_level = self.normalize_level(level)
        if cefr_level in self.level_components:
            component = self.level_components[cefr_level]
            return {
                "level": component.get("level"),
                "level_name": component.get("level_name"),
                "description": component.get("description"),
                "playback_speed": component.get("playback_speed", 1.0),
            }
        return {
            "level": cefr_level,
            "level_name": "Unknown",
            "description": "",
            "playback_speed": 1.0,
        }

    def get_correction_strategy(self, level: str) -> dict[str, Any]:
        """
        Get the correction strategy for a specific CEFR level.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Dictionary with correction strategy details
        """
        cefr_level = self.normalize_level(level)
        if cefr_level in self.level_components:
            component = self.level_components[cefr_level]
            return component.get("tutor_observer", {})
        return {}

    def get_vocabulary_constraints(self, level: str) -> dict[str, Any]:
        """
        Get vocabulary constraints for a specific CEFR level.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Dictionary with vocabulary constraints
        """
        cefr_level = self.normalize_level(level)
        if cefr_level in self.level_components:
            component = self.level_components[cefr_level]
            constraints = component.get("language_constraints", {})
            return constraints.get("vocabulary", {})
        return {}

    def get_playback_speed(self, level: str) -> float:
        """
        Get the recommended playback speed for a specific CEFR level.

        Args:
            level: CEFR level (A1-C2)

        Returns:
            Playback speed as float
        """
        cefr_level = self.normalize_level(level)
        if cefr_level in self.level_components:
            return self.level_components[cefr_level].get("playback_speed", 1.0)
        return 1.0

    def list_available_levels(self) -> list[dict[str, Any]]:
        """
        List all available CEFR levels with metadata.

        Returns:
            List of dictionaries with level info
        """
        levels_info = []
        for level in self.CEFR_LEVELS:
            if level in self.level_components:
                component = self.level_components[level]
                levels_info.append(
                    {
                        "level": level,
                        "level_name": component.get("level_name", ""),
                        "description": component.get("description", ""),
                        "playback_speed": component.get("playback_speed", 1.0),
                    }
                )
        return levels_info


# Singleton instance
_modular_builder_instance: ModularPromptBuilder | None = None


def get_modular_prompt_builder() -> ModularPromptBuilder:
    """
    Get the singleton ModularPromptBuilder instance.

    Returns:
        ModularPromptBuilder instance
    """
    global _modular_builder_instance
    if _modular_builder_instance is None:
        _modular_builder_instance = ModularPromptBuilder()
    return _modular_builder_instance
