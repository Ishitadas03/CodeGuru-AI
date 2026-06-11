import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_service import ReviewService
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter()
review_service = ReviewService()


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_code_review(
    payload: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    """Submit a code block to analyze and generate detailed review reports."""
    review = await review_service.submit_code_review(
        db,
        user_id=current_user.id,
        code=payload.code,
        language=payload.language
    )
    return review


@router.get("/history", response_model=List[ReviewResponse])
async def get_my_review_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ReviewResponse]:
    """Fetch the authenticated user's code review history list."""
    history = await review_service.get_user_review_history(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return history


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_code_review_details(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    """Fetch detailed code review findings by ID, enforcing user ownership boundaries."""
    review = await review_service.get_review(db, review_id=review_id)
    if not review:
        raise NotFoundError("Code review report not found.")

    # Eagerly load submission to verify ownership
    submission = review.submission
    if submission.user_id != current_user.id and not current_user.is_superuser:
        raise ForbiddenError("You do not have permission to view this review.")

    return review
