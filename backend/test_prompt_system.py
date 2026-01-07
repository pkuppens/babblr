#!/usr/bin/env python
"""
Manual test script to demonstrate the adaptive CEFR prompt system.

This script shows how the PromptBuilder generates different prompts
for different CEFR levels and how correction strategies adapt.
"""

import sys
from pathlib import Path

# Add the app directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.prompt_builder import get_prompt_builder


def test_prompt_generation():
    """Test prompt generation for all CEFR levels."""
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
    
    test_cases = [
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


if __name__ == "__main__":
    try:
        test_prompt_generation()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
