"""CEFR (Common European Framework of Reference) level definitions.

This module provides shared CEFR level definitions used across
vocabulary, grammar, and other language learning features.
"""

from enum import Enum


class CEFRLevel(str, Enum):
    """CEFR proficiency levels.

    Common European Framework of Reference for Languages levels:
    - A1: Beginner
    - A2: Elementary
    - B1: Intermediate
    - B2: Upper Intermediate
    - C1: Advanced
    - C2: Proficient
    """

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
