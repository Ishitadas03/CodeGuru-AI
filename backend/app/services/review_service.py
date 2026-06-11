import asyncio
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.debugger_agent import DebuggerAgent
from app.repositories.review_repo import ReviewRepository
from app.models.review import CodeReview


class ReviewService:
    """Service coordinating code submission, concurrent agent reasoning, and database tracking."""

    def _get_ai_provider(self):
        """Dynamic resolution of LLM provider: defaults to OpenAI, falls back to local Ollama."""
        # Simple validation check on secret key
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-xxxx") and settings.OPENAI_API_KEY != "MOCK_KEY" and settings.OPENAI_API_KEY.strip():
            return OpenAIProvider(model="gpt-4o-mini")
        else:
            return OllamaProvider(model="codellama")

    async def submit_code_review(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        code: str,
        language: str
    ) -> CodeReview:
        """Create code submission, execute analysis agents concurrently, and persist review report."""
        repo = ReviewRepository(db)
        
        # 1. Save submission details
        submission = await repo.create_submission(
            user_id=user_id,
            code=code,
            language=language
        )

        # 2. Run the CodeReviewEngine pipeline
        from app.engine.review_engine import CodeReviewEngine
        engine = CodeReviewEngine()
        result = await engine.analyze(code, language)

        # 3. Save CodeReview report including static_analysis
        review = await repo.create_code_review(
            submission_id=submission.id,
            score=result.get("score", 0),
            summary=result.get("summary", "No summary provided."),
            issues=result.get("issues", []),
            refactored_code=result.get("refactored_code", code),
            has_bugs=result.get("has_bugs", False),
            bugs=result.get("bugs", []),
            static_analysis=result.get("static_analysis")
        )
        return review

    async def get_review(self, db: AsyncSession, review_id: uuid.UUID) -> Optional[CodeReview]:
        """Retrieve a specific code review by ID."""
        repo = ReviewRepository(db)
        return await repo.get_review_by_id(review_id)

    async def get_user_review_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[CodeReview]:
        """Retrieve review history list for a user."""
        repo = ReviewRepository(db)
        return await repo.get_history_by_user(user_id, skip=skip, limit=limit)

