import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.agents.interviewer_agent import InterviewerAgent
from app.repositories.interview_repo import InterviewRepository
from app.models.interview import InterviewSession


class InterviewService:
    """Service managing technical mock interview flows, chatbot states, and evaluation reports."""

    def _get_ai_provider(self):
        """Dynamic resolution of LLM provider: defaults to OpenAI, falls back to local Ollama."""
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-xxxx") and settings.OPENAI_API_KEY != "MOCK_KEY" and settings.OPENAI_API_KEY.strip():
            return OpenAIProvider(model="gpt-4o-mini")
        else:
            return OllamaProvider(model="codellama")

    async def start_interview_session(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        topic: str,
        difficulty: str
    ) -> InterviewSession:
        """Initialize a new mock interview session and generate the first interviewer question."""
        repo = InterviewRepository(db)
        
        # 1. Create and persist empty session
        session = await repo.create_session(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty
        )

        # 2. Query Agent for introductory question
        from app.models.user import User
        from app.core.config import SubscriptionTier
        
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        tier_str = getattr(user, "subscription_tier", "free") if user else "free"
        tier = SubscriptionTier(tier_str)

        provider = self._get_ai_provider()
        agent = InterviewerAgent(provider, db=db, user_id=user_id, tier=tier)
        
        agent_res = await agent.generate_next_response(
            topic=topic,
            difficulty=difficulty,
            messages=[]
        )

        first_message = {
            "role": "interviewer",
            "content": agent_res.get("response", f"Welcome! Let's start the {topic} interview on {difficulty} level. Can you briefly introduce your experience with this?")
        }

        # 3. Update session with first message
        updated_session = await repo.update_session_messages(
            session=session,
            messages=[first_message]
        )
        return updated_session

    async def get_session(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> InterviewSession:
        """Fetch details of an interview session, asserting authorization."""
        repo = InterviewRepository(db)
        session = await repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundError("Interview session not found.")
        if session.user_id != user_id:
            raise ForbiddenError("You do not have access to this interview session.")
        return session

    async def get_user_sessions(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[InterviewSession]:
        """Fetch historical mock interview sessions list for a specific user."""
        repo = InterviewRepository(db)
        return await repo.get_sessions_by_user(user_id=user_id, skip=skip, limit=limit)

    async def send_user_message(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        message: str
    ) -> InterviewSession:
        """Append user message to session chat and query interviewer for the next follow-up question."""
        repo = InterviewRepository(db)
        session = await self.get_session(db, session_id=session_id, user_id=user_id)

        if session.is_completed:
            raise ValidationError("This interview session has already been completed.")

        # 1. Append User message
        messages = list(session.messages)
        messages.append({
            "role": "user",
            "content": message
        })

        # 2. Query Agent for next interviewer response
        from app.models.user import User
        from app.core.config import SubscriptionTier
        
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        tier_str = getattr(user, "subscription_tier", "free") if user else "free"
        tier = SubscriptionTier(tier_str)

        provider = self._get_ai_provider()
        agent = InterviewerAgent(provider, db=db, user_id=user_id, tier=tier)
        
        agent_res = await agent.generate_next_response(
            topic=session.topic,
            difficulty=session.difficulty,
            messages=messages
        )

        # 3. Append Interviewer response
        messages.append({
            "role": "interviewer",
            "content": agent_res.get("response", "Thank you. Let's move on to the next question.")
        })

        # 4. Save and return session
        updated_session = await repo.update_session_messages(
            session=session,
            messages=messages
        )
        return updated_session

    async def end_interview_session(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> InterviewSession:
        """End the interview session and trigger AI generation of overall scorecard and performance review."""
        repo = InterviewRepository(db)
        session = await self.get_session(db, session_id=session_id, user_id=user_id)

        if session.is_completed:
            raise ValidationError("This interview session has already been completed.")

        # If there are no candidate messages, complete session with default low/empty score
        candidate_replies = [msg for msg in session.messages if msg.get("role") == "user"]
        if not candidate_replies:
            evaluation = {
                "score": 0,
                "summary": "Interview completed with no answers provided by the candidate.",
                "strengths": [],
                "weakness_areas": ["Candidate did not provide any input."],
                "correct_code_suggestions": "// No candidate inputs received to comment on.",
                "improvement_tips": ["Participate in the dialogue by typing answers to the interviewer's prompts."]
            }
            completed_session = await repo.complete_session(
                session=session,
                score=0,
                feedback=evaluation
            )
            return completed_session

        # 1. Query Agent for session evaluation scorecard
        from app.models.user import User
        from app.core.config import SubscriptionTier
        
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        tier_str = getattr(user, "subscription_tier", "free") if user else "free"
        tier = SubscriptionTier(tier_str)

        provider = self._get_ai_provider()
        agent = InterviewerAgent(provider, db=db, user_id=user_id, tier=tier)
        
        evaluation = await agent.evaluate_session(
            topic=session.topic,
            difficulty=session.difficulty,
            messages=session.messages
        )

        score = evaluation.get("score", 50)

        # 2. Mark session completed and save evaluation
        completed_session = await repo.complete_session(
            session=session,
            score=score,
            feedback=evaluation
        )
        return completed_session
