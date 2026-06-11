import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.mark.asyncio
async def test_interview_session_lifecycle(client: AsyncClient, db: AsyncSession) -> None:
    """Verify starting, chatting, ending, and fetching history for an interview session."""
    # 1. Setup authenticated user
    email = "interview_candidate@example.com"
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

    # 2. Mock Agent calls
    mock_intro_response = """{
        "response": "Welcome! Let's start the System Design interview on hard difficulty. Can you describe how you would design a rate limiter?",
        "focus_area": "System Design"
    }"""
    mock_followup_response = """{
        "response": "Good choice of token bucket. How would you handle rate limiting across a distributed Redis cluster?",
        "focus_area": "Optimizations"
    }"""
    mock_evaluation_response = """{
        "score": 85,
        "summary": "Demonstrated excellent understanding of rate limiting and token bucket. Had some gaps in distributed Redis configurations.",
        "strengths": ["Clear communication", "Good trade-off understanding of token bucket"],
        "weakness_areas": ["Redis cluster synchronization overheads"],
        "correct_code_suggestions": "// Token bucket algorithm implementation details",
        "improvement_tips": ["Read about redis cell module or sliding window log in redis"]
    }"""

    with patch("app.agents.interviewer_agent.InterviewerAgent._call_llm", new_callable=AsyncMock) as mock_agent:
        # --- A. Start Interview Session ---
        mock_agent.return_value = mock_intro_response
        start_res = await client.post(
            f"{settings.API_V1_STR}/interview/start",
            json={"topic": "System Design", "difficulty": "hard"},
            headers=headers
        )
        assert start_res.status_code == 201
        session_data = start_res.json()
        assert session_data["topic"] == "System Design"
        assert session_data["difficulty"] == "hard"
        assert session_data["is_completed"] is False
        assert len(session_data["messages"]) == 1
        assert session_data["messages"][0]["role"] == "interviewer"
        assert "rate limiter" in session_data["messages"][0]["content"]
        session_id = session_data["id"]

        # --- B. Send User Answer / Chat ---
        mock_agent.return_value = mock_followup_response
        chat_res = await client.post(
            f"{settings.API_V1_STR}/interview/{session_id}/message",
            json={"message": "I would use a token bucket algorithm to rate limit requests. Every user has a bucket of tokens."},
            headers=headers
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert len(chat_data["messages"]) == 3  # [intro, user_reply, followup]
        assert chat_data["messages"][1]["role"] == "user"
        assert chat_data["messages"][2]["role"] == "interviewer"
        assert "Redis cluster" in chat_data["messages"][2]["content"]

        # --- C. End Interview Session and get scorecard ---
        mock_agent.return_value = mock_evaluation_response
        end_res = await client.post(
            f"{settings.API_V1_STR}/interview/{session_id}/end",
            headers=headers
        )
        assert end_res.status_code == 200
        end_data = end_res.json()
        assert end_data["is_completed"] is True
        assert end_data["score"] == 85
        assert end_data["feedback"]["score"] == 85
        assert len(end_data["feedback"]["strengths"]) == 2

        # --- D. Fetch Session History ---
        history_res = await client.get(
            f"{settings.API_V1_STR}/interview/sessions",
            headers=headers
        )
        assert history_res.status_code == 200
        history_data = history_res.json()
        assert len(history_data) >= 1
        assert history_data[0]["id"] == session_id

        # --- E. Get Single Session Details ---
        get_res = await client.get(
            f"{settings.API_V1_STR}/interview/{session_id}",
            headers=headers
        )
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["id"] == session_id
        assert get_data["score"] == 85

        # --- F. Validation: Action on completed session should fail ---
        fail_chat_res = await client.post(
            f"{settings.API_V1_STR}/interview/{session_id}/message",
            json={"message": "I want to continue the interview."},
            headers=headers
        )
        assert fail_chat_res.status_code == 422

        fail_end_res = await client.post(
            f"{settings.API_V1_STR}/interview/{session_id}/end",
            headers=headers
        )
        assert fail_end_res.status_code == 422


@pytest.mark.asyncio
async def test_interview_end_without_answers(client: AsyncClient, db: AsyncSession) -> None:
    """Verify that ending an interview immediately without answering results in zero score and basic comments."""
    email = "empty_candidate@example.com"
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

    mock_intro_response = """{
        "response": "Welcome! Let's start the System Design interview.",
        "focus_area": "System Design"
    }"""

    with patch("app.agents.interviewer_agent.InterviewerAgent._call_llm", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_intro_response
        start_res = await client.post(
            f"{settings.API_V1_STR}/interview/start",
            json={"topic": "System Design", "difficulty": "hard"},
            headers=headers
        )
        session_id = start_res.json()["id"]

        # End immediately without replying to the intro
        end_res = await client.post(
            f"{settings.API_V1_STR}/interview/{session_id}/end",
            headers=headers
        )
        assert end_res.status_code == 200
        end_data = end_res.json()
        assert end_data["is_completed"] is True
        assert end_data["score"] == 0
        assert "no answers provided" in end_data["feedback"]["summary"]
