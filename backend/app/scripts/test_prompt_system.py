"""Demonstrate the adaptive CEFR prompt system in the terminal.

This module is meant for manual verification during development. It prints
sample prompts and correction strategies across CEFR levels.

Run it after installing the backend in editable mode:
- `uv pip install -e ".[dev]"`
- `uv run babblr-test-prompt-system`
"""

from app.services.prompt_builder import get_prompt_builder


def test_prompt_generation() -> None:
    """Print a representative set of prompts and settings for all CEFR levels.

    The output includes:
    - Level normalization examples
    - Available CEFR levels and descriptions
    - Correction strategy differences across levels
    - Prompt previews for a few representative topics
    - A1 → C2 progression path
    """
    print("=" * 80)
    print("TESTING ADAPTIVE CEFR PROMPT SYSTEM")
    print("=" * 80)
    print()

    builder = get_prompt_builder()

    # Test basic functionality
    print("1. Testing level normalization:")
    print(f"   'beginner' normalizes to: {builder.normalize_level('beginner')}")
    print(f"   'intermediate' normalizes to: {builder.normalize_level('intermediate')}")
    print(f"   'advanced' normalizes to: {builder.normalize_level('advanced')}")
    print(f"   'a1' normalizes to: {builder.normalize_level('a1')}")
    print(f"   'B2' normalizes to: {builder.normalize_level('B2')}")
    print()

    # Test available levels
    print("2. Available CEFR levels:")
    levels = builder.list_available_levels()
    for level_info in levels:
        print(f"   {level_info['level']}: {level_info['level_name']} - {level_info['description']}")
    print()

    # Test correction strategies
    print("3. Correction strategies by level:")
    for level in ["A1", "B1", "C1"]:
        strategy = builder.get_correction_strategy(level)
        print(f"   {level}:")
        print(f"      Ignore punctuation: {strategy['ignore_punctuation']}")
        print(f"      Ignore capitalization: {strategy['ignore_capitalization']}")
        print(f"      Ignore diacritics: {strategy['ignore_diacritics']}")
        print(f"      Focus on: {', '.join(strategy['focus_on'])}")
        print()

    # Test prompt building for different levels
    print("4. Sample prompts for Spanish at different levels:")
    print()

    test_cases: list[tuple[str, str, str, list[str]]] = [
        ("A1", "beginner", "food and drinks", ["hola", "gracias", "agua"]),
        ("B1", "intermediate", "travel plans", ["viajar", "reservar", "equipaje"]),
        ("C1", "advanced", "philosophy and ethics", ["existencialismo", "ética", "dilema"]),
    ]

    for level, level_name, topic, vocab in test_cases:
        print(f"   Level {level} ({level_name}) - Topic: {topic}")
        print("   " + "-" * 76)

        prompt = builder.build_prompt(
            language="Spanish",
            level=level,
            topic=topic,
            native_language="English",
            recent_vocab=vocab,
            common_mistakes=["verb conjugation in past tense"],
        )

        # Print first 500 characters of the prompt
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        print(f"   {prompt_preview}")
        print(f"   (Full prompt length: {len(prompt)} characters)")
        print()

    # Test level progression
    print("5. Level progression:")
    current = "A1"
    progression = [current]
    while True:
        next_level = builder.get_next_level(current)
        if next_level is None:
            break
        progression.append(next_level)
        current = next_level
    print(f"   Progression path: {' -> '.join(progression)}")
    print()

    print("=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)


def main() -> None:
    """Run the prompt system demo as a console script.

    Exits with code 1 if an unexpected exception occurs.
    """
    try:
        test_prompt_generation()
    except Exception as exc:
        print(f"ERROR: {exc}")
        import traceback

        traceback.print_exc()
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
