import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_topics(client: AsyncClient) -> None:
    """Verify that a user can fetch all DSA topics."""
    # 1. Setup authenticated user
    email = "dsa_test1@example.com"
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

    # 2. Call endpoint
    response = await client.get(
        f"{settings.API_V1_STR}/dsa/topics",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(topic["slug"] == "arrays" for topic in data)


@pytest.mark.asyncio
async def test_get_topic_details_success(client: AsyncClient) -> None:
    """Verify that a user can fetch a single DSA topic by slug."""
    email = "dsa_test2@example.com"
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

    # Retrieve valid slug
    response = await client.get(
        f"{settings.API_V1_STR}/dsa/topics/arrays",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Arrays & Hashing"


@pytest.mark.asyncio
async def test_get_topic_details_not_found(client: AsyncClient) -> None:
    """Verify that requesting a non-existent topic returns 404."""
    email = "dsa_test3@example.com"
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

    response = await client.get(
        f"{settings.API_V1_STR}/dsa/topics/non-existent-slug",
        headers=headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_problems_unfiltered(client: AsyncClient) -> None:
    """Verify that a user can fetch all problems unfiltered."""
    email = "dsa_test4@example.com"
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

    response = await client.get(
        f"{settings.API_V1_STR}/dsa/problems",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_problems_filtered(client: AsyncClient) -> None:
    """Verify that a user can fetch problems filtered by topic slug."""
    email = "dsa_test5@example.com"
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

    response = await client.get(
        f"{settings.API_V1_STR}/dsa/problems?topic_slug=arrays",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(problem["topic_slug"] == "arrays" for problem in data)


@pytest.mark.asyncio
async def test_get_problem_details(client: AsyncClient) -> None:
    """Verify details of a single DSA problem can be retrieved."""
    email = "dsa_test6@example.com"
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

    response = await client.get(
        f"{settings.API_V1_STR}/dsa/problems/two-sum",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Two Sum"
    assert "starter_code" in data
    assert "python" in data["starter_code"]


@pytest.mark.asyncio
async def test_explain_solution_success(client: AsyncClient) -> None:
    """Verify explaining a solution code uses the teacher agent and returns structures."""
    email = "dsa_test7@example.com"
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
        "explanation": "Utilize a hash map to map values to their indices, reducing complexity to O(N).",
        "complexity": {
            "time_complexity": "O(N)",
            "time_explanation": "Each element is visited at most once.",
            "space_complexity": "O(N)",
            "space_explanation": "Hash map stores up to N elements."
        },
        "dry_run": [
            {
                "step": 1,
                "line_number": 2,
                "description": "Initialize index tracker dict.",
                "variables_state": "tracker={}"
            }
        ]
    }"""

    with patch("app.agents.teacher_agent.TeacherAgent._call_llm", new_callable=AsyncMock) as mock_teach:
        mock_teach.return_value = mock_teacher_response

        response = await client.post(
            f"{settings.API_V1_STR}/dsa/problems/two-sum/explain",
            json={
                "code": "def twoSum(nums, target):\\n    tracker = {}\\n    for i, n in enumerate(nums):\\n        diff = target - n\\n        if diff in tracker:\\n            return [tracker[diff], i]\\n        tracker[n] = i",
                "language": "python"
            },
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["concept_name"] == "Two Sum HashMap"
        assert "O(N)" in data["complexity"]["time_complexity"]
        assert len(data["dry_run"]) == 1
        assert data["dry_run"][0]["variables_state"] == "tracker={}"
