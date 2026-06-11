import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.mark.asyncio
async def test_create_review_success(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that a user can request a code review and receive structured reports."""
    # 1. Setup authenticated user
    email = "reviewer_test@example.com"
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

    # 2. Mock Agent outputs to bypass live LLM API calls
    mock_reviewer_response = """{
        "score": 85,
        "summary": "Code is functional but bubble sort is suboptimal.",
        "issues": [
            {
                "category": "performance",
                "line": 4,
                "description": "Bubble sort has O(N^2) complexity.",
                "suggestion": "Consider QuickSort or built-in sorted()."
            }
        ],
        "refactored_code": "def bubble_sort(arr): return sorted(arr)"
    }"""
    mock_debugger_response = """{
        "has_bugs": false,
        "bugs": []
    }"""

    # Patch CodeReviewEngine.analyze
    mock_analyze_res = {
        "score": 85,
        "summary": "Code is functional but bubble sort is suboptimal.",
        "issues": [
            {
                "category": "performance",
                "line": 4,
                "description": "Bubble sort has O(N^2) complexity.",
                "suggestion": "Consider QuickSort or built-in sorted()."
            }
        ],
        "refactored_code": "def bubble_sort(arr): return sorted(arr)",
        "has_bugs": False,
        "bugs": [],
        "static_analysis": {
            "language": "python",
            "treesitter": {"analyzer": "treesitter", "supported": True, "results": {}},
            "pylint": {"analyzer": "pylint", "supported": True, "results": {"lint_score": 100.0, "issues": []}},
            "bandit": {"analyzer": "bandit", "supported": True, "results": {"security_score": 100.0, "findings": []}},
            "radon": {"analyzer": "radon", "supported": True, "results": {"maintainability": {"score": 100.0}}},
        }
    }
    with patch("app.engine.review_engine.CodeReviewEngine.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_analyze_res

        # 3. Request review
        response = await client.post(
            f"{settings.API_V1_STR}/reviews",
            json={"code": "def bubble_sort(arr): ...", "language": "python"},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 85
        assert data["summary"] == "Code is functional but bubble sort is suboptimal."
        assert len(data["issues"]) == 1
        assert data["issues"][0]["category"] == "performance"
        assert data["has_bugs"] is False
        assert len(data["bugs"]) == 0
        assert "id" in data


@pytest.mark.asyncio
async def test_get_review_history(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that a user can fetch their historical code reviews."""
    email = "history_test@example.com"
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

    # Mock outputs
    mock_rev_res = """{
        "score": 90,
        "summary": "Clean code.",
        "issues": [],
        "refactored_code": "def code(): pass"
    }"""
    mock_deb_res = """{
        "has_bugs": false,
        "bugs": []
    }"""

    mock_analyze_res = {
        "score": 90,
        "summary": "Clean code.",
        "issues": [],
        "refactored_code": "def code(): pass",
        "has_bugs": False,
        "bugs": [],
        "static_analysis": {
            "language": "python",
            "treesitter": {"analyzer": "treesitter", "supported": True, "results": {}},
            "pylint": {"analyzer": "pylint", "supported": True, "results": {"lint_score": 100.0, "issues": []}},
            "bandit": {"analyzer": "bandit", "supported": True, "results": {"security_score": 100.0, "findings": []}},
            "radon": {"analyzer": "radon", "supported": True, "results": {"maintainability": {"score": 100.0}}},
        }
    }
    with patch("app.engine.review_engine.CodeReviewEngine.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_analyze_res

        # Create first review
        await client.post(
            f"{settings.API_V1_STR}/reviews",
            json={"code": "def my_code(): pass", "language": "python"},
            headers=headers
        )

        # Retrieve history
        history_res = await client.get(f"{settings.API_V1_STR}/reviews/history", headers=headers)
        assert history_res.status_code == 200
        history_data = history_res.json()
        assert len(history_data) == 1
        assert history_data[0]["score"] == 90
