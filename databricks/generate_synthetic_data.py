#!/usr/bin/env python3
"""
Generate synthetic Babblr learning data for Databricks demo.

Creates realistic sample data with:
- 50 simulated students (user_ids)
- 500+ conversations across 6 languages
- 1000+ lesson progress records
- 200+ assessment attempts
- Realistic progression patterns and correlations

Usage:
    python generate_synthetic_data.py [--output-dir DIR] [--seed SEED]
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np


# Configuration
LANGUAGES = ["spanish", "italian", "german", "french", "dutch", "english"]
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_ORDER = {level: i for i, level in enumerate(CEFR_LEVELS)}

TOPICS = [
    "greetings", "restaurant", "shopping", "travel", "weather",
    "family", "work", "hobbies", "health", "directions",
    "food", "sports", "music", "movies", "technology"
]

LESSON_TYPES = ["vocabulary", "grammar", "listening"]
ASSESSMENT_TYPES = ["cefr_placement", "vocabulary", "grammar", "comprehensive"]

VOCAB_SUBJECTS = [
    "numbers", "colors", "food", "clothing", "animals",
    "household", "transportation", "professions", "body_parts", "time"
]

GRAMMAR_SUBJECTS = [
    "present_tense", "past_tense", "future_tense", "subjunctive",
    "articles", "pronouns", "adjectives", "prepositions", "conditionals"
]


def generate_user_journeys(n_users: int, start_date: datetime, seed: int) -> list:
    """Generate realistic user learning journeys."""
    random.seed(seed)
    np.random.seed(seed)

    journeys = []
    for user_id in range(1, n_users + 1):
        # Each user has characteristics that affect their learning
        language = random.choice(LANGUAGES)
        starting_level_idx = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        learning_speed = np.random.normal(1.0, 0.3)  # Multiplier
        engagement = np.random.beta(2, 2)  # 0-1, how active they are
        error_tendency = np.random.beta(2, 5)  # Lower = fewer errors

        # User's journey start date (spread over 90 days)
        user_start = start_date + timedelta(days=random.randint(0, 90))

        journeys.append({
            "user_id": user_id,
            "language": language,
            "starting_level_idx": starting_level_idx,
            "learning_speed": max(0.3, learning_speed),
            "engagement": engagement,
            "error_tendency": error_tendency,
            "start_date": user_start,
        })

    return journeys


def generate_conversations(journeys: list, seed: int) -> pd.DataFrame:
    """Generate conversation data based on user journeys."""
    random.seed(seed)
    conversations = []
    conv_id = 1

    for journey in journeys:
        # Number of conversations based on engagement
        n_convs = int(5 + journey["engagement"] * 20)
        current_date = journey["start_date"]
        current_level_idx = journey["starting_level_idx"]

        for _ in range(n_convs):
            # Progress level occasionally
            if random.random() < 0.1 * journey["learning_speed"]:
                current_level_idx = min(current_level_idx + 1, 5)

            conversations.append({
                "id": conv_id,
                "user_id": journey["user_id"],
                "language": journey["language"],
                "difficulty_level": CEFR_LEVELS[current_level_idx],
                "topic_id": random.choice(TOPICS),
                "created_at": current_date.isoformat(),
                "updated_at": (current_date + timedelta(minutes=random.randint(5, 30))).isoformat(),
            })
            conv_id += 1
            current_date += timedelta(hours=random.randint(12, 72))

    return pd.DataFrame(conversations)


def generate_messages(conversations_df: pd.DataFrame, journeys: list, seed: int) -> pd.DataFrame:
    """Generate messages for each conversation."""
    random.seed(seed)
    messages = []
    msg_id = 1

    journey_map = {j["user_id"]: j for j in journeys}

    for _, conv in conversations_df.iterrows():
        journey = journey_map[conv["user_id"]]
        n_exchanges = random.randint(3, 8)
        msg_time = datetime.fromisoformat(conv["created_at"])

        for i in range(n_exchanges * 2):
            role = "user" if i % 2 == 0 else "assistant"

            # Generate corrections for user messages based on error tendency
            corrections = None
            if role == "user" and random.random() < journey["error_tendency"]:
                error_types = ["grammar", "vocabulary", "spelling"]
                corrections = json.dumps([{
                    "type": random.choice(error_types),
                    "original": "example error",
                    "corrected": "example correction",
                    "explanation": "Brief explanation"
                }])

            messages.append({
                "id": msg_id,
                "conversation_id": conv["id"],
                "role": role,
                "content": f"Sample {role} message in {conv['language']} about {conv['topic_id']}",
                "audio_path": None,
                "corrections": corrections,
                "created_at": msg_time.isoformat(),
            })
            msg_id += 1
            msg_time += timedelta(seconds=random.randint(10, 60))

    return pd.DataFrame(messages)


def generate_lessons(seed: int) -> pd.DataFrame:
    """Generate lesson catalog."""
    random.seed(seed)
    lessons = []
    lesson_id = 1

    for language in LANGUAGES:
        for level in CEFR_LEVELS:
            # Vocabulary lessons
            for subject in VOCAB_SUBJECTS:
                lessons.append({
                    "id": lesson_id,
                    "language": language,
                    "lesson_type": "vocabulary",
                    "title": f"{subject.replace('_', ' ').title()} - {level}",
                    "subject": subject,
                    "difficulty_level": level,
                    "order_index": lesson_id,
                    "is_active": True,
                    "created_at": datetime(2024, 1, 1).isoformat(),
                })
                lesson_id += 1

            # Grammar lessons
            for subject in GRAMMAR_SUBJECTS:
                lessons.append({
                    "id": lesson_id,
                    "language": language,
                    "lesson_type": "grammar",
                    "title": f"{subject.replace('_', ' ').title()} - {level}",
                    "subject": subject,
                    "difficulty_level": level,
                    "order_index": lesson_id,
                    "is_active": True,
                    "created_at": datetime(2024, 1, 1).isoformat(),
                })
                lesson_id += 1

    return pd.DataFrame(lessons)


def generate_lesson_progress(lessons_df: pd.DataFrame, journeys: list, seed: int) -> pd.DataFrame:
    """Generate lesson progress records."""
    random.seed(seed)
    np.random.seed(seed)
    progress = []
    progress_id = 1

    for journey in journeys:
        # Filter lessons for this user's language
        user_lessons = lessons_df[lessons_df["language"] == journey["language"]]

        # User completes lessons based on engagement and learning speed
        n_lessons = int(len(user_lessons) * journey["engagement"] * 0.5)
        selected_lessons = user_lessons.sample(n=min(n_lessons, len(user_lessons)))

        current_date = journey["start_date"]

        for _, lesson in selected_lessons.iterrows():
            # Determine status based on engagement
            status_roll = random.random()
            if status_roll < 0.6:
                status = "completed"
                completion_pct = 100.0
                completed_at = (current_date + timedelta(hours=random.randint(1, 4))).isoformat()
            elif status_roll < 0.85:
                status = "in_progress"
                completion_pct = random.uniform(20, 80)
                completed_at = None
            else:
                status = "not_started"
                completion_pct = 0.0
                completed_at = None

            # Mastery score correlates with learning speed
            mastery = None
            if status == "completed":
                mastery = min(1.0, max(0.3, np.random.normal(
                    0.6 + journey["learning_speed"] * 0.2, 0.15
                )))

            progress.append({
                "id": progress_id,
                "user_id": journey["user_id"],
                "lesson_id": lesson["id"],
                "language": journey["language"],
                "status": status,
                "completion_percentage": completion_pct,
                "mastery_score": mastery,
                "started_at": current_date.isoformat(),
                "completed_at": completed_at,
                "last_accessed_at": current_date.isoformat(),
            })
            progress_id += 1
            current_date += timedelta(hours=random.randint(6, 48))

    return pd.DataFrame(progress)


def generate_assessments(seed: int) -> pd.DataFrame:
    """Generate assessment catalog."""
    assessments = []
    assessment_id = 1

    for language in LANGUAGES:
        for atype in ASSESSMENT_TYPES:
            for level in CEFR_LEVELS:
                assessments.append({
                    "id": assessment_id,
                    "language": language,
                    "assessment_type": atype,
                    "title": f"{atype.replace('_', ' ').title()} - {level} ({language.title()})",
                    "description": f"Assessment for {level} level {atype}",
                    "difficulty_level": level,
                    "duration_minutes": random.randint(15, 45),
                    "is_active": True,
                    "created_at": datetime(2024, 1, 1).isoformat(),
                })
                assessment_id += 1

    return pd.DataFrame(assessments)


def generate_assessment_attempts(
    assessments_df: pd.DataFrame, journeys: list, seed: int
) -> pd.DataFrame:
    """Generate assessment attempt records."""
    random.seed(seed)
    np.random.seed(seed)
    attempts = []
    attempt_id = 1

    for journey in journeys:
        # Filter assessments for this user's language
        user_assessments = assessments_df[assessments_df["language"] == journey["language"]]

        # Number of attempts based on engagement
        n_attempts = int(2 + journey["engagement"] * 8)
        current_date = journey["start_date"] + timedelta(days=7)  # Start after a week
        current_level_idx = journey["starting_level_idx"]

        for _ in range(n_attempts):
            # Pick an assessment at or near current level
            level_filter = CEFR_LEVELS[max(0, current_level_idx - 1):current_level_idx + 2]
            eligible = user_assessments[user_assessments["difficulty_level"].isin(level_filter)]

            if len(eligible) == 0:
                continue

            assessment = eligible.sample(n=1).iloc[0]

            # Score based on learning speed and whether level is appropriate
            level_diff = abs(CEFR_ORDER[assessment["difficulty_level"]] - current_level_idx)
            base_score = 70 - level_diff * 15 + journey["learning_speed"] * 10
            score = min(100, max(20, np.random.normal(base_score, 10)))

            total_questions = random.randint(15, 30)
            correct = int(total_questions * score / 100)

            # Skill breakdown
            skills = ["reading", "writing", "listening", "vocabulary", "grammar"]
            skill_scores = []
            for skill in skills:
                skill_total = total_questions // len(skills)
                skill_correct = int(skill_total * (score / 100) * np.random.uniform(0.8, 1.2))
                skill_scores.append({
                    "skill": skill,
                    "total": skill_total,
                    "correct": min(skill_correct, skill_total),
                    "score": min(100, skill_correct / skill_total * 100) if skill_total > 0 else 0
                })

            # Recommended level based on score
            if score >= 80:
                rec_level_idx = min(current_level_idx + 1, 5)
            elif score >= 60:
                rec_level_idx = current_level_idx
            else:
                rec_level_idx = max(current_level_idx - 1, 0)

            attempts.append({
                "id": attempt_id,
                "user_id": journey["user_id"],
                "assessment_id": assessment["id"],
                "language": journey["language"],
                "score": round(score, 1),
                "total_questions": total_questions,
                "correct_answers": correct,
                "started_at": current_date.isoformat(),
                "completed_at": (current_date + timedelta(minutes=random.randint(10, 40))).isoformat(),
                "answers_json": None,
                "recommended_level": CEFR_LEVELS[rec_level_idx],
                "skill_scores_json": json.dumps(skill_scores),
            })

            # Progress level based on performance
            if score >= 75 and random.random() < 0.3:
                current_level_idx = min(current_level_idx + 1, 5)

            attempt_id += 1
            current_date += timedelta(days=random.randint(3, 14))

    return pd.DataFrame(attempts)


def generate_user_levels(journeys: list, attempts_df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Generate current user level records."""
    random.seed(seed)
    user_levels = []
    level_id = 1

    for journey in journeys:
        # Find user's latest assessment to determine current level
        user_attempts = attempts_df[attempts_df["user_id"] == journey["user_id"]]

        if len(user_attempts) > 0:
            latest = user_attempts.sort_values("completed_at").iloc[-1]
            cefr_level = latest["recommended_level"]
            proficiency = latest["score"]
            assessed_at = latest["completed_at"]
        else:
            cefr_level = CEFR_LEVELS[journey["starting_level_idx"]]
            proficiency = 50.0
            assessed_at = journey["start_date"].isoformat()

        user_levels.append({
            "id": level_id,
            "user_id": journey["user_id"],
            "language": journey["language"],
            "cefr_level": cefr_level,
            "proficiency_score": round(proficiency, 1),
            "assessed_at": assessed_at,
            "updated_at": assessed_at,
        })
        level_id += 1

    return pd.DataFrame(user_levels)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Babblr data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data"),
        help="Output directory for Parquet files",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--n-users",
        type=int,
        default=50,
        help="Number of simulated users",
    )
    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Generating synthetic Babblr data")
    print(f"[INFO] Users: {args.n_users}, Seed: {args.seed}")
    print(f"[INFO] Output: {args.output_dir}")
    print()

    # Starting date for data generation
    start_date = datetime(2024, 6, 1)

    # Generate user journeys (internal, not exported)
    print("[STEP] Generating user journeys...")
    journeys = generate_user_journeys(args.n_users, start_date, args.seed)

    # Generate all datasets
    print("[STEP] Generating conversations...")
    conversations_df = generate_conversations(journeys, args.seed)
    conversations_df.to_parquet(args.output_dir / "conversations.parquet", index=False)
    print(f"  -> {len(conversations_df)} conversations")

    print("[STEP] Generating messages...")
    messages_df = generate_messages(conversations_df, journeys, args.seed + 1)
    messages_df.to_parquet(args.output_dir / "messages.parquet", index=False)
    print(f"  -> {len(messages_df)} messages")

    print("[STEP] Generating lessons...")
    lessons_df = generate_lessons(args.seed + 2)
    lessons_df.to_parquet(args.output_dir / "lessons.parquet", index=False)
    print(f"  -> {len(lessons_df)} lessons")

    print("[STEP] Generating lesson progress...")
    progress_df = generate_lesson_progress(lessons_df, journeys, args.seed + 3)
    progress_df.to_parquet(args.output_dir / "lesson_progress.parquet", index=False)
    print(f"  -> {len(progress_df)} progress records")

    print("[STEP] Generating assessments...")
    assessments_df = generate_assessments(args.seed + 4)
    assessments_df.to_parquet(args.output_dir / "assessments.parquet", index=False)
    print(f"  -> {len(assessments_df)} assessments")

    print("[STEP] Generating assessment attempts...")
    attempts_df = generate_assessment_attempts(assessments_df, journeys, args.seed + 5)
    attempts_df.to_parquet(args.output_dir / "assessment_attempts.parquet", index=False)
    print(f"  -> {len(attempts_df)} attempts")

    print("[STEP] Generating user levels...")
    levels_df = generate_user_levels(journeys, attempts_df, args.seed + 6)
    levels_df.to_parquet(args.output_dir / "user_levels.parquet", index=False)
    print(f"  -> {len(levels_df)} user levels")

    print()
    print("[DONE] All data generated successfully!")
    print()
    print("Files created:")
    for f in sorted(args.output_dir.glob("*.parquet")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.1f} KB")

    print()
    print("Next steps:")
    print("  1. Upload files to Databricks DBFS: /FileStore/babblr/bronze/")
    print("  2. Run notebook 01_bronze_layer.py")


if __name__ == "__main__":
    main()
