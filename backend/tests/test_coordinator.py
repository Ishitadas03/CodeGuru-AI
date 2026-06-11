import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.mark.asyncio
async def test_coordinator_route_requires_auth(client: AsyncClient) -> None:
    """Verify that posting to coordinator route without auth returns 401."""
    response = await client.post(
        f"{settings.API_V1_STR}/coordinator/route",
        json={"user_input": "hello"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_coordinator_route_empty_query(client: AsyncClient) -> None:
    """Verify empty query returns validation error."""
    # 1. Setup authenticated user
    email = "coord_test@example.com"
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

    response = await client.post(
        f"{settings.API_V1_STR}/coordinator/route",
        json={"user_input": "  "},
        headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_coordinator_route_review_success(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that coordinator correctly routes code review requests."""
    # 1. Setup authenticated user
    email = "coord_review@example.com"
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

    # Mock coordinator classification output
    mock_coord_response = """{
        "intent": "review",
        "confidence": 0.95,
        "reasoning": "User submitted python code block for review.",
        "parameters": {
            "language": "python",
            "code": "def func(): pass"
        }
    }"""
    mock_reviewer_response = """{
        "score": 88,
        "summary": "Clean python code block.",
        "issues": [],
        "refactored_code": "def func(): pass"
    }"""
    mock_debugger_response = """{
        "has_bugs": false,
        "bugs": []
    }"""

    # Mock all internal LLM calls
    with patch("app.agents.coordinator_agent.CoordinatorAgent._call_llm", new_callable=AsyncMock) as mock_coord, \
         patch("app.agents.reviewer_agent.ReviewerAgent._call_llm", new_callable=AsyncMock) as mock_rev, \
         patch("app.agents.debugger_agent.DebuggerAgent._call_llm", new_callable=AsyncMock) as mock_deb:
        
        mock_coord.return_value = mock_coord_response
        mock_rev.return_value = mock_reviewer_response
        mock_deb.return_value = mock_debugger_response

        # Execute router
        response = await client.post(
            f"{settings.API_V1_STR}/coordinator/route",
            json={"user_input": "review this code: def func(): pass"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "review"
        assert data["data"]["score"] == 88
        assert data["data"]["has_bugs"] is False


@pytest.mark.asyncio
async def test_coordinator_route_dsa_success(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that coordinator correctly routes DSA concept tracing requests."""
    email = "coord_dsa@example.com"
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

    # Mock coordinator classification output
    mock_coord_response = """{
        "intent": "dsa",
        "confidence": 0.90,
        "reasoning": "User asked about two-sum coding challenges.",
        "parameters": {
            "problem_id": "two-sum",
            "language": "python",
            "code": "def twoSum(): pass"
        }
    }"""
    mock_teacher_response = """{
        "concept_name": "Two Sum",
        "explanation": "Find two numbers in array adding to target.",
        "complexity": {
            "time_complexity": "O(N)",
            "time_explanation": "Single hashmap pass.",
            "space_complexity": "O(N)",
            "space_explanation": "Hashmap stores elements."
        },
        "dry_run": [
            {
                "step": 1,
                "line_number": 2,
                "description": "Initialize empty map.",
                "variables_state": "map={}"
            }
        ]
    }"""

    with patch("app.agents.coordinator_agent.CoordinatorAgent._call_llm", new_callable=AsyncMock) as mock_coord, \
         patch("app.agents.teacher_agent.TeacherAgent._call_llm", new_callable=AsyncMock) as mock_teach:
        
        mock_coord.return_value = mock_coord_response
        mock_teach.return_value = mock_teacher_response

        response = await client.post(
            f"{settings.API_V1_STR}/coordinator/route",
            json={"user_input": "explain two-sum solution: def twoSum(): pass"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "dsa"
        assert data["data"]["concept_name"] == "Two Sum"
        assert data["data"]["complexity"]["time_complexity"] == "O(N)"


@pytest.mark.asyncio
async def test_coordinator_route_general_fallback(client: AsyncClient, db: AsyncSession) -> None:
    """Verify general conversation fallback when user asks an arbitrary question."""
    email = "coord_general@example.com"
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

    # Mock coordinator classification output
    mock_coord_response = """{
        "intent": "general",
        "confidence": 1.0,
        "reasoning": "Standard greeting.",
        "parameters": {}
    }"""
    mock_general_chat_response = "Hello! I am your AI coding mentor. How can I help you today?"

    with patch("app.agents.coordinator_agent.CoordinatorAgent._call_llm", new_callable=AsyncMock) as mock_coord:
        # Mock first call (classification), and second call (general chat response)
        mock_coord.side_effect = [mock_coord_response, mock_general_chat_response]

        response = await client.post(
            f"{settings.API_V1_STR}/coordinator/route",
            json={"user_input": "hello!"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "general"
        assert data["response"] == "Hello! I am your AI coding mentor. How can I help you today?"
