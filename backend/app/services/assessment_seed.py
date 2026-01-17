"""
Assessment seed data service.

Creates sample CEFR placement assessments for development and testing.
"""

import json
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Assessment, AssessmentQuestion

logger = logging.getLogger(__name__)

# Sample questions for Spanish CEFR placement test
# Covers grammar (8+) and vocabulary (7+) skill categories
SPANISH_PLACEMENT_QUESTIONS = [
    # Grammar questions (10 questions)
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Yo ___ español todos los días.",
        "options": ["hablo", "hablas", "habla", "hablamos"],
        "correct_answer": "hablo",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Ella ___ una estudiante.",
        "options": ["soy", "eres", "es", "somos"],
        "correct_answer": "es",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Nosotros ___ en Madrid.",
        "options": ["vivo", "vives", "vive", "vivimos"],
        "correct_answer": "vivimos",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "¿Tú ___ café por la mañana?",
        "options": ["bebo", "bebes", "bebe", "bebemos"],
        "correct_answer": "bebes",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Ellos ___ muy inteligentes.",
        "options": ["soy", "eres", "es", "son"],
        "correct_answer": "son",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Mi hermano ___ 25 años.",
        "options": ["tiene", "tienes", "tengo", "tienen"],
        "correct_answer": "tiene",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Ayer yo ___ al cine.",
        "options": ["fui", "fue", "fuiste", "fueron"],
        "correct_answer": "fui",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "Mañana nosotros ___ a la playa.",
        "options": ["vamos", "iremos", "fuimos", "íbamos"],
        "correct_answer": "iremos",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "___ libro es muy interesante.",
        "options": ["Este", "Esta", "Estos", "Estas"],
        "correct_answer": "Este",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "grammar",
        "question_text": "El coche es ___ que la bicicleta.",
        "options": ["más rápido", "más rápida", "muy rápido", "tan rápido"],
        "correct_answer": "más rápido",
        "points": 1,
    },
    # Vocabulary questions (8 questions)
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "What does 'casa' mean?",
        "options": ["car", "house", "table", "book"],
        "correct_answer": "house",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "The word for 'water' in Spanish is:",
        "options": ["leche", "pan", "agua", "vino"],
        "correct_answer": "agua",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "'Perro' means:",
        "options": ["cat", "dog", "bird", "fish"],
        "correct_answer": "dog",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "What is 'apple' in Spanish?",
        "options": ["naranja", "plátano", "manzana", "uva"],
        "correct_answer": "manzana",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "'Trabajo' means:",
        "options": ["travel", "work", "study", "play"],
        "correct_answer": "work",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "The Spanish word 'hermano' means:",
        "options": ["friend", "father", "brother", "cousin"],
        "correct_answer": "brother",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "'Ciudad' translates to:",
        "options": ["country", "city", "village", "street"],
        "correct_answer": "city",
        "points": 1,
    },
    {
        "question_type": "multiple_choice",
        "skill_category": "vocabulary",
        "question_text": "What does 'tiempo' mean?",
        "options": ["time/weather", "space", "place", "money"],
        "correct_answer": "time/weather",
        "points": 1,
    },
]


async def seed_assessment_data(
    db: AsyncSession,
    language: str = "es",
) -> Optional[Assessment]:
    """
    Seed the database with a CEFR placement assessment.

    Args:
        db: Database session
        language: Target language code

    Returns:
        Created assessment or None if already exists
    """
    # Check if assessment already exists
    existing = await db.execute(
        select(Assessment).where(
            Assessment.language == language,
            Assessment.assessment_type == "cefr_placement",
        )
    )
    if existing.scalar():
        logger.info(f"Assessment already exists for {language}")
        return None

    # Create assessment
    assessment = Assessment(
        language=language,
        assessment_type="cefr_placement",
        title=f"CEFR Placement Test ({language.upper()})",
        description="Test your proficiency level to get personalized recommendations",
        difficulty_level="mixed",  # Covers multiple levels
        duration_minutes=20,
        is_active=True,
    )
    db.add(assessment)
    await db.flush()  # Get ID

    # Add questions
    questions = SPANISH_PLACEMENT_QUESTIONS if language == "es" else SPANISH_PLACEMENT_QUESTIONS
    for idx, q_data in enumerate(questions):
        question = AssessmentQuestion(
            assessment_id=assessment.id,
            question_type=q_data["question_type"],
            skill_category=q_data["skill_category"],
            question_text=q_data["question_text"],
            options=json.dumps(q_data["options"]),
            correct_answer=q_data["correct_answer"],
            points=q_data["points"],
            order_index=idx,
        )
        db.add(question)

    await db.commit()
    logger.info(f"Seeded assessment for {language} with {len(questions)} questions")
    return assessment


async def get_seeded_assessment(
    db: AsyncSession,
    language: str,
) -> Optional[Assessment]:
    """Get seeded assessment with questions loaded."""
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.assessment_questions))
        .where(
            Assessment.language == language,
            Assessment.assessment_type == "cefr_placement",
        )
    )
    return result.scalar()


async def get_all_assessments(
    db: AsyncSession,
    language: str,
) -> list[Assessment]:
    """Get all assessments for a language."""
    result = await db.execute(
        select(Assessment).where(
            Assessment.language == language,
            Assessment.assessment_type == "cefr_placement",
        )
    )
    return list(result.scalars().all())
