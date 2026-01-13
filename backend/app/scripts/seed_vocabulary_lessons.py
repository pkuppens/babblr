"""Seed script for vocabulary lessons.

Creates initial vocabulary lessons for Spanish, Italian, German, French, and Dutch
at A1 level to ensure the UI is not empty.
"""

import asyncio
import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.db import Base
from app.models.models import Lesson, LessonItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample vocabulary lessons data
VOCABULARY_LESSONS = {
    "es": [  # Spanish
        {
            "title": "Greetings and Basic Phrases",
            "description": "Learn essential greetings and polite expressions in Spanish",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hola",
                    "item_metadata": json.dumps(
                        {"translation": "Hello", "pronunciation": "OH-lah"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Buenos días",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "BWEH-nos DEE-ahs"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Buenas tardes",
                    "item_metadata": json.dumps(
                        {"translation": "Good afternoon", "pronunciation": "BWEH-nas TAR-des"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Buenas noches",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening/night", "pronunciation": "BWEH-nas NO-ches"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Adiós",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "ah-DYOHS"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Por favor",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "por fah-VOR"}
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Gracias",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "GRAH-see-ahs"}
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "De nada",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "deh NAH-dah"}
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Numbers 1-20",
            "description": "Learn to count from 1 to 20 in Spanish",
            "difficulty_level": "A1",
            "order_index": 2,
            "items": [
                {
                    "item_type": "word",
                    "content": "uno",
                    "item_metadata": json.dumps({"translation": "one", "pronunciation": "OO-no"}),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "dos",
                    "item_metadata": json.dumps({"translation": "two", "pronunciation": "dohs"}),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "tres",
                    "item_metadata": json.dumps({"translation": "three", "pronunciation": "trehs"}),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "cuatro",
                    "item_metadata": json.dumps(
                        {"translation": "four", "pronunciation": "KWAH-troh"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "cinco",
                    "item_metadata": json.dumps(
                        {"translation": "five", "pronunciation": "SEEN-koh"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "seis",
                    "item_metadata": json.dumps({"translation": "six", "pronunciation": "says"}),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "siete",
                    "item_metadata": json.dumps(
                        {"translation": "seven", "pronunciation": "SYEH-teh"}
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "ocho",
                    "item_metadata": json.dumps(
                        {"translation": "eight", "pronunciation": "OH-choh"}
                    ),
                    "order_index": 8,
                },
                {
                    "item_type": "word",
                    "content": "nueve",
                    "item_metadata": json.dumps(
                        {"translation": "nine", "pronunciation": "NWEH-veh"}
                    ),
                    "order_index": 9,
                },
                {
                    "item_type": "word",
                    "content": "diez",
                    "item_metadata": json.dumps({"translation": "ten", "pronunciation": "dyehs"}),
                    "order_index": 10,
                },
            ],
        },
    ],
    "it": [  # Italian
        {
            "title": "Greetings and Basic Phrases",
            "description": "Learn essential greetings and polite expressions in Italian",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Ciao",
                    "item_metadata": json.dumps(
                        {"translation": "Hello/Goodbye", "pronunciation": "CHOW"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Buongiorno",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "bwon-JOR-no"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Buonasera",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "bwoh-nah-SEH-rah"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Per favore",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "per fah-VOH-reh"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Grazie",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "GRAH-tsee-eh"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Prego",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "PREH-goh"}
                    ),
                    "order_index": 6,
                },
            ],
        },
    ],
    "de": [  # German
        {
            "title": "Greetings and Basic Phrases",
            "description": "Learn essential greetings and polite expressions in German",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hallo",
                    "item_metadata": json.dumps(
                        {"translation": "Hello", "pronunciation": "HAH-loh"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Guten Morgen",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "GOO-ten MOR-gen"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Guten Tag",
                    "item_metadata": json.dumps(
                        {"translation": "Good day", "pronunciation": "GOO-ten TAHK"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Guten Abend",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "GOO-ten AH-bent"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Auf Wiedersehen",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "owf VEE-der-zay-en"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Bitte",
                    "item_metadata": json.dumps(
                        {"translation": "Please/You're welcome", "pronunciation": "BIT-teh"}
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Danke",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "DAHN-keh"}
                    ),
                    "order_index": 7,
                },
            ],
        },
    ],
    "fr": [  # French
        {
            "title": "Greetings and Basic Phrases",
            "description": "Learn essential greetings and polite expressions in French",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Bonjour",
                    "item_metadata": json.dumps(
                        {"translation": "Hello/Good morning", "pronunciation": "bon-ZHOOR"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Bonsoir",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "bon-SWAHR"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Au revoir",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "oh ruh-VWAHR"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "S'il vous plaît",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "seel voo PLAY"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Merci",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "mehr-SEE"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "De rien",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "duh RYEHN"}
                    ),
                    "order_index": 6,
                },
            ],
        },
    ],
    "nl": [  # Dutch
        {
            "title": "Greetings and Basic Phrases",
            "description": "Learn essential greetings and polite expressions in Dutch",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hallo",
                    "item_metadata": json.dumps(
                        {"translation": "Hello", "pronunciation": "HAH-loh"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Goedemorgen",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "KHOOH-deh-MOR-ghen"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Goedemiddag",
                    "item_metadata": json.dumps(
                        {"translation": "Good afternoon", "pronunciation": "KHOOH-deh-MID-dahkh"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Goedenavond",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "KHOOH-den-AH-vont"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Tot ziens",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "tot ZEENS"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Alsjeblieft",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "AHL-shuh-bleeft"}
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Dank je",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "dahnk yuh"}
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "Graag gedaan",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "khrahkh kheh-DAHN"}
                    ),
                    "order_index": 8,
                },
            ],
        },
    ],
}


async def seed_vocabulary_lessons():
    """Seed vocabulary lessons into the database."""
    # Create async engine
    engine = create_async_engine(settings.babblr_conversation_database_url, echo=False)

    # Create session factory
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Import models to ensure they're registered
            from app.models import models  # noqa: F401

            # Create tables if they don't exist
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Starting vocabulary lessons seed...")

            lessons_created = 0
            items_created = 0

            for language, lessons in VOCABULARY_LESSONS.items():
                logger.info(f"Seeding vocabulary lessons for language: {language}")

                for lesson_data in lessons:
                    # Check if lesson already exists (by title and language)
                    from sqlalchemy import select

                    existing = await session.execute(
                        select(Lesson).where(
                            Lesson.language == language,
                            Lesson.lesson_type == "vocabulary",
                            Lesson.title == lesson_data["title"],
                        )
                    )
                    if existing.scalar_one_or_none():
                        logger.info(
                            f"Lesson '{lesson_data['title']}' already exists for {language}, skipping..."
                        )
                        continue

                    # Create lesson
                    lesson = Lesson(
                        language=language,
                        lesson_type="vocabulary",
                        title=lesson_data["title"],
                        description=lesson_data["description"],
                        difficulty_level=lesson_data["difficulty_level"],
                        order_index=lesson_data["order_index"],
                        is_active=True,
                        created_at=datetime.utcnow(),
                    )

                    session.add(lesson)
                    await session.flush()  # Get lesson.id

                    # Create lesson items
                    for item_data in lesson_data["items"]:
                        item = LessonItem(
                            lesson_id=lesson.id,
                            item_type=item_data["item_type"],
                            content=item_data["content"],
                            item_metadata=item_data["item_metadata"],
                            order_index=item_data["order_index"],
                            created_at=datetime.utcnow(),
                        )
                        session.add(item)
                        items_created += 1

                    lessons_created += 1
                    logger.info(f"Created lesson: {lesson_data['title']} ({language})")

            await session.commit()

            logger.info(f"Seed completed: {lessons_created} lessons, {items_created} items created")

        except Exception as e:
            logger.error(f"Error seeding vocabulary lessons: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_vocabulary_lessons())
