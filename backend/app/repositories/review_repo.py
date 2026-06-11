import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.review import CodeReview
from app.models.submission import Submission


class ReviewRepository(BaseRepository[CodeReview]):
    """Repository managing CodeReview and associated Submission database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(CodeReview, db)

    async def create_submission(
        self,
        *,
        user_id: uuid.UUID,
        code: str,
        language: str
    ) -> Submission:
        """Create and persist a new user code submission."""
        submission = Submission(user_id=user_id, code=code, language=language)
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async def create_code_review(
        self,
        *,
        submission_id: uuid.UUID,
        score: int,
        summary: str,
        issues: List[dict],
        refactored_code: str,
        has_bugs: bool,
        bugs: List[dict],
        static_analysis: Optional[dict] = None
    ) -> CodeReview:
        """Create and persist a new code review report."""
        review = CodeReview(
            submission_id=submission_id,
            score=score,
            summary=summary,
            issues=issues,
            refactored_code=refactored_code,
            has_bugs=has_bugs,
            bugs=bugs,
            static_analysis=static_analysis
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_review_by_id(self, review_id: uuid.UUID) -> Optional[CodeReview]:
        """Fetch code review by ID with submission eagerly loaded."""
        result = await self.db.execute(
            select(CodeReview)
            .where(CodeReview.id == review_id)
            .options(selectinload(CodeReview.submission))
        )
        return result.scalars().first()

    async def get_history_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[CodeReview]:
        """Fetch the chronological review history associated with a user ID."""
        result = await self.db.execute(
            select(CodeReview)
            .join(Submission)
            .where(Submission.user_id == user_id)
            .order_by(CodeReview.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_reviews_by_user(self, user_id: uuid.UUID) -> List[CodeReview]:
        """Fetch all reviews for a user chronologically without limit (for analytics)."""
        result = await self.db.execute(
            select(CodeReview)
            .join(Submission)
            .where(Submission.user_id == user_id)
            .order_by(CodeReview.created_at.asc())
        )
        return list(result.scalars().all())

