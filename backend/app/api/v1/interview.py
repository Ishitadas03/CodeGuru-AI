import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewMessageRequest,
    InterviewSessionResponse
)
from app.services.interview_service import InterviewService

router = APIRouter()
interview_service = InterviewService()


@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: InterviewStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InterviewSessionResponse:
    """Initialize a new mock technical interview session."""
    session = await interview_service.start_interview_session(
        db=db,
        user_id=current_user.id,
        topic=payload.topic,
        difficulty=payload.difficulty
    )
    return session


@router.get("/sessions", response_model=List[InterviewSessionResponse])
async def list_interview_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[InterviewSessionResponse]:
    """Retrieve the user's historical interview sessions list."""
    sessions = await interview_service.get_user_sessions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return sessions


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InterviewSessionResponse:
    """Retrieve detailed state of a specific interview session."""
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )
    return session


@router.post("/{session_id}/message", response_model=InterviewSessionResponse)
async def send_interview_message(
    session_id: uuid.UUID,
    payload: InterviewMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InterviewSessionResponse:
    """Send candidate's response message and receive the interviewer's follow-up question."""
    session = await interview_service.send_user_message(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        message=payload.message
    )
    return session


@router.post("/{session_id}/end", response_model=InterviewSessionResponse)
async def end_interview(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InterviewSessionResponse:
    """Complete the mock interview session and compile the performance evaluation scorecard."""
    session = await interview_service.end_interview_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )
    return session
