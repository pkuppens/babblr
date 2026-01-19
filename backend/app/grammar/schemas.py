"""Request/response schemas for grammar endpoints."""

from typing import Optional, Union

from pydantic import BaseModel, Field


class SubmitExerciseRequest(BaseModel):
    """Request schema for submitting an exercise answer."""

    answer: Union[str, int, list] = Field(
        ...,
        description="User's answer (string for fill-in, int for multiple choice, list for word order)",
    )
    lesson_session_id: Optional[str] = Field(None, description="Optional session identifier")
    time_taken_seconds: int = Field(default=0, description="Time taken to answer in seconds")
    hints_used: int = Field(default=0, description="Number of hints used")


class ExerciseResult(BaseModel):
    """Response schema for exercise submission result."""

    is_correct: bool
    correct_answer: Union[str, int, list] = Field(
        ..., description="Correct answer (type depends on exercise type)"
    )
    explanation: str
    mastery_delta: float = Field(
        ..., description="Change in mastery score (positive for correct, negative for incorrect)"
    )
