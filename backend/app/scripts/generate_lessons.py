"""Generate lessons using GenAI for Spanish (A1-C2).

This script uses LLM to generate lesson metadata (title, oneliner, tutor_prompt)
for Spanish lessons across all CEFR levels. Lessons are stored in the database.

Usage:
    cd backend
    python -m app.scripts.generate_lessons
"""

import asyncio
import json
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.models import Lesson
from app.services.llm.factory import ProviderFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Curriculum structure: key topics per level (not exhaustive)
SPANISH_CURRICULUM = {
    "A1": {
        "grammar": [
            {"subject": "present_ar_verbs", "order": 1},
            {"subject": "present_er_ir_verbs", "order": 2},
            {"subject": "ser_estar_basic", "order": 3},
            {"subject": "hay", "order": 4},
            {"subject": "adjective_agreement", "order": 5},
        ],
        "vocabulary": [
            {"subject": "greetings", "topic_id": "greetings", "order": 1},
            {"subject": "numbers", "topic_id": "numbers", "order": 2},
            {"subject": "colors", "topic_id": "colors", "order": 3},
        ],
    },
    "A2": {
        "grammar": [
            {"subject": "stem_changing_verbs", "order": 1},
            {"subject": "reflexive_verbs", "order": 2},
            {"subject": "preterite_regular", "order": 3},
            {"subject": "imperfect_intro", "order": 4},
        ],
        "vocabulary": [
            {"subject": "family", "topic_id": "family", "order": 1},
            {"subject": "food", "topic_id": "food", "order": 2},
        ],
    },
    "B1": {
        "grammar": [
            {"subject": "preterite_imperfect_contrast", "order": 1},
            {"subject": "present_subjunctive_intro", "order": 2},
            {"subject": "future_tense", "order": 3},
        ],
        "vocabulary": [
            {"subject": "travel", "topic_id": "travel", "order": 1},
        ],
    },
    "B2": {
        "grammar": [
            {"subject": "past_subjunctive", "order": 1},
            {"subject": "conditional", "order": 2},
        ],
        "vocabulary": [
            {"subject": "work", "topic_id": "work", "order": 1},
        ],
    },
    "C1": {
        "grammar": [
            {"subject": "subjunctive_advanced", "order": 1},
            {"subject": "passive_voice", "order": 2},
        ],
    },
    "C2": {
        "grammar": [
            {"subject": "literary_tenses", "order": 1},
        ],
    },
}


async def generate_lesson_metadata(
    provider, subject: str, lesson_type: str, level: str, topic_id: Optional[str] = None
) -> dict:
    """Generate lesson metadata using LLM.

    Args:
        provider: LLM provider instance
        subject: Subject identifier (e.g., "present_ar_verbs")
        lesson_type: Type of lesson ("grammar", "vocabulary", "listening")
        level: CEFR level (A1-C2)
        topic_id: Optional vocabulary topic ID

    Returns:
        Dictionary with title, oneliner, and tutor_prompt
    """
    # Build prompt for lesson generation
    prompt = f"""You are creating a Spanish language lesson for {level} level learners.

Lesson type: {lesson_type}
Subject: {subject}
Level: {level}
{f"Vocabulary topic: {topic_id}" if topic_id else ""}

Generate lesson metadata in JSON format:
{{
    "title": "Clear, engaging lesson title",
    "oneliner": "Brief one-sentence description for lesson cards (max 100 words)",
    "tutor_prompt": "Extensive prompt for LLM content generation. Include:
    - Learning objectives
    - Key concepts to cover
    - Example structures
    - Common mistakes to address
    - Teaching approach suitable for {level} level"
}}

Make it suitable for {level} level learners. Keep explanations clear and encouraging.
"""

    try:
        response = await provider.generate(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert language curriculum designer.",
            max_tokens=1500,
            temperature=0.7,
        )

        # Parse JSON response
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        metadata = json.loads(content)
        return metadata

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response was: {response.content}")
        # Fallback to basic metadata
        return {
            "title": f"{subject.replace('_', ' ').title()}",
            "oneliner": f"Learn {subject.replace('_', ' ')} in Spanish",
            "tutor_prompt": f"Teach {subject} to {level} level Spanish learners.",
        }
    except Exception as e:
        logger.error(f"Error generating lesson metadata: {e}")
        raise


async def generate_lessons_for_level(
    db: AsyncSession, provider, language: str, level: str, curriculum: dict
):
    """Generate lessons for a specific level.

    Args:
        db: Database session
        provider: LLM provider instance
        language: Language code (e.g., "es")
        level: CEFR level (A1-C2)
        curriculum: Curriculum structure for this level
    """
    logger.info(f"Generating lessons for {language} {level}...")

    for lesson_type, topics in curriculum.items():
        logger.info(f"  Generating {lesson_type} lessons...")

        for topic_def in topics:
            subject = topic_def["subject"]
            order = topic_def["order"]
            topic_id = topic_def.get("topic_id")

            # Check if lesson already exists
            existing = await db.execute(
                select(Lesson).where(
                    Lesson.language == language,
                    Lesson.lesson_type == lesson_type,
                    Lesson.subject == subject,
                    Lesson.difficulty_level == level,
                )
            )
            if existing.scalar_one_or_none():
                logger.info(f"    Lesson {subject} already exists, skipping...")
                continue

            # Generate metadata
            logger.info(f"    Generating metadata for {subject}...")
            metadata = await generate_lesson_metadata(
                provider, subject, lesson_type, level, topic_id
            )

            # Create lesson
            lesson = Lesson(
                language=language,
                lesson_type=lesson_type,
                title=metadata["title"],
                oneliner=metadata.get("oneliner"),
                tutor_prompt=metadata.get("tutor_prompt"),
                subject=subject,
                topic_id=topic_id,
                difficulty_level=level,
                order_index=order,
                is_active=True,
            )

            db.add(lesson)
            await db.commit()
            await db.refresh(lesson)

            logger.info(f"    Created lesson: {metadata['title']}")


async def main():
    """Generate Spanish lessons for all CEFR levels."""
    # Initialize database
    engine = create_async_engine(settings.babblr_conversation_database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # Get LLM provider
    provider = ProviderFactory.get_provider()

    async with async_session_maker() as db:
        # Generate lessons for each level
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            if level in SPANISH_CURRICULUM:
                await generate_lessons_for_level(
                    db, provider, "es", level, SPANISH_CURRICULUM[level]
                )

    logger.info("Lesson generation completed!")


if __name__ == "__main__":
    asyncio.run(main())
