import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.dsa_progress import UserProblemProgress
from app.models.review import CodeReview
from app.models.submission import Submission


@pytest.mark.asyncio
async def test_get_analytics_overview_empty(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that get_overview returns zeroed structures for a new user with no activity."""
    # 1. Setup authenticated user
    email = "analytics_empty@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get analytics overview
    response = await client.get(
        f"{settings.API_V1_STR}/analytics/overview",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["dsa_stats"]["total_solved"] == 0
    assert data["dsa_stats"]["total_attempted"] == 0
    assert data["review_stats"]["total_reviews"] == 0
    assert data["review_stats"]["average_score"] == 0.0
    assert len(data["review_stats"]["common_issues"]) == 0
    assert len(data["review_stats"]["score_history"]) == 0
    assert data["streak"]["current_streak"] == 0
    assert data["streak"]["longest_streak"] == 0
    assert len(data["heatmap"]) > 360  # Should be populated for the last 365 days


@pytest.mark.asyncio
async def test_manual_dsa_progress_update(client: AsyncClient, db: AsyncSession) -> None:
    """Verify manual upserting of DSA progress via endpoints."""
    email = "analytics_manual@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Post progress update
    response = await client.post(
        f"{settings.API_V1_STR}/analytics/dsa/progress",
        json={
            "problem_id": "two-sum",
            "topic_slug": "arrays",
            "status": "solved",
            "language": "python",
            "code": "def twoSum(): pass"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["problem_id"] == "two-sum"
    assert data["status_value"] == "solved"

    # Verify overview reflects this solved problem
    overview_res = await client.get(
        f"{settings.API_V1_STR}/analytics/overview",
        headers=headers
    )
    assert overview_res.status_code == 200
    overview = overview_res.json()
    assert overview["dsa_stats"]["total_solved"] == 1
    assert overview["dsa_stats"]["solved_by_difficulty"]["easy"] == 1
    assert overview["dsa_stats"]["solved_by_topic"]["arrays"] == 1
    assert overview["streak"]["current_streak"] == 1


@pytest.mark.asyncio
async def test_explain_dsa_problem_updates_analytics(client: AsyncClient, db: AsyncSession) -> None:
    """Verify calling the explain API endpoint automatically saves progress and updates analytics."""
    email = "analytics_explain@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock response from LLM for DSA Explanation
    mock_teacher_response = """{
        "concept_name": "Two Sum HashMap",
        "explanation": "Solve it using dict.",
        "complexity": {
            "time_complexity": "O(N)",
            "time_explanation": "Single loop.",
            "space_complexity": "O(N)",
            "space_explanation": "Space used."
        },
        "dry_run": []
    }"""

    with patch("app.agents.teacher_agent.TeacherAgent._call_llm", new_callable=AsyncMock) as mock_teach:
        mock_teach.return_value = mock_teacher_response

        # Request explanation (which triggers DB progress save)
        explain_res = await client.post(
            f"{settings.API_V1_STR}/dsa/problems/two-sum/explain",
            json={
                "code": "def twoSum(nums, target): pass",
                "language": "python"
            },
            headers=headers
        )
        assert explain_res.status_code == 200

    # Get overview and assert stats changed
    overview_res = await client.get(
        f"{settings.API_V1_STR}/analytics/overview",
        headers=headers
    )
    assert overview_res.status_code == 200
    overview = overview_res.json()
    assert overview["dsa_stats"]["total_solved"] == 1
    assert overview["streak"]["current_streak"] == 1


@pytest.mark.asyncio
async def test_streak_calculation_consecutive_days(client: AsyncClient, db: AsyncSession) -> None:
    """Verify streak counting works correctly when active dates span multiple consecutive days."""
    email = "analytics_streak@example.com"
    reg_res = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    import uuid
    user_id = uuid.UUID(reg_res.json()["id"])

    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Manually inject historical submissions to test streak logic
    now = datetime.now(timezone.utc)
    
    # Active today, yesterday, and day before yesterday (3-day streak)
    dates_to_inject = [
        now,
        now - timedelta(days=1),
        now - timedelta(days=2),
        now - timedelta(days=5),  # Gap of two days, then another active day
    ]

    for idx, dt in enumerate(dates_to_inject):
        sub = Submission(
            user_id=user_id,
            language="python",
            code="print('streak test')",
            created_at=dt,
            updated_at=dt
        )

        db.add(sub)
        await db.flush()

        review = CodeReview(
            submission_id=sub.id,
            score=80 + idx,
            summary="Streak test review",
            issues=[{"category": "performance", "description": "suboptimal"}],
            refactored_code="print('streak')",
            has_bugs=False,
            bugs=[],
            created_at=dt,
            updated_at=dt
        )
        db.add(review)

    await db.commit()

    # Get overview
    overview_res = await client.get(
        f"{settings.API_V1_STR}/analytics/overview",
        headers=headers
    )
    assert overview_res.status_code == 200
    overview = overview_res.json()
    
    # 3 consecutive days active from today (today, yesterday, day before)
    assert overview["streak"]["current_streak"] == 3
    assert overview["streak"]["longest_streak"] == 3
    assert overview["review_stats"]["total_reviews"] == 4
    assert overview["review_stats"]["average_score"] == 81.5
    assert len(overview["review_stats"]["common_issues"]) == 1
    assert overview["review_stats"]["common_issues"][0]["category"] == "performance"
    assert overview["review_stats"]["common_issues"][0]["count"] == 4
