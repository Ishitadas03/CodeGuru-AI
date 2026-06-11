from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dsa import TopicResponse, ProblemResponse, ExplanationResponse, ExplainRequest
from app.services.dsa_service import DSAService
from app.core.exceptions import NotFoundError

router = APIRouter()
dsa_service = DSAService()


@router.get("/topics", response_model=List[TopicResponse])
def get_topics(
    current_user: User = Depends(get_current_user)
) -> List[TopicResponse]:
    """Fetch all supported data structure and algorithm topics."""
    return dsa_service.get_topics()


@router.get("/topics/{slug}", response_model=TopicResponse)
def get_topic_details(
    slug: str,
    current_user: User = Depends(get_current_user)
) -> TopicResponse:
    """Fetch a single DSA topic's metadata by its slug."""
    topic = dsa_service.get_topic_by_slug(slug)
    if not topic:
        raise NotFoundError("DSA topic not found.")
    return topic


@router.get("/problems", response_model=List[ProblemResponse])
def get_problems(
    topic_slug: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[ProblemResponse]:
    """Fetch all coding challenges catalog, optionally filtered by topic slug."""
    return dsa_service.get_problems(topic_slug)


@router.get("/problems/{problem_id}", response_model=ProblemResponse)
def get_problem_details(
    problem_id: str,
    current_user: User = Depends(get_current_user)
) -> ProblemResponse:
    """Fetch a specific coding challenge definition by ID."""
    problem = dsa_service.get_problem_by_id(problem_id)
    if not problem:
        raise NotFoundError("Coding challenge not found.")
    return problem


@router.post("/problems/{problem_id}/explain", response_model=ExplanationResponse)
async def explain_solution_code(
    problem_id: str,
    payload: ExplainRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExplanationResponse:
    """Submit code solution for a challenge to receive interactive compiler traces and complexity analysis."""
    explanation = await dsa_service.explain_concept_for_problem(
        db=db,
        user_id=current_user.id,
        problem_id=problem_id,
        code=payload.code,
        language=payload.language
    )
    return explanation

