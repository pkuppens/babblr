"""Demonstrate the adaptive CEFR prompt system in the terminal.

This module is meant for manual verification during development. It logs
sample prompts and correction strategies across CEFR levels.

Run it after installing the backend in editable mode:
- `uv pip install -e ".[dev]"`
- `uv run babblr-test-prompt-system`
"""

import logging
import sys

# Configure logging for standalone script output
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

from app.services.prompt_builder import get_prompt_builder


def test_prompt_generation() -> None:
    """Log a representative set of prompts and settings for all CEFR levels.

    The output includes:
    - Level normalization examples
    - Available CEFR levels and descriptions
    - Correction strategy differences across levels
    - Prompt previews for a few representative topics
    - A1 → C2 progression path
    """
    logger.info("=" * 80)
    logger.info("TESTING ADAPTIVE CEFR PROMPT SYSTEM")
    logger.info("=" * 80)
    logger.info("")

    builder = get_prompt_builder()

    # Test basic functionality
    logger.info("1. Testing level normalization:")
    logger.info(f"   'beginner' normalizes to: {builder.normalize_level('beginner')}")
    logger.info(f"   'intermediate' normalizes to: {builder.normalize_level('intermediate')}")
    logger.info(f"   'advanced' normalizes to: {builder.normalize_level('advanced')}")
    logger.info(f"   'a1' normalizes to: {builder.normalize_level('a1')}")
    logger.info(f"   'B2' normalizes to: {builder.normalize_level('B2')}")
    logger.info("")

    # Test available levels
    logger.info("2. Available CEFR levels:")
    levels = builder.list_available_levels()
    for level_info in levels:
        logger.info(
            f"   {level_info['level']}: {level_info['level_name']} - {level_info['description']}"
        )
    logger.info("")

    # Test correction strategies
    logger.info("3. Correction strategies by level:")
    for level in ["A1", "B1", "C1"]:
        strategy = builder.get_correction_strategy(level)
        logger.info(f"   {level}:")
        logger.info(f"      Ignore punctuation: {strategy['ignore_punctuation']}")
        logger.info(f"      Ignore capitalization: {strategy['ignore_capitalization']}")
        logger.info(f"      Ignore diacritics: {strategy['ignore_diacritics']}")
        logger.info(f"      Focus on: {', '.join(strategy['focus_on'])}")
        logger.info("")

    # Test prompt building for different levels
    logger.info("4. Sample prompts for Spanish at different levels:")
    logger.info("")

    test_cases: list[tuple[str, str, str, list[str]]] = [
        ("A1", "beginner", "food and drinks", ["hola", "gracias", "agua"]),
        ("B1", "intermediate", "travel plans", ["viajar", "reservar", "equipaje"]),
        ("C1", "advanced", "philosophy and ethics", ["existencialismo", "ética", "dilema"]),
    ]

    for level, level_name, topic, vocab in test_cases:
        logger.info(f"   Level {level} ({level_name}) - Topic: {topic}")
        logger.info("   " + "-" * 76)

        prompt = builder.build_prompt(
            language="Spanish",
            level=level,
            topic=topic,
            native_language="English",
            recent_vocab=vocab,
            common_mistakes=["verb conjugation in past tense"],
        )

        # Log first 500 characters of the prompt
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        logger.info(f"   {prompt_preview}")
        logger.info(f"   (Full prompt length: {len(prompt)} characters)")
        logger.info("")

    # Test level progression
    logger.info("5. Level progression:")
    current = "A1"
    progression = [current]
    while True:
        next_level = builder.get_next_level(current)
        if next_level is None:
            break
        progression.append(next_level)
        current = next_level
    logger.info(f"   Progression path: {' -> '.join(progression)}")
    logger.info("")

    logger.info("=" * 80)
    logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


def main() -> None:
    """Run the prompt system demo as a console script.

    Exits with code 1 if an unexpected exception occurs.
    """
    try:
        test_prompt_generation()
    except Exception as exc:
        logger.error(f"ERROR: {exc}")
        import traceback

        traceback.print_exc()
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
