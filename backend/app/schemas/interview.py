import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewStartRequest(BaseModel):
    """Request schema to initialize a new interview session."""
    topic: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The main technical topic of the interview (e.g. System Design, Algorithms)."
    )
    difficulty: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The level of difficulty (easy, medium, hard)."
    )


class InterviewMessageRequest(BaseModel):
    """Request schema for sending a user reply/message in a session."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Candidate's verbal response or code submission during the interview."
    )


class InterviewMessage(BaseModel):
    """Schema representing a single message within the session log."""
    role: str = Field(..., description="Role of the message creator (interviewer or user).")
    content: str = Field(..., description="Message text or code.")


class InterviewEvaluationResponse(BaseModel):
    """Schema representing the completed interview scorecard and feedback report."""
    model_config = ConfigDict(from_attributes=True)

    score: int = Field(..., ge=0, le=100, description="Overall score out of 100.")
    summary: str = Field(..., description="Qualitative performance summary.")
    strengths: List[str] = Field(..., description="Key technical/behavioral strengths.")
    weakness_areas: List[str] = Field(..., description="Key improvement focus areas.")
    correct_code_suggestions: str = Field(..., description="Optimal code solution or design snippet in markdown.")
    improvement_tips: List[str] = Field(..., description="List of actionable practice tips.")


class InterviewSessionResponse(BaseModel):
    """Full session response schema detailing progress, messages, and any evaluation."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    topic: str
    difficulty: str
    messages: List[InterviewMessage]
    score: Optional[int] = None
    feedback: Optional[InterviewEvaluationResponse] = None
    is_completed: bool
    created_at: datetime
