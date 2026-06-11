from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsOverviewResponse, DSAProgressUpdateRequest
from app.services.analytics_service import AnalyticsService
from app.repositories.dsa_progress_repo import DSAProgressRepository

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnalyticsOverviewResponse:
    """Fetch aggregated study analytics, streaks, and chart data for the current user."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_overview(current_user.id)


@router.post("/dsa/progress", status_code=status.HTTP_200_OK)
async def update_dsa_problem_progress(
    payload: DSAProgressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually record or override a user's progress on a specific DSA problem."""
    dsa_repo = DSAProgressRepository(db)
    progress = await dsa_repo.upsert_progress(
        user_id=current_user.id,
        problem_id=payload.problem_id,
        topic_slug=payload.topic_slug,
        status=payload.status,
        language=payload.language,
        code=payload.code
    )
    return {
        "status": "success",
        "problem_id": progress.problem_id,
        "status_value": progress.status
    }
