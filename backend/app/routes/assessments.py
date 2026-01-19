"""Assessment endpoints for CEFR proficiency testing."""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.models.models import Assessment, AssessmentAttempt, AssessmentQuestion
from app.models.schemas import (
    AssessmentDetailResponse,
    AssessmentListResponse,
    AssessmentQuestionResponse,
    AttemptCreate,
    AttemptResultResponse,
    AttemptSummary,
    QuestionAnswer,
    SkillScore,
)
from app.services.language_catalog import find_variant
from app.services.scoring_service import (
    calculate_scores,
    determine_cefr_level,
    generate_practice_recommendations,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessments", tags=["assessments"])


def validate_language(language: str) -> None:
    """Validate that language code is supported."""
    if not find_variant(language):
        raise HTTPException(status_code=400, detail=f"Invalid language code '{language}'")


@router.get("/attempts", response_model=list[AttemptSummary])
async def list_attempts(
    language: str = Query(..., description="Target language code"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's assessment attempt history.

    Returns attempts ordered by date (newest first).
    """
    result = await db.execute(
        select(AssessmentAttempt, Assessment.title)
        .join(Assessment)
        .where(AssessmentAttempt.language == language)
        .order_by(AssessmentAttempt.completed_at.desc())
        .limit(limit)
    )

    attempts = []
    for row in result:
        attempt = row[0]
        title = row[1]
        attempts.append(
            AttemptSummary(
                id=attempt.id,
                assessment_id=attempt.assessment_id,
                assessment_title=title,
                language=attempt.language,
                score=attempt.score,
                recommended_level=attempt.recommended_level,
                completed_at=attempt.completed_at,
            )
        )

    return attempts


@router.get("/attempts/{attempt_id}", response_model=AttemptResultResponse)
async def get_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed results for a specific assessment attempt.

    Returns full attempt details including skill breakdown, recommendations, and question-by-question answers.
    """
    result = await db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id))
    attempt = result.scalar()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Parse skill scores from JSON
    skill_scores_json_value = attempt.skill_scores_json
    skill_scores_data = (
        json.loads(skill_scores_json_value) if skill_scores_json_value is not None else []
    )  # type: ignore[arg-type]
    skill_scores = [SkillScore(**s) for s in skill_scores_data]

    # Generate practice recommendations from skill scores
    skill_scores_dict = {
        s.skill: {"score": s.score, "total": s.total, "correct": s.correct} for s in skill_scores
    }
    recommendations = generate_practice_recommendations(skill_scores_dict)

    # Build question answers for review
    question_answers = []
    answers_json_value = attempt.answers_json
    if answers_json_value is not None:
        user_answers = json.loads(answers_json_value)  # type: ignore[arg-type]

        # Get assessment with questions to access correct answers
        assessment_result = await db.execute(
            select(Assessment)
            .options(selectinload(Assessment.assessment_questions))
            .where(Assessment.id == attempt.assessment_id)
        )
        assessment = assessment_result.scalar()

        if assessment:
            # Create a map of question ID to question for quick lookup
            question_map = {str(q.id): q for q in assessment.assessment_questions}

            for question_id_str, user_answer in user_answers.items():
                question = question_map.get(question_id_str)
                if question:
                    is_correct = user_answer == question.correct_answer
                    options = json.loads(question.options) if question.options else None

                    question_answers.append(
                        QuestionAnswer(
                            question_id=question.id,
                            question_text=question.question_text,
                            skill_category=question.skill_category,
                            user_answer=user_answer,
                            correct_answer=question.correct_answer,
                            is_correct=is_correct,
                            options=options,
                        )
                    )

    return AttemptResultResponse(
        id=attempt.id,
        assessment_id=attempt.assessment_id,
        language=attempt.language,
        score=attempt.score,
        recommended_level=attempt.recommended_level,
        skill_scores=skill_scores,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        practice_recommendations=recommendations,
        question_answers=question_answers if question_answers else None,
    )


@router.delete("/attempts/{attempt_id}")
async def delete_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an assessment attempt.

    Permanently removes the attempt from the user's history.
    """
    result = await db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id))
    attempt = result.scalar()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    await db.delete(attempt)
    await db.commit()

    logger.info(f"Deleted assessment attempt {attempt_id}")
    return {"message": "Attempt deleted successfully"}


@router.get("", response_model=list[AssessmentListResponse])
async def list_assessments(
    language: str = Query(..., description="Target language code (e.g., 'es', 'fr')"),
    db: AsyncSession = Depends(get_db),
):
    """
    List available assessments for a language.

    Returns active assessments with question counts.
    """
    validate_language(language)

    # Query assessments with question count
    result = await db.execute(
        select(Assessment, func.count(AssessmentQuestion.id).label("question_count"))
        .outerjoin(AssessmentQuestion)
        .where(
            Assessment.language == language,
            Assessment.is_active == True,  # noqa: E712
        )
        .group_by(Assessment.id)
    )

    assessments = []
    for row in result:
        assessment = row[0]
        question_count = row[1] or 0

        # Get skill categories from questions
        skill_result = await db.execute(
            select(AssessmentQuestion.skill_category)
            .where(AssessmentQuestion.assessment_id == assessment.id)
            .distinct()
        )
        skill_categories = [r[0] for r in skill_result.fetchall()]

        assessments.append(
            AssessmentListResponse(
                id=assessment.id,
                language=assessment.language,
                assessment_type=assessment.assessment_type,
                title=assessment.title,
                description=assessment.description,
                difficulty_level=assessment.difficulty_level,
                duration_minutes=assessment.duration_minutes,
                skill_categories=skill_categories,
                is_active=assessment.is_active,
                created_at=assessment.created_at,
                question_count=question_count,
            )
        )

    logger.info(f"Found {len(assessments)} assessments for language={language}")
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
async def get_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get assessment details with questions.

    Questions are returned WITHOUT correct answers to prevent cheating.
    """
    # Query assessment
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.assessment_questions))
        .where(
            Assessment.id == assessment_id,
            Assessment.is_active == True,  # noqa: E712
        )
    )
    assessment = result.scalar()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Build response without correct answers
    questions = [
        AssessmentQuestionResponse(
            id=q.id,
            assessment_id=q.assessment_id,
            question_type=q.question_type,
            skill_category=q.skill_category,
            question_text=q.question_text,
            options=json.loads(q.options) if q.options else None,
            points=q.points,
            order_index=q.order_index,
        )
        for q in sorted(assessment.assessment_questions, key=lambda x: x.order_index)
    ]

    skill_categories = list({q.skill_category for q in questions})

    return AssessmentDetailResponse(
        id=assessment.id,
        language=assessment.language,
        assessment_type=assessment.assessment_type,
        title=assessment.title,
        description=assessment.description,
        difficulty_level=assessment.difficulty_level,
        duration_minutes=assessment.duration_minutes,
        skill_categories=skill_categories,
        is_active=assessment.is_active,
        created_at=assessment.created_at,
        question_count=len(questions),
        questions=questions,
    )


@router.post("/{assessment_id}/attempts", response_model=AttemptResultResponse)
async def submit_attempt(
    assessment_id: int,
    attempt_data: AttemptCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit assessment answers and get scored results.

    Returns overall score, recommended CEFR level, and per-skill breakdown.
    """
    # Get assessment with questions
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.assessment_questions))
        .where(
            Assessment.id == assessment_id,
            Assessment.is_active == True,  # noqa: E712
        )
    )
    assessment = result.scalar()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Validate question IDs
    valid_question_ids = {str(q.id) for q in assessment.assessment_questions}
    invalid_ids = set(attempt_data.answers.keys()) - valid_question_ids
    if invalid_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question ID in answers: {', '.join(sorted(invalid_ids))}",
        )

    # Prepare questions for scoring
    questions = [
        {
            "id": str(q.id),
            "skill_category": q.skill_category,
            "correct_answer": q.correct_answer,
            "points": q.points,
        }
        for q in assessment.assessment_questions
    ]

    # Calculate scores
    scores = calculate_scores(questions, attempt_data.answers)
    overall_score = scores["overall"]["score"]
    recommended_level = determine_cefr_level(overall_score)

    # Build skill scores list
    skill_scores = [
        SkillScore(
            skill=skill,
            score=data["score"],
            total=data["total"],
            correct=data["correct"],
        )
        for skill, data in scores.items()
        if skill != "overall"
    ]

    # Generate recommendations
    skill_scores_dict = {k: v for k, v in scores.items() if k != "overall"}
    recommendations = generate_practice_recommendations(skill_scores_dict)

    # Store attempt
    attempt = AssessmentAttempt(
        assessment_id=assessment_id,
        language=assessment.language,
        score=overall_score,
        recommended_level=recommended_level,
        skill_scores_json=json.dumps([s.model_dump() for s in skill_scores]),
        total_questions=scores["overall"]["total"],
        correct_answers=scores["overall"]["correct"],
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        answers_json=json.dumps(attempt_data.answers),
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    logger.info(
        f"Assessment attempt {attempt.id}: score={overall_score:.1f}%, "
        f"recommended={recommended_level}"
    )

    return AttemptResultResponse(
        id=attempt.id,
        assessment_id=assessment_id,
        language=assessment.language,
        score=overall_score,
        recommended_level=recommended_level,
        skill_scores=skill_scores,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        practice_recommendations=recommendations,
    )
