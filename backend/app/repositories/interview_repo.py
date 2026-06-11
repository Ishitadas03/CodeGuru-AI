import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.interview import InterviewSession


class InterviewRepository(BaseRepository[InterviewSession]):
    """Repository managing InterviewSession database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(InterviewSession, db)

    async def get_session_by_id(self, session_id: uuid.UUID) -> Optional[InterviewSession]:
        """Fetch an interview session by its ID."""
        return await self.get(session_id)

    async def get_sessions_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[InterviewSession]:
        """Fetch chronological interview sessions for a specific user."""
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_session(
        self,
        *,
        user_id: uuid.UUID,
        topic: str,
        difficulty: str
    ) -> InterviewSession:
        """Create and initialize a new interview session."""
        session = InterviewSession(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            messages=[],
            is_completed=False
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_session_messages(
        self,
        *,
        session: InterviewSession,
        messages: List[dict]
    ) -> InterviewSession:
        """Update the message history log for a session."""
        session.messages = messages
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def complete_session(
        self,
        *,
        session: InterviewSession,
        score: int,
        feedback: dict
    ) -> InterviewSession:
        """Complete an interview session and save evaluation metrics."""
        session.score = score
        session.feedback = feedback
        session.is_completed = True
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
