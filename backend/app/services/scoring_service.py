"""
Assessment scoring service.

Calculates scores, determines CEFR levels, and generates recommendations.
"""

from typing import Any

# CEFR level thresholds (percentage)
# Scores are mapped to CEFR levels based on these thresholds
CEFR_THRESHOLDS = [
    (91, "C2"),  # >= 91%: Proficient
    (81, "C1"),  # >= 81%: Advanced
    (61, "B2"),  # >= 61%: Upper Intermediate
    (41, "B1"),  # >= 41%: Intermediate
    (21, "A2"),  # >= 21%: Elementary
    (0, "A1"),  # >= 0%: Beginner
]

# Threshold below which a skill needs practice
PRACTICE_THRESHOLD = 70.0


def calculate_scores(
    questions: list[dict[str, Any]],
    answers: dict[int, str],
) -> dict[str, dict[str, Any]]:
    """
    Calculate overall and per-skill scores.

    Args:
        questions: List of question dicts with id, skill_category, correct_answer, points
        answers: Dict mapping question_id to user's answer

    Returns:
        Dict with 'overall' and per-skill scores, each containing:
        - score: percentage (0-100)
        - correct: number of correct answers
        - total: total questions/points
    """
    skill_results: dict[str, dict[str, int]] = {}
    overall_correct = 0
    overall_total = 0

    for q in questions:
        skill = q["skill_category"]
        if skill not in skill_results:
            skill_results[skill] = {"correct": 0, "total": 0}

        skill_results[skill]["total"] += q["points"]
        overall_total += q["points"]

        user_answer = answers.get(q["id"])
        if user_answer == q["correct_answer"]:
            skill_results[skill]["correct"] += q["points"]
            overall_correct += q["points"]

    # Calculate percentages
    results: dict[str, dict[str, Any]] = {}
    for skill, data in skill_results.items():
        score = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
        results[skill] = {
            "score": round(score, 1),
            "correct": data["correct"],
            "total": data["total"],
        }

    overall_score = (overall_correct / overall_total * 100) if overall_total > 0 else 0
    results["overall"] = {
        "score": round(overall_score, 1),
        "correct": overall_correct,
        "total": overall_total,
    }

    return results


def determine_cefr_level(score: float) -> str:
    """
    Determine CEFR level from percentage score.

    Args:
        score: Percentage score (0-100)

    Returns:
        CEFR level string (A1-C2)
    """
    for threshold, level in CEFR_THRESHOLDS:
        if score >= threshold:
            return level
    return "A1"  # Fallback


def generate_practice_recommendations(
    skill_scores: dict[str, dict[str, Any]],
) -> list[str]:
    """
    Generate practice recommendations based on skill scores.

    Args:
        skill_scores: Dict of skill -> {score, total, correct}

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Find skills below threshold
    weak_skills = [
        (skill, data["score"])
        for skill, data in skill_scores.items()
        if skill != "overall" and data["score"] < PRACTICE_THRESHOLD
    ]

    # Sort by score (weakest first)
    weak_skills.sort(key=lambda x: x[1])

    for skill, score in weak_skills:
        if skill == "grammar":
            recommendations.append(f"Focus on grammar practice - your score was {score:.0f}%")
        elif skill == "vocabulary":
            recommendations.append(f"Expand your vocabulary - your score was {score:.0f}%")
        elif skill == "listening":
            recommendations.append(
                f"Practice listening comprehension - your score was {score:.0f}%"
            )

    return recommendations
