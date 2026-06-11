import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.dsa_progress import UserProblemProgress


class DSAProgressRepository(BaseRepository[UserProblemProgress]):
    """Repository managing UserProblemProgress database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(UserProblemProgress, db)

    async def get_by_problem(self, user_id: uuid.UUID, problem_id: str) -> Optional[UserProblemProgress]:
        """Fetch progress for a specific user and problem."""
        result = await self.db.execute(
            select(UserProblemProgress)
            .where(UserProblemProgress.user_id == user_id)
            .where(UserProblemProgress.problem_id == problem_id)
        )
        return result.scalars().first()

    async def get_user_progress(self, user_id: uuid.UUID) -> List[UserProblemProgress]:
        """Fetch all problem progress records for a user."""
        result = await self.db.execute(
            select(UserProblemProgress)
            .where(UserProblemProgress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def upsert_progress(
        self,
        *,
        user_id: uuid.UUID,
        problem_id: str,
        topic_slug: str,
        status: str,
        language: str,
        code: str
    ) -> UserProblemProgress:
        """Create or update a user's progress on a DSA problem."""
        existing = await self.get_by_problem(user_id=user_id, problem_id=problem_id)
        
        now = datetime.now(timezone.utc)
        
        if existing:
            existing.language = language
            existing.code = code
            existing.last_attempted_at = now
            
            # Upgrade status to solved if currently solved, or retain solved status
            if status == "solved" or existing.status == "solved":
                existing.status = "solved"
                if not existing.solved_at:
                    existing.solved_at = now
            else:
                existing.status = status
                
            self.db.add(existing)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            solved_at = now if status == "solved" else None
            new_progress = UserProblemProgress(
                user_id=user_id,
                problem_id=problem_id,
                topic_slug=topic_slug,
                status=status,
                language=language,
                code=code,
                solved_at=solved_at,
                last_attempted_at=now
            )
            self.db.add(new_progress)
            await self.db.commit()
            await self.db.refresh(new_progress)
            return new_progress
